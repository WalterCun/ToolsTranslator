# Desarrollo

## Configuración del Entorno

```bash
# Clonar repositorio
git clone https://github.com/WalterCun/ToolsTranslator.git
cd ToolsTranslator

# Instalar en modo desarrollo con todas las dependencias
pip install -e ".[dev,yml,server]"
```

## Estructura del Proyecto

```
ToolsTranslator/
├── translator/              # Código fuente
│   ├── core/               # Translator, AutoTranslate
│   ├── adapters/           # TranslationAdapter, LibreTranslateClient, HttpClient
│   ├── handlers/           # JSON, YAML, io_handlers
│   ├── managers/           # DockerManager
│   ├── cli/                # CLI (Typer)
│   ├── utils/              # TranslateFile, helpers
│   ├── config.py           # Settings
│   └── exceptions.py       # Excepciones
├── tests/                   # Tests (pytest)
├── docs/                    # Documentación
├── examples/                # Ejemplos de uso
├── pyproject.toml           # Configuración del proyecto
└── pytest.ini               # Configuración de tests
```

## Testing

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Ejecutar un archivo específico

```bash
pytest tests/test_translator_init.py -v
```

### Con coverage

```bash
pip install pytest-cov
pytest tests/ --cov=translator --cov-report=term-missing
```

### Tests por categoría

```bash
# Unit tests
pytest tests/test_io_handlers.py tests/test_deep_ops.py tests/test_http_client.py -v

# Integration tests
pytest tests/test_integration.py tests/test_cache_and_dynamic.py -v

# Concurrency tests
pytest tests/test_concurrency.py -v
```

## Linting y Formato

### Ruff (linter + formatter)

```bash
pip install ruff

# Lint
ruff check translator/

# Format
ruff format translator/

# Fix automático
ruff check translator/ --fix
```

### Configuración de Ruff

Ver `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120
target-version = "py310"
```

## Type Checking

El proyecto usa type hints extensivamente. Para verificar:

```bash
pip install mypy
mypy translator/
```

## Flujo de Contribución

1. **Fork** el repositorio
2. **Crear rama** desde `dev`:
   ```bash
   git checkout dev
   git pull
   git checkout -b fix/mi-mejora
   ```
3. **Hacer cambios** con tests correspondientes
4. **Verificar**:
   ```bash
   pytest tests/ -v
   ruff check translator/
   ```
5. **Commitear** con mensaje descriptivo:
   ```bash
   git commit -m "feat: agregar soporte para X"
   ```
6. **Push y PR** hacia `dev`

### Convención de commits

| Prefijo | Uso |
|---------|-----|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `refactor:` | Refactorización sin cambio de comportamiento |
| `test:` | Agregar o modificar tests |
| `docs:` | Documentación |
| `perf:` | Mejora de rendimiento |

## Branching

```
main       ← Producción estable
├── dev    ← Desarrollo activo
├── preprod ← Pre-producción
├── qa      ← Quality assurance
└── fix/*   ← Ramas de trabajo
```

## Configuración del Editor

### VS Code

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

## Publicación (mantenedores)

```bash
# Build
python -m build

# Test en TestPyPI
python -m twine upload --repository testpypi dist/*

# Publicar en PyPI
python -m twine upload dist/*
```
