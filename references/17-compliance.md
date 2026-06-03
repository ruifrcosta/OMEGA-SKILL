# Compliance & Governance Reference

## Table of Contents
1. [ISO 27001 ISMS Implementation Roadmap](#iso-27001)
2. [ISO 9001 Quality Management Standards](#iso-9001)
3. [SOC 2 Type II Control Mapping](#soc2)
4. [GDPR & HIPAA Data Privacy Governance](#privacy-governance)

---

## 1. ISO 27001 ISMS Implementation Roadmap {#iso-27001}

OMEGA TITAN structures its cybersecurity controls under the **ISO/IEC 27001:2022** standard for Information Security Management Systems (ISMS).

### Core ISO 27001 Control Domains
*   **Annex A.5 (Organizational Controls)**: Explicit policies governing access privileges, asset classifications, and continuous risk assessments.
*   **Annex A.8 (Technological Controls)**: Enforce hardware security, automated system backups, secure configuration baselines, and end-to-end traffic encryption (mTLS).
*   **Incident Logging**: All security-related alerts must map to the `{vault}/16-Incidents/` repository for forensic tracing.

---

## 2. ISO 9001 Quality Management Standards {#iso-9001}

To satisfy **ISO 9001:2015** quality guidelines, the development factory enforces systematic delivery pipelines:

```
User Story / Spec
   └── 1. Peer Architecture Review (ADR approved)
   └── 2. Implementation & Strict Unit Tests (Target: 85% coverage)
   └── 3. Automated E2E & Accessibility Scans (Playwright/Axe-core)
   └── 4. Quality Audit Verification Gate (Pull Request merged)
   └── 5. Continuous Observability & health checks (SLO monitoring)
```

---

## 3. SOC 2 Type II Control Mapping {#soc2}

Our infrastructure validates the 5 Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, and Privacy):

### SOC 2 Control Reference Matrix

| Trust Criterion | Control Implementation | Automated Verification Pipeline |
|-----------------|------------------------|---------------------------------|
| **Security** | RBAC validation + Auth Guards | unit tests in `07-security.md` |
| **Availability** | Multi-AZ replica distributions | pod zonal checks in `03-infrastructure.md` |
| **Confidentiality** | Secrets locked in KMS vaults | lint checks preventing plain text secrets |
| **Privacy** | Strict data encryption at rest | Database configuration flags |

---

## 4. GDPR & HIPAA Data Privacy Governance {#privacy-governance}

To operate inside European (GDPR) and medical (HIPAA) compliance spaces, applications must isolate Personal Data (PII / PHI):

*   **Right to Be Forgotten (GDPR Article 17)**: The database schema must support cascading deletions of user profile records.
*   **Encryption of PHI (HIPAA)**: All medical records or personal identifiers must reside inside encrypted database fields using column-level AES-GCM encryption.

### GDPR Article 17 Purge Transaction Script
```sql
CREATE OR REPLACE FUNCTION public.purge_user_data(target_user_id uuid)
RETURNS void AS $$
BEGIN
  -- 1. Eliminate personal profile data
  DELETE FROM public.profiles WHERE id = target_user_id;
  
  -- 2. Eliminate session identifiers
  DELETE FROM auth.users WHERE id = target_user_id;
  
  -- 3. Log anonymized audit event
  INSERT INTO public.compliance_logs (event_type, description)
  VALUES ('DATA_PURGE', 'User records completely deleted under Article 17 request.');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 5. ISO 27001 Audit Preparation & Certification Roadmap {#iso-audit}

### Phase 1 — Gap Assessment (Weeks 1-4)

```
ISMS Scope Definition:
□ Define organizational boundary (which systems, data, people)
□ Identify information assets: list ALL systems, databases, APIs, repos, laptops
□ Classify data: Public / Internal / Confidential / Restricted
□ Map data flows: where data enters, lives, exits, and is deleted

Gap Analysis Against Annex A Controls:
□ A.5  Organizational controls (policies, roles)
□ A.6  People controls (HR, training, clearances)
□ A.7  Physical controls (office, server room, clean desk)
□ A.8  Technological controls (see control checklist below)

Output: Gap Register → {vault}/21-Compliance/iso-27001-gap-register.md
```

### Phase 2 — Risk Assessment (Weeks 4-8)

```markdown
## Risk Register Format (ISO 27001 Annex A compliant)
# {vault}/21-Compliance/risk-register.md

| ID | Asset | Threat | Vulnerability | Likelihood | Impact | Risk Score | Control | Residual Risk | Owner |
|----|-------|--------|--------------|-----------|--------|------------|---------|---------------|-------|
| R001 | Customer PII in Postgres | Unauthorized access | No RLS on tables | High | Critical | 16 | RLS + RBAC + encryption | Low | CTO |
| R002 | JWT signing key | Key exposure | Key in .env committed | Medium | Critical | 12 | Vault + rotation | Low | CTO |
| R003 | S3 bucket | Data exfiltration | Public bucket | Low | High | 8 | Block public access | Low | DevOps |

Risk Score = Likelihood × Impact (1-4 scale each, max 16)
Acceptance threshold: ≤4 = Accept, 5-8 = Monitor, 9-12 = Treat, 13-16 = Avoid/Transfer
```

### Phase 3 — Control Implementation (Weeks 8-16)

```
Technical Controls (A.8) — Implementation Status:

A.8.1  User endpoint devices
  □ MDM enrollment for all laptops (Jamf / Intune)
  □ Full disk encryption enforced (FileVault / BitLocker)
  □ Automatic screen lock after 5 minutes

A.8.2  Privileged access rights
  □ Break-glass accounts documented and audited quarterly
  □ No shared admin credentials
  □ MFA on all privileged accounts (TOTP or hardware key)
  □ Just-in-time access via Vault (not permanent IAM roles)

A.8.3  Information access restriction
  □ RBAC implemented in application layer (07-security.md)
  □ Database RLS on all tables containing personal data
  □ Network segmentation (production namespace isolated)
  □ API keys scoped to minimum required permissions

A.8.7  Protection against malware
  □ SCA (Software Composition Analysis) in CI — SAST + Trivy
  □ Container images scanned on push (ECR scan-on-push)
  □ Dependency audit in pipeline (pnpm audit --audit-level=high)

A.8.9  Configuration management
  □ All infra declared as code (Terraform) — no manual changes
  □ Drift detection: Terraform plan in CI on schedule
  □ Immutable infrastructure: no SSH to production servers

A.8.10 Information deletion
  □ GDPR Article 17 purge transaction implemented
  □ Data retention policy documented and automated
  □ Backup deletion on schedule (S3 lifecycle rules)

A.8.12 Data leakage prevention
  □ TruffleHog in pre-commit + CI pipeline
  □ No PII in logs (structured logging with redact middleware)
  □ No PII in error messages returned to clients

A.8.15 Logging
  □ Audit log for all admin actions (who, what, when)
  □ Log integrity: logs written to append-only store
  □ Log retention: minimum 12 months
  □ Log alerting: auth failures, privilege escalation

A.8.24 Use of cryptography
  □ AES-256 at rest, TLS 1.2+ in transit
  □ No MD5/SHA-1 for security-sensitive operations
  □ Key management policy documented
```

### Phase 4 — Documentation Package (Weeks 12-16)

```
Mandatory ISMS documents for certification:
□ Information Security Policy (signed by leadership)
□ Scope document (what's in, what's out)
□ Risk assessment methodology
□ Risk treatment plan
□ Statement of Applicability (SoA) — every Annex A control: applicable/not, implemented/not
□ Asset inventory (last updated < 3 months)
□ Supplier security policy
□ Incident response plan
□ Business continuity plan
□ Internal audit report (must have at least one completed cycle)
□ Management review minutes
□ Competence records (training certificates, awareness training logs)
```

```markdown
# Statement of Applicability (SoA) Template
# {vault}/21-Compliance/statement-of-applicability.md

| Control | Title | Applicable | Reason if N/A | Implemented | Evidence Location |
|---------|-------|-----------|--------------|-------------|------------------|
| A.5.1 | Information security policies | Yes | - | Yes | /policies/security-policy.md |
| A.5.2 | Information security roles and responsibilities | Yes | - | Yes | /policies/raci.md |
| A.6.1 | Screening | Yes | - | Partial | HR onboarding checklist |
| A.8.3 | Information access restriction | Yes | - | Yes | 07-security.md + RLS policies |
```

### Phase 5 — Internal Audit (Weeks 16-20)

```bash
# Internal audit checklist — run before external audit
# Auditor must be independent of the area being audited

AUDIT AREAS:
□ Access control audit: list all users with production access, verify least privilege
  Query: SELECT grantee, privilege_type, table_name FROM information_schema.role_table_grants WHERE grantee != 'postgres';

□ Password/key rotation audit: verify all secrets rotated per policy
  Check: AWS SSM parameter history, Vault audit log

□ Incident log review: all incidents from last 12 months
  Check: {vault}/16-Incidents/ — every incident has post-mortem, action items closed?

□ Change management audit: all infra changes via Terraform/Helm, no manual changes
  Check: git log on infra/ repo, Terraform Cloud run history

□ Backup audit: restore test performed within last 3 months?
  Check: {vault}/28-Disaster-Recovery/ — DR test report

□ Training audit: all staff completed security awareness training?
  Check: LMS completion records

OUTPUT: {vault}/21-Compliance/internal-audit-report-YYYY-MM.md
```

### Phase 6 — External Certification Audit (Weeks 20-24)

```
Stage 1 — Documentation Review (1-2 days, remote):
  Auditor reviews all ISMS documentation
  Common findings at Stage 1:
  - SoA not complete (every control must have documented justification)
  - Risk register not signed/dated by management
  - No evidence of management review meeting
  Action: close all Stage 1 findings before Stage 2

Stage 2 — Evidence Review (2-5 days, on-site or remote):
  Auditor reviews evidence of implementation:
  - Access control: demonstrate user provisioning/deprovisioning process
  - Monitoring: show Grafana dashboards, alert history
  - Incident management: walk through a real incident from last 12 months
  - Change management: show a recent change from ticket → PR → deploy
  - Training: show training completion records
  - Backup: demonstrate restore procedure

Common findings to pre-empt:
□ Logging: ensure all admin actions are logged with user ID and timestamp
□ Access review: document a quarterly access review was performed
□ Supplier list: every SaaS tool must be in the supplier register
□ Asset inventory: every laptop, server, and service must be listed
```

### Continuous Compliance Automation

```typescript
// Automated compliance checks — run daily in CI
async function runComplianceChecks(): Promise<ComplianceReport> {
  const checks = await Promise.allSettled([
    // Access control
    checkNoUsersWithProductionDirectDbAccess(),
    checkAllAdminsMFAEnabled(),
    checkServiceAccountsHaveMinimalPermissions(),

    // Data protection
    checkAllTablesHaveRLS(),
    checkNoSecretsInEnvVars(),
    checkNoPIIInLogs(),

    // Change management
    checkNoManualInfraChanges(),           // compare Terraform state vs actual
    checkAllChangesHaveApproval(),         // GitHub PR reviews

    // Incident response
    checkIncidentResponsePlanUpdated(),    // last updated < 6 months
    checkDRTestCompleted(),                // last completed < 3 months

    // Monitoring
    checkAlertingConfigured(),
    checkLogRetentionPolicy(),             // >= 12 months
  ]);

  const failures = checks.filter(c => c.status === 'rejected');
  if (failures.length > 0) {
    await notify('#compliance-alerts', formatFailures(failures));
  }

  // Write to vault
  await writeComplianceReport(checks);
  return buildReport(checks);
}
```

---

## 6. SOC 2 Continuous Evidence Collection {#soc2-evidence}

```
Evidence Collection Automation (run monthly):

Access Control (CC6):
□ Export user access list with roles and last login
□ Export MFA status for all accounts
□ Screenshot: production access requires VPN + MFA

Availability (A1):
□ Export uptime report from Grafana (last 30 days)
□ Export SLO compliance report
□ Export on-call incident log

Security (CC7):
□ Export vulnerability scan results (Trivy)
□ Export dependency audit results
□ Export penetration test results (annual)
□ Export security training completion records

Change Management (CC8):
□ Export all production deployments (Helm history)
□ Export all PR merge history with approvals
□ Export Terraform plan/apply history

Monitoring (CC7):
□ Export alert history (Grafana)
□ Export log retention configuration
□ Export incident history and resolution times
```

```bash
# Monthly evidence collection script
#!/bin/bash
MONTH=$(date +%Y-%m)
OUT="{vault}/21-Compliance/evidence/${MONTH}"
mkdir -p "$OUT"

# User access review
aws iam list-users --query 'Users[*].[UserName,CreateDate,PasswordLastUsed]' > "$OUT/iam-users.json"
aws iam list-roles --query 'Roles[*].[RoleName,Arn]' > "$OUT/iam-roles.json"

# CloudTrail — all API calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventSource,AttributeValue=iam.amazonaws.com \
  --start-time $(date -d '30 days ago' --iso-8601) > "$OUT/cloudtrail-iam.json"

# ECR vulnerability scans
aws ecr describe-image-scan-findings \
  --repository-name myproject/api \
  --image-id imageTag=latest > "$OUT/ecr-scan.json"

echo "Evidence collected at $OUT"
```
