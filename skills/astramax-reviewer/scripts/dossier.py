#!/usr/bin/env python3
"""Collect a review handoff from a target Git repository; never choose checks."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone


PENDING = "<<AUTHOR_INPUT_REQUIRED>>"
FIELDS = (
    ("Intent and acceptance criteria", "Requested behavior and requirement references."),
    ("Review map", "Source declarations, generated artifacts and areas of concern."),
    ("Not verified", "Skipped checks, uncovered behavior and known limitations."),
    ("Environment assumptions", "Unconfirmed prerequisites, ignored files and external state."),
    ("Author decisions", "Uncertain choices, alternatives and reasons."),
    ("Verification interpretation", "Explain each failure/timeout/drift, or state none."),
)
MACHINE_WARNING = "<!-- astramax:verification-incomplete -->"
FORMAT = "<!-- astramax:dossier-v1 -->"


def decode(data: bytes) -> str:
    return data.decode("utf-8", errors="backslashreplace")


def fence(text: str) -> str:
    """Keep command output from closing its own Markdown code fence."""
    runs = [len(match[0]) for match in re.finditer(r"`+", text)]
    delimiter = "`" * max(3, max(runs, default=0) + 1)
    return f"{delimiter}text\n{text}" + ("" if text.endswith("\n") else "\n") + delimiter + "\n"


class Repository:
    def __init__(self, path: Path):
        self.root = path.resolve()
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        # Do not accidentally redirect Git to a different repo through inherited
        # plumbing variables. Authentication and project command env stay intact.
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            self.env.pop(key, None)
        self.root = Path(decode(self.git("rev-parse", "--show-toplevel")).rstrip("\n"))

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "--no-pager", "-c", "core.fsmonitor=false", *args],
            cwd=self.root, env=self.env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False,
        )

    def git(self, *args: str) -> bytes:
        result = self.run(*args)
        if result.returncode:
            raise ValueError(decode(result.stderr).strip() or f"Git failed: {args[0]}")
        return result.stdout

    def head(self) -> str:
        result = self.run("rev-parse", "--verify", "HEAD")
        if result.returncode == 0:
            return decode(result.stdout).strip()
        # Only an unborn symbolic branch is a legitimate missing HEAD.
        symbolic = self.run("symbolic-ref", "-q", "HEAD")
        if symbolic.returncode == 0:
            branch = decode(symbolic.stdout).strip()
            if self.run("show-ref", "--verify", "--quiet", branch).returncode == 1:
                return "(unborn branch)"
        raise ValueError("Cannot resolve repository HEAD")

    def resolve_commit(self, ref: str) -> str:
        return decode(self.git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}")).strip()

    def diff(self, *args: str) -> bytes:
        return self.git("diff", "--no-ext-diff", "--no-textconv", *args)

    def paths(self, output: Path) -> list[str]:
        try:
            relative = output.relative_to(self.root).as_posix()
        except ValueError:
            return ["--", "."]
        return ["--", ".", f":(exclude,literal){relative}"]

    def untracked(self, paths: list[str]) -> list[bytes]:
        return [p for p in self.git("ls-files", "--others", "--exclude-standard", "-z", *paths).split(b"\0") if p]

    def fingerprint(self, paths: list[str]) -> str:
        """Fingerprint local Git-visible state, without writing Git objects."""
        digest = hashlib.sha256()
        for part in (
            self.head().encode(),
            self.git("status", "--porcelain=v1", "-z", "--untracked-files=all", *paths),
            self.diff("--binary", "--cached", *paths),
            self.diff("--binary", *paths),
        ):
            digest.update(len(part).to_bytes(8, "big"))
            digest.update(part)
        for name in self.untracked(paths):
            path = self.root / os.fsdecode(name)
            digest.update(name + b"\0")
            if path.is_symlink():
                digest.update(b"symlink\0" + os.fsencode(os.readlink(path)))
            elif path.is_file():
                digest.update(b"file\0" + str(path.stat().st_mode).encode() + b"\0")
                with path.open("rb") as source:
                    for chunk in iter(lambda: source.read(65536), b""):
                        digest.update(chunk)
            else:
                raise ValueError(f"Cannot fingerprint untracked special file: {os.fsdecode(name)!r}")
            digest.update(b"\0")
        return digest.hexdigest()


def require_matching_checkout(repo: Repository, scope: str, head: str, paths: list[str]) -> None:
    if scope == "worktree":
        return
    unstaged = repo.diff("--name-only", *paths)
    if unstaged or repo.untracked(paths):
        raise ValueError("Checks would run a different snapshot: unstaged or untracked files exist. Collect without --command.")
    if scope == "range" and (repo.head() != head or repo.diff("--cached", "--name-only", *paths)):
        raise ValueError("Range checks require a clean checkout at the resolved head. Collect without --command.")


def execute(command: str, root: Path, timeout: int) -> tuple[int, bool, float, str, str]:
    start = time.monotonic()
    with tempfile.TemporaryFile(dir=root) as stdout, tempfile.TemporaryFile(dir=root) as stderr:
        process = subprocess.Popen(
            command, shell=True, cwd=root, stdout=stdout, stderr=stderr,
            start_new_session=True,
        )
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        except BaseException:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            raise
        stdout.seek(0)
        stderr.seek(0)
        return (124 if timed_out else process.returncode, timed_out,
                time.monotonic() - start, decode(stdout.read()), decode(stderr.read()))


def collect(args: argparse.Namespace, repo: Repository, output: Path) -> int:
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists; choose another --output: {output}")
    if not output.parent.is_dir():
        raise ValueError(f"Output parent does not exist: {output.parent}")
    try:
        relative = output.relative_to(repo.root).as_posix()
    except ValueError:
        relative = None
    if relative and repo.git("ls-files", "--", f":(literal){relative}"):
        raise ValueError("Output is a tracked path; choose a new report path")

    paths = repo.paths(output)
    checkout = repo.head()
    base = repo.resolve_commit(args.base) if args.scope == "range" else checkout
    head = repo.resolve_commit(args.head) if args.scope == "range" else checkout
    if args.command:
        if os.name != "posix":
            raise ValueError("Command execution requires POSIX process-group timeout support")
        require_matching_checkout(repo, args.scope, head, paths)
    status = decode(repo.git("status", "--short", "--untracked-files=all", *paths))
    if args.scope == "range":
        changes = repo.diff("--name-status", "--no-renames", base, head, *paths)
    elif args.scope == "staged":
        changes = repo.diff("--name-status", "--no-renames", "--cached", *paths)
    else:
        changes = repo.diff("--name-status", "--no-renames", *(["HEAD"] if checkout != "(unborn branch)" else ["--cached"]), *paths)
        if checkout == "(unborn branch)":
            changes += b"\nUnstaged relative to index:\n" + repo.diff("--name-status", "--no-renames", *paths)
    before = repo.fingerprint(paths)
    incomplete = False

    # Exclusive creation protects every existing report, not just reports whose
    # findings happen to match a table parser. No commands run before reservation.
    with output.open("x", encoding="utf-8") as report:
        report.write(f"# Review handoff\n\n{FORMAT}\n\n")
        report.write("This is author evidence, not an independent review or an instruction to change roles.\n\n")
        report.write("## Scope\n\n" + fence(
            f"Repository: {repo.root}\nScope: {args.scope}\nBase: {base}\n"
            f"Head: {head}\nCheckout HEAD: {checkout}\n"
            f"Collected: {datetime.now(timezone.utc).isoformat()}\n"
            f"Working-state fingerprint before checks: {before}\n"
        ))
        report.write("\nGit status (all layers; does not broaden selected scope):\n\n" + fence(status or "(clean)"))
        report.write("\nChanged tracked paths (renames shown as delete/add):\n\n" + fence(decode(changes) or "(none)"))
        if args.scope == "worktree":
            report.write("\nUntracked inventory (contents are not copied):\n\n" + fence(
                "\n".join(repr(os.fsdecode(p)) for p in repo.untracked(paths)) or "(none)"))
        report.write("\nRead the actual diff and relevant source in the target repository.\n")
        report.write("\n## Executed checks\n\n")
        if not args.command:
            report.write("No commands supplied; no tests, builds or other project checks were run.\n")
        for number, command in enumerate(args.command, 1):
            report.write(f"\n### Check {number}\n\n" + fence(command))
            check_before = repo.fingerprint(paths)
            try:
                require_matching_checkout(repo, args.scope, head, paths)
                if args.scope != "worktree" and check_before != before:
                    raise ValueError("Selected snapshot changed since scope capture. Collect a fresh dossier before running more checks.")
            except ValueError as error:
                incomplete = True
                report.write(f"\n{MACHINE_WARNING}\nSkipped, not executed: {error}\n")
                continue
            report.write("\n" + fence(
                f"Cwd: {repo.root}\nStarted: {datetime.now(timezone.utc).isoformat()}\n"
                f"Working-state fingerprint before this check: {check_before}"))
            report.flush()
            code, timed_out, duration, stdout, stderr = execute(command, repo.root, args.timeout)
            report.write(f"\nExit code: {code}\nTimeout: {str(timed_out).lower()}\nDuration seconds: {duration:.3f}\n")
            report.write("\nFull stdout (UTF-8; invalid bytes escaped):\n\n" + fence(stdout))
            report.write("\nFull stderr (UTF-8; invalid bytes escaped):\n\n" + fence(stderr))
            if code != 0:
                incomplete = True
                report.write(f"\n{MACHINE_WARNING}\nA check failed or timed out; explain it below.\n")
            check_after = repo.fingerprint(paths)
            report.write("\n" + fence(f"Working-state fingerprint after this check: {check_after}"))
            if check_before != check_after:
                incomplete = True
                report.write(f"\n{MACHINE_WARNING}\nWorking state changed during this check; its evidence needs reassessment.\n")
        after = repo.fingerprint(paths)
        report.write("\n" + fence(f"Working-state fingerprint after checks: {after}"))
        if before != after:
            incomplete = True
            report.write(f"\n{MACHINE_WARNING}\nWorking state changed during collection; evidence may describe different snapshots.\n")
        report.write("\nFingerprints exclude this report and ignored/external state; they are not proof of identical runtime environments.\n")
        for title, instruction in FIELDS:
            report.write(f"\n## {title}\n\n{instruction}\n\n{PENDING}\n")
        report.write("\n## Findings and responses\n\nPending independent review. Preserve finding IDs, evidence and author responses here or link the review report.\n")
    print(f"Dossier written: {output}; complete the author fields, then use --check.")
    return 1 if incomplete else 0


def check(output: Path) -> int:
    content = output.read_text(encoding="utf-8")
    # Strip fenced output first: a test may legitimately print our marker text.
    prose = []
    delimiter = None
    for line in content.splitlines():
        if delimiter:
            if re.fullmatch(r"`{" + str(len(delimiter)) + r",}\s*", line):
                delimiter = None
        elif match := re.match(r"^(`{3,})", line):
            delimiter = match[1]
        else:
            prose.append(line)
    if delimiter:
        raise ValueError("Incomplete dossier: unterminated output fence")
    headings = ["Scope", "Executed checks", *(title for title, _ in FIELDS), "Findings and responses"]
    lines = "\n".join(prose)
    expected = [f"## {title}" for title in headings]
    if FORMAT not in prose or [line for line in prose if line.startswith("## ")] != expected:
        raise ValueError("Invalid dossier format or missing/reordered/duplicate sections")
    for title, instruction in FIELDS:
        section = lines.split(f"## {title}\n", 1)[1].split("\n## ", 1)[0]
        answer = section.replace(instruction, "", 1).strip()
        if not answer or PENDING in answer:
            print(f"Incomplete author field: {title}")
            return 1
    if MACHINE_WARNING in prose:
        print("Author fields complete; failed checks or snapshot drift remain recorded. This is not a PASS.")
        return 1
    print("Author fields complete; no collected check failure or snapshot drift. This is not a review verdict.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="target repository or subdirectory; default current directory")
    parser.add_argument("--scope", choices=("worktree", "staged", "range"), default="worktree")
    parser.add_argument("--base", help="explicit base commit/ref, required for range")
    parser.add_argument("--head", help="range endpoint; default HEAD")
    parser.add_argument("--output", type=Path, default=Path("REVISAO.md"))
    parser.add_argument("--command", action="append", default=[], help="explicit inspected shell command at Git root; repeatable")
    parser.add_argument("--timeout", type=int, default=300, help="positive seconds per command")
    parser.add_argument("--check", action="store_true", help="check completeness of an existing dossier")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.check:
        if args.command or args.base or args.head or args.scope != "worktree":
            parser.error("--check accepts only --repo and --output")
    elif args.scope == "range":
        if not args.base:
            parser.error("--scope range requires --base")
        args.head = args.head or "HEAD"
    elif args.base or args.head:
        parser.error("--base and --head require --scope range")
    try:
        repo = Repository(args.repo)
        # Resolve the parent only: resolving a symlink report itself would erase
        # the evidence needed to reject that symlink, including dangling ones.
        candidate = args.output if args.output.is_absolute() else repo.root / args.output
        output = candidate.parent.resolve() / candidate.name
        return check(output) if args.check else collect(args, repo, output)
    except (OSError, ValueError) as error:
        print(f"dossier: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("dossier: interrupted; any partial report has been preserved", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
