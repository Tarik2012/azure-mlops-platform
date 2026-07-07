# mlops-azure-fastapi-demo

Proyecto base para construir una plataforma MLOps end-to-end en Azure con Python, scikit-learn, FastAPI, Docker, MLflow, Azure Machine Learning y despliegue automatizado con GitHub Actions.

## Local training

Activa el entorno virtual en PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Ejecuta el entrenamiento local:

```powershell
python -m src.training.train
```

El entrenamiento genera estos artefactos:

- `models/iris_model.joblib`
- `mlflow.db`

En este proyecto, MLflow se usa para:

- tracking de experimentos
- registro de metricas
- registro de parametros
- almacenamiento de artifacts

MLflow usa SQLite local para el tracking de experimentos en `mlflow.db`. Mas adelante, este tracking se conectara con Azure Machine Learning Tracking.
## Run local pipeline

Run the full local MLOps flow, including data ingestion, profiling, validation, preprocessing, and model training, with:

```bash
python scripts/run_local_pipeline.py
```

## Run API locally

First ensure the trained model exists:

```powershell
.\venv\Scripts\python.exe scripts/run_local_pipeline.py
```

Start the API locally:

```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.main:app --reload
```

Open Swagger UI:

`http://127.0.0.1:8000/docs`

Example JSON for `/predict`:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

## Run with Docker

Build the image:

```powershell
docker build -t azure-mlops-platform-api .
```

Run the container:

```powershell
docker run -p 8000:8000 azure-mlops-platform-api
```

Open Swagger UI:

`http://127.0.0.1:8000/docs`

## Azure deployment practice

The Azure deployment flow is prepared in `azure/deploy_container_app.ps1` and `azure/deployment_notes.md`, but it is not executed automatically.

This practice creates temporary Azure resources for learning purposes and they should be deleted at the end of the exercise.

Delete script:

```powershell
.\azure\delete_resources.ps1
```

## Azure CI/CD flow

The repository now separates Azure deployment into three Terraform stacks:

- `infra/terraform/bootstrap`
- `infra/terraform/platform`
- `infra/terraform/app`

GitHub Actions is set up for:

- CI on `push` and `pull_request`
- manual Azure deployment with GitHub OIDC in `.github/workflows/deploy-azure.yml`

The intended Azure flow is:

1. Bootstrap the Terraform remote state backend
2. Configure GitHub OIDC and repository variables
3. Apply the platform stack
4. Build and push the API image to ACR
5. Apply the app stack
6. Smoke test `/health`, `/model-info`, and `/predict`

More detail is documented in [infra/terraform/README.md](</C:/Users/erroc/Projects/mlops-azure-fastapi-demo/infra/terraform/README.md>).
