# Lambda wiring reference
# Yo-ai Platform — handler-to-path mapping

## Architecture

```
Inbound request
      │
      ▼
  lambda_handler.yo_ai_handler(event, context)
      │
      ▼
  mode_discriminator.discriminate(event)
      │
      ├── "a2a"  →  a2a_handler.handle(event, route_fn)
      ├── "api"  →  api_handler.api_handler(event, route_fn)
      ├── "app"  →  app_handler.handle(request, route_fn)
      └── "op"   →  op_handler.handle(event, route_fn)
                         │
                   route_fn = A2ATransport.handle_a2a
                         │
                   SolicitorGeneral → YoAiRuntime → capability handler
```

`mesh` has no Lambda or API Gateway path — in-process only via
`PlatformEventBus`. `mesh_handler.register_on_bus(bus, route_fn)` is
called once in `platform_bootstrap.bootstrap()`.

---

## Lambda function topology

Four Lambda functions cover all paths. One per startup mode.
No function per agent, no function per capability.

```
┌──────────────────────────────────────────────────────────────┐
│  yo-ai-a2a                                                   │
│  Entry:   lambda_handler.yo_ai_handler                       │
│  Mode:    a2a                                                │
│  Handler: core/handlers/a2a_handler.py                       │
│  Paths:                                                      │
│    POST /a2a                       (shared root)             │
│    POST /agents/{agentName}/a2a    (agent-scoped)            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  yo-ai-api                                                   │
│  Entry:   lambda_handler.yo_ai_handler                       │
│  Mode:    api                                                │
│  Handler: core/handlers/api_handler.py                       │
│  Paths:                                                      │
│    POST /agents/{agentName}/api/{capability}                 │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  yo-ai-app                                                   │
│  Entry:   lambda_handler.yo_ai_handler                       │
│  Mode:    app                                                │
│  Handler: core/handlers/app_handler.py                       │
│  Paths:                                                      │
│    POST /agents/{agentName}/app                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  yo-ai-op                                                    │
│  Entry:   lambda_handler.yo_ai_handler                       │
│  Mode:    op                                                 │
│  Handler: core/handlers/op_handler.py                        │
│  Paths:                                                      │
│    POST /op/{capability}                                     │
└──────────────────────────────────────────────────────────────┘
```

All four functions use the same `lambda_handler.yo_ai_handler` entry point
and the same `platform_bootstrap.bootstrap()` cold-start wiring. The
discriminator reads the path suffix and routes to the correct handler.

---

## Path convention — camelCase throughout

| Component | Convention | Example |
|-----------|-----------|---------|
| Agent name | camelCase | `doorKeeper` |
| Capability segment | camelCase | `trustAssign` |
| Mode suffix | lowercase | `a2a` `api` `app` `op` |

---

## How the discriminator reads the path

```
Path                                      [0]      [1]         [2]   [3]
────────────────────────────────────────  ───────────────────────────────────
/a2a                                      a2a      —           —     —
/agents/doorKeeper/a2a                    agents   doorKeeper  a2a   —
/agents/doorKeeper/api/trustAssign        agents   doorKeeper  api   trustAssign
/agents/doorKeeper/app                    agents   doorKeeper  app   —
/op/trustAssign                           op       trustAssign —     —
```

If `segments[0] == "agents"` the mode is `segments[2]`.
If `segments[0] == "op"` the mode is `"op"`.
If `segments == ["a2a"]` the mode is `"a2a"`.

---

## Capability resolution — api_handler vs op_handler

Both handlers share `load_capability_segment_map()` from `api_handler.py`.
Both use the same `capability_map.yaml` and the same lookup key
(the camelCase capability segment). The only difference is which path
segment holds the key.

```
api:  /agents/doorKeeper/api/trustAssign  →  segments[3] = "trustAssign"
op:   /op/trustAssign                     →  segments[1] = "trustAssign"
```

Both resolve to `Trust.Assign`. The capability map entry is the same.

---

## openapi.yaml integration blocks

### /a2a and /agents/{agentName}/a2a  →  yo-ai-a2a

