"""FastAPI integration example.

Uso:
    pip install fastapi uvicorn toolstranslator
    uvicorn examples.fastapi_example:app --reload

Endpoints:
    GET /translate/{key}?lang=es  → Traducción de una clave
    GET /languages                → Idiomas disponibles
    GET /metrics                  → Métricas internas del translator
"""

from fastapi import FastAPI, Query
from translator import Translator

app = FastAPI(title="ToolsTranslator API")
trans = Translator(lang="es", directory="./locales")


@app.get("/translate/{key}")
async def get_translation(key: str, lang: str = Query("es", description="Idioma destino")):
    """Obtiene la traducción de una clave."""
    if lang != trans.lang:
        trans.change_lang(lang)
    return {"key": key, "value": trans.get(key, default="NOT_FOUND"), "lang": lang}


@app.get("/languages")
async def list_languages():
    """Lista los idiomas disponibles."""
    return trans.available_languages()


@app.get("/metrics")
async def get_metrics():
    """Métricas internas del translator."""
    return trans.metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
