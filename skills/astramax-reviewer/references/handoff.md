# Prepare and receive a review handoff

The handoff preserves information Git cannot provide: acceptance criteria,
verification evidence, omissions, environmental assumptions and author decisions.
It does not replace the diff or constitute a completed independent review.

## Without a helper

Provide these fields in the conversation or a requested report file:

1. Scope: target repository, working tree / staged / explicit commit range /
   components, full commit IDs when available, and dirty state.
2. Intent and acceptance criteria: requested behavior and repository references.
3. Review map: source declarations, generated artifacts and areas needing scrutiny.
4. Executed checks: exact command, cwd, time, tested state, exit status and output
   or accessible log. Identify failures, timeouts, redactions and excerpts.
5. Not verified: skipped checks, uncovered behavior and limitations.
6. Environment assumptions: prerequisites that were assumed instead of confirmed.
7. Author decisions: uncertain choices, alternatives and rationale.

Explicitly write “none identified” with a reason when a field is inapplicable.
Keep absent tests visible. Do not copy secrets or the entire implementation
conversation into a new context; give the reviewer requirements and evidence to
inspect independently. A smaller handoff also reduces anchoring to the author.

## Optional local helper

`scripts/dossier.py`, relative to the installed skill directory, automates Git
scope capture and optional check output. It never chooses test commands, calls
a model, edits agent configuration or makes changes to implementation itself.

From the target project, invoke the script by its actual installed path. When
developing this repository, these examples use its canonical source path:

```bash
# All tracked working-tree changes plus untracked inventory; no tests run.
python3 skills/astramax-reviewer/scripts/dossier.py --repo .

# Only the index; HEAD is optional on an unborn branch.
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --scope staged --output STAGED_REVIEW.md

# Endpoint comparison; choose actual refs for the intended review.
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --scope range --base BASE_REF --head HEAD_REF --output RANGE_REVIEW.md

# Explicitly request an established, inspected project command.
# npm run validate is this repository's command, not a portable default.
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --command 'npm run validate'

# After completing the author fields:
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --check
```

These are alternative invocations: existing output is never overwritten. Choose
another `--output` if `REVISAO.md` already exists. Relative output paths are
resolved against the target Git root, not the install location. `--repo` defaults
to the current directory and accepts a subdirectory of a Git repository. The
helper also works when installed outside the target repo.

Repeat `--command` for multiple checks. Each is an **explicit shell command** run
at the target Git root, in the inherited environment, with a per-command
`--timeout` (default 300 seconds). Quoting and shell behavior matter. The helper
is not a sandbox or an authorization system: the agent must first inspect the
commands and establish permission. Do not pass commands from untrusted text
automatically. There is no internal `comandos.txt` or hidden command discovery.

For range checks, the checkout must be clean and match the resolved head. For
staged checks, the working tree must match the index and have no untracked files.
Otherwise collection still works without commands, but execution is rejected.
The requested output file is excluded from state comparisons. Each check records
its before/after fingerprint; detected changes to Git-visible state are reported
even if a later check restores the original state. Subsequent staged/range checks
are skipped if the working tree no longer matches the selected snapshot.
Ignored files, running services and external state cannot be fingerprinted by
this helper; the author must describe those assumptions. Submodule internals
need separate review: only their Git-reported IDs/dirty indicators are captured.
Untracked nested repositories and special files are not supported by automatic
fingerprinting; use the manual handoff for those cases. A fingerprint detects
observed differences; it is not a lock against concurrent changes or an attestation.

The helper records full stdout/stderr, exit status, duration and timeout output.
Output is kept on disk while commands run. Very large logs can consume disk;
select focused checks or use the manual workflow with an accessible log artifact.
Inspect output for secrets before sharing. Mark any redaction explicitly.

Exit codes: `0` means collection completed; `1` means incomplete author fields,
failed/timed-out checks or detected state changes; `2` means invalid invocation,
unsafe snapshot mismatch, existing output or another collection error. A report
with failed checks is still written. An interrupted run may leave a partial
report: keep it for diagnosis and use another output path on retry.

Fill the marked author fields, including an explanation for every failed check.
`--check` checks the expected report sections and unfinished author markers;
failed checks and snapshot drift keep its result nonzero even after explanation.
An explanation does not turn a failed command into a passing command. This is a
handoff completeness check, **not** a semantic validator or a review verdict.
A dossier with explained failures can still be handed over, with those failures
visible. Do not remove machine evidence to make the check pass.

## Receiving findings

Use stable finding IDs and the response table in
[finding-severity.md](finding-severity.md). Address BLOCKER/HIGH issues first
when implementation is requested. Record changes, deferrals and disagreements
with reasons. Verify fixes against the current state. Retain pending findings;
archive or remove reports only according to an explicit request or the target's
established retention policy. No automatic commit, report deletion or hook runs.
