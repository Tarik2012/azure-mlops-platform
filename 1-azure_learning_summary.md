# Azure Services Summary

## 1. Resource Group

Un **Resource Group** sirve para agrupar todos los recursos de un proyecto en Azure.

Lo importante:

```text
Resource Group = organización + control + borrado conjunto
```

Permite tener los recursos del proyecto juntos y eliminarlos todos de una vez.

---

## 2. Azure Region

Una **Azure Region** es la ubicación física donde se crean los recursos.

Ejemplos:

```text
francecentral
westeurope
northeurope
eastus
```

Lo importante:

```text
Region = dónde vive físicamente tu infraestructura
```

No todos los servicios están disponibles siempre en todas las regiones.

---

## 3. Azure Resource Provider

Un **Resource Provider** es el proveedor interno de Azure que permite crear un tipo de recurso.

Ejemplos:

```text
Microsoft.ContainerRegistry
Microsoft.App
Microsoft.OperationalInsights
```

Lo importante:

```text
Resource Provider = módulo de Azure necesario para crear ciertos servicios
```

Si el provider no está registrado, Azure puede bloquear la creación del recurso.

---

## 4. Azure Container Registry

**Azure Container Registry**, o **ACR**, sirve para guardar imágenes Docker privadas en Azure.

Lo importante:

```text
ACR = repositorio privado de imágenes Docker
```

ACR no ejecuta la aplicación. Solo almacena imágenes como:

```text
mi-registry.azurecr.io/mi-api:v1
```

Flujo típico:

```text
docker build
docker tag
docker push
```

Después, otros servicios de Azure pueden descargar esa imagen para ejecutarla.

---

## 5. Azure Container Apps Environment

Un **Container Apps Environment** es el entorno donde viven las Azure Container Apps.

Lo importante:

```text
Container Apps Environment = capa de infraestructura para ejecutar Container Apps
```

No es la aplicación directamente.

Sirve para gestionar internamente:

```text
red
runtime
escalado
logs
configuración del entorno
```

Una o varias Container Apps pueden vivir dentro del mismo Environment.

---

## 6. Azure Container App

Una **Azure Container App** es la aplicación real ejecutándose en Azure desde una imagen Docker.

Lo importante:

```text
Container App = tu aplicación Docker corriendo en Azure
```

Ejemplos:

```text
API FastAPI
API Django
microservicio
worker
backend
```

La Container App descarga una imagen desde ACR y la ejecuta.

Configuraciones importantes:

```text
image
target port
ingress
cpu
memory
min replicas
max replicas
environment variables
```

---

## 7. Ingress

**Ingress** controla si una Container App es accesible desde fuera.

Tipos principales:

```text
external
internal
```

Lo importante:

```text
external ingress = API pública en internet
internal ingress = API privada dentro de Azure
```

Si activas `external`, Azure genera una URL HTTPS pública.

---

## 8. Managed Identity

Una **Managed Identity** es una identidad creada y gestionada por Azure.

Sirve para que un recurso de Azure pueda acceder a otro sin usar usuario y contraseña.

Lo importante:

```text
Managed Identity = identidad segura sin passwords
```

Ejemplo:

```text
Container App
→ usa Managed Identity
→ accede a Azure Container Registry
```

Es más seguro que guardar credenciales manuales.

---

## 9. AcrPull

**AcrPull** es un rol de Azure que permite leer imágenes desde Azure Container Registry.

Lo importante:

```text
AcrPull = permiso para descargar imágenes Docker desde ACR
```

Flujo típico:

```text
Managed Identity
→ tiene rol AcrPull
→ puede hacer pull desde ACR
→ Container App puede arrancar
```

Sin AcrPull, la Container App puede fallar porque no tiene permiso para descargar la imagen.

---

## 10. Role Assignment

Un **Role Assignment** sirve para asignar permisos a una identidad dentro de Azure.

Lo importante:

```text
Role Assignment = dar permisos a una identidad sobre un recurso
```

Ejemplo:

```text
Identidad: Managed Identity
Rol: AcrPull
Recurso: Azure Container Registry
```

Eso significa:

```text
Esta Managed Identity puede leer imágenes de este ACR.
```

---

## 11. Logs Destination

**Logs Destination** define dónde se envían los logs de una aplicación o entorno.

Ejemplos:

```text
Log Analytics
none
```

Lo importante:

```text
logs-destination = destino de los logs
```

En producción normalmente se usan logs.

En una práctica barata se puede usar:

```text
--logs-destination none
```

para evitar configurar monitorización avanzada.

---

## 12. Replicas

Las **replicas** son instancias de la aplicación corriendo.

Lo importante:

```text
replicas = número de copias activas de la app
```

Ejemplo:

```text
min replicas: 0
max replicas: 1
```

Significa:

```text
min replicas 0 = puede apagarse cuando no hay tráfico
max replicas 1 = como máximo una instancia
```

Esto ayuda a controlar costes.

---

## 13. CPU y Memory

Azure Container Apps permite definir cuánta CPU y memoria tendrá la aplicación.

Ejemplo:

```text
cpu: 0.25
memory: 0.5Gi
```

Lo importante:

```text
más CPU/memoria = más capacidad pero más coste
menos CPU/memoria = más barato pero menos potencia
```

Para pruebas pequeñas conviene usar valores bajos.

---

## 14. Azure CLI

**Azure CLI** es la herramienta de terminal para gestionar Azure con comandos.

Lo importante:

```text
az = comando principal de Azure CLI
```

Ejemplos:

```powershell
az group create
az acr create
az containerapp create
az group delete
```

Sirve para crear, consultar, modificar y borrar recursos de Azure desde terminal.

---

## 15. Idea principal

```text
Resource Group
→ agrupa todos los recursos.

Region
→ decide dónde se crean.

ACR
→ guarda imágenes Docker.

Container Apps Environment
→ entorno donde viven las apps.

Container App
→ aplicación Docker ejecutándose.

Ingress
→ expone la app al exterior o la deja privada.

Managed Identity
→ identidad segura sin contraseñas.

AcrPull
→ permiso para leer imágenes desde ACR.

Role Assignment
→ asigna permisos a una identidad.

Replicas / CPU / Memory
→ controlan escalado, capacidad y coste.

Azure CLI
→ permite gestionar Azure desde terminal.
```
