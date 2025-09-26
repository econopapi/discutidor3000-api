# Discutidor3000 API

Una API HTTP que sirve un chatbot cuya única misión es defender, argumentar y discutir a favor de cualquier tema, por absurdo que sea, asignado por el usuario.

Desarrollada en FastAPI, con Redis como capa de datos y utilizando el modelo `DeepSeek-V3.1-Terminus` de DeepSeek, a través de OperRouter como proveedor.

## Características

- 🤖 **Chatbot argumentativo**: Defiende cualquier postura sin importar qué tan absurda sea
- 🔄 **Conversaciones persistentes**: Almacenamiento en Redis con TTL de 2 semanas
- 🚀 **API REST**: Endpoints HTTP para integración fácil
- 💬 **CLI interactivo**: Interfaz de línea de comandos para pruebas
- 🧪 **Testing completo**: Suite de tests unitarios y de integración con cobertura completa
- 📊 **Logging**: Sistema de logging detallado para debugging
- 🐳 **Containerización**: Despliegue completo con Docker y Docker Compose

## Quickstart


Lo primero es clonar el repositorio:
```bash
git clone https://github.com/econopapi/discutidor3000-api.git
cd discutidor3000-api
```

Luego, copia el archivo de ejemplo `.env-example` a `.env` y edítalo para agregar tu API key de DeepSeek y otras variables de entorno según sea necesario:
```bash
cp .env-example .env
# Editar .env y agregar variables de entorno
```

### Variables de Entorno
#### Variables requeridas

