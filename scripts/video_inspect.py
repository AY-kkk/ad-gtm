#!/usr/bin/env python3
"""Inspect local video delivery metadata without uploading or generating media."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path


PROFILES = {
    "vertical-short": {"min_duration": 1.0, "max_duration": 60.0, "ratio": 9 / 16, "ratio_tolerance": 0.04},
    "horizontal-short": {"min_duration": 1.0, "max_duration": 60.0, "ratio": 16 / 9, "ratio_tolerance": 0.04},
}


def run_json(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def probe(path):
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        data = run_json([
            ffprobe, "-v", "error", "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate",
            "-of", "json", str(path),
        ])
        if data is not None:
            return data, "ffprobe"
    mdls = shutil.which("mdls")
    if mdls:
        values = {}
        for key in ["kMDItemDurationSeconds", "kMDItemPixelWidth", "kMDItemPixelHeight", "kMDItemFSSize"]:
            try:
                result = subprocess.run([mdls, "-raw", "-name", key, str(path)], check=True, capture_output=True, text=True)
                value = result.stdout.strip()
                if value and value != "(null)":
                    values[key] = value
            except (OSError, subprocess.CalledProcessError):
                return None, "mdls failed"
        if values.get("kMDItemDurationSeconds") and values.get("kMDItemPixelWidth") and values.get("kMDItemPixelHeight"):
            return {
                "format": {"duration": values["kMDItemDurationSeconds"], "size": values.get("kMDItemFSSize")},
                "streams": [{"codec_type": "video", "width": int(float(values["kMDItemPixelWidth"])), "height": int(float(values["kMDItemPixelHeight"]))}],
            }, "mdls"
    return None, "ffprobe and mdls unavailable"


def check(name, status, value=None, reason=None):
    result = {"status": status}
    if value is not None:
        result["value"] = value
    if reason:
        result["reason"] = reason
    return name, result


def inspect(path, profile_name="vertical-short"):
    path = Path(path)
    profile = PROFILES[profile_name]
    if not path.is_file():
        return {"status": "fail", "file": path.name, "checks": {"file": {"status": "fail", "reason": "file not found"}}}

    data, tool = probe(path)
    checks = dict([check("file", "pass", path.name), check("inspection_tool", "observed", tool)])
    if data is None:
        checks.update(dict([
            check("metadata", "not_run", reason=tool),
            check("duration", "not_run"),
            check("dimensions", "not_run"),
            check("audio_stream", "not_run"),
            check("black_frames", "not_run", reason="requires decoded-frame analysis"),
            check("text_readability", "not_run", reason="requires OCR and sampled frames"),
            check("audio_sync", "not_run", reason="requires continuous audio/video analysis"),
        ]))
        return {"status": "review_required", "file": path.name, "profile": profile_name, "checks": checks,
                "boundary": "Metadata and semantic review were not run; no upload was performed."}

    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    duration = float(fmt["duration"]) if fmt.get("duration") else None
    if duration is None:
        checks["duration"] = {"status": "not_run", "reason": "duration unavailable"}
    else:
        checks["duration"] = {"status": "pass" if profile["min_duration"] <= duration <= profile["max_duration"] else "fail", "value": round(duration, 3), "allowed": [profile["min_duration"], profile["max_duration"]]}
    if not video or not video.get("width") or not video.get("height"):
        checks["dimensions"] = {"status": "fail", "reason": "video stream dimensions unavailable"}
    else:
        width, height = int(video["width"]), int(video["height"])
        actual = width / height
        checks["dimensions"] = {"status": "pass" if abs(actual - profile["ratio"]) <= profile["ratio_tolerance"] else "fail", "value": {"width": width, "height": height, "ratio": round(actual, 4)}}
        checks["video_codec"] = {"status": "observed", "value": video.get("codec_name")}
    if audio:
        checks["audio_stream"] = {"status": "observed", "value": True, "codec": audio.get("codec_name")}
    elif tool == "mdls":
        checks["audio_stream"] = {"status": "not_run", "reason": "mdls metadata does not expose stream types"}
    else:
        checks["audio_stream"] = {"status": "fail", "value": False}
    checks["black_frames"] = {"status": "not_run", "reason": "requires decoded-frame analysis"}
    checks["text_readability"] = {"status": "not_run", "reason": "requires OCR and sampled frames"}
    checks["audio_sync"] = {"status": "not_run", "reason": "requires continuous audio/video analysis"}
    failures = [item for item in checks.values() if item.get("status") == "fail"]
    return {"status": "fail" if failures else "review_required", "file": path.name, "profile": profile_name, "checks": checks,
            "boundary": "Technical metadata was inspected locally. Human, semantic, rights, policy, OCR, and sync review remain separate."}


def markdown(result):
    lines = ["# Video inspection", "", f"- File: `{result['file']}`", f"- Profile: `{result.get('profile', 'unknown')}`", f"- Overall: `{result['status']}`", "", "| Check | Status | Value / reason |", "| --- | --- | --- |"]
    for name, item in result["checks"].items():
        value = item.get("value", item.get("reason", ""))
        lines.append(f"| {name} | `{item['status']}` | {value} |")
    lines += ["", result["boundary"], ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="vertical-short")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args(argv)
    result = inspect(args.video, args.profile)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown(result)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
