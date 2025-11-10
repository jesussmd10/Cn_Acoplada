# Proyecto Pokémon API (Acoplada)

Este proyecto implementa una API RESTful para gestionar Pokémon, utilizando Flask como framework web, DynamoDB como base de datos y desplegándose en AWS ECS Fargate con API Gateway. Incluye un frontend básico en HTML/JavaScript para probar la API.

## Estructura del Proyecto

```
.
├── db_dynamodb.yml         # Plantilla CloudFormation para la tabla DynamoDB
├── Dockerfile              # Dockerfile para construir la imagen de la aplicación
├── ecr.yml                 # Plantilla CloudFormation para el repositorio ECR
├── frontend.html           # Frontend HTML/JavaScript para probar la API
├── main.yml                # Plantilla CloudFormation principal para el despliegue en ECS/API Gateway
├── requirements.txt        # Dependencias de Python
└── app/
    ├── main.py             # Aplicación Flask principal con los endpoints de la API
    ├── db/
    │   ├── db.py           # Interfaz abstracta para la base de datos
    │   ├── dynamodb_db.py  # Implementación de la base de datos para DynamoDB
    │   └── factory.py      # Fábrica para obtener la instancia de la base de datos
    └── model/
        └── pokemon.py      # Modelos de datos Pydantic para Pokémon
```

## Componentes Principales

### Backend (Python/Flask)

La API está construida con Flask y sigue una arquitectura modular:

*   **`app/main.py`**:
    *   Define los endpoints REST para las operaciones CRUD de Pokémon:
        *   `POST /pokemon`: Crea un nuevo Pokémon.
        *   `GET /pokemon/<int:id>`: Obtiene un Pokémon por su ID.
        *   `GET /pokemon`: Obtiene todos los Pokémon.
        *   `PUT /pokemon/<int:id>`: Actualiza un Pokémon existente.
        *   `DELETE /pokemon/<int:id>`: Elimina un Pokémon por su ID.
    *   Incluye manejo de CORS para permitir solicitudes desde el frontend.
    *   Un endpoint `/health` para verificaciones de salud.
    *   Utiliza `gunicorn` para servir la aplicación en producción.

*   **`app/db/`**:
    *   **`db.py`**: Define la interfaz `DBInterface` con métodos abstractos para las operaciones de base de datos.
    *   **`dynamodb_db.py`**: Implementa `DBInterface` para interactuar con Amazon DynamoDB. Espera la variable de entorno `DYNAMODB_TABLE` para el nombre de la tabla.
    *   **`factory.py`**: Proporciona una función `get_db()` que devuelve una instancia de la base de datos configurada (actualmente solo DynamoDB, basada en la variable de entorno `DB_TYPE`).

*   **`app/model/pokemon.py`**:
    *   Define los modelos de datos `Pokemon` y `PokemonUpdate` utilizando Pydantic para la validación de datos. `pokedex_id` es la clave principal.

*   **`requirements.txt`**:
    *   Lista las dependencias de Python necesarias: `flask`, `boto3`, `pydantic`, `python-dotenv`, `psycopg2-binary` (aunque no se usa Postgres en esta versión, está listado), y `gunicorn`.

### Frontend (HTML/JavaScript)

*   **`frontend.html`**:
    *   Una página web simple que permite interactuar con la API de Pokémon.
    *   Proporciona formularios para realizar operaciones de Crear, Leer (uno y todos), Actualizar y Eliminar.
    *   Requiere la URL del API Gateway y una API Key para funcionar.

### Infraestructura como Código (AWS CloudFormation)

El despliegue de la infraestructura se gestiona mediante plantillas de AWS CloudFormation.

*   **`db_dynamodb.yml`**:
    *   Crea una tabla de DynamoDB (`PokemonPokedexTable` por defecto) con `pokedex_id` como clave primaria de tipo `Number`.

*   **`ecr.yml`**:
    *   Crea un repositorio de Amazon ECR (`pokedex-api` por defecto) para almacenar la imagen Docker de la aplicación.
    *   Configura una política de ciclo de vida para mantener solo las últimas 2 imágenes.

