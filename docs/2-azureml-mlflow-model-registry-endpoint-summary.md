# 2 - Azure ML + MLflow + Model Registry + Managed Online Endpoint

## Proyecto

En esta segunda práctica hemos desplegado un modelo de Machine Learning usando **Azure Machine Learning**.

Flujo aprendido:

```text
Terraform
→ Azure ML Workspace
→ Azure ML Compute Cluster
→ Azure ML Environment
→ Training Job
→ MLflow Tracking
→ Model Registry
→ Managed Online Endpoint
→ Deployment blue
→ Online prediction
```

Este módulo continúa después del primer módulo:

```text
1-azure_learning_summary.md
```

El primer módulo fue sobre:

```text
Docker image
→ Azure Container Registry
→ Managed Identity
→ Azure Container Apps
→ Public API endpoint
→ CI/CD base
```

Este segundo módulo entra en una parte más real de **MLOps empresarial**.

---

## 1. Objetivo del módulo

El objetivo era aprender cómo funciona el ciclo completo de un modelo en Azure ML:

```text
Entrenar modelo
→ Registrar métricas con MLflow
→ Guardar artefacto del modelo
→ Registrar modelo en Model Registry
→ Desplegar modelo en un endpoint online
→ Enviar una petición real
→ Recibir una predicción
```

Resultado final conseguido:

```text
Endpoint online funcionando
Deployment blue funcionando
Modelo iris-classifier:1 cargado correctamente
Predicción real devuelta correctamente
```

Respuesta obtenida del endpoint:

```json
"{\"predictions\": [0]}"
```

Esto confirma que el endpoint recibió datos, cargó el modelo y devolvió una predicción.

---

## 2. Recursos principales creados

Terraform creó la infraestructura base de Azure ML.

Resource Group:

```text
rg-azure-mlops-tarik2012-dev
```

Azure ML Workspace:

```text
mlw-azure-mlops-tarik2012-dev
```

Compute Cluster:

```text
cpu-amlops-tarik2012-dev
```

Azure Container Registry:

```text
acrtarik2012azuremlopsdev
```

Storage Account:

```text
sttarik2012azuremlopsdev
```

Key Vault:

```text
kv-amlops-tarik2012-dev
```

Application Insights:

```text
appi-azure-mlops-tarik2012-dev
```

Terraform remote state:

```text
Resource Group: rg-azure-mlops-tfstate-dev
Storage Account: sttarik2012mlopstfdev
Container: tfstate
State key: aml.tfstate
```

---

## 3. Estructura del módulo en el repositorio

Archivos importantes:

```text
infra/terraform/aml/
```

Contiene Terraform para Azure ML:

```text
providers.tf
variables.tf
main.tf
outputs.tf
backend.hcl.example
terraform.tfvars.example
```

Training script:

```text
src/training/train_azureml.py
```

Scoring script:

```text
src/inference/score_azureml.py
```

Azure ML job:

```text
azureml/jobs/train_iris.yml
```

Azure ML environment:

```text
azureml/environments/sklearn-mlflow.yml
azureml/environments/conda/sklearn-mlflow-conda.yml
```

Endpoint y deployment:

```text
azureml/endpoints/iris_endpoint.yml
azureml/endpoints/iris_deployment.yml
```

Tests:

```text
tests/test_train_azureml.py
tests/test_score_azureml.py
```

---

## 4. Conceptos aprendidos

### Azure ML Workspace

El **Workspace** es el centro del proyecto de Machine Learning en Azure.

Dentro del workspace viven:

```text
Jobs
Experiments
MLflow runs
Models
Environments
Endpoints
Deployments
Metrics
Artifacts
```

En entrevista:

```text
Azure ML Workspace is the central place where I manage experiments, models, environments, compute resources and deployments.
```

---

### Azure ML Compute Cluster

El **Compute Cluster** es la máquina o grupo de máquinas que Azure ML usa para entrenar modelos.

En este proyecto:

```text
cpu-amlops-tarik2012-dev
```

Configuración:

```text
min_nodes = 0
max_nodes = 2
```

Esto es importante porque con `min_nodes = 0`, el cluster puede apagarse cuando no se usa.

En entrevista:

```text
I use Azure ML Compute Cluster to run training jobs in a reproducible and scalable environment.
```

---

### Azure ML Environment

