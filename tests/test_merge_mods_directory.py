import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "Tools" / "genshin_merge_mods.py"


class MergeDirectoryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = pathlib.Path(directory.name)
        self.mods = self.root / "Character Mods"
        self.launcher = self.root / "launcher"
        self.mods.mkdir()
        self.launcher.mkdir()
        self.script = self.mods / SCRIPT.name
        shutil.copyfile(SCRIPT, self.script)
        self.selected = self.mods / "Costume" / "mod.ini"
        self.selected.parent.mkdir()
        self.selected.write_text("[TextureOverrideSelectedPosition]\nhash = 12345678\n", encoding="utf-8")
        self.unrelated = self.launcher / "unrelated.ini"
        self.unrelated.write_text("[TextureOverrideUnrelatedPosition]\nhash = 87654321\n", encoding="utf-8")

    def merge(self, cwd, *arguments):
        result = subprocess.run(
            [sys.executable, str(self.script), "-k", "x", *arguments],
            cwd=cwd, input="\n", text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All operations completed", result.stdout)

    def test_default_uses_script_directory_from_an_unrelated_working_directory(self):
        self.merge(self.launcher)

        output = self.mods / "merged.ini"
        self.assertTrue(output.exists(), "Output must be beside the script and selected mods")
        contents = output.read_text(encoding="utf-8")
        self.assertIn("12345678", contents)
        self.assertNotIn("87654321", contents)
        self.assertTrue(self.selected.with_name("DISABLEDmod.ini").exists())
        self.assertTrue(self.unrelated.exists())
        self.assertFalse((self.launcher / "merged.ini").exists())

    def test_default_still_works_when_launched_beside_the_mods(self):
        self.merge(self.mods)

        self.assertIn("12345678", (self.mods / "merged.ini").read_text(encoding="utf-8"))
        self.assertTrue(self.selected.with_name("DISABLEDmod.ini").exists())
        self.assertTrue(self.unrelated.exists())

    def test_explicit_root_keeps_the_callers_working_directory(self):
        self.merge(self.launcher, "--root", ".")

        self.assertIn("87654321", (self.launcher / "merged.ini").read_text(encoding="utf-8"))
        self.assertTrue(self.unrelated.with_name("DISABLEDunrelated.ini").exists())
        self.assertTrue(self.selected.exists())
        self.assertFalse((self.mods / "merged.ini").exists())


if __name__ == "__main__":
    unittest.main()
