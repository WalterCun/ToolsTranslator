# Guía de Buenas Prácticas para Desarrollo

Este documento describe las buenas prácticas y estándares que deben seguirse al desarrollar y contribuir al código de este proyecto. Estas directrices aseguran la legibilidad, coherencia y calidad del código en todo momento, y ayudan a que el proyecto sea escalable y mantenible.

---

## 1. Configuración del Entorno de Desarrollo

Antes de comenzar, asegúrate de que tu entorno esté configurado correctamente:

### Requisitos:

- **Python 3.10 o superior**: Este proyecto utiliza características específicas de esta versión.
- **Editor recomendado**: [Visual Studio Code](https://code.visualstudio.com/) o [PyCharm](https://www.jetbrains.com/pycharm/).
- **Dependencias**: Instálalas ejecutando:
  ```bash
  pip install -r requirements.txt
  ```

### Formateador de Código:

Utilizamos **Black** como formateador principal. Instálalo con:

```bash
pip install black
```

Ejecuta Black para formatear tu código antes de enviarlo al repositorio:

```bash
black .
```

---

## 2. Estilo de Código

Siguiendo la convención PEP 8 para Python, estas son las principales reglas de estilo que deben cumplirse:

### Nombres de Variables y Funciones
- Utiliza **snake_case** para los nombres de variables y funciones.
- Ejemplo:
  ```python
  def traducir_archivo():
      ruta_archivo = "archivo.json"
  ```

### Clases:
- Utiliza **CamelCase** para nombres de clases.
- Ejemplo:
  ```python
  class TraductorDeArchivos:
      pass
  ```

### Líneas de Código:
- Limita las líneas de código a un máximo de **79 caracteres**.
- Si es necesario continuar en una nueva línea, usa sangría adecuada:
  ```python
  resultado = largo_funcion_ejemplo(
      param1, param2, param3, param4
  )
  ```

### Comentarios:
- Agrega comentarios claros y útiles para explicar la lógica cuando sea necesario.
- Utiliza comentarios tipo docstring para funciones y clases.
  ```python
  def traducir_texto(texto, idioma_destino):
      """
      Traduce un texto dado al idioma deseado.

      :param texto: El texto que se traducirá.
      :param idioma_destino: Código del idioma al que se traduce.
      :return: El texto traducido.
      """
      pass
  ```

---

## 3. Organización de Archivos y Módulos

Organiza el proyecto de acuerdo con la siguiente estructura:

```plaintext
 raíz/
 ├── core/                     # Contiene la lógica principal
 │   ├── translate.py          # Funciones relacionadas con la traducción
 │   ├── utils.py              # Funciones auxiliares
 │   └── ...
 ├── tests/                    # Pruebas unitarias y de integración
 ├── docs/                     # Documentación del proyecto
 ├── cli.py                    # Interfaz de línea de comandos
 ├── requirements.txt          # Dependencias del proyecto
 └── README.md                 # Guía del repositorio
```

### Las funciones y clases deben:

- Dividirse en módulos lógicos (por ejemplo, usa `utils.py` para funciones reutilizables).
- Evitar la duplicación de código.

---

## 4. Pruebas

### Requisitos de las Pruebas

- Todo nuevo código debe ser cubierto con **pruebas unitarias** y, si aplica, **pruebas de integración**.
- Las pruebas deben incluirse dentro del directorio `tests/`.

### Escribir Pruebas Unitarias

Utiliza **pytest** para las pruebas. Instálalo con:

```bash
pip install pytest
```

Ejemplo de prueba unitaria básica en `tests/test_translate.py`:

```python
from core.translate import traducir_texto

def test_traducir_texto():
    texto = "Hola, mundo"
    resultado = traducir_texto(texto, "en")
    assert resultado == "Hello, world"
```

### Ejecutar las Pruebas

Ejecuta todas las pruebas utilizando el siguiente comando:

```bash
pytest tests/
```

Antes de enviar un cambio al repositorio, asegúrate de que todas las pruebas pasen.

---

## 5. Control de Versiones

### Ramas y Pull Requests

- **Rama principal:** `main` o `master`.
- **Ramas de características:** Cada nueva funcionalidad debe desarrollarse en una rama separada. Por ejemplo:
  ```
  git checkout -b feature/nueva-funcionalidad
  ```
- Realiza Pull Requests (PR) para fusionar el código en `main`.

### Commits

Escribe mensajes de commit claros y descriptivos. Sigue las buenas prácticas como:

- **Formato:** `tipo: descripción breve del cambio`
    - **Tipos comunes**: `feat` (funcionalidad), `fix` (corrección), `docs` (documentación), `test` (pruebas), etc.
- **Ejemplo:**
  ```
  feat: añadir soporte para traducción al portugués
  fix: corregir errores en la API de traducción
  ```

---

## 6. Revisión de Código (Code Review)

Cuando crees un Pull Request:

1. Asegúrate de que las pruebas pasen y que el código esté formateado.
2. Haz que un miembro del equipo revise los cambios antes de fusionarlos.
3. Responde de manera proactiva a los comentarios en la revisión.

---

## 7. Prácticas Recomendadas

- **Escribe código reutilizable y modular.**
    - Cada función debe tener un propósito claro.
    - Evita escribir bloques de código muy largos: divídelos en funciones más pequeñas si es necesario.
- **Documenta tu código y funcionalidades.**
    - Esto asegurará que otros usuarios o tú mismo puedan entender el propósito y la lógica de tu contribución en el futuro.
- **Sé consistente con el estilo existente.**
    - Si el proyecto ya sigue un estilo particular, adáptate a él.

---

## 8. Herramientas Recomendadas

### Analizadores estáticos de código:

- **Flake8**: Para verificar errores comunes de estilo. Instálalo con:
  ```bash
  pip install flake8
  ```
  Usa:
  ```bash
  flake8 .
  ```

### Realización de pruebas y cobertura de código:

- **Coverage**: Para verificar qué porcentaje del código está cubierto por pruebas, instálalo con:
  ```bash
  pip install coverage
  ```
  Usa:
  ```bash
  coverage run -m pytest
  coverage report
  ```

---

## 9. Documentación

- Todo nuevo módulo o funcionalidad debe documentarse en la carpeta `docs/`.
- Agrega ejemplos para facilitar el entendimiento.
- Si introduces un cambio importante, actualiza el `README.md`.

---

## 10. Código Limpio

Recuerda: **¡El código debe ser legible tanto por humanos como por máquinas!**

1. Nombre las variables y funciones de forma descriptiva.
2. Evita duplicar código (usa funciones comunes).
3. Escribe pruebas unitarias para prevenir errores.

---

Gracias por seguir estas prácticas. ¡El mantenimiento y crecimiento del proyecto dependen de todos! 😊