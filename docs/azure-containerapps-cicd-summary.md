# Azure MLOps Platform — Versión CI/CD con Terraform

## Objetivo del proyecto

En esta práctica desplegamos una API de Machine Learning en Azure usando un flujo más cercano a empresa:

```text
Código Python / FastAPI
→ Tests
→ Docker image
→ Azure Container Registry
→ Terraform
→ Azure Container Apps
→ GitHub Actions CI/CD
→ Smoke tests
```

El objetivo fue aprender Azure de forma práctica para entrevistas MLOps, especialmente:

```text
Terraform
Azure Container Registry
Azure Container Apps
Managed Identity
RBAC
GitHub Actions
OIDC
Remote Terraform State
CI/CD
```

---

## Arquitectura final

La arquitectura quedó separada en tres bloques Terraform:

```text
infra/terraform/bootstrap
infra/terraform/platform
infra/terraform/app
```

### 1. bootstrap

Crea la infraestructura mínima para guardar el estado remoto de Terraform.

Recursos:

```text
Resource Group: rg-azure-mlops-tfstate-dev
Storage Account: sttarik2012mlopstfdev
Blob Container: tfstate
```

Función:

```text
Guardar platform.tfstate y app.tfstate en Azure Storage
```

Esto permite que GitHub Actions pueda ejecutar Terraform sin depender de un `terraform.tfstate` local.

---

### 2. platform

Crea la infraestructura base de Azure para la aplicación.

Recursos:

```text
Resource Group: rg-azure-mlops-platform-dev
Azure Container Registry: acrazuremlopsplatform
Managed Identity: id-azure-mlops-api-dev
Role Assignment: AcrPull
Log Analytics Workspace: law-ca-azure-mlops-api-dev
Container Apps Environment: cae-azure-mlops-platform-dev
```

Función:

```text
Preparar la plataforma donde se desplegará la API
```

---

### 3. app

Crea la aplicación final.

Recurso:

```text
Azure Container App: ca-azure-mlops-api-dev
```

Función:

```text
Desplegar la imagen Docker subida al ACR
Exponer la API FastAPI públicamente
Probar endpoints
```

---

## Recursos de Azure usados

### Resource Group

Un Resource Group agrupa recursos de Azure de forma lógica.

Usamos dos:

```text
rg-azure-mlops-platform-dev
→ recursos reales de la app

rg-azure-mlops-tfstate-dev
→ backend remoto de Terraform
```

---

### Azure Container Registry

ACR es el almacén privado de imágenes Docker.

Nombre usado:

```text
acrazuremlopsplatform
```

Imagen generada por CI/CD:

```text
acrazuremlopsplatform.azurecr.io/azure-mlops-platform-api:<github_sha>
```

Aprendido:

```text
Container Apps no puede arrancar si la imagen todavía no existe en ACR.
```

---

### Managed Identity

Creamos una identidad administrada:

```text
id-azure-mlops-api-dev
```

Función:

```text
Permitir que la Container App acceda al ACR sin usuario/contraseña.
```

---

### AcrPull

Role assignment:

```text
Managed Identity → AcrPull → ACR
```

Función:

```text
Permite a la Container App descargar la imagen Docker desde ACR.
```

Error aprendido:

```text
Contributor no puede crear role assignments.
Para crear AcrPull desde Terraform, la identidad de GitHub Actions necesitó User Access Administrator.
```

---

### Log Analytics Workspace

Recurso:

```text
law-ca-azure-mlops-api-dev
```

Función:

```text
Guardar logs y métricas de Azure Container Apps.
```

---

### Container Apps Environment

Recurso:

```text
cae-azure-mlops-platform-dev
```

Función:

```text
Entorno administrado donde vive la Container App.
```

---

### Azure Container App

Recurso:

```text
ca-azure-mlops-api-dev
```

Función:

```text
Ejecutar la API FastAPI como contenedor serverless.
```

Endpoints probados:

```text
/health
/model-info
/predict
```

---

## CI/CD con GitHub Actions

Creamos dos workflows:

```text
.github/workflows/ci.yml
.github/workflows/deploy-azure.yml
```

---

## Workflow 1: CI

Nombre:

```text
Azure MLOps Platform CI
```

Se ejecuta automáticamente con push / pull request.

Hace:

```text
Checkout
Setup Python
Install dependencies
Create .tmp
Run pytest
Terraform fmt check
Terraform validate bootstrap
Terraform validate platform
Terraform validate app
```

No crea recursos en Azure.

---

## Workflow 2: Deploy Azure MLOps Platform

Nombre:

```text
Deploy Azure MLOps Platform
```

Se ejecuta manualmente con:

```text
Actions → Deploy Azure MLOps Platform → Run workflow
```

Hace:

