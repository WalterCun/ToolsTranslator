# Arquitectura del Sistema

## Visión General

ToolsTranslator sigue una arquitectura modular con separación clara de responsabilidades.

```
translator/
├── core/           # Lógica principal del SDK
├── adapters/       # Backends de traducción (pluggable)
├── handlers/       # Lectura/escritura de archivos (JSON, YAML)
├── managers/       # Gestión de servicios externos (Docker)
├── cli/            # Interfaz de línea de comandos
├── utils/          # Utilidades (fileinfo, etc.)
├── config.py       # Configuración centralizada
└── exceptions.py   # Jerarquía de excepciones
```

## Componentes Principales

### Core (`translator/core/`)

**`Translator`** — Entrada principal del SDK. Responsabilidades:
- Cargar y cachear archivos de idioma
- Resolver claves por atributos (`trans.home.title`) o por puntos (`get("home.title")`)
- Delegar traducciones al adapter configurado
- Gestionar claves faltantes (auto-add, fallback, etc.)
- Thread-safe con `threading.RLock`

**`TranslationProxy`** — Proxy para acceso dinámico por atributos.
- Navega dicts anidados como `trans.section.subsection.key`
- Resuelve automáticamente `__translate__` dinámicos

**`AutoTranslate`** — Generación automática de archivos de idioma.
- Lee un archivo base y genera traducciones para múltiples idiomas
- Usa adapter de traducción (LibreTranslate u otro)

### Adapters (`translator/adapters/`)

**`TranslationAdapter`** (Protocol) — Contrato que debe cumplir cualquier backend:
```python
class TranslationAdapter(Protocol):
    def available(self) -> tuple[bool, str]: ...
    def translate(self, text: str, source: str, target: str) -> str: ...
```

**`LibreTranslateClient`** — Implementación por defecto:
- HTTP client para LibreTranslate API
- Cache TTL de 30s en `available()` (evita doble HTTP call)
- Retry con backoff en errores transitorios

**`HttpClient`** — Wrapper HTTP con stdlib:
- Retry automático (3 intentos, backoff exponencial)
- No reintenta errores 4xx del cliente (excepto 429)

### Handlers (`translator/handlers/`)

- **`JsonHandler`** — Lectura/escritura atómica de JSON
- **`YamlHandler`** — Lectura/escritura atómica de YAML (lazy import)
- **`io_handlers`** — Funciones compartidas: `read_mapping`, `write_mapping`, `flatten`, `unflatten`

### Managers (`translator/managers/`)

**`DockerManager`** — Gestión del ciclo de vida de LibreTranslate en Docker:
- Diagnóstico (estilo `flutter doctor`)
- Pull de imagen con retry
- Creación/arranque/parada de contenedor
- Healthcheck HTTP

## Flujo de Ejecución

### Inicialización

```
Translator.__init__()
  ├── Leer configuración (env vars)
  ├── Crear adapter (LibreTranslateClient o custom)
  ├── Crear directorio de locales si no existe
  └── Cargar archivo de idioma activo → _load_language(lang)
        ├── Buscar {lang}.json, {lang}.yaml, {lang}.yml
        ├── Si no existe → usar fallback_lang
        └── Cachear en _lang_cache
```

### Acceso a traducción

```
trans.get("home.title")
  ├── Verificar _resolved_cache → hit? retornar
  ├── Cargar datos del idioma (cacheado)
  ├── _deep_get(data, "home.title")
  ├── Si es None → manejar missing key
  ├── Si es dict con __translate__ → resolver dinámico
  ├── Si es dict → retornar TranslationProxy
  ├── Si es string → resolver dynamic value
  └── Guardar en cache y retornar
```

### Traducción directa

```
trans.translate("Hello", target="es")
  ├── Resolver idiomas source/target
  ├── adapter.available() → cache TTL 30s
  ├── adapter.translate(text, source, target)
  └── Retornar resultado o fallback
```

### Instalación automática

```
toolstranslator install
  ├── [1/5] Verificar Docker instalado
  ├── [2/5] Verificar Docker daemon activo
  ├── [3/5] Pull imagen LibreTranslate (con retry)
  ├── [4/5] Crear/arrancar contenedor
  └── [5/5] Healthcheck HTTP
```

## Jerarquía de Excepciones

```
ToolsTranslatorError (base del SDK)
├── ServiceUnavailableError     — Servicio de traducción caído
├── ExtraNotInstalledError      — Falta dependencia opcional
├── TranslationFileError        — Archivo corrupto o inaccesible
└── LanguageNotAvailableError   — Idioma no encontrado

AutoTranslateError (base de AutoTranslate)
├── ServerDependencyMissingError — Sin adapter ni servidor
└── LanguageDetectionError       — No se detectó idioma del archivo
```

## Patrones de Diseño

| Patrón | Uso |
|--------|-----|
| **Protocol** | `TranslationAdapter` define contrato sin herencia |
| **Proxy** | `TranslationProxy` para acceso dinámico por atributos |
| **Facade** | `Translator` encapsula handlers, cache, proxy, adapter |
| **Adapter** | `LibreTranslateClient` implementa traducción vía HTTP |
| **Cache TTL** | `available()` cachea resultado por 30 segundos |
| **Atomic Write** | Handlers escriben a temp file + rename |
