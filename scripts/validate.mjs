// Repository maintenance only: no dependencies, downloads or model invocation.
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const skill = 'skills/astramax-reviewer';
const required = [
  'README.md', 'LICENSE', 'CHANGELOG.md', 'CONTRIBUTING.md', 'SECURITY.md',
  'package.json', '.gitignore', '.npmignore',
  'docs/DESIGN.md', 'docs/VALIDATION.md', 'docs/PUBLISHING.md',
  `${skill}/SKILL.md`, `${skill}/references/review-methodology.md`,
  `${skill}/references/finding-severity.md`, `${skill}/references/compatibility.md`,
  `${skill}/references/handoff.md`, `${skill}/scripts/dossier.py`,
];
const errors = [];
function ensure(condition, message) { if (!condition) errors.push(message); }
function read(path) { return readFileSync(resolve(root, path), 'utf8'); }
function walk(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    if (['.git', '.npm-cache', 'node_modules', '__pycache__', '.venv'].includes(entry.name)
        || entry.name.startsWith('.astramax-test-')) return [];
    const path = resolve(directory, entry.name);
    if (entry.isSymbolicLink()) {
      errors.push(`Unexpected symlink in source tree: ${relative(root, path)}`);
      return [];
    }
    return entry.isDirectory() ? walk(path) : [relative(root, path).split(sep).join('/')];
  });
}

try {
  for (const path of required) ensure(existsSync(resolve(root, path)), `Missing ${path}`);
  if (errors.length) throw new Error('Required files missing');
  const files = walk(root);
  const canonical = files.filter(path => path.split('/').at(-1) === 'SKILL.md');
  ensure(canonical.length === 1 && canonical[0] === `${skill}/SKILL.md`, 'Expected one canonical SKILL.md');
  ensure(!files.some(path => path.startsWith('.claude/skills/revisao/')), 'Legacy skill must be migrated, not duplicated');

  const body = read(`${skill}/SKILL.md`);
  const front = body.match(/^---\n([\s\S]*?)\n---\n/);
  ensure(Boolean(front), 'SKILL.md must begin with YAML frontmatter');
  const metadata = {};
  for (const line of (front?.[1] ?? '').split('\n')) {
    const match = line.match(/^([a-z-]+): (.+)$/);
    ensure(Boolean(match), `Expected simple single-line frontmatter: ${line}`);
    if (match) {
      ensure(!(match[1] in metadata), `Duplicate frontmatter: ${match[1]}`);
      metadata[match[1]] = match[2];
    }
  }
  ensure(Object.keys(metadata).sort().join(',') === 'description,license,name', 'Keep frontmatter to name, description and license');
  ensure(metadata.name === 'astramax-reviewer', 'Skill name must match its directory');
  ensure(metadata.license === 'MIT', 'Skill license must be MIT');
  ensure(metadata.description?.length > 80 && metadata.description.length <= 1024, 'Description must be useful and at most 1024 characters');
  ensure(/review/i.test(metadata.description ?? '') && /use /i.test(metadata.description ?? ''), 'Description must state purpose and triggers');
  ensure(body.split('\n').length < 150, 'Keep SKILL.md concise; move details into references');
  for (const token of ['PASS', 'PASS WITH MINOR FINDINGS', 'CHANGES RECOMMENDED', 'CHANGES REQUIRED', 'UNABLE TO VERIFY']) {
    ensure(body.includes(`\`${token}\``), `Missing verdict: ${token}`);
  }
  ensure(!/parents\[3\]|make dbt-build|CLAUDE\.md.{0,3}§|comandos\.txt/.test(body), 'Project-specific coupling in core skill');

  const pkg = JSON.parse(read('package.json'));
  ensure(/^(?:@[a-z0-9._-]+\/)?astramax-reviewer$/.test(pkg.name), 'Package may be scoped, but must retain astramax-reviewer');
  ensure(/^\d+\.\d+\.\d+(?:-[\w.-]+)?$/.test(pkg.version), 'Expected semantic package version');
  ensure(read('CHANGELOG.md').includes(`## ${pkg.version}`), 'Changelog must include package version');
  ensure(pkg.license === 'MIT' && read('LICENSE').startsWith('MIT License\n'), 'Package and repository license must be MIT');
  ensure(!pkg.bin && !pkg.main && !pkg.exports, 'The skill package must not pretend to be a runtime application');
  for (const field of ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']) {
    ensure(!Object.keys(pkg[field] ?? {}).length, `Unexpected ${field}`);
  }
  for (const hook of ['preinstall', 'install', 'postinstall', 'prepare']) {
    ensure(!pkg.scripts?.[hook], `Unexpected install lifecycle hook: ${hook}`);
  }
  ensure(pkg.scripts?.validate === 'node scripts/validate.mjs', 'Validation must remain local and dependency-free');
  ensure(pkg.scripts?.prepack === 'npm run validate', 'prepack must validate the source');
  const intendedFiles = [
    `${skill}/SKILL.md`, `${skill}/references/*.md`, `${skill}/scripts/dossier.py`,
    'README.md', 'LICENSE', 'CHANGELOG.md',
  ];
  ensure(JSON.stringify(pkg.files) === JSON.stringify(intendedFiles), 'Unexpected npm file allowlist; review package contents');
  const intendedSkillFiles = required.filter(path => path.startsWith(`${skill}/`));
  ensure(files.filter(path => path.startsWith(`${skill}/`)).every(path => intendedSkillFiles.includes(path)), 'Unexpected file in installable skill');
  ensure(pkg.repository?.url === 'git+https://github.com/alencardoug/astramax.git', 'Repository metadata differs from recorded origin; update intentionally');
  ensure(!JSON.stringify(pkg).includes('<github-user>'), 'Replace placeholder package metadata');

  for (const path of required.filter(path => path.endsWith('.md'))) {
    const text = read(path);
    // This repository uses ordinary inline Markdown links. Remote URLs and
    // anchors are deliberately not fetched or claimed to be validated.
    for (const match of text.matchAll(/\[[^\]\n]+\]\(([^)\s]+)\)/g)) {
      const target = match[1];
      if (/^[a-z][a-z0-9+.-]*:|^#/i.test(target)) continue;
      const destination = resolve(root, dirname(path), decodeURIComponent(target.split('#')[0]));
      ensure(destination.startsWith(root + sep), `Link escapes repository in ${path}: ${target}`);
      ensure(existsSync(destination), `Broken local link in ${path}: ${target}`);
      if (path.startsWith(`${skill}/`)) {
        ensure(destination.startsWith(resolve(root, skill) + sep), `Installed skill link escapes its package in ${path}: ${target}`);
      }
    }
  }
} catch (error) {
  errors.push(error.message);
}

if (errors.length) {
  for (const error of errors) console.error(`FAIL: ${error}`);
  process.exitCode = 1;
} else {
  console.log('Local validation passed: canonical skill, metadata, references, package contract and migration checks.');
  console.log('Official Agent Skills validation and live host/installer compatibility are separate, unverified release checks.');
}
