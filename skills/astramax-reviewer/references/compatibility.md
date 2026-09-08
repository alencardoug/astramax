# Compatibility

Last external verification: **not performed**.

The initial migration was deliberately limited to repository-local evidence.
No vendor availability, CLI syntax, registry name or installer interoperability
has been verified. This is a compatibility record, not a support claim.

## OpenAI Codex and reviewer configuration

Desired model: **GPT-6 Astra**. Desired effort: **maximum supported reasoning
effort for that model in the user's current environment**.

Tested Codex version: not established.
Live Astra availability: not established.
Maximum reasoning setting and invocation syntax: not established.

The repository contains a historical screenshot of a different project's session
displaying `gpt-6-astra` and `xhigh`. It is not evidence of current availability,
supported CLI flags, or the highest setting in another environment.

Before an actual review, within the user's permitted sources:

1. Confirm a fresh context separate from the implementation context. The author
   cannot establish independence by renaming its role or writing a dossier.
2. Inspect the installed Codex interface/help and environment-provided model and
   reasoning metadata, or current provider documentation when allowed. Record
   the actual version, model identifier, setting and source of confirmation.
3. Confirm that the selected setting is the maximum supported for this model in
   that environment. Do not assume that a label such as `high`, `xhigh` or `max`
   is portable or that a model name alone implies a reasoning setting.
4. Start the separate review through that confirmed interface, manually if
   necessary. Do not embed an unverified invocation in the stable skill. Once
   running as the independent reviewer, perform the review directly; do not
   launch another copy of this workflow.
5. If unavailable, unknown or impossible to confirm under the user's constraints,
   say what is missing and return `UNABLE TO VERIFY`. Handoff preparation can
   continue. Version 0.1 does not silently fall back to another model or effort.

Do not read or publish authentication tokens. The provider tool handles login;
this repository supplies neither credentials nor model access.

## Claude Code and other authors

Tested Claude Code version: not established.
Tested implementation model: not established.

Claude Code is the reference implementation agent. Another implementation agent
can prepare the same evidence, but reviewer context independence remains required.
Claude Code access depends on the user's subscription and current product limits.
Astra availability and usage limits depend on the user's current OpenAI plan and
rollout. Verify current provider information and local availability when allowed.

## Skill tooling

| Tool | Status |
| --- | --- |
| `skills` GitHub installer | Command pattern from the specification; not integration-tested |
| `skillpm` npm installer | Expected layout supplied; installation/discovery not integration-tested |
| `skills-ref` Agent Skills validator | Not installed or executed during the repository-only migration |
| Local validator | Dependency-free structural and repository contract checks; not a replacement for `skills-ref` |

Installer examples describe the intended post-publication workflow. Confirm
current syntax, supported runtime versions and package ownership before release.
Do not infer that installation works because an archive was produced.

## Optional dossier helper

The instruction-only skill needs no Python or Node runtime. The optional
`scripts/dossier.py` uses Python 3.9+ standard library and local Git. Check
execution uses the POSIX shell on POSIX systems; Windows execution is not
supported by the helper. Dossier collection/checking itself is portable Python.
No script launches Codex or manages credentials. Repository maintenance uses
Node.js 18+ and npm for local validation/packaging; these are not review runtimes.

Record actual local checks and outstanding integration tests in
`docs/VALIDATION.md` in the source repository. Update this reference after real
compatibility checks, with version, date, command and result rather than guesses.
