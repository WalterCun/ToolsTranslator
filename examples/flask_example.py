"""Flask integration example.

Uso:
    pip install flask toolstranslator
    python examples/flask_example.py

Endpoints:
    GET /translate/<key>?lang=es  → Traducción de una clave
    GET /languages                → Idiomas disponibles
"""

from flask import Flask, request, jsonify
from translator import Translator

app = Flask(__name__)
trans = Translator(lang="es", directory="./locales")


@app.route("/translate/<key>")
def get_translation(key: str):
    """Obtiene la traducción de una clave en el idioma solicitado."""
    lang = request.args.get("lang", "es")
    if lang != trans.lang:
        trans.change_lang(lang)
    value = trans.get(key, default="NOT_FOUND")
    return jsonify({"key": key, "value": value, "lang": lang})


@app.route("/languages")
def list_languages():
    """Lista los idiomas disponibles."""
    return jsonify(trans.available_languages())


if __name__ == "__main__":
    app.run(debug=True, port=8080)
