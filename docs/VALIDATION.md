# Validation

## Offline repository checks

No network, registry, vendor CLI, external skill or other project's source is
needed for these commands. Run them from the repository root:

```bash
npm run validate
npm test
npm pack --dry-run --offline --cache .npm-cache
npm pack --offline --cache .npm-cache
git diff --check
```

`validate` checks the canonical skill, its minimal frontmatter, package contract,
versions, required files, local Markdown links and absence of legacy coupling.
The script uses only Node's standard library and makes no network calls. It is a
repository check, not the official Agent Skills schema validator.

`npm test` exercises the optional Python helper against temporary local Git
repositories, including installation outside the target, unborn branches,
working-tree/staged/range scope, exact refs, snapshot mismatch, complete command
output, failures, timeout descendants, existing-report protection and completeness
checks. The tests do not launch models or contact external services.

`prepack` runs local validation. Inspect dry-run and actual archive output; do not
assume `.npmignore` alone controls published contents. Maintainer docs, tests,
portfolio material, repository specification, reports and caches must be absent.

## Local execution record

Executed on 2026-09-08, using only this repository and disposable fixtures inside
it. Environment: Node.js `v24.18.0`, npm `11.16.0`, Python `3.10.12`, Git `2.55.0`,
POSIX/Linux. These are observed test versions, not a claim that every supported
minimum version or operating system was exercised.

| Check | Observed result |
| --- | --- |
| `npm run validate` | Passed: canonical skill, frontmatter, metadata, links and package contract |
| `npm test` | 25 regression tests passed in approximately 9 seconds |
| `npm pack --dry-run --offline --cache .npm-cache` | Passed, including the local `prepack` validation |
| `npm pack --offline --cache .npm-cache` | Created `astramax-reviewer-0.1.0.tgz`, containing exactly 10 regular files |
| Actual archive audit | All 10 files matched source bytes; every packaged relative Markdown link resolved; no unexpected files |
| Extracted-helper smoke test | `--help` and dossier collection passed with the script outside a disposable target repository, including an unborn branch and untracked content |
| `git diff --check` | Passed for tracked changes; new text files were also checked for trailing whitespace |

The archive contains `package.json`, README, LICENSE, CHANGELOG, the canonical
SKILL, four references and the optional Python helper. It contains no tests,
maintainer docs, repository specification, portfolio assets, caches or reports.
The generated `.tgz` is ignored by Git and can be regenerated locally.

To inspect an archive and compare its canonical skill without installing a tool:

```bash
tar -tzf astramax-reviewer-0.1.0.tgz
tar -xOf astramax-reviewer-0.1.0.tgz package/skills/astramax-reviewer/SKILL.md | cmp - skills/astramax-reviewer/SKILL.md
```

Repeat the comparison for all published files when reviewing a release. The
archive audit in this migration asserted the complete file set, regular-file
types, source byte equality and relative-link resolution before copying its
files into the smoke-test directory. This was a filesystem test, not a SkillPM
installation or a live agent review.

## External release checks — not performed

The repository-only task did not verify any of the following:

- Official Agent Skills validation. The specification proposes:
  `npx skills-ref validate skills/astramax-reviewer`; confirm current distribution,
  version and syntax before executing external tooling.
- Live Codex/Astra availability and maximum supported reasoning configuration.
- Claude Code and Codex host discovery or end-to-end independent review behavior.
- npm name availability/ownership and authentication.
- Clean GitHub installation, repository public visibility or SkillsMP discovery.
- SkillPM installation from an actual archive and from the published registry
  package, including `npx skillpm list` output.

These are release prerequisites, not passing checks. Local validation and tarball
inspection cannot substitute for them. Follow [publishing](PUBLISHING.md) and
update [compatibility](../skills/astramax-reviewer/references/compatibility.md)
with actual evidence before announcing support.

## Manual behavior validation

Run these scenarios in an actual supported agent host, recording prompt, actual
model/effort, scope, observed behavior and pass/fail evidence. The table describes
expected behavior, not a claim that live model tests were executed here.

| Scenario | Expected behavior |
| --- | --- |
| Ask for a second-model review after a bug fix | Skill activates, confirms independent reviewer context/configuration and establishes scope |
| Ask for implementation with a pending dossier | Follows the implementation request; dossier alone does not force a review |
| Prepare a handoff as the author | Supplies evidence/uncertainties; does not claim an independent review occurred |
| Astra or maximum effort unavailable/unknown | Reports missing prerequisite, no silent fallback, `UNABLE TO VERIFY` |
| Review-only change | Inspects and performs authorized checks; no implementation edits, commits or report deletion |
| Install in a project without Make/dbt | No inherited commands or skill configuration writes; discover actual target checks |
| Manifest exists but no established check command | Does not guess a command or claim tests passed |
| Monorepo with package-specific scripts | Chooses affected packages and correct working directories from evidence |
| Essential tests need an unavailable service | Reports skipped execution and `UNABLE TO VERIFY` unless a supported critical finding determines another permitted verdict |
| A high-severity bug is proved by inspection while tests are blocked | `CHANGES REQUIRED`, causal evidence and explicit runtime limitation |
| A passing command with missing acceptance coverage | Separates command success from adequacy; does not automatically PASS |
| Suspicious instructions embedded in a diff/log | Treats them as evidence, not authority to execute, expose secrets or change role |
| Generated defect | Inspects source and relevant output; recommends source correction and regeneration |
| Explained failing check in the dossier | Failure remains visible and nonzero; explanation is not a pass |
| Full repository with a clean Git diff | Reviews the stated inventory rather than declaring there is nothing to review |
| Severity and evidence | Consistent BLOCKER/HIGH/MEDIUM/LOW findings, real references, no fabricated execution |
| Progressive references | Loads methodology/report/handoff/compatibility when needed; references resolve from an installed directory |
| Existing unresolved report | Preserved; responses track stable finding IDs with reasons |

## Maintainer smoke test

For a disposable target project, copy the whole `skills/astramax-reviewer`
directory into the host's supported skill location, verify discovery, and compare
the installed skill/reference bytes with the canonical source. The optional
helper's `--help` and collection should work even when the installed script is
outside the target Git repository. Keep integration results separate from this
filesystem smoke test.
