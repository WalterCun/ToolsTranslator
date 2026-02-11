# Uso

## Proxy básico
```python
from toolstranslator import Translator

translator = Translator(lang="es")
translator.translate("Hola", source="es", target="en")
```

## Idioma por defecto y cambio en caliente
```python
trans = Translator(lang="es", directory="./locales")
print(trans.lang)  # es

trans.lang = "en"        # recarga archivo en caliente
trans.change_lang("fr")  # alternativa explícita
```

Si el idioma solicitado no existe y hay idiomas disponibles, se lanza `LanguageNotAvailableError`.
Opcionalmente se puede configurar `fallback_lang`.

## Acceso dinámico por atributos (`__getattr__`)
```python
trans = Translator(lang="es", directory="./locales")

str(trans.hola)               # "mundo"
str(trans.bienvenida.usuario) # acceso anidado
```

## auto_add_missing_keys (crítico)
```python
trans = Translator(
    lang="es",
    directory="./locales",
    auto_add_missing_keys=True,
)

str(trans.dashboard.title)  # crea la clave faltante en disco
```

- Si `auto_add_missing_keys=True`: crea la clave faltante con `"TODO: agregar traducción"`.
- Si `False`: devuelve la clave como fallback y no escribe archivo.
- Se puede cambiar en caliente: `trans.auto_add_missing_keys = False`.

## Generación de idioma
```python
trans.generate_language_file(
    base_file="./locales/es.json",
    target_lang="en",
    output="./locales/en.json",
    source_lang="es",
    mark_pending=True,
)
```

## Traducción dinámica remota por valor
Puedes marcar un valor para traducirse bajo demanda:

```json
{
  "hero": {
    "title": {"__translate__": "Hola mundo", "source": "es", "target": "en"}
  }
}
```

Al resolver la clave, el SDK usa LibreTranslate y aplica fallback seguro.

## Conversión JSON↔YAML
> Requiere `toolstranslator[yml]`

```python
translator.convert_json_to_yaml("es.json", "es.yaml")
translator.convert_yaml_to_json("es.yaml", "es.json")
```


## Operación del servidor desde CLI
> Requiere `toolstranslator[server]`

```bash
toolstranslator install
toolstranslator doctor
toolstranslator status
```

`install` y `doctor` muestran progreso y recomendaciones accionables en consola.