El **Environment** define el entorno Python donde corre el training o la inferencia.

Incluye:

```text
Docker base image
conda dependencies
pip dependencies
scikit-learn
mlflow
azureml-mlflow
azureml-inference-server-http
```

Environment final usado para inferencia:

```text
sklearn-mlflow:2
```

La versión 2 fue necesaria porque faltaba:

```text
azureml-inference-server-http
```

Sin este paquete, el contenedor de inferencia no puede arrancar el servidor HTTP de Azure ML.

---

### Azure ML Job

Un **Job** es una ejecución de entrenamiento.

Job ejecutado:

```text
coral_lamp_wwdf40x2fl
```

Experiment:

```text
iris-azureml-training
```

Resultado:

```text
Status: Completed
```

El job entrenó un modelo de clasificación usando el dataset Iris.

---

### MLflow Tracking

MLflow se usó para registrar métricas durante el entrenamiento.

Métricas registradas:

```text
accuracy: 0.9000
f1_macro: 0.8997
```

Estas métricas están en:

```text
Azure ML Workspace
→ Jobs
→ Experiment: iris-azureml-training
→ Job: coral_lamp_wwdf40x2fl
→ Metrics
```

Concepto importante:

Cuando el entrenamiento corre en Azure ML, MLflow no guarda las métricas en una carpeta local `mlruns/`.

Las guarda en el backend gestionado de Azure ML:

```text
Azure ML Workspace = MLflow Tracking Server gestionado
```

En entrevista:

```text
During training, I use MLflow to log metrics, parameters and artifacts. When the job runs in Azure ML, those MLflow runs are stored in the Azure ML Workspace, so I can compare experiments, track model performance and register the best model.
```

---

### Model Registry

El modelo se registró en Azure ML Model Registry.

Nombre:

```text
iris-classifier
```

Versión:

```text
1
```

Tipo:

```text
custom_model
```

Path original:

```text
azureml://jobs/coral_lamp_wwdf40x2fl/outputs/model_output
```

En entrevista:

```text
After training, I register the trained model in Azure ML Model Registry. This allows me to version models and deploy a specific version to production.
```

---

### Managed Online Endpoint

El **Endpoint** es la puerta HTTPS pública o privada por donde se consulta el modelo.

Endpoint creado:

```text
ep-iris-classifier-dev
```

Scoring URI:

```text
https://ep-iris-classifier-dev.francecentral.inference.ml.azure.com/score
```

Auth mode:

```text
key
```

Concepto:

```text
Endpoint = puerta HTTPS
Deployment = modelo corriendo detrás de la puerta
```

---

### Online Deployment

El **Deployment** es la instancia real que carga el modelo y ejecuta el scoring script.

Deployment creado:

```text
blue
```

Modelo usado:

```text
iris-classifier:1
```

Environment usado:

```text
sklearn-mlflow:2
```

Instance type usado:

```text
Standard_DS2_v2
```

Resultado final:

```text
provisioning_state: Succeeded
```

En entrevista:

```text
I deployed the registered model to an Azure ML Managed Online Endpoint using a blue deployment. The deployment loads the model artifact, starts the Azure ML inference server and exposes a scoring API.
```

---

## 5. Comandos principales usados

### Crear Azure ML Environment

```powershell
az ml environment create `
  --file azureml/environments/sklearn-mlflow.yml `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev
```

---

### Enviar training job

```powershell
az ml job create `
  --file azureml/jobs/train_iris.yml `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --stream
```

Job creado:

```text
coral_lamp_wwdf40x2fl
```

---

### Ver estado del job

```powershell
az ml job show `
  --name coral_lamp_wwdf40x2fl `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --query "{status:status, display_name:display_name, experiment_name:experiment_name}" `
  -o table
```

Resultado:

```text
Completed
```

---

### Registrar modelo

```powershell
az ml model create `
  --name iris-classifier `
  --type custom_model `
  --path azureml://jobs/coral_lamp_wwdf40x2fl/outputs/model_output `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev
```

---

### Listar modelo registrado

```powershell
az ml model list `
  --name iris-classifier `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  -o table
```

Resultado:

```text
iris-classifier    version 1    custom_model
```

---

### Crear endpoint

```powershell
az ml online-endpoint create `
  --file azureml/endpoints/iris_endpoint.yml `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev
