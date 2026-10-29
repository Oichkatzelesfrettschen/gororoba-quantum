# Free-plan usage, credits, and activities

This note is the measured billing model for the project in
[the AWS account note](README.md). It records what the free plan can run, which
of that usage leaves the credit balance alone, and which usage draws the
credits. The service names in
[Supported AWS services for Sign up for AWS (new)](https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html)
are the availability list. The quantities below are the published price bands
inside that list.

The plan reads are from 2026-10-24 and 2026-10-28. The public price files were
read on 2026-10-29 from
`https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<offer>/current/us-east-2/index.json`,
or the global `index.json` where the meter is global. A 2026-10-29 re-read of
the project itself did not run: the `aws login` session had expired.

## How a call is paid for

The free plan keeps one credit balance, `accountPlanRemainingCredits`. A new
customer receives 100 USD at sign-up and can earn up to another 100 USD from
the activities below. The balance on 2026-10-24 was 100.00 USD. On 2026-10-28
it was 99.91 USD. The plan expiration is 2027-04-24T18:14:41Z. The plan ends at
that instant or when the balance reaches zero, whichever comes first. No
invoice is sent while the plan stays free. Past that point the project is
suspended, content is kept for 90 days, and then the account and its data are
deleted unless the owner upgrades. Sources:
[Free Tier in our new AWS experience](https://docs.aws.amazon.com/accounts/latest/reference/bcm-lite-free-tier.html),
[Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html),
and the [Free Tier FAQ](https://aws.amazon.com/free/free-tier-faqs/).

| Layer | What happens to the balance | What this project showed |
|---|---|---|
| List price zero, or usage inside an always-free band | The balance stays put. Past the band, the overage draws credits. | `get-free-tier-usage` returned no rows on 2026-10-28, so no always-free meter had recorded usage. |
| Billable usage with no always-free band | Every charged unit draws credits. | The balance fell 0.09 USD between the two reads. The service that drew it was not in those reads. |
| Activity reward | Completing an activity adds 20 USD. The reward is not a price and not a hold. | No activity was `COMPLETED` on 2026-10-28, so none of the 20 USD rewards had been granted. |

The free plan activates always-free offers only. Short-term trials are a paid
plan feature
([Tracking your AWS Free Tier usage](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html)).
A service can be on the free-plan list and still have no always-free band.
Lightsail, Location Service, DataZone, Timestream, and SageMaker runtime are in
that position: their published free meters are short-term trials, so their
billable use draws credits. Amazon EC2 for an account opened on or after 15
July 2025 is the same shape. The hour allowance of the older free tier is not
this account's allowance. EC2 use draws credits
([Track your Free Tier usage for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html)).

Credits apply across the project's one Region. They are not transferable, and
this plan is not eligible for other promotional credits. Activity rewards, once
granted, expire 12 months after the account was opened and can take up to 30
minutes to appear. The plan expiration above is the free plan's own end, which
is six months. Each activity also has its own complete-by time, `expiresAt`,
which this session did not retrieve.

## What was running

On 2026-10-28, `us-east-2` had no EC2 instances, S3 buckets, Lambda functions,
RDS instances, EKS clusters, or budgets. The IAM roles present were the managed
roles of this sign-up, including `AccountFullAccessRole`. Both CLI profiles
sign in to the same project. Regional calls succeed on `gororoba` because that
profile's region is `us-east-2`. The `default` profile's region is `us-east-1`,
and `ec2:DescribeInstances` there was denied by the region policy.

`us-east-1` still accepts the partitional calls in the published region policy:
billing reads, `freetier:*`, IAM, STS, Route 53, CloudFront, logs, WAF, and
Bedrock invoke calls that do not create a regional resource. `us-west-2`
accepts a shorter list of the same kind. Every other Region is denied apart
from those Bedrock invoke calls. The policy text is
[Managed policies for your organization](https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html),
statements `UsEast1Partitional`, `UsWest2Partitional`, and `RegionFloor`.

## The five activities

`reward.credit` is "the credits gained by activity rewards", granted when the
activity is completed
([ActivityReward](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_freetier_ActivityReward.html)).
The 20 USD is money added to the balance. It is not the cost of the activity.

Four of the five activity pages also say the work incurs service charges that
are deducted from the credits. Those charges are the service's own price, at
the bands in this note, and they can start before the reward is granted. The
net change at completion is 20 USD minus whatever those charges were. Leaving
the instance, function, or database in place keeps drawing credits after the
reward, and there is no second reward. The Budgets page does not carry that
charge sentence. Its meter is the always-free budgets band below.

The list was read on 2026-10-28 with `aws freetier list-account-activities`.

| Activity | API id | Status on 2026-10-28 | Reward | Charges while doing it |
|---|---|---|---|---|
| Launch an instance using EC2 | `6fffb441b82fa60bf08e7e869e0d96fb` | `IN_PROGRESS` | 20 USD when completed | Yes. EC2 On-Demand price, deducted from credits. This is the only activity that had been started, and it is the candidate for the 0.09 USD already drawn. |
| Use a foundation model in the Bedrock playground | `8ad1ecaa66a78d4e3c2f8a678d28b595` | `NOT_STARTED` | 20 USD when completed | Yes. Bedrock inference price, deducted from credits. |
| Set up a cost budget using AWS Budgets | `7cd845309d890faf7270bb426560c01e` | `NOT_STARTED` | 20 USD when completed | The activity page states no deduction. The always-free band is 62 action-enabled budget-days at a list price of zero. |
| Create a web app using Lambda | `798b3b7acc72600f4aed6544f1c1e7fb` | `NOT_STARTED` | 20 USD when completed | Yes, where the tutorial leaves the Lambda always-free band. The page says the charges are deducted from credits. |
| Create an Aurora or RDS database | `8205347977b6d2134653bc122ea7d4f3` | `NOT_STARTED` | 20 USD when completed | Yes. RDS and Aurora have no always-free band on this plan, so the database draws credits while it exists. |

The descriptions are
[Earning additional credits](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans-activities.html).
`get-account-activity` also returns `startedAt`, `completedAt`, `expiresAt`,
and the instructions URL. Those fields were not in the list payload, and the
2026-10-29 call did not run.

## Always-free bands

Usage inside a band has list price zero and does not draw credits. The next
unit past the band has a non-zero list price and draws credits. The bands are
monthly unless the unit says otherwise. "Global" in the usage type is one
allowance for the whole project, which here means `us-east-2` plus the
partitional calls the region policy allows.

| Meter | Zero-price band | Past the band |
|---|---|---|
| Lambda requests, `Global-Request` | 1,000,000 requests | Request price draws credits. |
| Lambda duration, `Global-Lambda-GB-Second` | 400,000 GB-seconds | Duration price draws credits. |
| Lambda streaming response, `Global-Lambda-Streaming-Response-Processed-Bytes` | 100 processed GB | Further processed GB draw credits. |
| DynamoDB storage, `USE2-TimedStorage-ByteHrs` | 25 GB-months | 0.25 USD per GB-month. |
| DynamoDB read capacity, `USE2-ReadCapacityUnit-Hrs` | 18,600 unit-hours, the price text's "25 units for a month" | 0.00013 USD per unit-hour. |
| DynamoDB write capacity, `USE2-WriteCapacityUnit-Hrs` | 18,600 unit-hours, the same "25 units for a month" | 0.00065 USD per unit-hour. |
| DynamoDB Streams, `USE2-Streams-Requests` | 2,500,000 read request units | 0.0000002 USD per unit. |
| CloudWatch metrics, `Global-CW:MetricMonitorUsage` | 10 metrics | Further metrics draw credits. |
| CloudWatch alarms, `Global-CW:AlarmMonitorUsage` | 10 alarms | Further alarms draw credits. |
| CloudWatch logs storage, `Global-TimedStorage-ByteHrs` | 5 GB-months | Further storage draws credits. |
| CloudWatch logs scanned, delivered, and processed | 5 GB on each of those three meters | Further GB draw credits. |
| CloudWatch requests, `Global-CW:Requests` | 1,000,000 requests | Further requests draw credits. |
| CloudWatch Live Tail | 1,800 minutes | Further minutes draw credits. |
| CloudWatch canaries | 100 runs | Further runs draw credits. |
| CloudWatch Contributor Insights | 1,000,000 events and 1 rule-hour | Further use draws credits. |
| CloudWatch Database Insights API | 1,000,000 API calls | Further calls draw credits. |
| SQS requests, `Global-Requests` | 1,000,000 requests | Further requests draw credits. |
| SNS API requests, `USE2-Requests-Tier1` | 1,000,000 requests | Further requests draw credits. |
| SNS HTTP or HTTPS deliveries | 100,000 | Further deliveries draw credits. |
| SNS email deliveries | 1,000 | Further deliveries draw credits. |
| SNS mobile push | 1,000,000 | Further notifications draw credits. |
| EventBridge schema-discovery ingest, `Global-Event-8K-Chunks` | 5,000,000 events | Further events draw credits. |
| EventBridge Scheduler invocations, `USE2-ScheduledInvocation` | 14,000,000 | Further invocations draw credits. |
| Step Functions transitions, `Global-StateTransition` | 4,000 | Further transitions draw credits. |
| Data transfer out to the internet, `Global-DataTransfer-Out-Bytes` | 100 GB, aggregated globally | 0.090 USD per GB for the next 10 TB from `us-east-2`. |
| Regional data transfer, `Global-DataTransfer-Regional-Bytes` | 1 GB | Further regional transfer draws credits. |
| CloudFront requests, `Global-Requests-Tier1` | 10,000,000 HTTP or HTTPS requests | Further requests draw credits. |
| CloudFront data out, `Global-DataTransfer-Out-Bytes` | 1,024 GB | Further data out draws credits. |
| CloudFront Functions, `Executions-CloudFrontFunctions` | 2,000,000 executions | Further executions draw credits. |
| CloudFront invalidations | 1,000 URLs | Further URLs draw credits. |
| X-Ray traces stored | 100,000 | Further traces draw credits. |
| X-Ray traces accessed | 1,000,000 | Further retrievals draw credits. |
| KMS requests, `Global-KMS-Requests` | 20,000 | Further requests draw credits. A customer-managed key has its own monthly price and is not in this band. |
| Glue Data Catalog requests | 1,000,000 | Further requests draw credits. Glue jobs and crawlers are outside this band. |
| Glue Data Catalog storage | 1,000,000 object-months | Further objects draw credits. |
| CodeBuild `build.general1.small` | 100 build minutes | Other compute sizes, and minutes past 100, draw credits. |
| CodeBuild Lambda 1 GB | 6,000 build seconds | Further seconds draw credits. |
| CodeCommit users, `User-Month` | 5 users | Further users draw credits. |
| CodePipeline | 1 active pipeline and 100 action-execution minutes | Further pipelines and minutes draw credits. |
| CodeArtifact storage | 2 GB under the monthly free tier | Further storage draws credits. |
| CodeArtifact requests | 100,000 | Further requests draw credits. |
| CloudFormation, `Global-Resource-Invocation-Count-FreeTier` | 1,000 operations | Further operations draw credits. |
| Budgets, `ActionEnabledBudgetsUsage` | 62 action-enabled budget-days | Further budget-days draw credits. |
| SWF workflow executions | 1,000 | 0.0001 USD each past the band. |
| SWF tasks, signals, timers, and markers | 10,000 | 0.000025 USD each past the band. |
| SWF open and retained workflow-days | 30,000 | 0.000005 USD per day past the band. |
| Cognito user-pool MAU, `Global-CognitoUserPoolMAU` | 50,000 | Further monthly active users draw credits. |
| Cognito free-tier MAU, `Global-CognitoFreeTierMAU` | 10,000 | The price text calls this the global free tier. |
| Cognito enterprise MAU | 50 | Further enterprise users draw credits. |
| Prometheus samples ingested | 40,000,000 in `us-east-2` | Further samples draw credits. |
| Prometheus storage | 10 GB-months | Further storage draws credits. |
| Prometheus query samples | 200,000,000,000 | Further samples draw credits. |
| SES mailbox simulator, `Global-Recipients-MailboxSim-EC2` | 62,000 recipients | The simulator address is the meter. |
| SES virtual deliverability queries, `Global-VirtDelivMgr` | 5,000 queries | The deliverability dashboard action is denied, so this band cannot be turned on from this project. |

DynamoDB replicated writes also have a 25-unit always-free band. Replication is
a cross-region feature, and the region policy denies it, so that band is not
usable here.

CloudFront Lambda@Edge is a separate price and is outside this project's
service list. SNS SMS is End User Messaging, which is a paid-plan service.
Ordinary SES send and receive prices in the `us-east-2` file start at
0.00015 USD and 0.0001 USD per message, with no zero band. The usage tracker
still names `Message` as an always-free type, and `get-free-tier-usage` had no
row for it, so a send is treated as credit-metered until a free-tier row
appears. The `us-east-2` Route 53 file likewise has no zero band. The tracker
names only `Cidr-Blocks` and `Health-Check-AWS` as always free, and those
quantities were not in that file. A hosted zone's list price draws credits.

S3 Standard storage in `us-east-2` is priced from the first byte. The only
zero-priced S3 meter in that file is Storage Lens Free Tier, whose object-count
price is zero for the whole range. The S3 usage report separately calls the
first 2,000 general-purpose buckets an account-level free tier for the
bucket-count charge. Bucket storage still draws credits.

A few Bedrock meters are priced at zero for their whole range rather than for
a monthly quantity. In the `us-east-2` file those are some Nova cache-write
token counts and some guardrail text units. Ordinary model inference is priced
and draws credits, which is why the Bedrock activity says its charges come out
of the credits. Cross-region Bedrock meters are outside the region policy.

## Credit-metered on this plan

These services are on the free-plan list and have no always-free quantity in
the sources above. Billable use draws credits from the first unit. Control-plane
calls whose list price is zero, such as a describe that returns an empty list,
do not move the balance. That is what the empty inventory reads did.

| Service | What draws the credits |
|---|---|
| EC2 and EBS | Instance hours, EBS GB-months, and public IPv4 where the price is non-zero. No micro-instance hour allowance applies to this account. |
| ECS, EKS, ECR, Batch, Elastic Beanstalk, Auto Scaling, ELB | The compute, storage, and load-balancer hours they create. ECS Anywhere hours are a short-term trial and are not active. |
| RDS, Aurora, Aurora DSQL, ElastiCache, OpenSearch | Instance, storage, and I/O hours for as long as the resource exists. DocumentDB is denied. |
| S3, EFS | Storage and requests at the regional list price. S3 Glacier and Deep Archive storage classes are denied. |
| API Gateway, AppSync, Amplify, AppFlow, MQ, MWAA Serverless | Request, connection, and environment charges past any zero control-plane call. |
| Bedrock inference, SageMaker, Rekognition, Lex, Polly | Model and inference units. SageMaker's published free meter is a short-term trial and is not active. |
| Lightsail, Location Service, DataZone, Timestream | The whole bundle or request price. Their free meters are short-term trials and are not active. |
| Backup, Config, CloudTrail, Secrets Manager, Certificate Manager, customer-managed KMS keys | Resource-hours and records. KMS request 1 through 20,000 stays in the band above. Exportable public certificates are denied. |
| NAT gateways, public IPv4, and VPC endpoints that carry a price | Hourly and data charges. Transit gateways, Client VPN, and Site-to-Site VPN are denied outright. |
| Athena, Glue jobs, DataZone compute | Query and job hours. Glue catalog requests and storage stay in the band above. |

## Standing denies, finer than the service list

The free-tier service control policy allows the free-plan service list and then
denies particular actions inside it. The text is the `AllowFreeTierServices`
policy and the statements that follow it in
[Managed policies for your organization](https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html).
Braket is absent from the allow list, so every Braket call is denied. The same
is true of the services in the paid-plan and unsupported lists.

Inside the allowed services, these actions are denied on their own:

| Statement | What it refuses |
|---|---|
| `DenyEC2CapacityBlock` | Purchasing an EC2 Capacity Block or an extension. |
| `DenyEC2Fleet` | `ec2:CreateFleet`. |
| `DenyRequestSpotInstances`, `DenySpotMarketType` | Spot requests, and `RunInstances` whose market type is spot. |
| `DenyEC2BYOLAndLicenseConfigurations` | `RunInstances` and `StartInstances` with host tenancy. |
| `DenyEC2InstanceStoreRootDevice` | `RunInstances` whose root device is instance-store. |
| `DenyReservedInstanceAndCapacityPurchases` | Reserved Instances, Savings Plans, capacity reservations, and dedicated hosts. |
| `DenyGlacierStorageClasses` | `s3:PutObject` with storage class `GLACIER` or `DEEP_ARCHIVE`. |
| `DenyDocDB` | Creating an RDS instance or cluster whose engine is `docdb`. |
| `DenyTransitGatewayAndVPN`, `DenyCloudWAN` | Transit Gateway, Client VPN, Site-to-Site VPN, and Cloud WAN attachments. |
| `DenyExportableCertificateRequests` | `acm:RequestCertificate` with export allowed. |
| `DenySESGlobalDeliverability` | `ses:PutDeliverabilityDashboardOption`. |
| `DenySageMakerGroundTruth` | Ground Truth labeling jobs, workteams, and workforces. |
| `DenyIAMRestrictedActions`, `DenySSOCreateInstance` | Creating a group, login profiles, SAML providers, and an Identity Center instance. |
| `DenyRestrictedAgreements` | Accepting the named Artifact HIPAA and SEC agreements. |

An ordinary On-Demand `ec2:RunInstances` with an EBS root volume is not in that
deny list. The earlier account note recorded a `simulate-principal-policy`
result as a blanket `ec2:RunInstances` deny. That blanket deny is
`DenyCompute` in the spend-limit policy, which AWS attaches when a paid-plan
spend limit is nearly reached. This free plan has no spend limit, and that
policy is not the standing one. A dry run of `RunInstances` in `us-east-2` was
not repeated after the login session expired.

The region floor is a separate deny. Ordinary regional resources outside
`us-east-2` fail even when the service is on the free-plan list. The starter
rules document a narrow exception: AWS WAF and CloudWatch Logs resources may be
created in `us-east-1` when a global resource requires dependencies there; they
should not be used there for other reasons.

## Reads that refresh this note

```sh
aws freetier get-account-plan-state --profile gororoba --region us-east-1
aws freetier get-free-tier-usage --profile gororoba --region us-east-1
aws freetier list-account-activities --profile gororoba --region us-east-1
aws ce get-cost-and-usage --profile gororoba --region us-east-1 \
    --time-period Start=$(date -u +%Y-%m-01),End=$(date -u -d tomorrow +%F) \
    --granularity MONTHLY --metrics UnblendedCost \
    --group-by Type=DIMENSION,Key=SERVICE
```

`get-account-activity --activity-id <id> --language-code en-US` returns one
activity's `expiresAt` and description. The ids are in the table above. The
[provider credits monitor](../../runbooks/provider-credits.md) already records
the balance and the month-to-date unblended cost. Unblended cost is the charge
estimate. The balance is the credits still available. An always-free band can
show usage in `get-free-tier-usage` while the balance stays still.
