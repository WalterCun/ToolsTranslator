# Uso de ToolsTranslator

Esta guía cubre el uso básico y avanzado de la librería `ToolsTranslator` para gestionar traducciones en tus aplicaciones Python.

## Inicialización

Para comenzar, importa la clase `Translator` y crea una instancia. Puedes especificar el idioma inicial y el directorio donde se encuentran tus archivos de traducción.

```python
from translator import Translator

# Inicializa el traductor apuntando a tu directorio de locales
trans = Translator(
    lang="es",
    directory="./locales",
    auto_add_missing_keys=True  # Crea claves faltantes automáticamente en el archivo
)
```

## Acceso a Traducciones

Supongamos que tienes un archivo `locales/es.json` con el siguiente contenido:

```json
{
  "home": {
    "title": "Bienvenido",
    "button": "Entrar"
  }
}
```

Puedes acceder a las traducciones de dos formas:

### 1. Acceso por Atributos (Recomendado)

Esta forma es más legible y permite navegar por la estructura anidada del JSON como si fueran objetos Python.

```python
print(trans.home.title)  # Salida: Bienvenido
```

### 2. Acceso por Clave (Método `get`)

Útil cuando la clave es dinámica o contiene caracteres especiales.

```python
print(trans.get("home.button")) # Salida: Entrar
```

## Cambio de Idioma

Puedes cambiar el idioma activo en cualquier momento. Esto recargará las traducciones desde el archivo correspondiente.

```python
trans.change_lang("en")
# O mediante la propiedad
trans.lang = "fr"
```

## Manejo de Claves Faltantes

Si `auto_add_missing_keys=True`, al acceder a una clave que no existe en el archivo de idioma actual, `Translator` la añadirá automáticamente con un valor por defecto ("TODO: agregar traducción").

```python
print(trans.new.key) # Escribe "new.key" en el archivo y devuelve el placeholder
```

Esto es muy útil durante el desarrollo para identificar rápidamente qué textos faltan por traducir.

## Traducción en Tiempo Real (Proxy)

Si tienes configurado un servidor de traducción (ver [CLI](cli.md)), puedes traducir textos al vuelo utilizando el método `translate`.

```python
translated_text = trans.translate("Hola mundo", source="es", target="en")
print(translated_text) # Salida: Hello world
```

También puedes proporcionar una función de fallback en caso de que el servicio de traducción no esté disponible.

```python
translated = trans.translate(
    "Hola mundo",
    source="es",
    target="en",
    fallback=lambda text: f"[pending]{text}",
)
```
