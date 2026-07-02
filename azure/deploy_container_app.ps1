# Este script crea recursos Azure que pueden generar coste. Ejecutar solo si se entiende y borrar despues.

# Variables base para la practica controlada.
$RESOURCE_GROUP = "rg-azure-mlops-platform-dev"
$LOCATION = "westeurope"
$ACR_NAME = "acrazuremlopsplatform"
$IMAGE_NAME = "azure-mlops-platform-api"
$IMAGE_TAG = "v1"
$CONTAINER_APP_ENV = "cae-azure-mlops-platform-dev"
$CONTAINER_APP_NAME = "ca-azure-mlops-api-dev"

# 1. Verificar la cuenta activa antes de crear recursos.
az account show --output table

# 2. Crear el resource group donde quedaran agrupados todos los recursos temporales.
az group create --name $RESOURCE_GROUP --location $LOCATION

# 3. Crear un Azure Container Registry en SKU Basic y habilitar el usuario admin para la practica.
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# 4. Hacer login en ACR para poder subir la imagen Docker.
az acr login --name $ACR_NAME

# 5. Construir la imagen local de la API FastAPI desde la raiz del repositorio.
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# 6. Obtener el login server de ACR para usarlo en el tag y en el despliegue.
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv

# 7. Reetiquetar la imagen local con el nombre completo del registro Azure.
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}

# 8. Subir la imagen al Azure Container Registry.
docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}

# 9. Crear el entorno de Azure Container Apps donde vivira la aplicacion.
az containerapp env create --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP --location $LOCATION

# 10. Crear la Container App publica apuntando a la imagen subida en ACR.
# Nota: si Azure pide credenciales explicitas del registro, anade --registry-username y --registry-password.
az containerapp create `
  --name $CONTAINER_APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $CONTAINER_APP_ENV `
  --image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} `
  --target-port 8000 `
  --ingress external `
  --registry-server $ACR_LOGIN_SERVER `
  --min-replicas 0 `
  --max-replicas 1 `
  --cpu 0.25 `
  --memory 0.5Gi

# 11. Obtener el FQDN publico asignado a la Container App.
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv

# 12. Seguir los logs de la aplicacion desplegada para validar arranque y peticiones.
az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow
