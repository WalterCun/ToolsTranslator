# Changelog

## 1.0.0 (2026-03-28)

Primera versión estable. API congelada.

- `Translator` — Entrada principal del SDK
- `TranslationAdapter` — Protocol para backends personalizados
- `AutoTranslate` — Generación masiva de archivos de idioma
- CLI completa (`doctor`, `install`, `status`, `restart`, `clean-server`, `translate`)
- 95+ tests pasando
- Documentación completa (README, docs/, examples/)

## 0.6.0

- Modo debug (`TOOLSTRANSLATOR_DEBUG=1`)
- Métricas internas (`trans.metrics`)
- Logging mejorado

## 0.5.0

- Lectura de archivos optimizada (1 dict lookup vs 3 exists checks)
- Cache de `available_languages()` con invalidación automática
- Traducción batch con `ThreadPoolExecutor` en AutoTranslate

## 0.4.0

- `FallbackAdapter` — Encadena múltiples adapters con fallback automático
- `CachedAdapter` — Decorator con cache TTL por traducción

## 0.3.0

- Cache LRU acotada para archivos de idioma (max 50)
- CLI: comando `toolstranslator translate "texto" --to en`
- `Translator`: `__contains__`, `__iter__`, `__len__`
- `DockerManager.stop_container()` — Detener sin eliminar
- Cache invalidation al cambiar de idioma
- Cache de `available_languages()` con `.yml` incluido

## 0.2.0

- `TranslationAdapter` Protocol para backends custom
- Inyección de adapter en `Translator`
- Retry con backoff en `HttpClient`
- Cache TTL para verificación de servidor (30s)
- Suite completa de tests (95 tests)
- Documentación completa

## 0.1.0

- Versión inicial
- Gestión de archivos JSON/YAML
- Acceso dinámico por atributos
- Traducción con LibreTranslate
- CLI básico (doctor, install, status)
