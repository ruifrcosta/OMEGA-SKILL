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

---

## 5. Error Budget & SLO Burn Rate Alerts {#error-budget}

```yaml
# SLO burn rate alert — fires before SLO is fully exhausted
groups:
- name: slo-burn-rate
  rules:
  # Fast burn: consuming 5% of 30-day budget in 1 hour
  - alert: SLOFastBurn
    expr: |
      (
        sum(rate(http_requests_total{status=~"5.."}[1h])) /
        sum(rate(http_requests_total[1h]))
      ) > (5 * 0.001)
    for: 2m
    labels: { severity: critical, page: 'true' }
    annotations:
      summary: "SLO fast burn — 5% budget consumed in 1h"

  # Slow burn: on track to exhaust budget in 3 days
  - alert: SLOSlowBurn
    expr: |
      (
        sum(rate(http_requests_total{status=~"5.."}[6h])) /
        sum(rate(http_requests_total[6h]))
      ) > (2 * 0.001)
    for: 15m
    labels: { severity: warning }
```

## 6. Alert Routing & On-Call {#routing}

```yaml
# Alertmanager routing
route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-warning'

  routes:
  - match: { severity: critical }
    receiver: 'pagerduty-critical'
    repeat_interval: 30m

  - match: { severity: warning }
    receiver: 'slack-warning'

receivers:
- name: 'pagerduty-critical'
  pagerduty_configs:
  - routing_key: '${PAGERDUTY_KEY}'
    description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

- name: 'slack-warning'
  slack_configs:
  - api_url: '${SLACK_WEBHOOK}'
    channel: '#alerts-warning'
    text: '{{ .CommonAnnotations.summary }}'
```

## 7. Mandatory Instrumentation Template {#instrumentation}

```typescript
// Every service must emit these — zero exceptions
import { trace, metrics } from '@opentelemetry/api';

const tracer = trace.getTracer('service-name');
const meter = metrics.getMeter('service-name');

// Business metric counters (not just technical)
const ordersCreated = meter.createCounter('orders.created', {
  description: 'Number of orders created',
});
const checkoutDuration = meter.createHistogram('checkout.duration_ms', {
  description: 'Checkout flow duration in milliseconds',
});

// Structured logging format (every log line)
logger.info('Order created', {
  trace_id: span.spanContext().traceId,
  user_id: userId,
  tenant_id: tenantId,
  order_id: orderId,
  amount_cents: amount,
  // NEVER log: passwords, tokens, PII beyond user_id
});
```