```

Resultado:

```text
provisioning_state: Succeeded
```

---

### Crear deployment blue

```powershell
az ml online-deployment create `
  --file azureml/endpoints/iris_deployment.yml `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --all-traffic
```

Resultado final:

```text
provisioning_state: Succeeded
```

---

### Crear request de prueba

```powershell
'{"data": [[5.1, 3.5, 1.4, 0.2]]}' | Out-File -Encoding utf8 request.json
```

---

### Invocar endpoint

```powershell
az ml online-endpoint invoke `
  --name ep-iris-classifier-dev `
  --request-file request.json `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev
```

Respuesta:

```json
"{\"predictions\": [0]}"
```

---

## 6. Errores encontrados y soluciones

Esta parte es la más importante para no repetir errores.

---

### Error 1 - Terraform remote state sin permisos Blob

Error:

```text
AuthorizationPermissionMismatch
```

Causa:

Terraform podía ver Azure, pero el usuario no tenía permisos suficientes sobre el Storage Account del remote state.

Solución:

Asignar el rol:

```text
Storage Blob Data Contributor
```

al usuario sobre el Storage Account:

```text
sttarik2012mlopstfdev
```

Comando usado:

```powershell
$SUBSCRIPTION_ID = "4cfcc350-8157-4c53-a3c4-5937dbc63be0"
$TFSTATE_RG = "rg-azure-mlops-tfstate-dev"
$TFSTATE_STORAGE = "sttarik2012mlopstfdev"
$USER_OBJECT_ID = az ad signed-in-user show --query id -o tsv

az role assignment create `
  --assignee-object-id $USER_OBJECT_ID `
  --assignee-principal-type User `
  --role "Storage Blob Data Contributor" `
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$TFSTATE_RG/providers/Microsoft.Storage/storageAccounts/$TFSTATE_STORAGE"
```

Lección:

```text
Para usar Terraform remote state en Azure Storage con Azure AD auth, no basta con Contributor. Se necesita permiso de datos sobre blobs.
```

---

### Error 2 - Azure ML intentaba subir demasiados archivos

Error:

```text
[WinError 5] Acceso denegado: '.pytest_cache'
```

Causa:

El job tenía:

```yaml
code: ../..
```

Eso hacía que Azure ML intentara empaquetar todo el repositorio, incluyendo carpetas locales como `.pytest_cache`.

Solución:

Cambiar el job para subir solo `src`:

```yaml
code: ../../src
```

Y añadir `.amlignore`.

Lección:

```text
En Azure ML jobs, el campo code debe apuntar solo al código necesario. No conviene subir todo el repositorio.
```

---

### Error 3 - Crear deployment antes de endpoint

Error:

```text
endpoint not found
```

Causa:

Se intentó crear el deployment `blue` antes de crear el endpoint.

Orden correcto:

```text
1. Crear endpoint
2. Crear deployment
3. Asignar tráfico
```

Lección:

```text
Endpoint = puerta
Deployment = modelo detrás de la puerta
```

---

### Error 4 - Cuota insuficiente con Standard_DS3_v2

Error:

```text
OutOfQuota
```

Causa:

El deployment pedía una VM `Standard_DS3_v2`, pero la suscripción no tenía cuota suficiente.

Solución temporal de desarrollo:

```yaml
instance_type: Standard_DS2_v2
```

Lección:

```text
En entornos de desarrollo se puede usar una VM más pequeña, pero en producción hay que revisar cuotas y SKUs recomendados.
```

---

### Error 5 - Deployment fallido ya existente

Error:

```text
A deployment with this name already exists
```

Causa:

Un intento anterior había dejado el deployment `blue` en estado fallido.

Solución correcta:

Primero mirar estado:

```powershell
az ml online-deployment show `
  --name blue `
  --endpoint-name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --query "{name:name, provisioning_state:provisioning_state, instance_type:instance_type}" `
  -o table
```

Si está fallido e irrecuperable, borrar:

```powershell
az ml online-deployment delete `
  --name blue `
  --endpoint-name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --yes
