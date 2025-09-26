.PHONY: help install test run down clean check-deps check-docker check-python

# Detect docker compose command
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null)
ifndef DOCKER_COMPOSE
	DOCKER_COMPOSE := docker compose
endif

# Default target - shows help
help:
	@echo "Discutidor3000 API - Comandos disponibles de Make:"
	@echo ""
	@echo "  make help     - Muestra este mensaje de ayuda"
	@echo "  make install  - Instala todos los requisitos para ejecutar el servicio"
	@echo "  make test     - Ejecuta todas las pruebas con cobertura"
	@echo "  make run      - Ejecuta el servicio y todos los servicios relacionados en Docker"
	@echo "  make down     - Detiene todos los servicios en ejecución"
	@echo "  make clean    - Elimina todos los contenedores y redes"
	@echo ""

# Check if required tools are installed
check-deps: check-docker check-python
	@echo "✅ All dependencies are available"

check-docker:
	@command -v docker >/dev/null 2>&1 || { \
	    echo "❌ Docker No instalado.:"; \
	    echo "   Ubuntu/Debian: sudo apt-get install docker.io docker-compose-plugin"; \
	    echo "   Fedora: sudo dnf install docker docker-compose-plugin"; \
	    echo "   CentOS/RHEL: sudo yum install docker docker-compose"; \
	    echo "   Fedora: sudo dnf install docker docker-compose"; \
	    echo "   macOS: brew install docker docker-compose"; \
	    echo "   Windows: Download from https://docker.com/products/docker-desktop"; \
	    exit 1; \
	}
	@command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { \
	    echo "❌ Docker Compose no instalado"; \
	    echo "   Fedora: sudo dnf install docker-compose"; \
	    echo "   Ubuntu/Debian: sudo apt-get install docker-compose-plugin"; \
	    echo "   CentOS/RHEL: sudo yum install docker-compose"; \
	    echo "   Fedora: sudo dnf install docker-compose"; \
	    echo "   Or: pip install docker-compose"; \
	    echo "   Or use Docker Desktop which includes Compose"; \
	    exit 1; \
	}

check-python:
	@command -v python3 >/dev/null 2>&1 || { \
	    echo "❌ Python 3 no instalado. Por favor instala Python 3.8+:"; \
	    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"; \
	    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"; \
	    echo "   Fedora: sudo dnf install python3 python3-pip python3-virtualenv"; \
	    echo "   macOS: brew install python3"; \
	    echo "   Windows: Download from https://python.org/downloads/"; \
	    exit 1; \
	}

# Install all requirements
install: check-deps
	@echo "🔧 Instalando dependencias para Discutidor3000 API..."
	@if [ ! -f .env ]; then \
	    echo "📋 Creando .env desde template..."; \
	    cp .env-example .env; \
	    echo "⚠️  Por favor edita .env y configura OPENROUTER_API_KEY"; \
	fi
	@if [ ! -d "venv" ]; then \
	    echo "🐍 Creando entorno de Python..."; \
	    python3 -m venv venv; \
	fi
	@echo "📦 Instalando dependencias de Python..."
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "🐳 Montando servicios de Docker..."
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "✅ Instalación completada!"
	@echo ""
	@echo "📝 Siguientes pasos:"
	@echo "   1. Edita .el archivo .env y agrega tu OPENROUTER_API_KEY"
	@echo "   2. Ejecuta 'make run' para iniciar todos los servicios"

# Run all tests with coverage - ÚNICO COMANDO DE TESTING
test: check-deps
	@echo "🧪 Ejecutando suite completa de tests..."
	@if [ ! -d "venv" ]; then \
	    echo "❌ Entorno virtual no encontrado. Ejecuta 'make install' primero."; \
	    exit 1; \
	fi
	@echo "📊 Ejecutando tests con cobertura..."
	@. venv/bin/activate && python -m pytest tests/ -v --cov=api --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "✅ Tests completados!"
	@echo "📊 Reporte detallado de cobertura disponible en: htmlcov/index.html"
	@echo "🎯 Para ver el reporte: open htmlcov/index.html (macOS) o xdg-open htmlcov/index.html (Linux)"

# Run the service and all related services in Docker
run: check-deps
	@echo "🚀 Iniciando Discutidor3000 API y servicios relacionados..."
	@if [ ! -f .env ]; then \
	    echo "❌ Archivo .env no encontrado. Ejecuta 'make install' primero."; \
	    exit 1; \
	fi
	@if ! grep -q "OPENROUTER_API_KEY=" .env || grep -q "OPENROUTER_API_KEY=$$" .env; then \
	    echo "❌ OPENROUTER_API_KEY no configurado en .env. Por favor agrega tu API key."; \
	    exit 1; \
	fi
	@$(DOCKER_COMPOSE) up --build -d
	@echo "✅ Los servicios se están iniciando..."
	@echo "📡 API estará disponible en: http://localhost:8000"
	@echo "🔗 Redis estará disponible en: localhost:6379"
	@echo ""
	@echo "📊 Estado de servicios:"
	@$(DOCKER_COMPOSE) ps

# Teardown all running services
down:
	@echo "🛑 Deteniendo servicios..."
	@$(DOCKER_COMPOSE) down
	@echo "✅ Todos los servicios detenidos"

# Teardown and removal of all containers
clean:
	@echo "🧹 Limpiando todos los contenedores"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Limpieza completada"

# Default target
default: help