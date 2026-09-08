# AstraMax Reviewer

**AstraMax Reviewer** is an Agent Skill that adds an independent second-model
review stage to AI-assisted software development. Its reference workflow uses
Claude Code for implementation and OpenAI Codex with GPT-6 Astra at maximum
supported reasoning effort for verification and defect discovery.

The implementing agent hands requirements and evidence to a separate reviewer
context. The reviewer inspects the repository and challenges the implementation
using a repeatable protocol.

**AstraMax Reviewer is an independent community project. It is not affiliated
with, endorsed by, or maintained by OpenAI or Anthropic.**

Status: `0.1.0` local development, not yet published. External model availability,
Agent Skills validation and GitHub/SkillPM installation have not been verified.
See the [compatibility record](skills/astramax-reviewer/references/compatibility.md).

## Why this exists

An implementation agent has already formed assumptions about requirements,
architecture and tests. A second model in a fresh context can challenge those
assumptions and provide another opportunity to find defects. Independence does
not guarantee correctness; the value is in evidence and reproducible findings.

## How it works

```text
Developer → Implementation agent → Checkpoint and evidence handoff
                                        ↓
                          Separate Codex / Astra context
                                        ↓
                      Inspect → Challenge → Verify → Report
                                        ↓
                         Developer decides what to change
```

The skill is instructions and references, with an optional Python dossier helper.
It does not call an API, select a model by itself, configure agent tools, run in
the background or install hooks. Use your environment's confirmed interface to
start the independent reviewer; there is no bundled Codex invocation command.

## Review workflow

1. Establish scope: working tree, staged changes, an explicit commit range, or
   selected components / the whole repository. Read requirements and constraints.
2. Inspect changed code together with callers, contracts, configuration and tests.
3. Challenge correctness, regressions, test coverage, architecture, security,
   data integrity and unnecessary complexity where relevant.
4. Discover the target project's verification commands, inspect their behavior
   and run relevant checks within the user's authorization.
5. Report supported findings by severity, verification gaps and one justified
   verdict: `PASS`, `PASS WITH MINOR FINDINGS`, `CHANGES RECOMMENDED`,
   `CHANGES REQUIRED` or `UNABLE TO VERIFY`.

Review-only is the default. Findings do not authorize implementation edits,
commits, pushes, publication or report deletion.

## Installation

### From a local checkout

The complete installable unit is `skills/astramax-reviewer/`, including its
references and optional script. For a project using `.claude/skills/`, copy it
from this checkout into that project's skill directory:

```bash
mkdir -p /path/to/target-project/.claude/skills
cp -R skills/astramax-reviewer /path/to/target-project/.claude/skills/
```

The destination `astramax-reviewer` directory must not already exist; inspect
an existing installation before replacing it. Other Agent Skills hosts can use
their supported installation directories. Keep the directory intact so relative
reference links resolve. Confirm discovery in your host; local layout checks
alone do not establish host compatibility.

### From GitHub — pending release validation

The configured origin is `alencardoug/astramax`; the skill name remains
`astramax-reviewer`. After confirming repository visibility and current installer
syntax, the intended command from the specification is:

```bash
npx skills add https://github.com/alencardoug/astramax --skill astramax-reviewer
```

### With SkillPM / npm — pending publication and installation test

The proposed package name is `astramax-reviewer`; registry availability and
ownership are unverified. Do not run this until the maintainer confirms the
published package and successful installation test:

```bash
npx skillpm install astramax-reviewer
```

If a scoped name is needed, use the announced package scope; the Agent Skill's
name stays unchanged. This package has no executable named `astramax-reviewer`.
The release procedure lives in `docs/PUBLISHING.md` in the source repository.

## Usage

Ask the implementation agent to prepare a handoff:

> Use AstraMax Reviewer to prepare an independent review of the current working
> tree. Record requirements, executed checks, what remains unverified and your
> environment assumptions.

Start a separate Codex context, confirm Astra and the maximum supported reasoning
setting, and ask:

> Use AstraMax Reviewer to review this change against the specification. Inspect
> the repository independently, run relevant established checks, and report
> findings with evidence. Keep this review-only.

Or in Portuguese:

> Use astramax-reviewer para revisar as alterações atuais contra a especificação.
> Confira as evidências, registre o que não foi verificado e apresente os achados
> por gravidade, sem alterar a implementação.

