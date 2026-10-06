# Prometheus 

Prometheus is a monitoring system that allows you to collect metrics from your application and store them in a time series database.

## Installation

```
pip install django-jsonrpc-framework[prometheus]
```

## Configuration

To enable prometheus integration, you need to add `enable_prometheus()` to your settings.py file.

Next step is to add `MetricsView` to your urlpatterns. It will serve the metrics endpoint.

```python linenums="1" hl_lines="10-13 15 38"
--8<-- "docs/docs/examples/prometheus.py"
```

Make test request to your JSON-RPC endpoint.

```bash
curl -X POST http://127.0.0.1:8000/jsonrpc -d '{"jsonrpc": "2.0", "method": "echo", "params": {"name": "test"}}'
```

Open [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics) to see the metrics.

## Metrics

There are three metrics that are collected by default:

| Metric | Description | Labels | Type |
|--------|-------------|--------|------|
| `jsonrpc_requests_total` | Total number of requests | `method`, `result` | Counter |
| `jsonrpc_request_duration_seconds` | Request duration | `method` | Histogram |
| `jsonrpc_errors_total` | Total number of errors | `method`, `code` | Counter |


## Warning

It's recommended to use IP allowlist or a separate port and not publish `/metrics` in internet.
