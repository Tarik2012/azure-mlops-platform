# WARNING: This script creates temporary Azure Machine Learning online compute,
# which incurs charges until the endpoint is deleted.

[CmdletBinding()]
param(
    [string]$ResourceGroup = "rg-azure-mlops-tarik2012-dev",
    [string]$WorkspaceName = "mlw-azure-mlops-tarik2012-dev",
    [ValidateRange(1, 100)]
    [int]$RequestCount = 5
)

$ErrorActionPreference = "Stop"

$EndpointName = "ep-iris-classifier-dev"
$DeploymentName = "blue"
$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$EndpointFile = Join-Path $RepositoryRoot "azureml\endpoints\iris_endpoint.yml"
$DeploymentFile = Join-Path $RepositoryRoot "azureml\endpoints\iris_deployment.yml"
$RequestFile = Join-Path $RepositoryRoot "azureml\requests\iris_sample.json"
$EndpointCreationAttempted = $false
$CleanupSucceeded = $false
$TestFailure = $null

function Invoke-AzureCli {
    param(
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    & az @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI command failed with exit code ${LASTEXITCODE}: az $($Arguments -join ' ')"
    }
}

Write-Warning "This smoke test creates billable temporary online compute. Keep this terminal open until cleanup completes."
Write-Host "Resource group: $ResourceGroup"
Write-Host "Workspace:      $WorkspaceName"
Write-Host "Endpoint:       $EndpointName"

try {
    foreach ($RequiredFile in @($EndpointFile, $DeploymentFile, $RequestFile)) {
        if (-not (Test-Path -LiteralPath $RequiredFile)) {
            throw "Required file not found: $RequiredFile"
        }
    }

    Write-Host "`nConfirming that the temporary endpoint name is available..."
    $ExistingEndpoint = Invoke-AzureCli -Arguments @(
        "ml", "online-endpoint", "list",
        "--resource-group", $ResourceGroup,
        "--workspace-name", $WorkspaceName,
        "--query", "[?name=='$EndpointName'].name | [0]",
        "--output", "tsv"
    )
    if ($ExistingEndpoint) {
        throw "Endpoint '$EndpointName' already exists. Refusing to modify or delete a pre-existing endpoint."
    }

    Write-Host "`nCreating temporary endpoint..."
    $EndpointCreationAttempted = $true
    Invoke-AzureCli -Arguments @(
        "ml", "online-endpoint", "create",
        "--file", $EndpointFile,
        "--resource-group", $ResourceGroup,
        "--workspace-name", $WorkspaceName
    )

    Write-Host "`nCreating deployment and assigning all traffic..."
    Invoke-AzureCli -Arguments @(
        "ml", "online-deployment", "create",
        "--file", $DeploymentFile,
        "--resource-group", $ResourceGroup,
        "--workspace-name", $WorkspaceName,
        "--all-traffic"
    )

    Write-Host "`nInvoking the endpoint $RequestCount times to generate telemetry..."
    for ($RequestNumber = 1; $RequestNumber -le $RequestCount; $RequestNumber++) {
        Write-Host "Request $RequestNumber of ${RequestCount}:"
        Invoke-AzureCli -Arguments @(
            "ml", "online-endpoint", "invoke",
            "--name", $EndpointName,
            "--request-file", $RequestFile,
            "--resource-group", $ResourceGroup,
            "--workspace-name", $WorkspaceName
        )
    }

    Write-Host "`nFetching the latest deployment logs..."
    Invoke-AzureCli -Arguments @(
        "ml", "online-deployment", "get-logs",
        "--name", $DeploymentName,
        "--endpoint-name", $EndpointName,
        "--resource-group", $ResourceGroup,
        "--workspace-name", $WorkspaceName,
        "--lines", "200"
    )

    Write-Host "`nTelemetry has been generated. Some metrics can take a few minutes to appear."
    Write-Host "Azure ML Studio: open the workspace, then Endpoints > $EndpointName > Monitoring (or Metrics)."
    Write-Host "Application Insights: open the resource linked to the Azure ML workspace, then review Overview, Live Metrics, Failures, Performance, and Logs."
    Write-Host "Azure Monitor: open Metrics for the Machine Learning workspace and filter by endpoint/deployment; use Alerts for production thresholds."
}
catch {
    $TestFailure = $_
    Write-Error -ErrorRecord $_ -ErrorAction Continue
}
finally {
    if ($EndpointCreationAttempted) {
        Write-Host "`nDeleting the temporary endpoint to stop compute charges..."
        try {
            & az ml online-endpoint delete `
                --name $EndpointName `
                --resource-group $ResourceGroup `
                --workspace-name $WorkspaceName `
                --yes

            if ($LASTEXITCODE -eq 0) {
                $CleanupSucceeded = $true
                Write-Host "Cleanup completed: endpoint '$EndpointName' was deleted."
            }
            else {
                Write-Warning "Azure CLI returned exit code $LASTEXITCODE during cleanup."
            }
        }
        catch {
            Write-Warning "Cleanup command error: $($_.Exception.Message)"
        }

        if (-not $CleanupSucceeded) {
            Write-Warning "Automatic cleanup failed. Delete the endpoint manually now to avoid ongoing charges:"
            Write-Warning "az ml online-endpoint delete --name $EndpointName --resource-group $ResourceGroup --workspace-name $WorkspaceName --yes"
        }
    }
}

if ($EndpointCreationAttempted -and -not $CleanupSucceeded) {
    throw "The smoke test ended without confirmed endpoint cleanup. Run the manual delete command shown above."
}

if ($null -ne $TestFailure) {
    throw $TestFailure
}