```text
Checkout
Setup Python
Install dependencies
Generate model artifact
Run tests
Azure login with OIDC
Terraform init/plan/apply platform
Read ACR outputs
Docker build
ACR login
Docker push
Terraform init/plan/apply app
Read Container App URL
Smoke test /health
Smoke test /model-info
Smoke test /predict
```

---

## OIDC con GitHub Actions

Creamos una App Registration en Microsoft Entra ID:

```text
github-azure-mlops-platform-dev
```

Valores usados en GitHub Environment `azure-dev`:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
TFSTATE_RESOURCE_GROUP_NAME
TFSTATE_STORAGE_ACCOUNT_NAME
TFSTATE_CONTAINER_NAME
```

OIDC evita usar secretos largos o passwords.

Subject configurado:

```text
repo:Tarik2012/azure-mlops-platform:environment:azure-dev
```

---

## GitHub Environment

Creamos un environment:

```text
azure-dev
```

Ahí guardamos las variables necesarias para el workflow de deploy.

---

## Errores encontrados y solución

### Error 1: imagen Docker no existía

Error:

```text
MANIFEST_UNKNOWN: manifest tagged by "v1" is not found
```

Causa:

```text
Terraform intentaba crear la Container App antes de subir la imagen al ACR.
```

Solución:

```text
Separar Terraform en platform y app.
Primero crear ACR.
Luego docker build + docker push.
Después crear Container App.
```

---

### Error 2: pytest fallaba por `.tmp`

Error:

```text
FileNotFoundError: .tmp/pytest_tmp
```

Causa:

```text
La carpeta .tmp estaba ignorada y no existía en GitHub Actions.
```

Solución:

```text
Añadir mkdir -p .tmp antes de ejecutar pytest.
```

---

### Error 3: permiso insuficiente para AcrPull

Error:

```text
AuthorizationFailed:
does not have authorization to perform action
Microsoft.Authorization/roleAssignments/write
```

Causa:

```text
La identidad de GitHub Actions tenía Contributor,
pero Contributor no puede crear role assignments.
```

Solución:

```powershell
az role assignment create `
  --assignee 972622c0-e61c-447b-83e4-66534dc97ad7 `
  --role "User Access Administrator" `
  --scope "/subscriptions/4cfcc350-8157-4c53-a3c4-5937dbc63be0"
```

---

## Flujo final correcto

```text
1. Commit y push a main
2. CI automático
3. Deploy manual desde GitHub Actions
4. Terraform crea platform
5. Docker build
6. Docker push a ACR
7. Terraform crea app
8. Smoke tests
```

---

## Deploy automático vs manual

Actualmente:

```text
push a main → ejecuta CI
deploy → manual con workflow_dispatch
```

Para hacerlo automático en dev, se podría cambiar `deploy-azure.yml`:

```yaml
on:
  workflow_dispatch:
  push:
    branches:
      - main
```

Recomendación:

```text
Mantener deploy manual mientras se aprende y se controla coste.
Luego automatizar deploy a dev.
```

---

## Comandos importantes

### Borrar Resource Groups de golpe

```powershell
az group delete --name rg-azure-mlops-platform-dev --yes --no-wait
az group delete --name rg-azure-mlops-tfstate-dev --yes --no-wait
```

### Comprobar si siguen existiendo

```powershell
az group list --query "[?contains(name, 'azure-mlops')].{name:name, location:location}" -o table
```

### Borrar App Registration / OIDC

```powershell
az ad app delete --id 972622c0-e61c-447b-83e4-66534dc97ad7
```

---

## Qué aprendimos para entrevistas

Puedes explicar el proyecto así:

```text
Desplegué una API FastAPI de Machine Learning en Azure usando un flujo CI/CD real.
Separé Terraform en bootstrap, platform y app.
Usé Azure Storage como remote backend para Terraform state.
GitHub Actions se autentica contra Azure mediante OIDC, sin client secrets.
El pipeline ejecuta tests, crea infraestructura base con Terraform,
construye la imagen Docker, la sube a ACR, despliega Azure Container Apps
y ejecuta smoke tests contra /health, /model-info y /predict.
También configuré Managed Identity y AcrPull para que la app pueda descargar la imagen desde ACR.
```

Versión corta:

```text
FastAPI ML API deployed to Azure Container Apps with Terraform, ACR,
Managed Identity, GitHub Actions CI/CD, OIDC authentication and remote Terraform state.
```

---

## Siguiente paso recomendado

El siguiente proyecto debería ser:

```text
Azure ML + MLflow Model Registry
```

Flujo objetivo:

```text
Azure ML Workspace
→ Compute Cluster
→ Training Job
→ MLflow Tracking
→ Model Registry
→ Managed Online Endpoint
→ Monitoring
→ CI/CD
```

Esto conecta directamente con MLOps profesional, Azure ML, MLflow y entrevistas.
