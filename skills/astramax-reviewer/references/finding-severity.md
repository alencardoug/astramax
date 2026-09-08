# Severity and report contract

Severity measures impact, not confidence. A severe hypothetical issue is still
a hypothesis until sufficiently supported. Put unsupported possibilities in
suggested verification, not in the confirmed findings list.

| Severity | Meaning |
| --- | --- |
| BLOCKER | Must not be accepted: major requirement absent, code cannot execute, critical regression, serious vulnerability or data loss |
| HIGH | Material defect likely to affect production correctness or behavior |
| MEDIUM | Relevant issue that normally deserves correction but may not block the whole change |
| LOW | Small actionable improvement with limited correctness impact |

Do not inflate severity or report a stylistic preference as a defect. Findings
can be supported by code inspection without a runnable reproduction, but label
that evidence and make the causal chain clear.

Each meaningful finding needs:

```text
ID: R1
Severity: HIGH
Location: actual/path.ext:observed-line (or symbol if a line is not established)
Problem: concrete incorrect behavior
Evidence: verified fact or reasoned concern, with code / command / artifact
Impact: affected users, requirement or system behavior
Recommended action: smallest useful correction
Verification: executed reproduction, or explicitly proposed check
```

Use stable IDs within a review so the author's response can track each finding.
Do not fabricate paths or line numbers. Cite generated output and its source
when both are relevant.

## Verdict selection

Apply these rules in order:

1. Reviewer independence, Astra identity or maximum reasoning configuration
   unavailable/unconfirmed: `UNABLE TO VERIFY`. Label any partial observations;
   do not claim that an Astra review completed.
2. Supported BLOCKER or HIGH finding: `CHANGES REQUIRED`, even if some checks
   remain blocked. Explain those verification limits as well.
3. Otherwise, missing evidence essential to acceptance: `UNABLE TO VERIFY`.
   This includes an essential failing check whose cause/impact is not established.
4. Supported MEDIUM finding: `CHANGES RECOMMENDED`.
5. Only LOW findings and adequate evidence for the stated scope:
   `PASS WITH MINOR FINDINGS`.
6. No findings and adequate evidence for the stated scope: `PASS`.

Adequate evidence depends on scope. Documentation-only changes may be verified
by inspection and link checks; an untested migration normally needs more. A
passing suite, a complete dossier or lack of findings alone never warrants PASS.

## Report template

Use the user's language for prose; keep severity and verdict tokens unchanged.
The first verdict and final justification must agree. Omit optional sections
only when they have no meaningful content.

```markdown
# AstraMax Review

Verdict: <one allowed verdict>

## Summary

Reviewer: <actual model, reasoning setting, source of confirmation, independent context>
Scope: <working tree / staged / full base and head IDs / component inventory>
Requirements: <sources or stated assumptions>
Reviewed: <components and boundaries>
Executed: <commands, cwd, tested state, exit codes, output/log references; or none>
Not verified: <omissions, environment assumptions, failed/skipped checks and reasons>

## Findings

<R1, R2, ... ordered BLOCKER, HIGH, MEDIUM, LOW using the finding fields>
<Or explicitly state no supported findings within the reviewed scope.>

## Test gaps

<Concrete missing behavior and useful checks, if any.>

## Architecture observations

<Material observations, if any.>

## Suggested verification

<Unverified hypotheses and proposed checks, clearly distinguished from execution.>

## Final verdict

<Justify the verdict above and its verification limits.>
```

For follow-up work, use a response table without rewriting the original evidence:

| Finding | Disposition | Reason / change | New verification |
| --- | --- | --- | --- |
| R1 | addressed / deferred / disputed | Concrete response | Evidence or pending check |

The report's presence does not authorize fixes, commits or deletion.
