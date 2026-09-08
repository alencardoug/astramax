# Design and migration plan

## Objective and boundaries

Implement [REPOSITORY_SPEC.md](../REPOSITORY_SPEC.md) as a small, portable Agent
Skill. The core product is independent, evidence-driven review, not an agent
orchestration framework. This migration uses only repository evidence; external
validation and publication are separate, explicitly outstanding steps.

The supplied remote is `git@github.com:alencardoug/astramax.git`. Package metadata
uses that identity rather than inventing an owner or renaming the repository.
`astramax-reviewer` remains the skill name and proposed npm package name.

## Why a second model?

The objective is reasoning independence. The author has already committed to an
interpretation and implementation strategy. A fresh model context gets an
opportunity to challenge those assumptions, like separation of authorship and
review in software engineering. Model diversity does not guarantee correctness.

The helper collects evidence but never invokes a model. The user or host starts
the reviewer through a confirmed interface. Unknown model availability or effort
produces `UNABLE TO VERIFY`, rather than a fabricated successful Astra review.

## Audit of the original skill

| Original behavior / issue | Decision in this migration |
| --- | --- |
| `comandos.txt` carries `make test` and `make dbt-build` into new projects | Remove the bundled list; discover established commands in the target and pass only explicitly selected commands |
| Root determined by `__file__.parents[3]` | Resolve Git root from cwd / `--repo`, independently of installation path |
| References to a specific `CLAUDE.md` section, Owner policy, PostgreSQL/Airbyte and old commits | Replace with applicable target instructions and generic evidence requirements |
| Evidence, omissions, environment assumptions and uncertain decisions | Preserve as explicit handoff fields |
| Only committed changes; empty commit range aborts review | Collect worktree, index or explicit range, including unborn branches; whole-repository review stays available through the core protocol |
| Only head frozen; base remains a movable ref | Resolve both range endpoints to full commit IDs |
| `--ate` may describe an old revision while tests run current files | Reject command execution on mismatched staged/range snapshots; still allow collection without commands |
| Last 12 nonempty lines called literal output | Preserve full stdout/stderr, blank lines and timeout output; dynamically fence Markdown output |
| Timeout can leave shell children running | Execute in a POSIX process group and terminate it on timeout/interruption |
| Rename paths split with simplistic tab parsing | Let Git render quoted name-status output; represent renames as deletion/addition |
| Generated classification reads today's files for historical ranges | Move source/derived classification to evidence-based author/reviewer inspection |
| Overwrite protection depends on finding-table syntax; `--forcar` bypasses it | Refuse every existing output, including symlinks, with exclusive creation before command execution |
| Validator counts markers anywhere, rejects even explained failures without a clear distinction | Check report structure/author fields separately from machine failure/drift flags; explanations preserve nonzero verification status |
| Automatic report deletion in the delivery commit | Preserve reports and unresolved findings; apply the target's requested retention policy |
| AGENTS/CLAUDE edits and rollback tied to original history | No implicit host configuration changes or project-specific rollback commands |

## Command configuration alternatives

| Alternative | Benefit | Cost / decision |
| --- | --- | --- |
| Edit a bundled command file on installation | Small initial implementation | Copies stale commands, mutates installed package, fails shared/global installs; rejected |
| Ship an empty bundled command file | Avoids stale defaults | Still requires install-directory writes and a manual project setup step; rejected |
| Require an AstraMax configuration file in each target | Explicit and repeatable | Duplicates scripts/CI and adds a schema to maintain; unnecessary for 0.1 |
| Detect a manifest and immediately run conventional commands | Convenient on simple projects | Wrong in monorepos and projects with custom scripts; command presence is not authorization; rejected |
| Have the agent inspect target instructions, CI and task definitions | Reuses the project's source of truth and works across ecosystems | Agent must explain selection and gaps; chosen for the protocol |
| Pass explicit commands to an optional collector | Preserves reproducible mechanical output without hidden configuration | Caller must inspect shell semantics and permissions; chosen for the helper |

There are no **project-specific** internal variables to edit. Generic constants
such as report headings and timeout defaults remain normal implementation details.
Scope, target path, output path and selected checks are explicit invocation inputs.

## Implementation plan and result

1. Migrate to one `skills/astramax-reviewer/SKILL.md`, with progressive disclosure
   into methodology, severity/reporting, compatibility and handoff references.
2. Preserve useful collection through a small optional standard-library script,
   independent of host layout; make project-check execution explicit.
3. Add README, MIT license, contributor/security/changelog documents and an npm
   manifest that distributes only the canonical skill and public package docs.
4. Add a dependency-free local validator and meaningful regression tests for the
   helper; check actual npm archive contents and relative reference resolution.
5. Record external validation and publication prerequisites without contacting
   a registry, vendor, installer or remote repository during this task.

## Packaging and validation choices

The package has no runtime dependencies, executable or install hooks. Node is
used only for repository maintenance and npm packaging. Python is optional for
reviewers; the handoff can be prepared in the conversation.

The specification's `npx skills-ref` validation command can require a network
download. `npm run validate` instead performs deterministic local checks with
Node's standard library; `prepack` invokes it. The official Agent Skills validator
remains a separate release requirement. We do not claim to implement its full
schema or to have verified its invocation syntax.

Development tests and maintainer docs stay out of the npm package. A positive
file allowlist avoids shipping the original screenshot, specification, caches,
reports or credentials. The original files are migrated rather than kept as a
second discoverable skill; their history remains in Git. Portfolio material and
the repository specification are preserved without being packaged.

## Deliberately deferred

No direct API client, Codex launcher, model fallback, required config schema,
automatic command detector, report database, hooks, CI review service or npm
executable. Add those only when a concrete use case justifies the maintenance.

External model/tool checks, package-name ownership, public visibility, installer
integration and SkillsMP discovery require evidence outside this repository.
They must pass before announcing compatibility or publication readiness.
