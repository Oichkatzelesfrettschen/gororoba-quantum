# AWS account (new AWS experience)

The owner's AWS account is a "project" under AWS's new AWS experience, on the
free account plan. Amazon Braket, AWS's quantum service, is not available to
it: the new experience excludes Braket unless advanced AWS features are
activated
([supported services](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#unsupported-services)),
and the project's managed service control policy answers every Braket call,
`braket:SearchDevices` included, with an explicit deny. The account is
therefore a credit-limited cloud for tooling, not a quantum backend. AWS
Settings (<https://settings.aws.com/>) and the CLI stay the authority. The
[usage note](free-plan-usage.md) separates always-free monthly bands, which
leave the credit balance alone, from usage that draws the plan credits, and
it records each credit activity's $20 as a reward rather than a price.

| Path | Content |
|---|---|
| [free-plan-usage.md](free-plan-usage.md) | measured plan, the five activities, always-free quantities, and credit-metered usage |
| [python-packages.md](python-packages.md) | host Python packages for AWS: imports, public names, and what was left uninstalled |
| [aws-starter-rules.md](aws-starter-rules.md) | the Agent Toolkit's rules for the new AWS experience, verbatim at commit `e8c63094` of `aws/agent-toolkit-for-aws`, under a header naming the URL and the sha256 |

## Account, plan and spend

| Item | Value | Source |
|---|---|---|
| Plan | `FREE`, status `ACTIVE` | `aws freetier get-account-plan-state`, 2026-10-24 and 2026-10-28 |
| Credits | 100.00 USD on 2026-10-24; 99.91 USD on 2026-10-28 | `accountPlanRemainingCredits` |
| Plan end | 2027-04-24T18:14:41Z | `accountPlanExpirationDate` |
| Month-to-date cost | 0 USD on 2026-10-24 | `aws ce get-cost-and-usage` |
| Always-free usage rows | none on 2026-10-28 | `aws freetier get-free-tier-usage` |
| Region | us-east-2 | `ec2:DescribeInstances` succeeded there on 2026-10-28 and the same call was denied in us-east-1, eu-north-1, and ap-southeast-2 |
| Profile | `gororoba` is us-east-2; `default` is us-east-1 and fails regional calls | `~/.aws/config` |
| Denied by the project's policy | `braket:*` reads and tasks; spot instance requests; EC2, Lambda, CodeBuild, SageMaker, Batch and ECS outside us-east-2 | `aws iam simulate-principal-policy`, observed errors |
| EC2 in us-east-2 | free-tier-eligible types only, the largest `m7i-flex.large` (2 vCPU, 8 GiB); a launch of another type fails with `InvalidParameterCombination` although `--dry-run` accepts it (read 2026-10-28); on-demand standard quota 16 vCPU | `ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true`, `ec2 run-instances` |

The 2026-10-29 re-read stopped because the `aws login` session had expired.
The 0.09 USD drop is credit-metered usage: an always-free band does not reduce
`accountPlanRemainingCredits`. Which service drew it was not in the 2026-10-28
reads. The only activity then in progress was the EC2 launch.

Three layers decide whether a call spends anything. A list price of zero, and
usage inside an always-free band, leaves the credit balance unchanged. Billable
usage past those bands draws the plan credits. The free plan sends no invoice.
The plan ends when the credits reach zero or at the expiration above, whichever
comes first, and the project is then suspended. Data is retained for 90 days.
An upgrade to the paid plan is the owner's decision alone. A paid plan is what
adds a spend limit, short-term trials, and an invoice for usage the credits do
not cover. The standing free-plan policy allows an ordinary On-Demand
`ec2:RunInstances` in us-east-2. It denies host tenancy, instance-store root
volumes, and spot. A blanket `ec2:RunInstances` deny belongs to the spend-limit
policy, which is not the policy in force. Details, quantities, and the activity
rewards are in [free-plan-usage.md](free-plan-usage.md).

Two read-only calls give the plan state, remaining credits, and month-to-date
cost:

```sh
aws freetier get-account-plan-state --profile gororoba --region us-east-1
aws ce get-cost-and-usage --profile gororoba --region us-east-1 \
    --time-period Start=$(date -u +%Y-%m-01),End=$(date -u -d tomorrow +%F) \
    --granularity MONTHLY --metrics UnblendedCost
```

The [provider credits monitor](../../runbooks/provider-credits.md) runs both
reads daily with every other provider's allotment and alerts within 7 days
of the plan's expiry.

## CLI and sign-in

`aws-cli-v2` comes from the Arch `extra` repository (2.37.9). The profile
`gororoba` holds the region and a browser sign-in:

```sh
aws configure set region us-east-2 --profile gororoba
aws login --region us-east-2 --profile gororoba
aws sts get-caller-identity --profile gororoba
```

`aws login` credentials last 12 hours and renew for 90 days without another
browser sign-in. The session assumes the managed `AccountFullAccessRole`.
The account id stays out of every commit and record.

## Agent Toolkit and the AWS MCP server

`aws configure agent-toolkit --yes --region us-east-1 --profile gororoba`
installed 24 AWS skills (into `~/.claude/skills` and `~/.agents/skills/`)
and registered an `aws-mcp` server in Claude Code, Codex, Gemini CLI,
OpenCode and Windsurf. The same command on 2026-10-28 refreshed those skills.
It rewrote the Codex entry to `mcp-proxy-for-aws@latest` and dropped the
profile variable; that entry was restored to the pin below. Grok
(`~/.grok/config.toml`) and Agy (`~/.gemini/config/mcp_config.json`, the file
`agy mcp` writes) are outside the installer's agent list, so the same pin and
profile variable were added with each tool's own MCP command. Each
registration runs the proxy at an exact release and names the profile:

```json
"aws-mcp": {
  "command": "uvx",
  "args": ["mcp-proxy-for-aws==1.7.0", "https://aws-mcp.us-east-1.api.aws/mcp",
           "--metadata", "INSTALL_SOURCE=aws-cli"],
  "env": {"AWS_MCP_PROXY_PROFILES": "gororoba"}
}
```

The installer writes `mcp-proxy-for-aws@latest`, which resolves a new
release at every start; the exact pin keeps the executed code fixed until a
deliberate update, and an update changes the version in all five files
together. Without `AWS_MCP_PROXY_PROFILES` the proxy falls back to the
`default` profile and fails with `JSON-RPC error: -32602`. A second account
joins by `aws login --profile NAME` and a space-separated addition to that
variable. `aws agent-toolkit list-available-skills --region us-east-1
--profile gororoba` lists the remote skill catalog (115 skills on
2026-10-24).

The starter rules govern AWS work in this account; where they conflict with
this repository's AGENTS.md, the repository wins, as the rules themselves
state. The current new-experience rules live, under the same begin and end
markers, in the user-level rule files for Grok, Claude, Codex, and Agy, which
every session in this repository loads; this repository's AGENTS.md carries no
copy, so a session reads them once.

The operator names Future Startup as the default group for this new-experience
organization. The project role can list one Identity Center group, the managed
AdministratorAccess group, and denies `identitystore:CreateGroup`, so the
Future Startup group does not exist yet; creating it needs a role that holds
that action.
