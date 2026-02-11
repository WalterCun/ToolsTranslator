# Visión General

ToolsTranslator es una librería diseñada para simplificar la gestión de traducciones en aplicaciones Python. Su objetivo principal es proporcionar una interfaz unificada para acceder a textos localizados, gestionar archivos de idioma y, opcionalmente, automatizar la traducción de contenidos mediante servicios externos como LibreTranslate.

## Problema que resuelve

En el desarrollo de aplicaciones multilingües, a menudo nos encontramos con desafíos como:

- **Gestión manual de archivos**: Mantener sincronizados múltiples archivos JSON/YAML para diferentes idiomas es propenso a errores.
- **Acceso verboso**: Acceder a claves anidadas (`data["home"]["title"]`) puede ensuciar el código.
- **Falta de automatización**: Agregar un nuevo idioma suele requerir copiar y traducir manualmente cada clave.
- **Dependencias complejas**: Integrar servicios de traducción automática a menudo implica configurar APIs y manejar errores de red.

## Solución propuesta

ToolsTranslator aborda estos problemas mediante:

1.  **Acceso intuitivo**: Uso de atributos (`trans.home.title`) para acceder a las traducciones, mejorando la legibilidad del código.
2.  **Gestión automática de claves**: Capacidad de detectar y agregar claves faltantes en los archivos de idioma durante el desarrollo.
3.  **Soporte multiprotocolo**: Compatibilidad nativa con archivos JSON y YAML.
4.  **Integración con LibreTranslate**: Herramientas integradas para levantar un servidor de traducción local (vía Docker) y utilizarlo para generar traducciones automáticamente.

## Casos de uso principales

### 1. Desarrollo de aplicaciones

El desarrollador utiliza `Translator` en su código para acceder a los textos. Si necesita un nuevo texto, simplemente lo escribe en el código (`trans.nueva.clave`) y la librería se encarga de añadirlo al archivo de idioma base, listo para ser traducido.

### 2. Generación de nuevos idiomas

Cuando se desea soportar un nuevo idioma (ej. Francés), se puede utilizar la funcionalidad de `AutoTranslate` para generar un archivo `fr.json` basado en el archivo `es.json` existente, traduciendo automáticamente los valores utilizando el servidor local.

### 3. Entorno de traducción local

Para equipos que requieren privacidad o no dependen de APIs externas costosas, el CLI de ToolsTranslator permite desplegar y gestionar una instancia de LibreTranslate en Docker con un solo comando.
