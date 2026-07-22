# 4. Azure ML Observability and Monitoring Summary

## Scope and cost boundary

The Azure ML training and model-registration pipeline is already operational, and the managed online endpoint was previously deployed and invoked successfully. That endpoint was deleted after validation to stop its online compute charges. This module adds monitoring configuration and a repeatable, temporary smoke test; it does not automate permanent endpoint creation and does not change training, registration, or Terraform.

## Logs, metrics, and observability

- **Logs** are timestamped records of discrete events. Container startup messages, scoring-script output, stack traces, and deployment errors explain what happened in a particular execution.
- **Metrics** are numeric time series aggregated over intervals. Request count, latency, failure rate, CPU use, and memory use show whether behavior is changing and support dashboards and alerts.
- **Observability** is the ability to understand a system's internal state from its outputs. It combines logs, metrics, traces, deployment metadata, model versions, health signals, and cost information so an operator can move from "the endpoint is unhealthy" to a likely cause.

Metrics reveal patterns and alert conditions; logs provide diagnostic detail. Neither alone gives a complete production picture.

## What deployment logs already proved

During manual endpoint validation, deployment logs were retrieved after creating deployment `blue`. Those logs were used to inspect provisioning and the inference container rather than treating a successful CLI submission as proof that the model was serving. Together with a real invocation that returned a prediction, they confirmed that the container started, the scoring code loaded, and inference completed. The endpoint was then deleted.

Deployment logs remain the first diagnostic tool for startup failures and scoring exceptions. They are a bounded view of recent container output, not a long-term monitoring system.

## Why `app_insights_enabled` matters

`azureml/endpoints/iris_deployment.yml` sets:

```yaml
app_insights_enabled: true
```

This enables Application Insights integration for the inference deployment. It makes application-level telemetry from the user/inference container available for investigating request behavior, failures, exceptions, and performance beyond a one-time container-log fetch.

Azure ML sends this telemetry to the Application Insights resource linked to the Azure ML workspace. The workspace must have a linked Application Insights resource; enabling the YAML property alone does not create a useful telemetry destination if no resource is linked. Azure Monitor supplies the broader metrics and logs platform: platform metrics are stored as time series, while configured resource logs can be queried through Log Analytics. Application Insights adds application-centric investigation experiences on top of that monitoring platform.

Telemetry can take several minutes to become queryable. Enabling telemetry also introduces ingestion and retention considerations, so production retention, sampling, access, and alert policies should be intentional.

## Production monitoring checklist

| Signal | What it answers | Example operational use |
| --- | --- | --- |
| Request count | How much traffic is arriving? | Detect unexpected drops, spikes, or missing traffic. |
| Latency | How long do responses take? | Track percentiles and alert on sustained degradation. |
| Errors | What exceptions or error responses occur? | Group recurring exceptions and correlate them with releases. |
| Failed requests | What fraction of scoring calls fail? | Alert on failure rate, not only absolute failure count. |
| Container crashes/restarts | Is the serving process stable? | Investigate startup, memory, dependency, and health-probe failures. |
| Model version | Which artifact served a request? | Correlate regressions with `iris-classifier` version and deployment. |
| Endpoint health | Is provisioning and serving healthy? | Watch endpoint/deployment state, availability, and replica health. |
| Cost | Is serving spend expected and justified? | Review endpoint/deployment cost, VM size, instance count, and idle resources. |

In production, dashboards should be paired with alerts and ownership. Useful first alerts include failed deployment, elevated failure rate, high latency, unavailable instances, and unexpected request or cost changes. Model/version identifiers should be included in deployment metadata and, where needed, structured application telemetry.

## Retrieve endpoint deployment logs

From the repository root, fetch the latest inference-server logs with:

```powershell
az ml online-deployment get-logs `
  --name blue `
  --endpoint-name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --lines 200
```

By default this returns inference-server container output. When diagnosing model download or mount initialization, request the storage-initializer container logs as well:

```powershell
az ml online-deployment get-logs `
  --name blue `
  --endpoint-name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --container storage-initializer `
  --lines 200
```

## Where to investigate

### Azure ML Studio

Open the workspace and select **Endpoints**, then `ep-iris-classifier-dev`. Use its details, monitoring/metrics, and deployment logs views to check provisioning state, traffic allocation, request activity, latency, resource utilization, and container output. This is the fastest endpoint-centered operational view.

### Application Insights

Open the Application Insights resource linked to the Azure ML workspace. Use Overview and application dashboards for a high-level view, Performance for request timing, Failures for failed operations and exceptions, Live Metrics when available for near-real-time behavior, and Logs for deeper telemetry queries. Filter by the endpoint/deployment identifiers and the time window of the smoke test.

### Azure Monitor

Use Azure Monitor Metrics for workspace and managed-online-endpoint time series, charts, dimensions, dashboards, and metric alerts. Use Log Analytics after diagnostic settings route supported resource logs to a Log Analytics workspace; online endpoint traffic logs can then support investigation of request duration and failure reason. Use alert rules to turn the monitoring signals into operational notifications.

## Temporary observability smoke test

The helper script first refuses to proceed if an endpoint with the configured name already exists. It then creates the endpoint and deployment, assigns all traffic to `blue`, invokes the tracked sample request several times, fetches logs, prints portal navigation hints, and deletes the endpoint in a `finally` cleanup block:

```powershell
.\scripts\azureml\observability-smoke-test.ps1 `
  -ResourceGroup "rg-azure-mlops-tarik2012-dev" `
  -WorkspaceName "mlw-azure-mlops-tarik2012-dev"
```

The script requires an authenticated Azure CLI with the Azure ML extension, access to the named workspace, and the configured model and environment versions already registered. It deliberately does not create an endpoint until an operator runs it manually.

## Cleanup is mandatory

A managed online deployment provisions the VM SKU declared in the deployment, here `Standard_DS2_v2` with one instance. That compute can continue generating charges while the endpoint exists, even when no test request is being sent. Application Insights and Log Analytics ingestion or retention can also carry costs.

The smoke test therefore deletes `ep-iris-classifier-dev` at the end. If automatic cleanup fails or the terminal is interrupted, run this immediately:

```powershell
az ml online-endpoint delete `
  --name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --yes
```

Confirm deletion before closing the test session. A smoke-test endpoint is temporary infrastructure, not a resource to leave idle.

## References

- [Monitor online endpoints in Azure Machine Learning](https://learn.microsoft.com/azure/machine-learning/how-to-monitor-online-endpoints)
- [Monitor Azure Machine Learning](https://learn.microsoft.com/azure/machine-learning/monitor-azure-machine-learning)
- [Troubleshoot online endpoint deployment](https://learn.microsoft.com/azure/machine-learning/how-to-troubleshoot-online-endpoints)
