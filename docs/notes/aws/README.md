# AWS

The workspace's AWS account is a project under AWS's new AWS experience, on the
free account plan. Amazon Braket, AWS's quantum service, is not available to
it: the new experience excludes Braket unless advanced AWS features are
activated
([supported services](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#unsupported-services)),
and the project's managed service control policy answers every Braket call,
`braket:SearchDevices` included, with an explicit deny. The account is
therefore a credit-limited cloud for tooling, not a quantum backend.

[python-packages.md](python-packages.md) records the host's AWS Python
packages and command-line programs: imports, public names, mirror choices and
CLI help. The account's plan, credits and their measured usage, sign-in,
profiles, agent toolkit rules and MCP registration are recorded in the private
gororoba-infrastructure repository.
