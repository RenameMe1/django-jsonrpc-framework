# Prometheus 

Prometheus is a monitoring system that allows you to collect metrics from your application and store them in a time series database.

## Installation

```
pip install django-jsonrpc-framework[prometheus]
```

## Configuration

To enable prometheus integration, you need to add `enable_prometheus()` to your settings.py file.

Next step is to add `MetricsView` to your urlpatterns. It will serve the metrics endpoint.

```python linenums="1" hl_lines="10-13 16 43"
--8<-- "docs/docs/examples/prometheus.py"
```

Make test request to your JSON-RPC endpoint.

```bash
curl -X POST http://127.0.0.1:8000/jsonrpc -d '{"jsonrpc": "2.0", "id": 1, "method": "echo", "params": {"name": "test"}}'
```

Make test request to your JSON-RPC endpoint with error.
```bash
curl -X POST http://127.0.0.1:8000/jsonrpc -d '{"jsonrpc": "2.0", "id": 1, "method": "error"}'
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


## Django-prometheus integration

To collect not only JSON-RPC metrics but others Django metrics (like HTTP requests, etc.), you need to add [django-prometheus](https://pypi.org/project/django-prometheus/) to your project. Or any other prometheus client implementation.

django_* metrics are collected by `django-prometheus`. jsonrpc_* metrics are collected by `django-jsonrpc-framework`.

Just use `django-prometheus` as usual. It will collect metrics from all your views and endpoints. Prometheus will collect both JSON-RPC and REST metrics.

You only need to add `enable_prometheus()` from `django-jsonrpc-framework` to your settings.py file. It will collect JSON-RPC metrics and add them to the same metric registry as `django-prometheus`.

> **Warning**  
> Do not use `MetricsView` from `django-jsonrpc-framework` together with `django-prometheus`. Use only the endpoint from `django-prometheus`. `django-prometheus` reads the same metric registry, so `jsonrpc_*` metrics will be collected.

> **Warning**  
> Do not use `enable_prometheus(registry=...)` from `django-jsonrpc-framework` together with `django-prometheus`. Use only the `enable_prometheus()` from `django-jsonrpc-framework`.  `enable_prometheus(registry=...)` collects `jsonrpc_*` metrics to the custom registry.

## Multiple workers (WSGI)

If you are using multiple workers, `django-prometheus` will collect metrics from multiple workers. `MetricsView` from `django-jsonrpc-framework` does not support multiple workers.
