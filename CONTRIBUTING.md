# Contributing

Keep AstraMax a small Agent Skill whose central contract is independent
verification: the implementation context and reviewer context are separate.
Read [the design](docs/DESIGN.md) and the canonical
[skill](skills/astramax-reviewer/SKILL.md) before changing the workflow.

For methodology changes, explain the concrete problem, expected improvement,
potential false positives, effect on review time/cost and how the change was
evaluated. Do not add rules solely because they sound like good practice.

Keep volatile model/tool information in the compatibility reference. Do not add
project-specific commands, automatic model fallback, credentials, runtime
dependencies or duplicate skill copies. The optional helper must remain usable
outside its target repository and must preserve failures and pending reports.

Run the offline checks from the repository root:

```bash
npm run validate
npm test
npm pack --dry-run --offline --cache .npm-cache
git diff --check
```

See [validation](docs/VALIDATION.md) for meaningful regression scenarios and
external release checks. Package changes must include an archive-content check.
Keep the package version and changelog synchronized. A maintainer handles
publication as a separate step described in [publishing](docs/PUBLISHING.md).