```bash
OPENROUTER_API_KEY=tu_api_key_aqui
```
- **Descripción**: API key de OpenRouter para acceso a los modelos de IA de DeepSeek
- **Requerido**: ✅ Sí
- **Obtención**: Regístrate en [OpenRouter](https://openrouter.ai/) y obtén tu API key

#### Cómo obtener una API Key de OpenRouter

1. Visita [https://openrouter.ai/](https://openrouter.ai/)
2. Crea una cuenta o inicia sesión
3. Ve a [Settings > API Keys](https://openrouter.ai/settings/preferences)
4. Genera una nueva API key
5. Copia la key y agrégala a tu archivo `.env`

#### Variables opcionales
```bash
REDIS_URL=redis://localhost:6379/0
```
- **Descripción**: URL de conexión a Redis para almacenamiento de conversaciones
- **Requerido**: ❌ No (usa valor por defecto)
- **Por defecto**: `redis://localhost:6379/0`
- **Uso**: Si tienes Redis en otro host/puerto o con autenticación


```bash
ROOT_PATH=/api/v1
```
- **Descripción**: Prefijo de ruta base para la API cuando se despliega detrás de un reverse proxy
- **Requerido**: ❌ No
- **Por defecto**: Sin prefijo (rutas directas)
- **Casos de uso**:
  - **Nginx/Apache**: Si tu API está en `https://midominio.com/api/v1/`
  - **API Gateway**: Para organizar múltiples servicios bajo rutas específicas
  - **Docker/Kubernetes**: En despliegues con ingress controllers

#### Ejemplo de ROOT_PATH:

**Sin ROOT_PATH** (desarrollo local):
```
http://localhost:8000/api/v1/chat
http://localhost:8000/API/V1/conversations
```

**Con ROOT_PATH=/discutidor** (producción):
```
https://miapp.com/discutidor/api/v1/chat
https://miapp.com/discutidor/api/v1/conversations
```

## Uso de Makefile
Este proyecto incluye un Makefile que automatiza todas las tareas de instalación, testing y despliegue:

Para ver los comandos disponibles y su descripción, simplemente ejecuta:
```bash
make
```

Instalar dependencias y configurar el entorno:
```bash
make install
```

Ejecutar la suite completa de tests:
```bash
make test
```

Ejecutar el servicio completo (API + Redis) en contenedores Docker:
```bash
make run
```

Detener todos los servicios:
```bash
make down
```

Limpiar todos los contenedores y volúmenes:
```bash
make clean
```

## Comandos del Makefile

| Comando | Descripción |
|---------|-------------|
| `make` o `make help` | Muestra lista de todos los comandos disponibles |
| `make install` | Instala todas las dependencias necesarias. Detecta herramientas faltantes y proporciona instrucciones |
| `make test` | Ejecuta toda la suite de tests |
| `make run` | Ejecuta el servicio y todas las dependencias en Docker |
| `make down` | Detiene todos los servicios en ejecución |
| `make clean` | Detiene y elimina todos los contenedores, redes y volúmenes |

## Instalación Manual (Alternativa)

Si prefieres no usar el Makefile, puedes seguir estos pasos:

### Prerrequisitos

- Python 3.8+
- Docker y Docker Compose
- Redis (para persistencia de conversaciones)
- API Key de DeepSeek

### Configuración

1. **Clonar el repositorio**
```bash
git clone https://github.com/econopapi/discutidor3000-api.git
cd discutidor3000-api
```

2. **Crear entorno virtual**
```bash
python3 -m venv venv # En Windows: python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env-example .env
# Editar .env y agregar tus variables de entorno
```

5. **Iniciar Redis**
```bash
docker-compose up -d redis
# O si tienes Redis instalado localmente: redis-server
```

## Uso

### Opción 1: Docker (Recomendado)

```bash
# Instalar y configurar todo automáticamente
make install

# Ejecutar el servicio completo
make run
```

La API estará disponible en `http://localhost:8000` y Redis en `localhost:6379`.

### Opción 2: Desarrollo Local

**Iniciar el servidor**
```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
uvicorn main:api --reload --host 0.0.0.0 --port 8000
```

**Endpoints disponibles:**

- `GET /` - Health check
- `POST /api/v1/chat` - Enviar mensaje al chatbot
- `GET /api/v1/conversations` - Listar todas las conversaciones

### CLI Interactivo

```bash
# Con entorno virtual activado
python cli.py

# O usando el contenedor
docker-compose exec api python cli.py
```

El CLI permite:
- Iniciar nuevas conversaciones con `/n`
- Salir con `/q`
- Conversación continua una vez establecida la postura

## API Reference

### POST /api/v1/chat

Envía un mensaje al chatbot. Si no se proporciona `conversation_id`, se inicia una nueva conversación.

**Request Body:**
```json
{
  "message": "Defiende que los gatos son mejores que los perros",
  "conversation_id": "opcional-uuid"
}
```

**Response:**
```json
{
  "conversation_id": "uuid-de-la-conversacion",
  "message": [
    {
      "role": "user",
      "content": "Mensaje del usuario"
    },
    {
      "role": "bot", 
      "content": "Respuesta del bot"
    }
  ]
}
```

### GET /api/v1/conversations

Obtiene un resumen de todas las conversaciones almacenadas.

**Response:**
```json
{
  "conversations": {
    "conversations": ["conversation:uuid1",
                      "conversation:uuid2"]
  }
}
```

## Estructura del Proyecto

```
discutidor3000-api/
├── api/
│   ├── endpoints/          # Endpoints de FastAPI
│   ├── services/           # Lógica backend
│   │   ├── discutidor3000.py  # Clase principal del chatbot
│   │   └── redis.py           # Servicio de Redis
│   └── structures/         # Modelos Pydantic
├── tests/                  # Tests unitarios
├── cli.py                  # Interfaz CLI
├── main.py                 # Aplicación FastAPI
├── Dockerfile             # Imagen Docker para la API
├── docker-compose.yml     # Orquestación de servicios
├── Makefile              # Automatización de tareas
├── requirements.txt      # Dependencias Python
└── README.md            # Esta documentación
```

## Testing

Ejecutar la suite completa de tests:

Usando el Makefile (recomendado):
```bash
make test
```
O directamente con pytest:
```bash
pytest -v --cov=api --cov-report=html
```
O usando unittest:
```bash
python -m unittest discover tests -v
```

### Cobertura de Testing

La suite de testing incluye **44 tests** organizados en 4 categorías con **97% de cobertura de código**:

#### 🧪 Tests Unitarios (25 tests)

**Discutidor3000 Service** (`test_discutidor3000.py`):
- ✅ Inicialización del chatbot (con/sin API key)
- ✅ Generación de prompts del sistema
- ✅ Comunicación con API de DeepSeek
- ✅ Extracción de posturas desde mensajes
- ✅ Inicialización y gestión de conversaciones
- ✅ Generación de respuestas del bot
- ✅ Formateo de respuestas
- ✅ Manejo de errores y excepciones personalizadas

**Redis Service** (`test_redis.py`):
- ✅ Operaciones CRUD de conversaciones
- ✅ Manejo de errores de conexión a Redis
- ✅ Serialización/deserialización de datos
- ✅ Gestión de TTL y expiración

#### 🌐 Tests de API (9 tests)

**Endpoints** (`test_endpoints.py`):
- ✅ Endpoint de health check (`/`)
- ✅ Endpoint de chat (`/chat`) con nuevas conversaciones
- ✅ Endpoint de chat con conversaciones existentes
- ✅ Endpoint de listado de conversaciones (`/conversations`)
- ✅ Manejo de errores HTTP (404, 500, 422)
- ✅ Validación de requests malformados

#### 🔗 Tests de Integración (3 tests)

**Flujos Completos** (`test_integration.py`):
- ✅ Flujo end-to-end de nueva conversación
- ✅ Flujo de continuación de conversación existente
- ✅ Manejo de errores en cadena

#### ⚙️ Configuración de Testing

**Fixtures Compartidas** (`conftest.py`):
- 🔧 Mocks reutilizables de Redis y servicios externos
- 🔧 Datos de prueba consistentes (conversaciones, mensajes)
- 🔧 Configuración de entorno de testing

### Reportes de Cobertura

Al ejecutar `make test` se generan automáticamente:

- **Reporte en terminal**: Muestra líneas no cubiertas
- **Reporte HTML**: Disponible en `htmlcov/index.html`

```bash
# Ver reporte HTML de cobertura
open htmlcov/index.html      # macOS
xdg-open htmlcov/index.html  # Linux
```

### Estructura de Tests

```
tests/
├── conftest.py              # Configuración y fixtures compartidas
├── test_discutidor3000.py   # Tests del servicio principal (17 tests)
├── test_redis.py            # Tests del servicio Redis (10 tests)
├── test_endpoints.py        # Tests de endpoints HTTP (9 tests)
└── test_integration.py      # Tests de integración (3 tests)
```

### Tecnologías de Testing

- **pytest**: Framework principal de testing
- **pytest-cov**: Generación de reportes de cobertura
- **unittest.mock**: Mocking de dependencias externas
- **FastAPI TestClient**: Testing de endpoints HTTP

Los tests cubren todos los casos críticos incluyendo:
- ✅ Casos exitosos (happy path)
- ✅ Manejo de errores y excepciones
- ✅ Validación de datos de entrada/salida
- ✅ Integración entre componentes
- ✅ Mocking de servicios externos (DeepSeek API, Redis)

## Configuración Avanzada

### Parámetros del Modelo

El chatbot usa los siguientes parámetros por defecto:
- **Modelo**: `deepseek/deepseek-v3.1-terminus` (a través de OpenRouter)
- **Temperatura**: `0.7`
- **Max tokens**: `3750`

### Configuración de Redis

Por defecto, Redis se configura con:
- **Puerto**: `6379`
- **TTL de conversaciones**: 2 semanas (1,120,000 segundos)
- **Persistencia**: Habilitada con appendonly

## Arquitectura

### Flujo de Nueva Conversación

1. Usuario envía mensaje inicial con la postura a defender
2. Sistema extrae la postura usando prompt especializado
3. Se genera prompt del sistema con la postura
4. Se inicializa conversación en Redis
5. Se genera primera respuesta del bot

### Flujo de Conversación Continua

1. Usuario envía mensaje a conversación existente
2. Sistema recupera historial de Redis
3. Se agrega mensaje del usuario al historial
4. Se genera respuesta usando todo el contexto
5. Se actualiza conversación en Redis

## Troubleshooting

### Problemas Comunes

**Error: "OPENROUTER_API_KEY not set"**
- Asegúrate de que el archivo `.env` existe y contiene `OPENROUTER_API_KEY=tu_api_key`

**Error: "Docker is not installed"**
- Instala Docker siguiendo las instrucciones que proporciona `make install`

**Error: "Connection refused" al conectar a Redis**
- Verifica que Redis esté ejecutándose: `docker-compose ps`
- Reinicia los servicios: `make down && make run`

**Tests fallan**
- Verifica que el entorno virtual esté activado
- Reinstala dependencias: `make install`

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Autor

- **Daniel Limón** - [GitHub](https://github.com/econopapi)