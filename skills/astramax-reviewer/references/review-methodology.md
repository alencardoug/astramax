# Review methodology

## 1. Establish scope and intent

Record the user's requested behavior, acceptance criteria, scope and relevant
constraints. Read applicable repository instructions and specifications before
forming an opinion. Author notes describe intent; verify their claims yourself.
If requirements are absent, state the inferred behavior and limits. Ask only
when the ambiguity materially prevents review; continue independent inspection.

Use Git when available; do not make Git a requirement for reviewing supplied
files. Useful local inspections include:

```bash
git rev-parse --show-toplevel
git status --short
git diff --stat
git diff
git diff --cached
git ls-files --others --exclude-standard
git log -5 --oneline
```

Choose and state what the comparison means:

| Scope | Evidence to inspect | Verification caveat |
| --- | --- | --- |
| Working tree | Tracked changes relative to HEAD, staged and unstaged layers, relevant untracked files | Tests execute the current working tree, including untracked files |
| Staged | Index relative to HEAD; include additions on an unborn branch | Tests still execute the working tree; unstaged or untracked content can make it a different snapshot |
| Commit range | Both endpoints resolved to full commit IDs; endpoint diff and relevant history | Current checkout may not match the reviewed head |
| Whole repository / components | Explicit file or component inventory and repository context | A clean diff does not mean there is nothing to review |

For a feature branch, use a merge base only when the user's scope calls for
changes since divergence. An endpoint diff and a merge-base diff are different
questions. Do not fetch, switch branches or create a worktree just to guess scope.
Record exact IDs once scope is established. A range with no commits or no diff
is an observation, not an error that proves no review is needed.

Record HEAD and dirty state alongside test evidence. If the intended snapshot
is not checked out, report the mismatch; prepare an isolated checkout only within
the user's authorization. Do not attribute current-checkout results to an older
commit or to the index. Recheck state after commands and before final reporting.
If relevant files changed, invalidate affected evidence and refresh it.

## 2. Build a review map

Read implementation, callers, configuration, public contracts and tests together.
Identify source declarations and generated output from repository build rules;
filename or header heuristics are clues, not proof. Spend most effort on source,
but inspect generated contracts, security-sensitive output and representative
artifacts. A faulty generator can make every generated file wrong consistently.

Map each acceptance criterion to code and verification evidence. Prioritize the
highest-impact changes first; list components omitted by time or context limits.

## 3. Challenge assumptions

Use the dimensions that apply to the change:

- Correctness: boundary values, empty/missing input, invalid states, error paths,
  retries, concurrency and partial completion.
- Regressions: callers, public API contracts, compatibility and existing behavior.
- Tests: negative cases, assertions that can pass with broken behavior, missing
  integration coverage and tests coupled too closely to implementation details.
- Architecture: module boundaries, dependency direction, established patterns and
  complexity relative to the actual requirement. Style preference is not a defect.
- Security: authorization, authentication, untrusted inputs, injection, secret
  handling, filesystem/network access and dependency or command execution changes.
- Data integrity: schema/migrations, transactions, idempotency, serialization,
  backward compatibility and data loss risks.

Prefer a reproducible counterexample or an existing invariant over a long
argument. New abstractions or tests need a concrete benefit. Do not modify the
implementation to prove a point during a review-only task.

## 4. Discover verification without project configuration in the skill

The skill ships **no project command list**. The project remains the source of
truth; copying this skill should never copy another project's build assumptions.

1. Read the target's applicable instructions and contributor documentation for
   commands, working directories, runtime versions and environment prerequisites.
2. Inspect CI jobs, project scripts and task definitions to corroborate them.
   Inspect invoked scripts and hooks as well as the visible command name.
3. In a monorepo, select affected packages and their shared contracts. Record
   the correct working directory; do not automatically run every package's suite.
4. Choose focused checks first, then the project's required broader checks.
   An installed tool or a manifest filename alone does not establish a command.
5. Execute only established, relevant commands within authorization. Discovery
   does not authorize installing dependencies, network access, deployment,
   destructive tasks or changing credentials. Explain only actual blockers.
6. If commands conflict, are missing, or need unavailable services, record what
   could not run and why. Do not create a configuration file inside the installed
   skill or invent conventional targets to fill the gap.

Examples of **sources to read**, not universal commands: `package.json` scripts
and workspace configuration; `pyproject.toml` test/tool settings; `Makefile` or
`justfile` targets; Cargo workspace manifests; CI workflow files. No single source
proves that execution is safe or sufficient. Existing project-specific task files
can remain in that project; AstraMax does not require its own schema.

## 5. Keep an evidence ledger

For each check record command, working directory, timestamp, tested snapshot,
exit code, and output or an accessible log. Keep stdout and stderr identifiable
when collecting them separately. Label excerpts and redactions; do not call an
excerpt complete literal output. Preserve failures and timeout output.

An exit code of zero means that command succeeded, not that all requirements
were met. A pre-existing failure still limits verification. An expected failure
needs an explanation and a valid independent check; do not erase or relabel it.

Use these evidence labels explicitly:

| Label | Meaning |
| --- | --- |
| Verified fact | Directly supported by inspected code, captured execution or another identified artifact; state which |
| Reasoned concern | A causal argument based on evidence, without executed reproduction |
| Unverified hypothesis | A possibility needing a named next check; keep outside confirmed findings |

Never fabricate tests, outputs, line numbers, model settings or tool versions.
Static inspection is evidence, but is not test execution. Missing verification
belongs in the report even when no defect was found.

## 6. Report and hand back control

Use the report contract in [finding-severity.md](finding-severity.md). Deduplicate
findings by root cause. Link each claim to evidence and explain practical impact.
Keep test gaps and architectural observations only when actionable.

The author may subsequently address, defer or dispute each finding with reasons.
Fix generated behavior at its source and regenerate when authorized. Re-run
affected checks after fixes; earlier evidence does not automatically cover them.
Never delete a pending report or unresolved findings as routine cleanup.
