# Deployment Notes

## Objetivo de esta practica

Esta practica prepara un despliegue real, pero controlado, de la API FastAPI Dockerizada en Azure Container Apps usando Azure Container Registry. La idea es aprender el flujo completo, probar la API y borrar todos los recursos al final.

## Recursos que se crean

- `Resource Group` (`rg-azure-mlops-platform-dev`)
- `Azure Container Registry` Basic (`acrazuremlopsplatform`)
- `Azure Container Apps Environment` (`cae-azure-mlops-platform-dev`)
- `Azure Container App` (`ca-azure-mlops-api-dev`)

## Para que sirve cada recurso

- `Resource Group`: agrupa todos los recursos de la practica para poder localizarlos y borrarlos juntos.
- `Azure Container Registry`: almacena la imagen Docker de la API en un registro privado de Azure.
- `Container Apps Environment`: proporciona el entorno administrado donde se ejecuta Container Apps.
- `Container App`: ejecuta la imagen de la API FastAPI con acceso HTTP publico.

## Flujo Docker -> ACR -> Container Apps

1. Construyes la imagen Docker localmente con `docker build`.
2. Haces login en Azure Container Registry.
3. Etiquetas la imagen local con el `loginServer` de ACR.
4. Haces `docker push` para subir la imagen al registro.
5. Creas el entorno de Azure Container Apps.
6. Creas la Container App apuntando a la imagen almacenada en ACR.
7. Obtienes la URL publica y validas que la API responda.

## Como probar la API desplegada

Cuando obtengas el FQDN publico de la Container App, usa `https://<FQDN>` como base URL.

- `GET /health`: valida que el servicio esta levantado.
- `GET /model-info`: devuelve metadatos del modelo cargado.
- `POST /predict`: ejecuta una prediccion con el payload JSON de inferencia.

Ejemplos:

```bash
curl https://<FQDN>/health
```

```bash
curl https://<FQDN>/model-info
```

```bash
curl -X POST https://<FQDN>/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

## Como borrar todo al final

Ejecuta el script:

```powershell
.\azure\delete_resources.ps1
```

Ese comando elimina el `Resource Group`, y con ello todos los recursos creados para la practica.

## Nota de seguridad y coste

No dejes recursos activos si no los estas usando. Aunque esta practica esta pensada para ser minima y temporal, ACR y Container Apps pueden generar coste mientras existan.
