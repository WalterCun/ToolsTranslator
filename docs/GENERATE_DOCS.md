# Generar Documentación

Este proyecto mantiene documentación en formato Markdown bajo la carpeta docs/. La referencia de API se basa en las docstrings incluidas en el código fuente.

Flujo recomendado

1) Actualiza las docstrings en el código fuente
   - Asegúrate de que las clases y funciones públicas tengan docstrings claras en español.
2) Actualiza manualmente los archivos Markdown
   - docs/USAGE.md: guía de inicio rápido y ejemplos
   - docs/API_REFERENCE.md: resumen de la API pública
   - docs/HOWTO_DOCKER.md: guía para el servicio LibreTranslate via Docker
3) Verifica ejemplos ejecutables en examples/
   - Los scripts .py deben poder ejecutarse sin modificaciones adicionales, asumiendo que LibreTranslate está disponible.

Opción avanzada (pdoc)

Si deseas generar una referencia automática desde docstrings, puedes usar pdoc (opcional, no requerido por el proyecto):

```powershell
pip install pdoc
pdoc translator -o site
start .\site\index.html
```

Nota: pdoc no forma parte de las dependencias del paquete. Úsalo solo si lo necesitas para publicar documentación HTML a partir de docstrings. Este repositorio prioriza los archivos Markdown en docs/.  
