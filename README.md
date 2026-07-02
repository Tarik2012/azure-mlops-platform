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
