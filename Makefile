# Environment detection: respects activated VIRTUAL_ENV or defaults to .venv
VENV ?= $(if $(VIRTUAL_ENV),$(VIRTUAL_ENV),.venv)

ifeq ($(wildcard $(VENV)/bin/python3),)
    PYTHON ?= python3
    RUFF ?= ruff
    MYPY ?= mypy
    TOX ?= tox
else
    PYTHON ?= $(VENV)/bin/python3
    RUFF ?= $(VENV)/bin/ruff
    MYPY ?= $(VENV)/bin/mypy
    TOX ?= $(if $(wildcard $(VENV)/bin/tox),$(VENV)/bin/tox,tox)
endif

PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest

.PHONY: help install install-dev test lint format typecheck all build clean tox

help:
	@echo "Disponibili i seguenti comandi:"
	@echo "  install      : Installa le dipendenze di runtime"
	@echo "  install-dev  : Installa le dipendenze di sviluppo"
	@echo "  test         : Esegue i test con copertura"
	@echo "  lint         : Controlla lo stile del codice (Ruff check & format check)"
	@echo "  format       : Formatta il codice (Ruff format e autofix)"
	@echo "  typecheck    : Controlla i tipi statici (Mypy)"
	@echo "  tox          : Esegue i test su ambienti multipli isolati"
	@echo "  all          : Esegue format, lint, typecheck e test"
	@echo "  build        : Crea i file per la distribuzione (wheel/sdist)"
	@echo "  clean        : Rimuove file temporanei e cache"

install:
	$(PIP) install .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTEST) --cov=sbk --cov-report=term-missing tests/

lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

format:
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

typecheck:
	$(MYPY) src/sbk/

tox:
	$(TOX)

all: format lint typecheck test

build:
	$(PIP) install build
	$(PYTHON) -m build

clean:
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.pytest_cache')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.mypy_cache')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('.tox')]"
	$(PYTHON) -c "import pathlib, os; [os.remove(p) for p in pathlib.Path('.').rglob('.coverage')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('dist')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('build')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('*.egg-info')]"
