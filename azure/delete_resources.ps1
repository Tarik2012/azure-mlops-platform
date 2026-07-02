# Este comando borra todos los recursos creados para la practica.

$RESOURCE_GROUP = "rg-azure-mlops-platform-dev"

az group delete --name $RESOURCE_GROUP --yes --no-wait
