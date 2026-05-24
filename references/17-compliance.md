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
*   **Incident Logging**: All security-related alerts must map to the `obsidian-vault/16-Incidents/` repository for forensic tracing.

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
