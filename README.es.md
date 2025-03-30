# Reddit Content API - Configuración y Uso

[![Estrellas en GitHub](https://img.shields.io/github/stars/jlcases/mcp-reddit?style=social)](https://github.com/jlcases/mcp-reddit/stargazers)
[![Forks en GitHub](https://img.shields.io/github/forks/jlcases/mcp-reddit?style=social)](https://github.com/jlcases/mcp-reddit/network/members)

Este proyecto proporciona herramientas MCP (Model Context Protocol) para interactuar con Reddit a través de Claude y Cursor.

## Características

- Lectura de posts populares de subreddits
- Análisis de discusiones de Reddit con sus comentarios
- Creación de posts en Reddit
- Adición de comentarios a posts o respuestas a comentarios
- Votación en posts y comentarios

## Requisitos

- Python 3.10+
- Una cuenta de Reddit
- Una aplicación de Reddit registrada (para obtener client_id y client_secret)
- Entorno virtual (venv o similar)
- Claude Desktop y/o Cursor (opcional pero recomendado)

## Instalación desde cero

Siga estos pasos cuidadosamente para evitar problemas de importación y configuración:

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/mcp-reddit.git
cd mcp-reddit

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar las dependencias (SIN instalar el paquete en modo editable)
pip install -r requirements.txt

# 4. Configurar las variables de entorno (ver más abajo)
# Crear y editar el archivo .env
```

> ⚠️ **IMPORTANTE**: NO instalar el paquete en modo editable (`pip install -e .`) 
> ya que puede causar problemas con la importación de módulos.

## Configuración del entorno

1. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_REFRESH_TOKEN=tu_refresh_token
```

2. Para obtener un refresh token, ejecutar:

```bash
python -m mcp_reddit.auth_helper
```

Sigue las instrucciones para autorizar la aplicación. El token obtenido se guardará automáticamente en el archivo `.env`.

## Estructura del proyecto

```
mcp-reddit/
│
├── src/
│   └── mcp_reddit/
│       ├── __init__.py
│       ├── main.py           # Punto de entrada para el servidor MCP
│       ├── reddit_fetcher.py # Implementación de herramientas de Reddit
│       └── auth_helper.py    # Ayudante para generar tokens de autenticación
│
├── .env                      # Variables de entorno (crear manualmente)
├── requirements.txt
├── setup.py
└── README.md
```

## Ejecución del servidor directamente

Para ejecutar manualmente (útil para desarrollo y pruebas):

```bash
cd /ruta/a/mcp-reddit
.venv/bin/python src/mcp_reddit/main.py
```

Deberías ver logs indicando:
- La inicialización del servidor
- Verificación de autenticación de Reddit
- Registro de las 10 herramientas (5 originales + 5 con prefijo)
- "Running MCP server..."

## Configuración de Claude Desktop

1. Localiza el archivo de configuración:
   - En macOS: `/Users/tu-usuario/Library/Application Support/Claude/claude_desktop_config.json`
   - En Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Añade la configuración para reddit-content-api:

```json
"reddit-content-api": {
  "command": "/ruta/completa/a/mcp-reddit/.venv/bin/python",
  "args": [
    "-m",
    "mcp_reddit.main",
    "--stdio"
  ],
  "cwd": "/ruta/completa/a/mcp-reddit",
  "env": {
    "PYTHONPATH": "/ruta/completa/a/mcp-reddit/src:/ruta/completa/a/mcp-reddit",
    "DEBUG": "true"
  }
}
```

> ⚠️ **EXTREMADAMENTE IMPORTANTE**: `PYTHONPATH` debe incluir tanto el directorio `src` como la raíz del proyecto, en ese orden y separados por `:` (en Unix/macOS) o `;` (en Windows)

## Configuración de Cursor

1. Localiza el archivo de configuración:
   - En macOS: `/Users/tu-usuario/.cursor/mcp.json`
   - En Windows: `%USERPROFILE%\.cursor\mcp.json`

2. Añade la misma configuración que en Claude, ajustando las rutas según sea necesario.

## Solución de Problemas Comunes

### Problema: Solo aparecen 2 herramientas de las 10 esperadas

**Síntomas**: Al ejecutar el servidor aparecen solo 2 herramientas en lugar de las 10 esperadas.

**Causas posibles y soluciones**:

1. **Problema de importación**: Python está importando una versión instalada desde `site-packages` en lugar del código local en `src/`.

   **Solución**: 
   - Asegúrate de NO instalar el paquete en modo editable (`pip install -e .`)
   - Añade explícitamente `src` al inicio de `PYTHONPATH` en las configuraciones
   - Si ya lo instalaste, usa `pip uninstall reddit-content-api` para eliminarlo

2. **Caché de Python**: Los archivos `.pyc` antiguos pueden causar problemas.

   **Solución**:
   - Elimina todos los directorios `__pycache__` del proyecto

3. **Conflictos de versiones**: Diferentes versiones de una misma biblioteca.

   **Solución**:
   - Reinstala las dependencias con `pip install -r requirements.txt`

### Problema: "Cannot create post: Reddit authentication is not configured properly"

**Causa**: El token de actualización no es válido o ha expirado.

**Solución**: Regenera el token ejecutando `python -m mcp_reddit.auth_helper` y asegúrate de que se guarde en `.env`.

### Problema: Herramientas no aparecen en Claude/Cursor

**Causa**: Configuración incorrecta en los archivos de configuración.

**Solución**: 
- Revisa las rutas y especialmente `PYTHONPATH` en los archivos de configuración
- Reinicia Claude/Cursor completamente después de modificar la configuración

## Uso de las herramientas en Claude/Cursor

Una vez configurado, puedes usar las siguientes herramientas:

1. `mcp_reddit_content_api_fetch_reddit_hot_threads` - Obtener posts populares
2. `mcp_reddit_content_api_fetch_reddit_post_content` - Analizar un post y sus comentarios
3. `mcp_reddit_content_api_create_reddit_post` - Crear un post nuevo
4. `mcp_reddit_content_api_add_reddit_comment` - Añadir un comentario
5. `mcp_reddit_content_api_vote_on_reddit_content` - Votar contenido

### Ejemplos

**Obtener posts populares**:
```
Subreddit: python
Número de posts: 5
```

**Crear un post**:
```
Subreddit: test
Título: Test desde MCP
Tipo de contenido: text
Contenido: Este es un test desde la API de contenido de Reddit usando MCP.
```

## Contribuciones

Si encuentras problemas o tienes mejoras, por favor crea un issue o envía un pull request.

## Licencia

[MIT](LICENSE)

## Apoya Este Proyecto

Si encuentras útil este proyecto en tu trabajo o investigación, por favor considera:

- ⭐ Darle una estrella al repositorio para mostrar tu apoyo
- 🔄 Seguir el repositorio para recibir actualizaciones sobre nuevas funcionalidades y mejoras
- 🐛 Abrir issues para reportar errores o solicitar nuevas características
- 🛠️ Contribuir con pull requests si tienes mejoras para compartir

¡Tu apoyo ayuda a hacer este proyecto mejor para todos!