```yaml
x-amazon-apigateway-integration:
  type: aws_proxy
  httpMethod: POST
  uri: arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{accountId}:function:yo-ai-a2a/invocations
  credentials: arn:aws:iam::{accountId}:role/APIGatewayLambdaExecRole
  passthroughBehavior: when_no_match
  timeoutInMillis: 29000
```

### /agents/{agentName}/api/{capability}  →  yo-ai-api

```yaml
x-amazon-apigateway-integration:
  type: aws_proxy
  httpMethod: POST
  uri: arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{accountId}:function:yo-ai-api/invocations
  credentials: arn:aws:iam::{accountId}:role/APIGatewayLambdaExecRole
  passthroughBehavior: when_no_match
  timeoutInMillis: 29000
```

### /agents/{agentName}/app  →  yo-ai-app

```yaml
x-amazon-apigateway-integration:
  type: aws_proxy
  httpMethod: POST
  uri: arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{accountId}:function:yo-ai-app/invocations
  credentials: arn:aws:iam::{accountId}:role/APIGatewayLambdaExecRole
  passthroughBehavior: when_no_match
  timeoutInMillis: 29000
```

### /op/{capability}  →  yo-ai-op

```yaml
x-amazon-apigateway-integration:
  type: aws_proxy
  httpMethod: POST
  uri: arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{accountId}:function:yo-ai-op/invocations
  credentials: arn:aws:iam::{accountId}:role/APIGatewayLambdaExecRole
  passthroughBehavior: when_no_match
  timeoutInMillis: 29000
```

---

## Per-agent paths (21 agents)

Each agent exposes three mode paths. The `{capability}` placeholder covers
all capabilities for that agent — one API Gateway resource per mode, not one
per capability.

| Agent | a2a | api | app |
|-------|-----|-----|-----|
| complaintManager | /agents/complaintManager/a2a | /agents/complaintManager/api/{capability} | /agents/complaintManager/app |
| complianceValidator | /agents/complianceValidator/a2a | /agents/complianceValidator/api/{capability} | /agents/complianceValidator/app |
| darkwebChecker | /agents/darkwebChecker/a2a | /agents/darkwebChecker/api/{capability} | /agents/darkwebChecker/app |
| dataAnonymizer | /agents/dataAnonymizer/a2a | /agents/dataAnonymizer/api/{capability} | /agents/dataAnonymizer/app |
| databrokerMonitor | /agents/databrokerMonitor/a2a | /agents/databrokerMonitor/api/{capability} | /agents/databrokerMonitor/app |
| dataSteward | /agents/dataSteward/a2a | /agents/dataSteward/api/{capability} | /agents/dataSteward/app |
| decisionMaster | /agents/decisionMaster/a2a | /agents/decisionMaster/api/{capability} | /agents/decisionMaster/app |
| doorKeeper | /agents/doorKeeper/a2a | /agents/doorKeeper/api/{capability} | /agents/doorKeeper/app |
| incidentResponder | /agents/incidentResponder/a2a | /agents/incidentResponder/api/{capability} | /agents/incidentResponder/app |
| ipInspector | /agents/ipInspector/a2a | /agents/ipInspector/api/{capability} | /agents/ipInspector/app |
| profileBuilder | /agents/profileBuilder/a2a | /agents/profileBuilder/api/{capability} | /agents/profileBuilder/app |
| purchasingAgent | /agents/purchasingAgent/a2a | /agents/purchasingAgent/api/{capability} | /agents/purchasingAgent/app |
| rewardsSeeker | /agents/rewardsSeeker/a2a | /agents/rewardsSeeker/api/{capability} | /agents/rewardsSeeker/app |
| riskAssessor | /agents/riskAssessor/a2a | /agents/riskAssessor/api/{capability} | /agents/riskAssessor/app |
| socialmediaChecker | /agents/socialmediaChecker/a2a | /agents/socialmediaChecker/api/{capability} | /agents/socialmediaChecker/app |
| solicitorGeneral | /agents/solicitorGeneral/a2a | /agents/solicitorGeneral/api/{capability} | /agents/solicitorGeneral/app |
| talentAgent | /agents/talentAgent/a2a | /agents/talentAgent/api/{capability} | /agents/talentAgent/app |
| techInspector | /agents/techInspector/a2a | /agents/techInspector/api/{capability} | /agents/techInspector/app |
| theSentinel | /agents/theSentinel/a2a | /agents/theSentinel/api/{capability} | /agents/theSentinel/app |
| vendorManager | /agents/vendorManager/a2a | /agents/vendorManager/api/{capability} | /agents/vendorManager/app |
| workflowBuilder | /agents/workflowBuilder/a2a | /agents/workflowBuilder/api/{capability} | /agents/workflowBuilder/app |