```

Luego crear de nuevo.

Lección:

```text
No repetir create encima de un deployment fallido. Primero mirar estado y logs.
```

---

### Error 6 - Faltaba azureml-inference-server-http

Error en logs:

```text
A required package azureml-inference-server-http is missing.
```

Causa:

El environment tenía librerías de MLflow y scikit-learn, pero no el servidor HTTP que Azure ML necesita para inferencia online.

Solución:

Añadir al environment:

```yaml
- azureml-inference-server-http
```

Crear nueva versión:

```text
sklearn-mlflow:2
```

Actualizar deployment para usar:

```yaml
environment: azureml:sklearn-mlflow:2
```

Lección:

```text
Para Managed Online Endpoints con scoring script personalizado, el environment debe incluir azureml-inference-server-http.
```

---

### Error 7 - El modelo estaba dentro de model_output/

Error:

```text
FileNotFoundError: Model artifact not found:
/var/azureml-app/azureml-models/iris-classifier/1/model.joblib
```

Logs mostraron que el modelo real estaba aquí:

```text
/var/azureml-app/azureml-models/iris-classifier/1/model_output/model.joblib
```

Causa:

Registramos el modelo desde el output del job:

```text
outputs/model_output
```

Azure ML conservó esa carpeta dentro del modelo registrado.

El scoring script buscaba solo:

```text
AZUREML_MODEL_DIR/model.joblib
```

Solución:

Hacer el discovery del modelo más robusto en:

```text
src/inference/score_azureml.py
```

Ahora `init()` busca:

```text
1. AZUREML_MODEL_DIR/model.joblib
2. AZUREML_MODEL_DIR/model_output/model.joblib
3. Búsqueda recursiva de model.joblib dentro de AZUREML_MODEL_DIR
```

Lección:

```text
Nunca asumir a ciegas la estructura exacta del artifact dentro de AZUREML_MODEL_DIR. El scoring script debe ser robusto.
```

---

### Error 8 - Warning de Standard_DS2_v2

Mensaje:

```text
Instance type Standard_DS2_v2 may be too small...
```

Causa:

Azure recomienda `Standard_DS3_v2` para endpoints generales.

Pero no era un error fatal.

Solución:

Continuar con `Standard_DS2_v2` para entorno dev porque la suscripción tenía límites de cuota.

Lección:

```text
No todo warning es error. Primero leer si el provisioning falla o continúa.
```

---

## 7. Orden correcto para depurar Azure ML Endpoints

Cuando un deployment falla, no improvisar.

Orden correcto:

```text
1. No volver a ejecutar create inmediatamente
2. Ver estado del deployment
3. Sacar logs
4. Leer el traceback real
5. Identificar causa
6. Corregir código/YAML/environment
7. Borrar deployment fallido si es necesario
8. Crear deployment de nuevo
```

Comando para logs:

```powershell
az ml online-deployment get-logs `
  --name blue `
  --endpoint-name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --lines 200
```

---

## 8. Flujo final que funcionó

Orden final correcto:

```text
1. Terraform apply AML infra
2. Crear Azure ML environment
3. Ejecutar training job
4. Ver métricas MLflow
5. Registrar modelo iris-classifier:1
6. Crear endpoint ep-iris-classifier-dev
7. Crear deployment blue con sklearn-mlflow:2
8. Invocar endpoint con request.json
9. Recibir {"predictions": [0]}
10. Borrar endpoint para evitar coste
```

---

## 9. Limpieza de costes

Después de probar el endpoint, se debe borrar el endpoint online.

Comando:

```powershell
az ml online-endpoint delete `
  --name ep-iris-classifier-dev `
  --resource-group rg-azure-mlops-tarik2012-dev `
  --workspace-name mlw-azure-mlops-tarik2012-dev `
  --yes
```

Esto borra:

```text
Endpoint
Deployment blue
Instancia online Standard_DS2_v2
```

No borra:

```text
Azure ML Workspace
Compute Cluster
Model Registry
MLflow runs
Storage Account
Terraform state
```

Nota:

```text
El Compute Cluster tiene min_nodes = 0, por lo que puede apagarse cuando no se usa.
```

---

## 10. Commit recomendado

Después de borrar el endpoint y comprobar que todo funciona:

```powershell
git status
git add src/inference/score_azureml.py tests/test_score_azureml.py
git commit -m "Fix Azure ML model artifact discovery"
```

También se puede añadir este documento:

```powershell
git add docs/2-azureml-mlflow-model-registry-endpoint-summary.md
git commit -m "Document Azure ML MLflow endpoint deployment"
```

---

## 11. Cómo explicarlo en entrevista en español

```text
En este proyecto construí un flujo MLOps completo con Azure ML. 
Primero provisioné la infraestructura con Terraform: Resource Group, Azure ML Workspace, Storage, Key Vault, Application Insights, ACR y Compute Cluster. 

