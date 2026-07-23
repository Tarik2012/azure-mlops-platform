# COST WARNING: This script creates a billable AKS worker node and related
# networking resources. Destroy the stack immediately after practice.

[CmdletBinding()]
param(
    [string]$ResourceGroup = "rg-azure-mlops-aks-dev",
    [string]$ClusterName = "aks-azure-mlops-dev",
    [int]$LocalPort = 8000
)

$ErrorActionPreference = "Stop"

$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$TerraformDirectory = Join-Path $RepositoryRoot "infra\terraform\aks"
$ManifestDirectory = Join-Path $RepositoryRoot "k8s\azure-mlops-api"
$BackendConfig = Join-Path $TerraformDirectory "backend.hcl"
$VariableFile = Join-Path $TerraformDirectory "terraform.tfvars"
$PlanDirectory = Join-Path $RepositoryRoot ".tmp"
$PlanFile = Join-Path $PlanDirectory "aks.tfplan"
$PortForwardProcess = $null
$ApplyAttempted = $false
$TestFailure = $null

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory)]
        [string]$Command,
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "> $Command $($Arguments -join ' ')"
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE."
    }
}

foreach ($Command in @("az", "terraform", "kubectl")) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "Required command '$Command' was not found on PATH."
    }
}

foreach ($RequiredFile in @(
        (Join-Path $ManifestDirectory "namespace.yml"),
        (Join-Path $ManifestDirectory "deployment.yml"),
        (Join-Path $ManifestDirectory "service.yml")
    )) {
    if (-not (Test-Path -LiteralPath $RequiredFile)) {
        throw "Required file not found: $RequiredFile"
    }
}

if (-not (Test-Path -LiteralPath $BackendConfig)) {
    throw "Create infra/terraform/aks/backend.hcl from backend.hcl.example and verify its remote-state settings."
}

if (-not (Test-Path -LiteralPath $VariableFile)) {
    throw "Create infra/terraform/aks/terraform.tfvars from terraform.tfvars.example and verify its Azure values."
}

New-Item -ItemType Directory -Path $PlanDirectory -Force | Out-Null

Write-Warning "AKS worker nodes, disks, public IP/networking, and traffic can incur charges even though the AKS control-plane tier is Free."
Write-Host "`nCurrent Azure account:"
Invoke-NativeCommand -Command "az" -Arguments @("account", "show", "--output", "table")

$CreateConfirmation = Read-Host "`nType CREATE to provision the temporary AKS cluster"
if ($CreateConfirmation -cne "CREATE") {
    Write-Host "Creation cancelled. No Terraform apply was run."
    return
}

try {
    Push-Location $TerraformDirectory
    try {
        Invoke-NativeCommand -Command "terraform" -Arguments @(
            "init",
            "-reconfigure",
            "-backend-config=backend.hcl"
        )
        Invoke-NativeCommand -Command "terraform" -Arguments @(
            "plan",
            "-var-file=terraform.tfvars",
            "-out=$PlanFile"
        )

        $ApplyAttempted = $true
        Invoke-NativeCommand -Command "terraform" -Arguments @("apply", $PlanFile)
    }
    finally {
        Pop-Location
    }

    Invoke-NativeCommand -Command "az" -Arguments @(
        "aks", "get-credentials",
        "--resource-group", $ResourceGroup,
        "--name", $ClusterName,
        "--overwrite-existing"
    )

    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "apply", "-f", (Join-Path $ManifestDirectory "namespace.yml")
    )
    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "apply",
        "-f", (Join-Path $ManifestDirectory "deployment.yml"),
        "-f", (Join-Path $ManifestDirectory "service.yml")
    )

    Write-Host "`nWaiting for the Deployment rollout..."
    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "rollout", "status", "deployment/azure-mlops-api",
        "--namespace", "azure-mlops",
        "--timeout=180s"
    )

    Write-Host "`nPods:"
    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "get", "pods", "--namespace", "azure-mlops", "--output", "wide"
    )
    Write-Host "`nServices:"
    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "get", "services", "--namespace", "azure-mlops"
    )

    Write-Host "`nStarting a temporary port-forward on http://localhost:$LocalPort ..."
    $PortForwardProcess = Start-Process `
        -FilePath "kubectl" `
        -ArgumentList @(
            "port-forward",
            "--namespace", "azure-mlops",
            "service/azure-mlops-api",
            "${LocalPort}:8000"
        ) `
        -PassThru `
        -WindowStyle Hidden

    $HealthUri = "http://localhost:$LocalPort/health"
    $HealthResponse = $null
    for ($Attempt = 1; $Attempt -le 10; $Attempt++) {
        try {
            $HealthResponse = Invoke-RestMethod -Uri $HealthUri -TimeoutSec 5
            break
        }
        catch {
            if ($Attempt -eq 10) {
                Write-Warning "The API did not become reachable at $HealthUri."
            }
            else {
                Start-Sleep -Seconds 2
            }
        }
    }

    if ($null -ne $HealthResponse) {
        Write-Host "`n/health response:"
        $HealthResponse | ConvertTo-Json -Depth 5
    }

    Write-Host "`nLatest API logs:"
    Invoke-NativeCommand -Command "kubectl" -Arguments @(
        "logs",
        "--namespace", "azure-mlops",
        "deployment/azure-mlops-api",
        "--tail=100"
    )
}
catch {
    $TestFailure = $_
    Write-Error -ErrorRecord $_ -ErrorAction Continue
}
finally {
    if ($null -ne $PortForwardProcess -and -not $PortForwardProcess.HasExited) {
        Stop-Process -Id $PortForwardProcess.Id
        Write-Host "Stopped the temporary port-forward."
    }

    if ($ApplyAttempted) {
        Write-Warning "`nThe temporary AKS stack may be billable until Terraform destroys it."
        $DestroyConfirmation = Read-Host "Type DESTROY to run terraform destroy now, or press Enter to keep it temporarily"

        if ($DestroyConfirmation -ceq "DESTROY") {
            Push-Location $TerraformDirectory
            try {
                Invoke-NativeCommand -Command "terraform" -Arguments @(
                    "destroy",
                    "-var-file=terraform.tfvars",
                    "-auto-approve"
                )
            }
            finally {
                Pop-Location
            }
        }
        else {
            Write-Warning "AKS was not destroyed. Run this command as soon as practice is complete:"
            Write-Warning "terraform -chdir=infra/terraform/aks destroy -var-file=terraform.tfvars"
        }
    }
}

if ($null -ne $TestFailure) {
    throw $TestFailure
}
