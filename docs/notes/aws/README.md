# AWS account (new AWS experience)

The owner's AWS account is a "project" under AWS's new AWS experience, on the
free account plan. Amazon Braket, AWS's quantum service, is not available to
it: the new experience excludes Braket unless advanced AWS features are
activated
([supported services](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html#unsupported-services)),
and the project's managed service control policy answers every Braket call,
`braket:SearchDevices` included, with an explicit deny. The account is
therefore a credit-limited cloud for tooling, not a quantum backend. The
facts below were read on 2026-10-24; AWS Settings (<https://settings.aws.com/>)
and the CLI stay the authority.

| Path | Content |
|---|---|
| [aws-starter-rules.md](aws-starter-rules.md) | the Agent Toolkit's rules for the new AWS experience, verbatim at commit `e8c63094` of `aws/agent-toolkit-for-aws`, under a header naming the URL and the sha256 |

## Account, plan and spend

| Item | Value | Source |
|---|---|---|
| Plan | `FREE`, status `ACTIVE` | `aws freetier get-account-plan-state` |
| Credits | 100.00 USD remaining | same, `accountPlanRemainingCredits` |
| Plan end | 2027-04-24T18:14Z | same, `accountPlanExpirationDate` |
| Month-to-date cost | 0 USD | `aws ce get-cost-and-usage` |
| Region | us-east-2, the project's single Region; the Agent Toolkit service runs in us-east-1 | AWS Settings; [starter rules](aws-starter-rules.md) |
| Denied by the project's policy | `braket:*` reads and tasks; spot instance requests; EC2, Lambda, CodeBuild, SageMaker, Batch and ECS outside us-east-2 | `aws iam simulate-principal-policy`, observed errors |
| EC2 in us-east-2 | free-tier-eligible types only, the largest `m7i-flex.large` (2 vCPU, 8 GiB); a launch of another type fails with `InvalidParameterCombination` although `--dry-run` accepts it (read 2026-10-28); on-demand standard quota 16 vCPU | `ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true`, `ec2 run-instances` |

On the free plan AWS charges nothing: usage draws the credits, and the plan
ends when they run out or at its expiration date. Charges begin only after
an upgrade to the paid plan, so an upgrade is the owner's decision alone and
never an agent's; a paid plan then takes a spend limit in AWS Settings, which
pauses the project when exceeded. Two read-only calls give the plan state,
remaining credits and month-to-date cost:

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
OpenCode and Windsurf. Each registration runs the proxy at an exact release
and names the profile:

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
state.
