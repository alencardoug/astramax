"""Behavioral regressions for portable evidence collection; no network or agents."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/astramax-reviewer/scripts/dossier.py"
spec = importlib.util.spec_from_file_location("dossier", SCRIPT)
dossier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dossier)


def python_command(code):
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"


class DossierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".astramax-test-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "target with spaces"
        self.repo.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid")
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            self.env.pop(key, None)
        self.git("init", "-b", "test-branch")
        (self.repo / "source.txt").write_text("initial\n")
        self.git("add", ".")
        self.git("commit", "-m", "Initial")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.output = self.repo / "REVISAO.md"

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                                capture_output=True, text=True, check=True)
        return result.stdout

    def invoke(self, *args, expected=0, cwd=None):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo", str(self.repo), *args],
                                cwd=cwd or ROOT, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def report(self):
        return self.output.read_text()

    def fill_fields(self):
        evidence, heading, author = self.report().partition("## Intent and acceptance criteria")
        self.output.write_text(evidence + heading + author.replace(
            dossier.PENDING, "None identified; documented scope is limited to this fixture."))

    def test_install_outside_target_collects_worktree_and_untracked(self):
        (self.repo / "source.txt").write_text("changed\n")
        (self.repo / "new file.txt").write_text("new\n")
        self.invoke()
        content = self.report()
        self.assertIn(str(self.repo), content)
        self.assertIn("source.txt", content)
        self.assertIn("new file.txt", content)
        self.assertIn("no tests, builds or other project checks were run", content)
        self.assertNotIn("make test", content)
        self.assertFalse((self.repo / "comandos.txt").exists())
        self.invoke("--check", expected=1)
        self.fill_fields()
        self.invoke("--check")

    def test_default_repo_is_current_directory_and_resolves_subdirectories(self):
        subdir = self.repo / "nested"
        subdir.mkdir()
        result = subprocess.run([sys.executable, "-B", str(SCRIPT)], cwd=subdir, env=self.env,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.output.exists())
        self.assertFalse((subdir / "REVISAO.md").exists())

    def test_unborn_branch_staged_and_untracked(self):
        self.git("checkout", "--orphan", "unborn")
        (self.repo / "untracked.txt").write_text("untracked\n")
        self.invoke()
        self.assertIn("(unborn branch)", self.report())
        self.assertIn("source.txt", self.report())
        self.assertIn("untracked.txt", self.report())

    def test_staged_scope_excludes_unstaged_from_changed_inventory(self):
        (self.repo / "staged.txt").write_text("staged\n")
        self.git("add", "staged.txt")
        (self.repo / "source.txt").write_text("unstaged\n")
        self.invoke("--scope", "staged")
        inventory = self.report().split("Changed tracked paths", 1)[1].split("Read the actual diff", 1)[0]
        self.assertIn("staged.txt", inventory)
        self.assertNotIn("source.txt", inventory)

    def test_staged_checks_require_matching_worktree(self):
        (self.repo / "source.txt").write_text("staged\n")
        self.git("add", "source.txt")
        (self.repo / "source.txt").write_text("different worktree\n")
        result = self.invoke("--scope", "staged", "--command", "touch should-not-exist", expected=2)
        self.assertIn("different snapshot", result.stderr)
        self.assertFalse((self.repo / "should-not-exist").exists())
        self.assertFalse(self.output.exists())

    def test_staged_checks_run_when_worktree_matches_index(self):
        (self.repo / "source.txt").write_text("staged\n")
        self.git("add", "source.txt")
        self.invoke("--scope", "staged", "--command", python_command("print('checked index contents')"))
        self.assertIn("checked index contents", self.report())
        self.assertNotIn(dossier.MACHINE_WARNING, self.report())

    def test_range_pins_both_endpoints_and_preserves_empty_range(self):
        self.git("branch", "base-ref")
        (self.repo / "source.txt").write_text("next\n")
        self.git("commit", "-am", "Next")
        head = self.git("rev-parse", "HEAD").strip()
        self.invoke("--scope", "range", "--base", "base-ref")
        self.assertIn(f"Base: {self.base}", self.report())
        self.assertIn(f"Head: {head}", self.report())
        self.git("branch", "-f", "base-ref", "HEAD")
        self.assertIn(f"Base: {self.base}", self.report())
        self.invoke("--scope", "range", "--base", "HEAD", "--output", "empty.md")
        self.assertIn("(none)", (self.repo / "empty.md").read_text())

    def test_range_checks_reject_old_head_and_dirty_checkout(self):
        (self.repo / "source.txt").write_text("next\n")
        self.git("commit", "-am", "Next")
        self.invoke("--scope", "range", "--base", self.base, "--head", self.base,
                    "--command", "touch should-not-exist", expected=2)
        (self.repo / "source.txt").write_text("dirty\n")
        self.invoke("--scope", "range", "--base", self.base,
                    "--command", "touch should-not-exist", expected=2)
        self.assertFalse((self.repo / "should-not-exist").exists())
        self.assertFalse(self.output.exists())

    def test_clean_range_checks_execute_on_current_head(self):
        self.invoke("--scope", "range", "--base", "HEAD", "--command", python_command("print('clean range')"))
        self.assertIn("clean range", self.report())
        self.assertNotIn(dossier.MACHINE_WARNING, self.report())

    def test_invalid_and_option_like_refs_fail_without_output(self):
        for ref in ("missing-ref", "--all"):
            with self.subTest(ref=ref):
                self.invoke("--scope", "range", f"--base={ref}", expected=2)
                self.assertFalse(self.output.exists())

    def test_existing_and_symlink_reports_are_preserved_before_execution(self):
        self.output.write_text("Unresolved findings without a special table")
        self.invoke("--command", "touch should-not-exist", expected=2)
        self.assertEqual(self.report(), "Unresolved findings without a special table")
        self.assertFalse((self.repo / "should-not-exist").exists())
        link = self.repo / "link.md"
        link.symlink_to(self.output)
        self.invoke("--output", str(link), expected=2)
        dangling = self.repo / "dangling.md"
        dangling.symlink_to(self.repo / "missing.md")
        self.invoke("--output", str(dangling), expected=2)
        self.assertFalse((self.repo / "missing.md").exists())

    def test_deleted_tracked_path_cannot_be_used_for_report(self):
        (self.repo / "source.txt").unlink()
        self.invoke("--output", "source.txt", expected=2)
        self.assertFalse((self.repo / "source.txt").exists())

    def test_absolute_output_outside_target_and_missing_file_errors(self):
        output = Path(self.temp.name) / "outside.md"
        self.invoke("--output", str(output))
        self.assertTrue(output.exists())
        self.invoke("--output", str(output), "--check", expected=1)
        result = self.invoke("--output", "missing.md", "--check", expected=2)
        self.assertNotIn("Traceback", result.stderr)

    def test_full_output_blank_lines_and_markers_in_output(self):
        code = "import sys; print('start\\n\\n' + '\\n'.join(str(i) for i in range(40))); print('```'); print(" + repr(dossier.PENDING) + "); print(" + repr(dossier.MACHINE_WARNING) + "); print('stderr detail', file=sys.stderr)"
        self.invoke("--command", python_command(code))
        text = self.report()
        self.assertIn("start\n\n0\n1\n", text)
        self.assertIn("\n39\n", text)
        self.assertIn("stderr detail", text)
        self.fill_fields()
        self.invoke("--check")

    def test_failed_check_preserves_output_and_explanation_does_not_pass(self):
        self.invoke("--command", python_command("import sys; print('failure evidence'); sys.exit(7)"), expected=1)
        self.assertIn("Exit code: 7", self.report())
        self.assertIn("failure evidence", self.report())
        self.fill_fields()
        self.invoke("--check", expected=1)

    @unittest.skipUnless(os.name == "posix", "POSIX process groups required")
    def test_timeout_preserves_output_and_kills_descendants(self):
        child = "import time; from pathlib import Path; time.sleep(2); Path('leaked-child').write_text('bad')"
        parent = "import subprocess, sys, time; print('before timeout', flush=True); subprocess.Popen([sys.executable, '-c', " + repr(child) + "]); time.sleep(5)"
        self.invoke("--timeout", "1", "--command", python_command(parent), expected=1)
        self.assertIn("Exit code: 124", self.report())
        self.assertIn("Timeout: true", self.report())
        self.assertIn("before timeout", self.report())
        time.sleep(1.3)
        self.assertFalse((self.repo / "leaked-child").exists())

    def test_snapshot_drift_detects_content_change_even_if_status_stays_modified(self):
        (self.repo / "source.txt").write_text("dirty before\n")
        code = "from pathlib import Path; Path('source.txt').write_text('dirty after\\n')"
        self.invoke("--command", python_command(code), expected=1)
        self.assertIn("Working state changed", self.report())
        self.fill_fields()
        self.invoke("--check", expected=1)

    def test_snapshot_drift_detects_untracked_content_change(self):
        (self.repo / "new.txt").write_text("before\n")
        code = "from pathlib import Path; Path('new.txt').write_text('after\\n')"
        self.invoke("--command", python_command(code), expected=1)
        self.assertIn("Working state changed", self.report())

    def test_each_check_records_drift_even_if_a_later_check_restores_state(self):
        change = "from pathlib import Path; Path('source.txt').write_text('changed\\n')"
        restore = "from pathlib import Path; Path('source.txt').write_text('initial\\n')"
        self.invoke("--command", python_command(change), "--command", python_command(restore), expected=1)
        self.assertEqual((self.repo / "source.txt").read_text(), "initial\n")
        self.assertEqual(self.report().count("Working state changed during this check"), 2)
        self.fill_fields()
        self.invoke("--check", expected=1)

    def test_later_staged_check_is_skipped_after_snapshot_drift(self):
        change = "from pathlib import Path; Path('source.txt').write_text('changed\\n')"
        self.invoke("--scope", "staged", "--command", python_command(change),
                    "--command", "touch should-not-exist", expected=1)
        self.assertIn("Skipped, not executed", self.report())
        self.assertFalse((self.repo / "should-not-exist").exists())
        self.fill_fields()
        self.invoke("--check", expected=1)

    def test_replacing_the_index_does_not_redefine_the_reviewed_snapshot(self):
        change = "from pathlib import Path; Path('source.txt').write_text('changed\\n')"
        self.invoke("--scope", "staged", "--command", python_command(change) + " && git add source.txt",
                    "--command", "touch should-not-exist", expected=1)
        self.assertIn("Selected snapshot changed since scope capture", self.report())
        self.assertFalse((self.repo / "should-not-exist").exists())

    def test_renames_deletions_and_unusual_names_collect_without_bad_parsing(self):
        self.git("mv", "source.txt", "renamed\tfile.txt")
        (self.repo / "new\nfile.txt").write_text("new\n")
        self.invoke()
        self.assertIn("source.txt", self.report())
        self.assertIn(r"renamed\tfile.txt", self.report())
        self.assertIn(r"new\nfile.txt", self.report())

    def test_empty_or_damaged_report_is_not_complete(self):
        self.output.write_text("Everything passed\n")
        self.invoke("--check", expected=2)
        self.output.unlink()
        self.invoke()
        self.output.write_text(self.report().replace(dossier.PENDING, ""))
        self.invoke("--check", expected=1)
        self.fill_fields()
        self.output.write_text(self.report().replace("## Scope", "## Wrong section"))
        self.invoke("--check", expected=2)

    def test_incomplete_output_fence_is_rejected(self):
        self.invoke()
        self.fill_fields()
        self.output.write_text(self.report() + "\n```text\ninterrupted output\n")
        self.invoke("--check", expected=2)

    def test_invalid_arguments_have_no_side_effects(self):
        for args in (("--timeout", "0"), ("--scope", "range"), ("--base", "HEAD"),
                     ("--check", "--command", "touch should-not-exist")):
            with self.subTest(args=args):
                self.invoke(*args, expected=2)
                self.assertFalse(self.output.exists())
                self.assertFalse((self.repo / "should-not-exist").exists())


if __name__ == "__main__":
    unittest.main()