*   **`main.yml`**:
    *   La plantilla principal que orquesta el despliegue completo en AWS.
    *   **Parámetros**: Permite configurar el nombre de la imagen Docker, la VPC, las subredes, el tipo de base de datos (DynamoDB por defecto), y detalles de la tabla DynamoDB.
    *   **Recursos de Red**:
        *   `ECSSecurityGroup`: Grupo de seguridad para las tareas de ECS, permitiendo tráfico en el puerto 8080.
        *   `NLB` (Network Load Balancer): Balanceador de carga interno para distribuir el tráfico a las tareas de ECS.
        *   `TargetGroup`: Grupo de destino para el NLB, con chequeos de salud en `/health`.
        *   `Listener`: Escucha en el puerto 8080 del NLB y reenvía al `TargetGroup`.
    *   **Recursos de ECS**:
        *   `ECSCluster`: Un clúster ECS llamado `pokedex-cluster`.
        *   `TaskDefinition`: Define la tarea de Fargate con 256 CPU y 512 MB de memoria. Configura el contenedor `pokedex-container` con la imagen ECR y mapea el puerto 8080. Pasa variables de entorno para la configuración de la base de datos.
        *   `ECSService`: Despliega una instancia de la tarea en el clúster ECS, asociada al NLB.
    *   **Recursos de API Gateway**:
        *   `VPCLink`: Un VPC Link para integrar API Gateway con el NLB interno.
        *   `RestAPI`: La API REST de API Gateway (`pokedex-api`).
        *   `PokemonResource` y `PokemonIdResource`: Recursos para las rutas `/pokemon` y `/pokemon/{id}`.
        *   `PostPokemonMethod`, `GetAllPokemonMethod`, `GetPokemonMethod`, `PutPokemonMethod`, `DeletePokemonMethod`: Métodos HTTP para cada endpoint, configurados como integraciones `HTTP_PROXY` con el VPC Link. Requieren una API Key.
        *   `OptionsPokemonMethod` y `OptionsPokemonIdMethod`: Métodos `OPTIONS` para manejar las solicitudes de pre-vuelo de CORS.
        *   `APIDeployment` y `APIStage`: Despliegue y etapa (`prod`) de la API.
        *   `APIKey` y `UsagePlan`: Configuración de una API Key y un plan de uso para asegurar la API.
    *   **Salidas (Outputs)**: Proporciona la URL del API Gateway y el ID de la API Key.

### Docker

*   **`Dockerfile`**:
    *   Utiliza una imagen base `python:3.11-slim`.
    *   Copia `requirements.txt` e instala las dependencias.
    *   Copia el código de la aplicación.
    *   Expone el puerto 8080.
    *   El comando `CMD` inicia la aplicación Flask usando `gunicorn` en el puerto 8080.

## Despliegue en AWS

Para desplegar este proyecto en AWS, necesitarás:

1.  **Crear el repositorio ECR**:
    Sube el archivo `ecr.yml` a AWS CloudFormation para crear el repositorio ECR.
    Una vez creado el stack, obtén el `RepositoryUri` de las salidas.

2.  **Construir y subir la imagen Docker**:
    ```bash
    docker build -t pokedex-api .
    docker tag pokedex-api:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/pokedex-api:latest
    aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
    docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/pokedex-api:latest
    ```
    Reemplaza `<ACCOUNT_ID>` y `<REGION>` con tus valores.

3.  **Crear la tabla DynamoDB**:
    Sube el archivo `db_dynamodb.yml` a AWS CloudFormation para crear la tabla DynamoDB.
    Una vez creado el stack, obtén el `TableName` de las salidas.

4.  **Desplegar la API y ECS**:
    Sube el archivo `main.yml` a AWS CloudFormation para desplegar la API y los recursos de ECS.
    Asegúrate de proporcionar los siguientes parámetros:
    *   `ImageName`: `pokedex-api:latest` (o el nombre de tu imagen)
    *   `VpcId`: El ID de tu VPC.
    *   `SubnetIds`: Una lista de al menos dos IDs de subred (preferiblemente privadas).
    *   `DBType`: `dynamodb`
    *   `DBDynamoName`: El nombre de tu tabla DynamoDB (obtenido del paso 3).
    *   `VpcCidr`: El CIDR de tu VPC.

## Uso del Frontend

Una vez desplegada la API:

1.  Abre `frontend.html` en tu navegador.
2.  En la sección "Configuración de la API", introduce la `API Endpoint URL` y la `API Key` obtenidas de las salidas del stack `pokedex-api-ecs-stack`.
3.  Utiliza los formularios para interactuar con la API (Crear, Obtener, Actualizar, Eliminar Pokémon).

## Variables de Entorno

La aplicación Flask utiliza las siguientes variables de entorno para la configuración de la base de datos:

*   `DB_TYPE`: Tipo de base de datos a usar (actualmente solo `dynamodb`).
*   `DYNAMODB_TABLE`: Nombre de la tabla DynamoDB.

## Consideraciones de Seguridad

*   La API Gateway está configurada para requerir una API Key. Asegúrate de proteger esta clave.
*   Los métodos `OPTIONS` para CORS no requieren API Key, lo cual es estándar para las solicitudes de pre-vuelo.
*   El `TaskRoleArn` y `ExecutionRoleArn` en la `TaskDefinition` asumen un rol `LabRole`. En un entorno de producción, se recomienda crear roles IAM con permisos mínimos necesarios.
