import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


benchmark = load("benchmark", "scripts/benchmark.py")
video_inspect = load("video_inspect", "scripts/video_inspect.py")


class OfflineToolTests(unittest.TestCase):
    def test_benchmark_uses_safe_denominators(self):
        row = {"spend": 100, "impressions": 1000, "clicks": 20, "conversions": 0, "revenue": 0, "production_cost": 80, "accepted_outputs": 1}
        result = benchmark.metrics(row)
        self.assertEqual(0.02, result["ctr"])
        self.assertIsNone(result["cpa"])
        self.assertEqual(80, result["accepted_output_cost"])

    def test_benchmark_rejects_inconsistent_counts(self):
        row = {"campaign_id": "x", "asset_id": "a", "platform": "p", "objective": "click", "audience": "all", "spend": 1, "impressions": 1, "clicks": 2, "conversions": 0, "revenue": 0}
        with self.assertRaises(ValueError):
            benchmark.validate_row(row, 1)

    def test_video_inspect_without_ffprobe_is_explicitly_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.mp4"
            path.write_bytes(b"placeholder")
            with patch.object(video_inspect.shutil, "which", return_value=None):
                result = video_inspect.inspect(path)
        self.assertEqual("review_required", result["status"])
        self.assertEqual("not_run", result["checks"]["duration"]["status"])
        self.assertEqual("not_run", result["checks"]["audio_sync"]["status"])

    def test_video_inspect_parses_probe_and_checks_vertical_profile(self):
        data = {"format": {"duration": "15.0"}, "streams": [{"codec_type": "video", "codec_name": "h264", "width": 720, "height": 1280}, {"codec_type": "audio", "codec_name": "aac"}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.mp4"
            path.write_bytes(b"placeholder")
            with patch.object(video_inspect.shutil, "which", return_value="ffprobe"), patch.object(video_inspect, "run_json", return_value=data):
                result = video_inspect.inspect(path)
        self.assertEqual("pass", result["checks"]["duration"]["status"])
        self.assertEqual("pass", result["checks"]["dimensions"]["status"])
        self.assertEqual("observed", result["checks"]["audio_stream"]["status"])

    def test_video_inspect_mdls_fallback_keeps_audio_unverified(self):
        data = {"format": {"duration": "15.0"}, "streams": [{"codec_type": "video", "width": 720, "height": 1280}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clip.mp4"
            path.write_bytes(b"placeholder")
            with patch.object(video_inspect, "probe", return_value=(data, "mdls")):
                result = video_inspect.inspect(path)
        self.assertEqual("pass", result["checks"]["dimensions"]["status"])
        self.assertEqual("not_run", result["checks"]["audio_stream"]["status"])


if __name__ == "__main__":
    unittest.main()
