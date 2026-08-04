"""
Synthetic issue generator for the Engineering Intelligence Platform.

Appends realistic engineering issues to the 13_Issues sheet of the
design workbook so the demo database represents a real organization
(~300 issues across all projects, twelve months of history).

The generated data intentionally contains analytical signal for the
demo narrative:

  - Enterprise Identity Integration carries long cycle times and
    aging open issues (a delivery bottleneck).
  - Cloud infrastructure work spikes in the last 90 days with
    Terraform / ArgoCD / Crossplane issues (emerging skills).
  - Acme Financial accumulates recent high-priority open issues
    (an at-risk strategic customer).
  - Customer Administration Portal closes issues quickly (a healthy
    project for contrast).

Deterministic: run with the same seed and you get the same workbook.

Usage:
    python tools/generate_issues.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import openpyxl

WORKBOOK = Path(__file__).resolve().parent.parent / "design" / "HD_Systems_Design_Workbook.xlsx"

SHEET = "13_Issues"

TODAY = date(2026, 8, 1)

SEED = 42


# ------------------------------------------------------------------
# Project Profiles
#
# Each project gets a topic pool whose titles/descriptions/labels
# deliberately contain keywords from the 11_Skills and 12_Themes
# dictionaries so keyword enrichment finds real matches.
#
# Profile knobs:
#   count        - issues to generate
#   recent_bias  - share of issues created in the last 90 days
#   cycle_days   - (median, spread) lognormal-ish cycle time
#   done_rate    - share of issues that get closed
#   aging_open   - number of old issues deliberately left open
#   high_rate    - share of High/Critical priority
# ------------------------------------------------------------------

PROJECTS = {
    "Executive Engineering Dashboard": {
        "prefix": "HDI",
        "count": 38,
        "recent_bias": 0.55,
        "cycle_days": (9, 6),
        "done_rate": 0.55,
        "aging_open": 2,
        "high_rate": 0.45,
        "assignees": ["EMP004", "EMP005", "EMP006", "EMP007", "EMP003"],
        "topics": "analytics",
    },
    "Enterprise Identity Integration": {
        "prefix": "EII",
        "count": 44,
        "recent_bias": 0.35,
        "cycle_days": (28, 14),
        "done_rate": 0.42,
        "aging_open": 8,
        "high_rate": 0.55,
        "assignees": ["EMP003", "EMP005", "EMP008", "EMP009"],
        "topics": "identity",
    },
    "Cloud Infrastructure Modernization": {
        "prefix": "CIM",
        "count": 40,
        "recent_bias": 0.60,
        "cycle_days": (12, 8),
        "done_rate": 0.50,
        "aging_open": 2,
        "high_rate": 0.40,
        "assignees": ["EMP004", "EMP009", "EMP010", "EMP006"],
        "topics": "cloud",
    },
    "Secure Application Compliance": {
        "prefix": "SAC",
        "count": 34,
        "recent_bias": 0.40,
        "cycle_days": (14, 9),
        "done_rate": 0.52,
        "aging_open": 3,
        "high_rate": 0.50,
        "assignees": ["EMP005", "EMP010", "EMP009"],
        "topics": "security",
    },
    "Executive Portfolio Analytics": {
        "prefix": "EPA",
        "count": 30,
        "recent_bias": 0.55,
        "cycle_days": (10, 6),
        "done_rate": 0.55,
        "aging_open": 1,
        "high_rate": 0.35,
        "assignees": ["EMP004", "EMP005", "EMP006", "EMP007"],
        "topics": "analytics",
    },
    "Customer Administration Portal": {
        "prefix": "CAP",
        "count": 26,
        "recent_bias": 0.45,
        "cycle_days": (5, 3),
        "done_rate": 0.75,
        "aging_open": 0,
        "high_rate": 0.20,
        "assignees": ["EMP003", "EMP006", "EMP010"],
        "topics": "portal",
    },
    "Cloud Cost Optimization": {
        "prefix": "CCO",
        "count": 30,
        "recent_bias": 0.75,
        "cycle_days": (8, 5),
        "done_rate": 0.45,
        "aging_open": 1,
        "high_rate": 0.35,
        "assignees": ["EMP004", "EMP009", "EMP005"],
        "topics": "cost",
    },
    "Cross-Platform Data Integration": {
        "prefix": "CPDI",
        "count": 36,
        "recent_bias": 0.50,
        "cycle_days": (13, 8),
        "done_rate": 0.50,
        "aging_open": 2,
        "high_rate": 0.40,
        "assignees": ["EMP005", "EMP007", "EMP008"],
        "topics": "integration",
    },
}


# ------------------------------------------------------------------
# Topic Pools
#
# (title, description, labels, issue_type)
# ------------------------------------------------------------------

TOPICS = {

    "analytics": [
        ("Add drill-down to {noun} dashboard",
         "Executives want to click from the {noun} dashboard into the underlying issue detail. "
         "Add Grafana data links and a detail table panel backed by a PostgreSQL view.",
         "grafana,dashboard,postgres,drill-down", "Feature"),
        ("Optimize slow PostgreSQL query behind {noun} panel",
         "The {noun} panel takes over 8 seconds to render. Query plan shows a sequential scan; "
         "add indexes and rewrite the aggregation to improve response time and reduce latency.",
         "postgres,performance,query,index", "Performance"),
        ("Dashboard variables reset after time range change",
         "Selecting a new time range clears the customer and project filter variables. "
         "Users lose their filter state and must reselect. Investigate Grafana variable persistence.",
         "grafana,bug,filters,dashboard", "Bug"),
        ("Add Prometheus metrics for ETL pipeline",
         "Instrument the workbook import and GitHub sync with Prometheus metrics so we can "
         "monitor load duration, record counts, and failures in Grafana with alerting.",
         "prometheus,metrics,monitoring,etl", "Feature"),
        ("Scheduled PDF export of executive dashboard",
         "Leadership wants a weekly PDF export of the executive dashboard emailed automatically. "
         "Evaluate Grafana reporting options and schedule generation via cron automation.",
         "grafana,pdf,report,automation", "Feature"),
        ("Cache expensive aggregation queries with Redis",
         "Repeated dashboard loads re-run heavy aggregations. Introduce a Redis cache for "
         "pre-computed rollups to improve dashboard response time.",
         "redis,cache,performance,postgres", "Performance"),
        ("Row-level security for customer-scoped dashboards",
         "Customer success engineers should only see dashboards for their assigned customers. "
         "Implement role-based access with RBAC policies and PostgreSQL row filters.",
         "rbac,security,postgres,grafana", "Feature"),
        ("Refactor legacy KPI SQL views",
         "The original KPI views contain duplicated logic and outdated column names. Refactor "
         "into layered views with consistent naming to reduce technical debt.",
         "postgres,refactor,technical-debt,views", "Technical Debt"),
        ("Sprint velocity trend widget",
         "Add a panel showing weekly completed weight per team so managers can track velocity "
         "trends and spot delivery slowdowns early.",
         "grafana,velocity,metrics,dashboard", "Feature"),
        ("Fix timezone drift in created_date reporting",
         "Issues created late in the evening appear under the wrong day in dashboards. Normalize "
         "timestamps to UTC in the ETL and cast to date at query time.",
         "bug,timezone,etl,postgres", "Bug"),
        ("AI executive summary panel formatting",
         "The AI-generated executive summary renders raw markdown in the panel. Improve the "
         "rendering, and add loading and error states for the AI analytics endpoint.",
         "ai,llm,dashboard,markdown", "Bug"),
        ("Alerting on stale data imports",
         "If the nightly import fails silently the dashboards show stale data. Add freshness "
         "metrics and Grafana alerting when the last successful load is older than 24 hours.",
         "alerting,monitoring,etl,grafana", "Feature"),
    ],

    "identity": [
        ("Keycloak realm export breaks after upgrade",
         "After upgrading Keycloak the automated realm export fails with a schema mismatch. "
         "Users report intermittent login failed errors during the export window.",
         "keycloak,bug,upgrade,sso", "Bug"),
        ("SAML assertion clock skew failures for {customer}",
         "{customer} users see intermittent authentication errors caused by SAML assertion "
         "timestamp validation. Add clock skew tolerance and better error logging.",
         "saml,sso,authentication,bug", "Bug"),
        ("Implement OIDC id token claims mapping",
         "Map group membership claims from the OpenID Connect id token into application roles "
         "so downstream services can enforce authorization consistently.",
         "oidc,openid connect,claims,rbac", "Feature"),
        ("Rotate expiring PKI certificates",
         "Several service certificates expire next quarter. Rotate certs issued by the internal "
         "certificate authority and automate renewal to avoid TLS outages.",
         "pki,certificate,tls,automation", "Task"),
        ("OAuth refresh token rotation policy",
         "Implement refresh token rotation with revocation on reuse to harden OAuth flows "
         "against token theft. Update client libraries accordingly.",
         "oauth,token,security,hardening", "Feature"),
        ("Okta to Keycloak migration runbook",
         "Document the migration path from Okta to Keycloak for workforce identity, including "
         "MFA enrollment, user federation, and rollback procedures in a runbook.",
         "okta,keycloak,migration,runbook", "Documentation"),
        ("MFA enrollment for privileged accounts",
         "Require multi-factor authentication for all admin and maintainer roles. Roll out "
         "in stages with communication and support documentation.",
         "mfa,security,access,policy", "Feature"),
        ("RBAC policy audit for production namespaces",
         "Audit role bindings across production namespaces and remove excessive privileges. "
         "Several service accounts have cluster-admin that should be scoped down.",
         "rbac,security,kubernetes,audit", "Task"),
        ("SSO login loop after session timeout",
         "Users bounce between the identity provider and the application after session timeout. "
         "Reproduce the redirect loop and fix the session cookie configuration.",
         "sso,bug,session,authentication", "Bug"),
        ("Automate service account credential rotation",
         "Service account credentials are rotated manually today. Automate rotation with the "
         "External Secrets Operator and Vault integration to remove the manual process.",
         "eso,vault,secrets,automation", "Technical Debt"),
        ("LDAP user federation sync performance",
         "Nightly user federation sync takes four hours. Profile the sync, batch the queries, "
         "and cut sync time so access changes propagate faster.",
         "keycloak,performance,ldap,sync", "Performance"),
        ("Standardize authorization error responses",
         "APIs return inconsistent 401 and 403 responses which complicates client handling. "
         "Standardize unauthorized and forbidden semantics across services.",
         "api,authorization,standards,refactor", "Technical Debt"),
    ],

    "cloud": [
        ("Terraform module refactor for VPC baseline",
         "Split the monolithic Terraform configuration into reusable modules for VPC, subnets, "
         "and security groups. Adopt terraform plan checks in the pipeline.",
         "terraform,iac,vpc,refactor", "Technical Debt"),
        ("Upgrade EKS cluster to next Kubernetes version",
         "Plan and execute the managed cluster upgrade including node group rotation, addon "
         "compatibility checks, and workload validation in staging before production.",
         "kubernetes,eks,upgrade,cluster", "Task"),
        ("ArgoCD application sync stuck in progressing",
         "Several ArgoCD applications hang in progressing state after a Helm chart update. "
         "Investigate the reconciliation loop and fix the health checks.",
         "argocd,gitops,helm,bug", "Bug"),
        ("Autoscaling policy for burst workloads",
         "Configure horizontal pod autoscaling and cluster autoscaler policies for burst "
         "traffic so throughput scales without manual intervention.",
         "kubernetes,autoscaling,performance,capacity", "Feature"),
        ("Migrate ingress to AWS ALB controller",
         "Replace the legacy ingress with the AWS application load balancer controller for "
         "better TLS handling and target group management.",
         "alb,ingress,kubernetes,migration", "Task"),
        ("Loki log retention and index optimization",
         "Log aggregation storage is growing fast. Tune Loki retention, compaction, and "
         "index settings to control cost while keeping troubleshooting logs available.",
         "loki,logging,retention,optimization", "Performance"),
        ("Crossplane composition for RDS provisioning",
         "Create a Crossplane composition so teams can provision PostgreSQL RDS instances "
         "through Kubernetes CRDs with guardrails instead of manual console work.",
         "crossplane,rds,iac,automation", "Feature"),
        ("Prometheus alert fatigue reduction",
         "On-call receives too many noisy alerts. Review alertmanager routing and thresholds, "
         "delete stale rules, and add runbook links to actionable alerts.",
         "prometheus,alerting,monitoring,oncall", "Task"),
        ("Terragrunt remote state locking issue",
         "Concurrent applies hit remote state lock contention. Restructure Terragrunt "
         "dependencies to reduce blast radius and speed up plans.",
         "terragrunt,terraform,state,bug", "Bug"),
        ("Zarf package for air gap deployment",
         "Build a Zarf package so the platform can deploy into a disconnected environment "
         "for the federal proof of concept.",
         "zarf,airgap,deployment,packaging", "Feature"),
        ("Helm values standardization across environments",
         "Environment values files have drifted. Standardize values.yaml structure across "
         "staging and production and document overrides.",
         "helm,configuration,standards,refactor", "Technical Debt"),
        ("Node disk pressure evictions in production",
         "Pods are evicted under disk pressure on two production nodes. Investigate image "
         "garbage collection and ephemeral storage limits for reliability.",
         "kubernetes,reliability,incident,storage", "Bug"),
    ],

    "security": [
        ("Triage critical CVEs from NeuVector scan",
         "The latest container security scan flagged critical vulnerabilities in three base "
         "images. Patch, rebuild, and redeploy affected services.",
         "neuvector,cve,vulnerability,containers", "Bug"),
        ("SonarQube quality gate for merge requests",
         "Enforce static code analysis quality gates on every merge request so new code "
         "cannot introduce critical code smells or security hotspots.",
         "sonarqube,quality,ci,security", "Feature"),
        ("Kyverno policy to block privileged pods",
         "Add an admission control policy that blocks privileged containers and enforces "
         "read-only root filesystems in production namespaces.",
         "kyverno,policy,kubernetes,hardening", "Feature"),
        ("Secrets sprawl cleanup with External Secrets Operator",
         "Secrets are duplicated across namespaces and CI variables. Consolidate into Vault "
         "with the External Secrets Operator and rotate exposed credentials.",
         "eso,vault,secrets,cleanup", "Technical Debt"),
        ("Quarterly compliance evidence automation",
         "Collecting audit evidence is a manual process each quarter. Automate report "
         "generation for access reviews and scan results.",
         "compliance,automation,audit,reporting", "Feature"),
        ("Penetration test finding: verbose error pages",
         "The pen test found stack traces leaking in error responses. Sanitize error handling "
         "and add security headers across public endpoints.",
         "security,pentest,hardening,bug", "Bug"),
        ("Dependency scanning in GitLab pipeline",
         "Add dependency and license scanning stages to the GitLab CI/CD pipeline with "
         "severity thresholds that fail the build.",
         "gitlab,ci,scanning,dependencies", "Feature"),
        ("Image signing and verification rollout",
         "Sign build artifacts and verify signatures at admission so only trusted images "
         "run in the cluster.",
         "supply-chain,signing,kubernetes,policy", "Feature"),
        ("Vulnerability SLA dashboard",
         "Track remediation SLAs for open vulnerabilities by severity in a Grafana dashboard "
         "backed by scan exports.",
         "vulnerability,sla,dashboard,reporting", "Feature"),
        ("Harden PostgreSQL authentication configuration",
         "Move database access to IAM authentication where possible, enforce TLS, and "
         "remove shared credentials from application configs.",
         "postgres,iam,tls,hardening", "Task"),
    ],

    "portal": [
        ("Customer search returns stale results",
         "Newly onboarded customers do not appear in search until the next day. Fix the "
         "indexing job so search reflects changes within minutes.",
         "search,bug,indexing,portal", "Bug"),
        ("Self-service account provisioning workflow",
         "Allow customer admins to provision user accounts with approval workflow, removing "
         "the manual onboarding queue.",
         "provisioning,workflow,automation,portal", "Feature"),
        ("Audit trail export to CSV",
         "Compliance teams need to export the customer audit trail with filters applied. "
         "Add CSV export with background generation for large ranges.",
         "audit,export,csv,compliance", "Feature"),
        ("License usage meter accuracy",
         "Reported license usage differs from billing records. Reconcile the counting logic "
         "and add tests around edge cases.",
         "licensing,bug,billing,accuracy", "Bug"),
        ("Bulk user import validation",
         "Bulk CSV imports fail silently on malformed rows. Validate input, report row-level "
         "errors, and support partial retries.",
         "import,validation,csv,portal", "Bug"),
        ("Portal session handling behind load balancer",
         "Sessions drop when traffic shifts between instances. Fix sticky session and cookie "
         "configuration behind the load balancer.",
         "session,alb,bug,reliability", "Bug"),
        ("Accessibility pass for admin screens",
         "Bring the admin screens to WCAG AA: keyboard navigation, contrast, and screen "
         "reader labels for form controls.",
         "accessibility,ui,frontend,quality", "Task"),
        ("Notification preferences per customer",
         "Customers want control over which lifecycle emails they receive. Add notification "
         "preference management with sensible defaults.",
         "notifications,feature,portal,email", "Feature"),
        ("Migrate portal database to managed RDS",
         "Move the self-hosted PostgreSQL database to Amazon RDS with minimal downtime, "
         "including replication cutover and backup validation.",
         "rds,postgres,migration,database", "Task"),
    ],

    "cost": [
        ("Rightsize overprovisioned EC2 instances",
         "Utilization data shows several instances under 15 percent CPU. Rightsize instance "
         "types and document the review cadence.",
         "ec2,cost,rightsizing,aws", "Task"),
        ("Idle resource detection automation",
         "Detect unattached volumes, idle load balancers, and stopped instances with a "
         "scheduled job and report candidates for cleanup.",
         "automation,cost,cleanup,aws", "Feature"),
        ("S3 lifecycle policies for log archives",
         "Move aging log archives to infrequent access and glacier tiers with lifecycle "
         "policies to cut object storage spend.",
         "s3,lifecycle,storage,cost", "Task"),
        ("Reserved instance and savings plan analysis",
         "Analyze steady-state compute usage and recommend reserved instance or savings "
         "plan purchases with projected savings.",
         "cost,analysis,aws,finance", "Task"),
        ("Cost allocation tagging enforcement",
         "Enforce required cost allocation tags via policy so spend can be attributed to "
         "teams and customers accurately.",
         "tagging,policy,cost,governance", "Feature"),
        ("Grafana cost dashboard per team",
         "Build a dashboard showing spend by team, service, and environment with month over "
         "month trend and budget thresholds.",
         "grafana,dashboard,cost,reporting", "Feature"),
        ("ElastiCache cluster consolidation",
         "Multiple underutilized Redis clusters can be consolidated. Plan migration with "
         "cache key namespace isolation.",
         "elasticache,redis,consolidation,cost", "Task"),
        ("Kubernetes requests and limits tuning",
         "Overstated resource requests cause poor bin packing and wasted nodes. Tune requests "
         "from usage data to reduce cluster cost.",
         "kubernetes,capacity,cost,tuning", "Performance"),
        ("Anomaly alerts on daily spend",
         "Alert when daily spend deviates from forecast so surprises are caught within a day "
         "instead of at invoice time.",
         "alerting,cost,anomaly,monitoring", "Feature"),
    ],

    "integration": [
        ("GitHub connector rate limit backoff",
         "Large syncs hit the GitHub REST API rate limit and fail mid-run. Implement "
         "exponential backoff and conditional requests with etags.",
         "github,api,rate-limit,bug", "Bug"),
        ("Jira issue import prototype",
         "Prototype a Jira connector that maps Jira fields into the normalized issue schema, "
         "proving the tracker-agnostic model with a second source.",
         "jira,connector,integration,prototype", "Feature"),
        ("Webhook-based incremental sync",
         "Replace polling with webhook-driven sync so issue changes appear in the platform "
         "within seconds and API usage drops.",
         "webhook,sync,integration,api", "Feature"),
        ("Normalize status vocabulary across trackers",
         "GitHub, GitLab, and Jira use different status models. Define the canonical status "
         "mapping and make it configurable per source.",
         "normalization,schema,integration,design", "Task"),
        ("GitLab issue import pagination bug",
         "The GitLab importer drops records past page ten because of a pagination cursor bug. "
         "Fix and add tests with mocked paged responses.",
         "gitlab,bug,pagination,import", "Bug"),
        ("RabbitMQ queue for sync jobs",
         "Move sync execution onto a message queue with retries and dead letter handling so "
         "long imports do not block the API.",
         "rabbitmq,queue,architecture,reliability", "Feature"),
        ("Field mapping configuration UI",
         "Administrators need to adjust source field mappings without code changes. Build a "
         "configuration screen with validation and preview.",
         "configuration,ui,mapping,integration", "Feature"),
        ("Azure DevOps work item connector",
         "Extend the connector framework to Azure DevOps work items including area path to "
         "project mapping.",
         "azure-devops,connector,integration,feature", "Feature"),
        ("Deduplicate issues synced from multiple sources",
         "Issues mirrored across trackers create duplicates. Add cross-source identity "
         "resolution using external references.",
         "deduplication,sync,data-quality,design", "Task"),
        ("Sync observability: per-run metrics and logs",
         "Emit per-run metrics (records, duration, failures) and structured logs so sync "
         "health is visible in Grafana with alerting on failures.",
         "monitoring,metrics,sync,observability", "Feature"),
    ],
}


CUSTOMER_BY_PROJECT = {
    "Executive Engineering Dashboard": "Acme Financial",
    "Enterprise Identity Integration": "BlueSky Health",
    "Cloud Infrastructure Modernization": "Nova Manufacturing",
    "Secure Application Compliance": "Pinnacle Energy",
    "Executive Portfolio Analytics": "Horizon Retail Group",
    "Customer Administration Portal": "City of Charlottesville",
    "Cloud Cost Optimization": "Summit Telecom",
    "Cross-Platform Data Integration": "BrightPath Logistics",
}

NOUNS = ["portfolio health", "team velocity", "customer tier", "issue aging", "risk overview", "skills coverage"]

VARIANTS = ["", "", "", " (staging)", " (production)", " - phase 2", " for EU region", " follow-up"]

WEIGHTS_BY_TYPE = {
    "Feature": [3, 5, 5, 8, 8, 13],
    "Bug": [1, 2, 3, 3, 5, 8],
    "Task": [2, 3, 3, 5, 5, 8],
    "Technical Debt": [3, 5, 8, 8, 13],
    "Performance": [3, 5, 5, 8],
    "Documentation": [1, 2, 3, 3],
}

SEVERITY_BY_PRIORITY = {
    "Critical": ["Critical", "Critical", "High"],
    "High": ["High", "High", "Medium", "Critical"],
    "Medium": ["Medium", "Medium", "Low", "High"],
    "Low": ["Low", "Low", "Medium"],
}


def pick_created(rng, recent_bias):
    """
    Sample a created date: recent_bias of issues land in the last 90
    days, the rest spread over the prior nine months.
    """

    if rng.random() < recent_bias:
        return TODAY - timedelta(days=rng.randint(1, 90))

    return TODAY - timedelta(days=rng.randint(91, 365))


def pick_cycle_days(rng, median, spread):

    days = rng.lognormvariate(0, 0.6) * median + rng.uniform(-spread / 2, spread / 2)

    return max(1, round(days))


def generate_for_project(rng, project_name, profile, start_number):

    customer = CUSTOMER_BY_PROJECT[project_name]

    topics = TOPICS[profile["topics"]]

    rows = []

    number = start_number

    aging_remaining = profile["aging_open"]

    for i in range(profile["count"]):

        title_t, desc_t, labels, issue_type = topics[i % len(topics)]

        noun = rng.choice(NOUNS)

        title = title_t.format(noun=noun, customer=customer)

        description = desc_t.format(noun=noun, customer=customer)

        #
        # Repeated topics get a variant suffix so titles stay unique.
        #
        if i >= len(topics):
            title += rng.choice(VARIANTS[3:])

        if rng.random() < profile["high_rate"]:
            priority = rng.choice(["High", "High", "Critical"])
        else:
            priority = rng.choice(["Medium", "Medium", "Medium", "Low"])

        severity = rng.choice(SEVERITY_BY_PRIORITY[priority])

        weight = rng.choice(WEIGHTS_BY_TYPE.get(issue_type, [3, 5]))

        created = pick_created(rng, profile["recent_bias"])

        closed = None

        if aging_remaining > 0 and created < TODAY - timedelta(days=120):

            #
            # Deliberately aging open issue (bottleneck signal).
            #
            status = rng.choice(["Open", "Open", "In Progress"])

            aging_remaining -= 1

        elif rng.random() < profile["done_rate"]:

            median, spread = profile["cycle_days"]

            cycle = pick_cycle_days(rng, median, spread)

            candidate = created + timedelta(days=cycle)

            if candidate < TODAY:
                closed = candidate
                status = "Done"
            else:
                status = rng.choice(["In Progress", "Review", "Open"])

        else:

            status = rng.choice(["Open", "Open", "In Progress", "Review"])

        assignee = rng.choice(profile["assignees"])

        rows.append(
            (
                f"{profile['prefix']}-{number}",
                project_name,
                title,
                description,
                labels,
                issue_type,
                priority,
                severity,
                status,
                assignee,
                weight,
                created,
                closed,
            )
        )

        number += 1

    return rows


def main():

    rng = random.Random(SEED)

    wb = openpyxl.load_workbook(WORKBOOK)

    ws = wb[SHEET]

    #
    # Find existing keys and the next number per prefix.
    #
    existing = [row[0] for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]

    next_number = {}

    for key in existing:

        prefix, num = key.rsplit("-", 1)

        next_number[prefix] = max(next_number.get(prefix, 100), int(num)) + 1

    total = 0

    for project_name, profile in PROJECTS.items():

        start = next_number.get(profile["prefix"], 101)

        rows = generate_for_project(rng, project_name, profile, start)

        for row in rows:
            ws.append(row)

        total += len(rows)

        print(f"{project_name}: +{len(rows)} issues")

    wb.save(WORKBOOK)

    print()
    print(f"Appended {total} issues. Workbook now has {len(existing) + total} issues.")


if __name__ == "__main__":
    main()
