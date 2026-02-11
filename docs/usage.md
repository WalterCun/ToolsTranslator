# Uso

## Proxy
```python
from toolstranslator import Translator

translator = Translator()
translator.translate("Hola", source="es", target="en")
```

## Directorio de locales
```python
translator = Translator(directory="./locales")
translator.get("dashboard.title", lang="es")
```

## Generación de idioma
```python
translator.generate_language_file(
    base_file="./locales/es.json",
    target_lang="en",
    output="./locales/en.json",
    source_lang="es",
)
```

## Conversión JSON↔YAML
> Requiere `toolstranslator[yml]`

```python
translator.convert_json_to_yaml("es.json", "es.yaml")
translator.convert_yaml_to_json("es.yaml", "es.json")
```
