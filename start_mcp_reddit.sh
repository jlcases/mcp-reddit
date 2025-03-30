#!/bin/bash
# Script para iniciar el servidor MCP-Reddit
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src:$(pwd)"
.venv/bin/python src/mcp_reddit/main.py