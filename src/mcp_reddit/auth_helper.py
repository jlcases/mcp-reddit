#!/usr/bin/env python
"""
Script para obtener un token de autenticación de Reddit.

Este script implementa el flujo OAuth2 para obtener un token de acceso y un refresh token
que permita a la aplicación realizar acciones en nombre del usuario.

Para usar este script:
1. Configura tu aplicación en https://www.reddit.com/prefs/apps/
2. Crea una aplicación de tipo "web app" con redirect_uri = http://localhost:8080
3. Toma nota del client_id y client_secret
4. Ejecuta este script y sigue las instrucciones

El token obtenido se guardará automáticamente en el archivo .env
"""
import os
import random
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import praw
from dotenv import load_dotenv, set_key

# Cargar variables de entorno
load_dotenv()

def receive_connection():
    """Espera y devuelve un socket conectado.
    
    Abre una conexión TCP en el puerto 8080 y espera a un cliente.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

def send_message(client, message):
    """Envía un mensaje al cliente y cierra la conexión."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()

def update_env_file(token):
    """Actualiza el archivo .env con el refresh token."""
    # Buscar el archivo .env
    env_path = Path(os.getcwd()) / '.env'
    if not env_path.exists():
        print(f"Archivo .env no encontrado, creando en {env_path}")
    
    # Actualizar o añadir el token
    set_key(env_path, "REDDIT_REFRESH_TOKEN", token)
    print(f"Token guardado exitosamente en {env_path}")
    return env_path

def get_auth_token(callback=None):
    """Obtiene un token de autenticación de Reddit.
    
    Args:
        callback: Función opcional a llamar con el token obtenido
        
    Returns:
        El refresh token o None si hubo un error
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: REDDIT_CLIENT_ID o REDDIT_CLIENT_SECRET no están configurados.")
        print("Configura estas variables en tu archivo .env")
        return None
    
    print("Este script obtendrá un refresh token para tu aplicación de Reddit.")
    print("Necesitarás este token para las acciones de escritura.")
    
    # Solicitar los scopes
    print("\nScopes necesarios para la aplicación:")
    print("  - identity: para verificar la identidad")
    print("  - submit: para crear posts")
    print("  - edit: para editar posts/comentarios")
    print("  - vote: para votar")
    
    scopes_list = ["identity", "submit", "edit", "vote"]
    print(f"\nUsando scopes: {', '.join(scopes_list)}")
    
    # Inicializar Reddit
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:8080",
        user_agent="MCP-Reddit-Content-API/v0.1.0",
    )
    
    # Generar URL de autorización
    state = str(random.randint(0, 65000))
    auth_url = reddit.auth.url(scopes=scopes_list, state=state, duration="permanent")
    
    print(f"\nPor favor, abre esta URL en tu navegador:\n{auth_url}\n")
    print("Una vez que autorices la aplicación, serás redirigido a localhost.")
    
    # Esperar la redirección
    print("Esperando redirección...")
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    
    # Extraer los parámetros de la URL
    url_path = data.split(" ", 2)[1]
    parsed_url = urlparse(url_path)
    query_params = parse_qs(parsed_url.query)
    
    # Convertir a diccionario simple
    params = {k: v[0] for k, v in query_params.items()}
    
    # Verificar state para prevenir CSRF
    if state != params.get("state"):
        error_msg = f"State mismatch. Expected: {state} Received: {params.get('state')}"
        send_message(client, error_msg)
        print(f"Error: {error_msg}")
        return None
    
    # Verificar si hay error
    if "error" in params:
        error_msg = f"Error en la autenticación: {params['error']}"
        send_message(client, error_msg)
        print(f"Error: {error_msg}")
        return None
    
    # Obtener refresh token
    refresh_token = reddit.auth.authorize(params["code"])
    
    # Actualizar el .env
    env_path = update_env_file(refresh_token)
    
    success_msg = f"¡Autenticación exitosa!\n\nRefresh token: {refresh_token}\n\n"
    success_msg += f"El token ha sido guardado automáticamente en {env_path}"
    
    send_message(client, success_msg)
    
    print("\n=== AUTENTICACIÓN COMPLETADA ===")
    print(f"Token guardado en {env_path}")
    print("No es necesario reiniciar manualmente el servidor.")
    
    # Llamar al callback si existe
    if callback and callable(callback):
        callback(refresh_token)
    
    return refresh_token

def main():
    """Punto de entrada del programa."""
    token = get_auth_token()
    return 0 if token else 1

if __name__ == "__main__":
    sys.exit(main()) 