Después ejecuté un training job en Azure ML usando un entorno reproducible con scikit-learn y MLflow. Durante el entrenamiento registré métricas como accuracy y f1_macro en MLflow, que quedaron almacenadas dentro del Azure ML Workspace.

Luego registré el modelo entrenado en Azure ML Model Registry como iris-classifier versión 1. 
Finalmente desplegué ese modelo en un Managed Online Endpoint usando un deployment blue, con un scoring script personalizado y un environment preparado para inferencia. 

También depuré errores reales de producción: permisos de Terraform remote state, problemas de empaquetado de código, cuota de compute, environment incompleto, deployments fallidos y paths de artefactos dentro de AZUREML_MODEL_DIR.
```

---

## 12. Cómo explicarlo en entrevista en inglés

```text
I built an end-to-end MLOps workflow using Azure Machine Learning. 
First, I provisioned the infrastructure with Terraform, including the Azure ML Workspace, Storage Account, Key Vault, Application Insights, Container Registry and Compute Cluster.

Then I submitted a training job to Azure ML using a reproducible environment with scikit-learn and MLflow. During training, I logged metrics such as accuracy and macro F1 score with MLflow. Those runs were stored in the Azure ML Workspace.

After training, I registered the trained model in Azure ML Model Registry as iris-classifier version 1. 
Finally, I deployed that registered model to a Managed Online Endpoint using a blue deployment, a custom scoring script and an inference environment.

I also troubleshooted real MLOps issues such as Terraform state permissions, Azure ML code packaging, compute quota limitations, missing inference dependencies, failed deployments and model artifact path resolution.
```

---

## 13. Preguntas de entrevista que ya puedo responder

### What is Azure ML Workspace?

```text
It is the central place where Azure ML stores experiments, jobs, MLflow runs, models, environments, endpoints and deployments.
```

### What is MLflow used for?

```text
MLflow is used to track experiments, metrics, parameters and artifacts. In Azure ML, MLflow runs are stored inside the Azure ML Workspace.
```

### What is Model Registry?

```text
Model Registry stores trained models with versions, so a specific model version can be deployed, promoted or rolled back.
```

### What is the difference between endpoint and deployment?

```text
The endpoint is the HTTPS entry point. The deployment is the actual model implementation running behind that endpoint.
```

### What is blue-green deployment?

```text
It is a deployment strategy where one version, for example blue, receives production traffic while another version can be prepared and tested before switching traffic.
```

### Why use Terraform?

```text
Terraform makes the infrastructure reproducible, version-controlled and easier to recreate across environments such as dev, staging and production.
```

---

## 14. Próximas etapas del proyecto

Siguiente etapa natural:

```text
GitHub Actions CI/CD for Azure ML
```

Objetivo:

```text
Push/manual workflow
→ Terraform apply Azure ML infra
→ Create/update Azure ML environment
→ Submit training job
→ Register model
→ Deploy endpoint
→ Smoke test prediction
```

Después:

```text
Observability
Model lifecycle
Blue-green deployment
Rollback
AKS/Kubernetes
Agentic AI in production
Databricks/Mosaic AI
```

Ruta completa pendiente:

```text
1. Automatizar Azure ML con GitHub Actions
2. Añadir observabilidad: logs, métricas, latencia, errores
3. Model lifecycle: versioning, staging, production, rollback
4. Kubernetes/AKS: pods, services, ingress, autoscaling
5. Agentes en producción: LangGraph, RAG, tools, tracing, monitoring
6. Databricks + Mosaic AI: MLflow, Unity Catalog, Model Serving, agents
```

---

## 15. Resumen final

Este módulo demuestra que sabemos hacer:

```text
Infrastructure as Code con Terraform
Azure ML Workspace
Training jobs en cloud
MLflow tracking
Model Registry
Managed Online Endpoint
Online inference
Debugging de deployments reales
Buenas prácticas de limpieza de costes
```

Frase clave:

```text
Terraform crea la plataforma.
Azure ML entrena y registra modelos.
Model Registry versiona los modelos.
Managed Online Endpoint sirve el modelo.
GitHub Actions automatizará el flujo.
```
