# Publishing

Publication is separate from repository preparation. No publication, remote push,
tag, registry lookup or authentication check was performed during the migration.
Run these flows only as an explicitly requested release task.

## Shared prerequisites

1. Read `docs/VALIDATION.md` and complete the outstanding external checks.
2. Confirm the desired Codex model/maximum effort and host compatibility; record
   actual versions, date and evidence in the compatibility reference.
3. Confirm current `skills`, `skillpm` and `skills-ref` invocation syntax. The
   patterns below come from the repository specification and are unverified.
4. Verify the package name and ownership, repository URLs/default branch and
   private security contact. Adjust README links and package metadata if needed.
5. Keep `package.json` and `CHANGELOG.md` synchronized; replace the unreleased
   wording only for the actual release. Do not announce installer support early.

Local checks, from the repository root:

```bash
npm run validate
npm test
npx skills-ref validate skills/astramax-reviewer
npm pack --dry-run --offline --cache .npm-cache
git diff --check
```

`npx skills-ref` is an external release check; unlike the other commands, it may
download and execute tooling. Confirm the trusted tool and version first, then
record the exact version/command used. Stop on a failed prerequisite.

## GitHub / Skills ecosystem

Review and commit the prepared source. Creating a tag and pushing are separate
release actions; use the intended branch and actual release version.

```bash
git status --short
git add README.md LICENSE CHANGELOG.md CONTRIBUTING.md SECURITY.md package.json .gitignore .npmignore skills scripts tests docs .claude/skills/revisao
git commit -m "Prepare AstraMax Reviewer 0.1.0"
git tag -a v0.1.0 -m "AstraMax Reviewer 0.1.0"
git push origin HEAD
git push origin v0.1.0
```

The `.claude/skills/revisao` path stages the legacy removals during the initial
migration only; omit it after that migration is committed. Check staged changes
before committing. Do not push unrelated work.

Confirm that `https://github.com/alencardoug/astramax` is public and that the
release includes the canonical skill and all references. In a clean disposable
project, after confirming installer syntax:

```bash
npx skills add https://github.com/alencardoug/astramax --skill astramax-reviewer
```

Verify detection, selection, description, complete references and byte-for-byte
`SKILL.md` agreement with the released source. Ensure installation does not run
checks or modify implementation. Record the destination and installer version.

Set a clear GitHub description and topics such as `agent-skill`, `agent-skills`,
`claude-code`, `codex`, `code-review`, `gpt-6-astra`, `ai-agents`, `skillsmp` and
`skillpm`. Verify SkillsMP discovery separately; do not promise indexing or add a
duplicated skill for an index.

## npm / SkillPM

Confirm authentication and proposed name separately:

```bash
npm whoami
npm view astramax-reviewer name version maintainers
```

A network/authentication error does not establish name availability. If the
unscoped name belongs to someone else, choose a scope you control, update the
package name and README installation command, and rerun validation. Never rename
the skill directory/frontmatter just to match an npm scope.

Create and inspect the actual archive:

```bash
npm pack --offline --cache .npm-cache
tar -tzf astramax-reviewer-0.1.0.tgz
```

Use the actual filename printed by `npm pack` if the package name changed. It
must contain only the package manifest, README, LICENSE, CHANGELOG and canonical
skill files. Confirm relative links and that there are no credentials, reports,
caches, portfolio assets or development files.

Before publishing, test that archive in a fresh disposable project with the
verified SkillPM version. Use its documented local-tarball installation syntax;
do not assume an untested argument form. Then check:

```bash
npx skillpm list
```

Verify `astramax-reviewer`, its description, reference contents and host discovery.
If local archives are unsupported by that version, resolve and document a real
pre-publication test path before declaring this prerequisite met. An npm archive
that extracts correctly is not a SkillPM installation test.

Only after reviewing the exact archive and passing prerequisites, publish it:

```bash
npm publish ./astramax-reviewer-0.1.0.tgz --access public
```

Again, use the actual filename. Publishing the inspected archive keeps the release
contents identical to those reviewed. After publication, test in another clean
project with the confirmed package name:

```bash
npx skillpm install astramax-reviewer
npx skillpm list
```

Record the released npm version, installed files, installer version and result.
Update compatibility and announce npm/SkillPM support only after this succeeds.
