#!/bin/bash
# Ejemplos de uso del CLI de ToolsTranslator
#
# Requisitos: pip install toolstranslator[server]

echo "=== Diagnóstico del entorno ==="
toolstranslator doctor

echo ""
echo "=== Instalación automática ==="
# toolstranslator install
echo "(Descomenta la línea anterior para ejecutar)"

echo ""
echo "=== Estado rápido ==="
toolstranslator status

echo ""
echo "=== Reiniciar servicio ==="
# toolstranslator restart
echo "(Descomenta la línea anterior para ejecutar)"

echo ""
echo "=== Eliminar contenedor ==="
# toolstranslator clean-server
echo "(Descomenta la línea anterior para ejecutar)"