Total API Gateway resources: 21 agents × 3 modes = 63 agent paths,
plus /a2a (shared root) and /op/{capability} = **65 resources**.
Previously the spec had 96 flat per-capability paths. The new structure
is 65 resources that cover all current and future capabilities without
any spec change when a new capability is added.

---

## op path inventory (95 capabilities)

All capabilities are addressable via `/op/{segment}`. Segment names are
camelCase and match the capability segment in the `/api/` paths exactly.

| Segment | Canonical capability |
|---------|----------------------|
| liabilityDiscover | Liability.Discover |
| enforcementAgencyGet | EnforcementAgency.Get |
| stakeholdersGet | Stakeholders.Get |
| complaintGenerate | Complaint.Generate |
| complaintSubmit | Complaint.Submit |
| complaintPublish | Complaint.Publish |
| stakeholderNotify | Stakeholder.Notify |
| complianceStandardGet | Compliance-Standard.Get |
| complianceValidate | Compliance.Validate |
| darkWebScan | DarkWeb.Scan |
| darkWebEvidenceCollect | DarkWeb.EvidenceCollect |
| dataOriginsTrace | DataOrigins.Trace |
| identifiabilityAssess | Identifiability.Assess |
| kAnonymityCompute | KAnonymity.Compute |
| deidentificationTechniquesApply | Deidentification.TechniquesApply |
| deidentificationStandardMap | Deidentification.StandardMap |
| dataForPurposeMinimize | DataForPurpose.Minimize |
| auxiliaryDataRiskEvaluate | AuxiliaryData.RiskEvaluate |
| reidentificationAttackSimulate | Reidentification.AttackSimulate |
| safeReleaseRecommend | SafeRelease.Recommend |
| deidentificationReportGenerate | Deidentification.ReportGenerate |
| deidentificationGuidancePublish | Deidentification.GuidancePublish |
| brokerInventoryScan | Broker.InventoryScan |
| brokerEvidenceCollect | Broker.EvidenceCollect |
| downstreamVendorsIdentify | DownstreamVendors.Identify |
| dataRequestGovern | DataRequest.Govern |
| emailRead | Email.Read |
| emailSend | Email.Send |
| phoneCall | Phone.Call |
| phoneAnswer | Phone.Answer |
| decisionDiaryManage | Decision-Diary.Manage |
| decisionEventsIdentify | Decision-Events.Identify |
| decisionOutcomeIdentify | Decision-Outcome.Identify |
| decisionOutcomeAnalyze | Decision-Outcome.Analyze |
| visitorIdentify | Visitor.Identify |
| subscriberRegister | Subscriber.Register |
| credentialsGenerate | Credentials.Generate |
| subscriberAuthenticate | Subscriber.Authenticate |
| agentRegister | Agent.Register |
| trustAssign | Trust.Assign |
| accessRightsManage | AccessRights.Manage |
| agentAuthenticate | Agent.Authenticate |
| handleException | Handle.Exception |
| ipAssetsDiscover | IP.AssetsDiscover |
| ipPortfolioCluster | IP.PortfolioCluster |
| ipProvenanceTrace | IP.ProvenanceTrace |
| ipRiskEvaluate | IP.RiskEvaluate |
| ipToProductsMap | IP.ToProductsMap |
| relatedIPDiscover | RelatedIP.Discover |
| useCasesInfer | UseCases.Infer |
| implementationInstancesSearch | Implementation.InstancesSearch |
| ipReportGenerate | IP.ReportGenerate |
| orgProfileBuild | OrgProfile.Build |
| budgetCheck | Budget.Check |
| budgetAfterPurchaseUpdate | Budget.AfterPurchaseUpdate |
| purchaseOptionsRecommend | Purchase.OptionsRecommend |
| purchaseEligibilityValidate | Purchase.EligibilityValidate |
| purchaseRiskEvaluate | Purchase.RiskEvaluate |
| purchaseInitiate | Purchase.Initiate |
| purchaseReceiptGenerate | Purchase.ReceiptGenerate |
| purchaseHistoryGenerate | Purchase.HistoryGenerate |
| orderStatusTrack | Order.StatusTrack |
| paymentCancel | Payment.Cancel |
| returnOrRefundInitiate | ReturnOrRefund.Initiate |
| purchaseIssuesResolve | Purchase.IssuesResolve |
| transactionCompleteVerify | Transaction.CompleteVerify |
| mandateManage | Mandate.Manage |
| rewardsDiscover | Rewards.Discover |
| rewardsProfileRequest | Rewards.ProfileRequest |
| promoEligibilityVerify | Promo.EligibilityVerify |
| redemptionPlanGenerate | Redemption.PlanGenerate |
| rewardRedeem | Reward.Redeem |
| risksAssess | Risks.Assess |
| evidenceCollect | Evidence.Collect |
| misappropriationDetect | Misappropriation.Detect |
| promotionalEngagementVerify | Promotional.EngagementVerify |
| justAsk | Just-Ask |
| eventLog | Event.Log |
| talentProfileRequest | Talent.ProfileRequest |
| jobPostingsScan | JobPostings.Scan |
| consultingServicesPitch | ConsultingServices.Pitch |
| applicationSubmit | Application.Submit |
| assetPortfolioCluster | Asset.PortfolioCluster |
| assetIntegrationsMap | Asset.IntegrationsMap |
| implementationDetailsAnalyze | Implementation.DetailsAnalyze |
| integrationProvenanceTrace | Integration.ProvenanceTrace |
| integrationRiskEvaluate | Integration.RiskEvaluate |
| thirdPartyAssetsDiscover | ThirdParty.AssetsDiscover |
| relatedAssetsDetect | RelatedAssets.Detect |
| usageInstancesSearch | Usage.InstancesSearch |
| technicalImpactInfer | Technical.ImpactInfer |
| techReportGenerate | Tech.ReportGenerate |
| platformMonitor | Platform.Monitor |
| orgProfileManage | Org-Profile.Manage |
| workflowBuild | Workflow.Build |

