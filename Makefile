# Copyright 2025 Abdiel Lopez.
# SPDX-License-Identifier: BSL-1.0

.PHONY: run migrate shell superuser

# Variables con rutas absolutas
BASE_DIR = C:/Users/alguien/Desktop/crud-django
VENV_ACTIVATE = $(BASE_DIR)/env/Scripts/activate.bat
PYTHON = $(BASE_DIR)/env/Scripts/python.exe
MANAGE = $(PYTHON) manage.py

# Comando principal para ejecutar el servidor
run:
	@echo Activando entorno virtual y ejecutando servidor...
	@cmd /C "$(VENV_ACTIVATE) && cd $(BASE_DIR) && $(MANAGE) runserver"

# Comando para realizar migraciones
migrate:
	@echo Realizando migraciones...
	@cmd /C "$(VENV_ACTIVATE) && cd $(BASE_DIR) && $(MANAGE) makemigrations && $(MANAGE) migrate"

# Comando para abrir shell de Django
shell:
	@echo Abriendo shell de Django...
	@cmd /C "$(VENV_ACTIVATE) && cd $(BASE_DIR) && $(MANAGE) shell"

# Comando para crear superusuario
superuser:
	@echo Creando superusuario...
	@cmd /C "$(VENV_ACTIVATE) && cd $(BASE_DIR) && $(MANAGE) createsuperuser"

# Ayuda
help:
	@echo Comandos disponibles:
	@echo   make run        - Ejecuta el servidor de desarrollo
	@echo   make migrate    - Realiza las migraciones de la base de datos
	@echo   make shell     - Abre el shell de Django
	@echo   make superuser - Crea un superusuario

