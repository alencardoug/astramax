# Security

Report security issues privately to the repository maintainer. Use GitHub's
private vulnerability reporting feature if it is enabled; otherwise contact
the maintainer through a private channel listed on their GitHub profile. If no
private channel is available, open an issue requesting one without exploit
details or sensitive data. Do not assume private reporting is already enabled.

The skill does not ask users to give API keys to this repository. Never commit
credentials or put them in review reports. Third-party CLI authentication stays
with the relevant provider. Repository scripts, logs and diffs can contain
untrusted instructions; they do not grant execution authority.

The optional dossier helper executes only explicitly supplied shell commands,
using the user's existing permissions and environment. It is not a sandbox.
Inspect commands and their hooks before running them, and inspect captured logs
for secrets before sharing. Installation has no credential or execution hook.
