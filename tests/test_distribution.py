import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_tools", ROOT / "scripts/skills.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.base = Path(self.work.name)
        self.data = tools.validate(ROOT)

    def test_every_pack_is_self_contained_and_manifest_matches(self):
        for pack, names in self.data["packs"].items():
            with self.subTest(pack=pack):
                archive = tools.build(ROOT, self.data, names, pack, self.base / pack)
                with zipfile.ZipFile(archive) as z:
                    manifest = json.loads(z.read("manifest.json"))
                    self.assertEqual(names, manifest["skills"])
                    self.assertEqual(set(z.namelist()), set(manifest["sha256"]) | {"manifest.json"})
                    for path, digest in manifest["sha256"].items():
                        self.assertEqual(hashlib.sha256(z.read(path)).hexdigest(), digest)
                    dest = self.base / (pack + "-extracted")
                    z.extractall(dest)
                for name in names:
                    folder = dest / "skills" / name
                    self.assertTrue((folder / "SKILL.md").exists())
                    for path in folder.rglob("*.md"):
                        tools.check_links(path, folder)

    def test_build_is_reproducible(self):
        args = (ROOT, self.data, self.data["packs"]["all"], "all")
        a = tools.build(*args, self.base / "first")
        b = tools.build(*args, self.base / "second")
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_single_skill_install_has_all_resources(self):
        target = self.base / "installed"
        tools.install(ROOT, ["ad-storyboard"], target)
        source = ROOT / "skills/ad-storyboard"
        for path in source.rglob("*"):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (target / "ad-storyboard" / path.relative_to(source)).read_bytes())
        self.assertEqual(["ad-storyboard"], [p.name for p in target.iterdir()])

    def test_conflict_preflight_changes_nothing(self):
        target = self.base / "installed"
        old = target / "ad-brief"
        old.mkdir(parents=True)
        (old / "personal.md").write_text("preserve")
        with self.assertRaises(ValueError):
            tools.install(ROOT, ["ad-gtm", "ad-brief"], target)
        self.assertFalse((target / "ad-gtm").exists())
        self.assertEqual("preserve", (old / "personal.md").read_text())

    def test_replace_backs_up_old_skill_and_preserves_neighbors(self):
        target = self.base / "installed"
        old = target / "ad-gtm"
        old.mkdir(parents=True)
        (old / "personal.md").write_text("custom instructions")
        neighbor = target / "unrelated"
        neighbor.mkdir()
        result = tools.install(ROOT, ["ad-gtm"], target, replace=True)
        self.assertEqual("custom instructions", (Path(result["backup"]) / "ad-gtm/personal.md").read_text())
        self.assertTrue((old / "SKILL.md").exists())
        self.assertTrue(neighbor.is_dir())

    def test_failed_install_restores_all_replaced_skills(self):
        target = self.base / "installed"
        for name in ["ad-gtm", "ad-brief"]:
            (target / name).mkdir(parents=True)
            (target / name / "old.md").write_text(name)
        real_replace = tools.os.replace

        def fail_second(source, destination):
            if ".ad-gtm-stage-" in str(source) and Path(destination).name == "ad-brief":
                raise OSError("simulated disk failure")
            return real_replace(source, destination)

        with patch.object(tools.os, "replace", side_effect=fail_second):
            with self.assertRaises(OSError):
                tools.install(ROOT, ["ad-gtm", "ad-brief"], target, replace=True)
        for name in ["ad-gtm", "ad-brief"]:
            self.assertEqual(name, (target / name / "old.md").read_text())
            self.assertFalse((target / name / "SKILL.md").exists())

    def test_rejects_install_over_source_checkout(self):
        checkout = self.base / "ad-gtm"
        checkout.mkdir()
        with self.assertRaises(ValueError):
            tools.install(checkout, ["ad-gtm"], self.base, replace=True)

    def test_rejects_symlink_destination(self):
        target = self.base / "installed"
        target.mkdir()
        other = self.base / "private"
        other.mkdir()
        (target / "ad-brief").symlink_to(other, target_is_directory=True)
        with self.assertRaises(ValueError):
            tools.install(ROOT, ["ad-brief"], target, replace=True)

    def test_rejects_unknown_pack_and_traversal_skill(self):
        with self.assertRaises(ValueError):
            tools.select(self.data, pack="missing")
        with self.assertRaises(ValueError):
            tools.select(self.data, skill="../../private")

    def test_rejects_cross_skill_file_dependency(self):
        folder = self.base / "one"
        folder.mkdir()
        (self.base / "two.md").write_text("outside")
        path = folder / "SKILL.md"
        path.write_text("[Required](../two.md)")
        with self.assertRaises(ValueError):
            tools.check_links(path, folder)

    def test_rejects_broken_reference_and_packaged_symlink(self):
        root = self.base / "source"
        shutil.copytree(ROOT / "skills/ad-creative", root / "skills/ad-creative")
        folder = root / "skills/ad-creative"
        (folder / "references/ad-patterns.md").unlink()
        with self.assertRaises(ValueError):
            tools.check_links(folder / "SKILL.md", folder)
        (folder / "secret.md").symlink_to(ROOT / "LICENSE")
        with self.assertRaises(ValueError):
            tools.skill_files(root, "ad-creative")


if __name__ == "__main__":
    unittest.main()