---

## capability_map.yaml — required shape

`api_handler` and `op_handler` share the same map and the same lookup key.
One `path_map` entry covers both modes — add a capability once, it works
everywhere.

```yaml
capabilities:
  Trust.Assign:
    agent:        door-keeper
    handler:      door-keeper-handler
    handlerType:  internal
    inputSchema:  trust.assign.input.schema.json
    outputSchema: trust.assign.output.schema.json
    dryRun:       false
    trace:        false

routes:
  doorKeeper:
    - path: /agents/doorKeeper/api/trustAssign
      capability: Trust.Assign

path_map:
  trustAssign: Trust.Assign
```

Run `capability_map_builder.py` to generate this file from extended agent
cards. The `path_map` section is the flat segment lookup both handlers use.

---

## Migration from current openapi.yaml

The current spec has 96 flat per-capability paths. The target has 65 resources.

| Step | Action |
|------|--------|
| 1 | Rename `/agents/{agent}/{capability}` to `/agents/{agent}/api/{capability}` |
| 2 | Add `/agents/{agent}/a2a` for each agent |
| 3 | Add `/agents/{agent}/app` for each agent |
| 4 | Add `/op/{capability}` resource (single parameterized resource) |
| 5 | Update each integration block Lambda ARN to the correct function |

Steps 2–4 are additive. Existing flat paths can remain during migration
and be deprecated once callers have updated.
