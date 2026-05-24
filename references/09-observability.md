# Observability & SRE Reference

## Table of Contents
1. [OpenTelemetry & Distributed Tracing](#opentelemetry)
2. [Prometheus Alerting Rules](#prometheus)
3. [Grafana Dashboard Standards](#grafana)
4. [SLOs, SLIs, & Incident Governance](#incident-governance)

---

## 1. OpenTelemetry & Distributed Tracing {#opentelemetry}

OMEGA TITAN structures distributed tracing using OpenTelemetry (OTel). This ensures direct visibility of microservice dependencies, databases, and third-party APIs.

### Next.js OpenTelemetry Configuration
```typescript
// instrumentation.ts
import { registerOTel } from '@vercel/otel';

export function register() {
  registerOTel({
    serviceName: 'titan-nextjs-web',
    instrumentationConfig: {
      fetch: {
        propagateContextUrls: ['https://api.omega-titan.com'],
      },
    },
  });
}
```

---

## 2. Prometheus Alerting Rules {#prometheus}

All production clusters scrape performance metrics via Prometheus and route alerts using Alertmanager to Slack and PagerDuty channels.

### Production Alert Rules Template (`prometheus.rules.yml`)
```yaml
groups:
- name: titan-service-alerts
  rules:
  # HTTP Error rate alert
  - alert: HighHttpErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100 > 2
    for: 2m
    labels:
      severity: critical
      tier: api
    annotations:
      summary: "High HTTP error rate detected on {{ $labels.instance }}"
      description: "HTTP 5xx error rate is {{ $value | printf \"%.2f\" }}% over the last 5 minutes."

  # Latency alert
  - alert: SlowApiLatency
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 1.2
    for: 5m
    labels:
      severity: warning
      tier: api
    annotations:
      summary: "95th percentile latency is elevated"
      description: "95th percentile latency is {{ $value }}s over the last 5 minutes."
```

---

## 3. Grafana Dashboard Standards {#grafana}

Production dashboards are categorized by perspective and optimized for cognitive simplicity:

*   **Executive Dashboard**: High-level system health, user interactions, total cost, and token expenditures.
*   **Engineering RED Dashboard**: Metrics reflecting **R**ate (requests per second), **E**rrors (failures count), and **D**uration (latency distribution).
*   **Infrastructure USE Dashboard**: Metrics reflecting cluster **U**tilization, **S**aturation, and **E**rrors across node instances.

---

## 4. SLO, SLI, & Incident Governance {#incident-governance}

We define strict reliability boundaries for core customer actions:

### Service Level Indicators (SLIs)
*   **Availability SLI**: The percentage of successful API calls returning non-5xx status. (Target SLO: **99.9%**).
*   **Latency SLI**: The percentage of API calls returning within **250ms**. (Target SLO: **95%**).

### Incident Recovery Targets
*   **Sev 1 (Critical Outage)**: Maximum **5 minutes** to acknowledge (PagerDuty), maximum **30 minutes** to mitigate (e.g. DNS fallback, service rollback).
*   **Sev 2 (Minor Outage)**: Maximum **15 minutes** to acknowledge, maximum **4 hours** to mitigate.
*   **Post-Mortem Policy**: Every Sev 1 incident requires a comprehensive, non-blaming post-mortem document inside `obsidian-vault/16-Incidents/` within 48 hours of recovery.
