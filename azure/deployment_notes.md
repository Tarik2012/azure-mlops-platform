# Deployment Notes

Base inicial para despliegue en Azure:

- Entrenamiento en Azure Machine Learning mediante `azure/aml_job.yml`.
- Imagen de inferencia construida con `Dockerfile`.
- Registro de contenedores previsto en Azure Container Registry.
- Despliegue previsto en Azure Container Apps o endpoint gestionado.
- Observabilidad prevista con Azure Monitor y Application Insights.