If the actual model, effort or independent context cannot be confirmed, the
result is `UNABLE TO VERIFY`; preparing a dossier does not count as an Astra review.

### No project variables to edit

There is no bundled `comandos.txt`, default branch, fixed repository root or
assumed build tool. The agent reads the target project's instructions, CI and task
definitions to choose checks. It records missing verification instead of guessing
a command. Existing project scripts remain the single source of truth.

The optional helper can collect scope without running tests. From this checkout:

```bash
python3 skills/astramax-reviewer/scripts/dossier.py --repo .
```

To include this repository's explicitly selected validation command instead:

```bash
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --command 'npm run validate'
```

These are alternatives: the helper preserves an existing `REVISAO.md`. Complete
the author fields, then check the handoff:

```bash
python3 skills/astramax-reviewer/scripts/dossier.py --repo . --check
```

When installed elsewhere, use the script's actual installed path and the target
repository as `--repo`. See [handoff instructions](skills/astramax-reviewer/references/handoff.md)
for staged/range scope, explicit commands, exit codes, timeouts and limitations.
No helper or dossier file is required for the instruction-only workflow.

## Example review

Illustrative only; these are fictional observations, not executed checks:

```text
AstraMax Review
Verdict: CHANGES REQUIRED

Reviewed: the described tenant authorization change.
Executed: none; static inspection only in this example.
Not verified: runtime reproduction and the project's test suite.

ID: R1
Severity: HIGH
Location: authorize_request (illustrative symbol)
Problem: a missing tenant ID enters the unrestricted access branch.
Evidence: reasoned concern from the illustrated branch condition.
Impact: requests can bypass the intended tenant boundary.
Recommended action: reject missing tenant identity before authorization.
Verification: proposed negative test; not executed.

Final verdict: CHANGES REQUIRED because the supported authorization defect
affects isolation. Runtime verification remains outstanding.
```

The full [report contract](skills/astramax-reviewer/references/finding-severity.md)
adds actual reviewer configuration, scope, requirements and evidence references.

## Requirements

For the reference Claude → Astra workflow:

- Claude Code access for implementation, or another implementation agent.
- OpenAI Codex access, with GPT-6 Astra available and its maximum reasoning
  setting confirmed in the user's environment.
- A separate reviewer context with access to the target repository and the
  tools needed for that project's verification.

For the optional dossier helper: Python 3.9+ and Git. Executing supplied commands
with the helper requires POSIX; no third-party Python dependencies are used.

For repository maintenance and npm packaging: Node.js 18+ and npm. For SkillPM
installation, use the Node/npm versions required by the currently verified
SkillPM release; those requirements have not been independently confirmed here.
Node and Python are not required to read and follow the core skill.

The skill supplies no subscription, credentials or model access. Vendor model
availability, usage limits and plan details can change; they are not guarantees
made by this project.

## Compatibility and limitations

- Model selection is an environment prerequisite, not something a Markdown
  instruction can enforce. No silent fallback is provided in version 0.1.
- Validation commands may need dependencies/services or have side effects;
  inspect them and respect the user's permissions. Missing evidence stays visible.
- The helper does not sandbox commands, attest report integrity, fingerprint
  ignored/external state or automatically create a historical test checkout.
- Local archive/structure checks do not prove GitHub, SkillsMP or SkillPM support.
- No automatic fixes, PR creation, CI service, API client, billing or credential
  management is included. Review increases scrutiny; it does not guarantee correctness.

See [compatibility](skills/astramax-reviewer/references/compatibility.md) for what
is confirmed and what needs validation in a real environment.

## Design principles and contributing

Preserve independent contexts, evidence over opinion, developer control and a
small implementation. Keep one canonical skill and project-specific details in
the target project. Contributions should explain the defect they prevent and
their cost in false positives and review time.

In a source checkout, read `CONTRIBUTING.md`, `docs/DESIGN.md`,
`docs/VALIDATION.md` and `docs/PUBLISHING.md`. Maintainer documents are intentionally
excluded from the npm archive. The package includes the full skill references.

## License and disclaimer

[MIT](LICENSE). This independent community project is not affiliated with,
endorsed by, or maintained by OpenAI or Anthropic. Developers remain responsible
for assessing findings, making changes and accepting their software.
