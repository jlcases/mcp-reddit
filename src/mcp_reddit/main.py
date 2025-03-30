"""
Main entry point for the Reddit Content API
"""
import logging
import sys
import traceback
import os

# Añadir la raíz del proyecto a sys.path para priorizar los módulos locales
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_root = os.path.join(project_root, 'src')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_root not in sys.path:
    sys.path.insert(0, src_root)

# Importar reddit_fetcher de forma más robusta - SOLO importamos mcp
try:
    import mcp_reddit.reddit_fetcher
    mcp = mcp_reddit.reddit_fetcher.mcp
except ImportError as e:
    print(f"FATAL: No se pudo importar mcp_reddit.reddit_fetcher: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Reddit Content API server...")
    
    # Función para listar las herramientas registradas
    def list_all_registered_tools():
        logger.info("Listing registered tools...")
        tool_manager = getattr(mcp, "_tool_manager", None)
        if tool_manager:
            all_tools = tool_manager.list_tools()
            logger.info(f"Total registered tools: {len(all_tools)}")
            for i, tool in enumerate(all_tools):
                logger.info(f"Tool {i+1}: NAME='{tool.name}', DESC='{tool.description}'")
        else:
            logger.error("Tool manager not found in MCP instance")
    
    # Listar herramientas
    list_all_registered_tools()
    
    try:
        # Start the server
        logger.info("Running MCP server...")
        mcp.run()
        logger.info("Server running. Press Ctrl+C to stop.")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1) 