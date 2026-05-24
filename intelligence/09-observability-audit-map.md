# OMEGA Observability Audit Map
## OpenTelemetry Tracing, Prometheus Alerting, & SLO Governance Standards

This document establishes the telemetry ingestion pipeline, Alerting Threshold configurations, and Service Level Objectives (SLOs) enforced within the OMEGA ecosystem.

---

## 1. Unified Telemetry Ingestion Pipeline

To provide complete system visibility, OMEGA requires all active services to stream metrics, logs, and traces through a unified **OpenTelemetry Collector** architecture.

```
 [Application Logs / Metrics / Traces] ──► [OpenTelemetry SDK Agent]
                                                    │
                                                    ▼
                                       [OpenTelemetry Collector]
                                                    │
                   ┌────────────────────────────────┼────────────────────────────────┐
                   ▼                                ▼                                ▼
         [Trace Store: Tempo]            [Metric Store: Prometheus]         [Log Store: Loki]
                   │                                │                                │
                   └────────────────────────────────┼────────────────────────────────┘
                                                    ▼
                                          [Grafana Dashboards]
```

- **Distributed Tracing**: All API gateway interactions inject a unique `X-Trace-Id` using W3C Trace Context propagation.
- **Log Aggregation**: System stdout is parsed into structured JSON and shipped directly to Grafana Loki.

---

## 2. Service Level Objectives (SLOs) & Alert Rules

We track system health against four Golden Signals (Latency, Traffic, Errors, Saturation).

| Target Service | SLO Metric | Target SLI | SLO Threshold | Critical Action / Alert |
| :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | Request Latency | p99 < 200ms | 99.5% | Page on-call engineer via PagerDuty |
| **API Gateway** | Error Rate | HTTP 5xx < 0.1% | 99.9% | Trigger SRE Incident Response |
| **Worker Pool** | Queue Saturation| Queue Delay < 5s | 99.0% | Autoscaling: spin up extra instances|
| **Database** | CPU Saturation | CPU usage < 80% | 95.0% | Cache invalidation / index audit |

---

## 3. Prometheus Alert Manager Rules

Alerting rules are stored inside IaC deployment modules, protecting systems against runtime exceptions.

```yaml
groups:
  - name: OMEGA-Gateway-Alerts
    rules:
      - alert: GatewayHighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100 > 1
        for: 2m
        labels:
          severity: critical
          tier: gateway
        annotations:
          summary: "Gateway HTTP 5xx error rate is highly elevated: {{ $value }}%"
          description: "API Gateway is returning 5xx responses exceeding 1% for more than 2 minutes. Immediate triage required."

      - alert: DatabaseCPUSaturation
        expr: pg_stat_activity_count{state="active"} > 50
        for: 5m
        labels:
          severity: warning
          tier: database
        annotations:
          summary: "Database active connections saturation high"
          description: "Postgres database active connection count has exceeded 50 active processes for 5 minutes."
```

---

## 4. Observability Gate Validation (Production Release)

No code may be deployed to the production environment unless it passes these observability tests:

- `[ ]` All new endpoints must declare custom OpenTelemetry counter and histogram metrics.
- `[ ]` Custom metrics names must match the standard namespacing rules (e.g., `omega.service_name.metric_name`).
- `[ ]` Structured logs must include tracing context markers (`trace_id`, `span_id`).
- `[ ]` CPU/Memory limits are set inside Kubernetes configurations to prevent unmonitored saturation.
