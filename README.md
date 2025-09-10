# Discutidor3000 API

Una API HTTP que sirve un chatbot cuya única misión es defender, argumentar y discutir a favor de cualquier tema, por absurdo que sea, asignado por el usuario.

Desarrollada en FastAPI y utilizando el modelo `DeepSeek-V3.1 (Non-thinking Mode)` de DeepSeek.

## Características

- 🤖 **Chatbot argumentativo**: Defiende cualquier postura sin importar qué tan absurda sea
- 🔄 **Conversaciones persistentes**: Almacenamiento en Redis con TTL de 2 semanas
- 🚀 **API REST**: Endpoints HTTP para integración fácil
- 💬 **CLI interactivo**: Interfaz de línea de comandos para pruebas
- 🧪 **Testing completo**: Suite de tests unitarios con cobertura amplia
- 📊 **Logging**: Sistema de logging detallado para debugging

## Instalación

### Prerrequisitos

- Python 3.8+
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
# Editar .env y agregar tu DEEPSEEK_API_KEY y, opcionalmente
# REDIS_URL si no usas la configuración por defecto
```

5. **Iniciar Redis**
```bash
docker-compose up -d redis
# O si tienes Redis instalado localmente: redis-server
```

## Uso

### API HTTP

**Iniciar el servidor**
```bash
uvicorn main:api --reload --host 0.0.0.0 --port 8000
```

**Endpoints disponibles:**

- `GET /` - Health check
- `POST /api/v1/chat` - Enviar mensaje al chatbot
- `GET /api/v1/conversations` - Listar todas las conversaciones

### CLI Interactivo

```bash
python cli.py
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
├── requirements.txt        # Dependencias Python
└── docker-compose.yml      # Configuración Redis
```

## Testing

Ejecutar la suite completa de tests:

```bash
# Desde la raíz del proyecto, con el entorno virtual activado
pytest -v
```

O usando unittest:
```bash
python -m unittest discover tests -v
```

Los tests cubren:
- Inicialización del chatbot
- Generación de prompts del sistema
- Comunicación con API de DeepSeek
- Extracción de posturas
- Gestión de conversaciones
- Formateo de respuestas

## Configuración Avanzada

### Variables de Entorno

- `DEEPSEEK_API_KEY`: API key de DeepSeek (requerida)
- `REDIS_URL`: URL de conexión a Redis (default: `redis://localhost:6379/0`)

### Parámetros del Modelo

El chatbot usa los siguientes parámetros por defecto:
- **Modelo**: `deepseek-chat`
- **Temperatura**: `0.7`
- **Max tokens**: `3750`

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

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Autor

- **Daniel Limón** - [GitHub](https://github.com/econopapi)