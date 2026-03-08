import os
import json
import asyncio
import tempfile
from datetime import datetime, timedelta

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ Error: La librería 'mcp' no está instalada. Ejecuta: pip install mcp")
    exit(1)

async def test_gsc_connection():
    gcp_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    site_url = os.environ.get("GSC_SITE_URL", "https://novumworld.com/")
    
    print("==== TEST DE CONEXIÓN GSC MCP ====")
    if not gcp_json:
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS_JSON no está configurada en las variables de entorno.")
        return

    print("✅ Credenciales de Google Cloud encontradas. Configurando archivo temporal...")
    
    tmp_cred_path = None
    env_vars = os.environ.copy()
    
    # Creamos un archivo temporal para que reciba la variable GOOGLE_APPLICATION_CREDENTIALS
    fd, tmp_cred_path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        f.write(gcp_json)
    env_vars["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_cred_path

    # Arrancamos el servidor del MCP
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@kimlimjustin/gsc-mcp"],  # Puedes cambiar a tu paquete habitual si es distinto
        env=env_vars
    )
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"📡 Conectando a GSC solicitando datos desde {start_str} a {end_str} para {site_url}...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("🔄 Sesión MCP inicializada. Llamando a 'get_search_analytics'...")
                # Llamada directa a get_search_analytics
                result = await session.call_tool("get_search_analytics", arguments={
                    "siteUrl": site_url,
                    "startDate": start_str,
                    "endDate": end_str,
                    "dimensions": ["PAGE"],
                    "rowLimit": 3
                })
                
                text_content = result.content[0].text if hasattr(result, 'content') and result.content else "[]"
                
                print("\n🏆 Top 3 URLs con más impresiones (Últimos 7 días):")
                print("-" * 50)
                try:
                    data = json.loads(text_content)
                    if isinstance(data, list) and len(data) > 0:
                        for i, row in enumerate(data, 1):
                            url = row.get("keys", ["Desconocida"])[0]
                            impressions = row.get("impressions", 0)
                            clicks = row.get("clicks", 0)
                            print(f"{i}. {url}")
                            print(f"   👀 Impresiones: {impressions} | 🖱️ Clics: {clicks}")
                    else:
                        print("No se encontraron resultados o no hubo impresiones recientes.")
                except json.JSONDecodeError:
                    print(f"GSC devolvió un formato no reconocible como JSON:\n{text_content}")

    except Exception as e:
        print(f"\n❌ Error durante la ejecución del MCP: {e}")
    finally:
        if tmp_cred_path and os.path.exists(tmp_cred_path):
            os.remove(tmp_cred_path)
            print("\n🧹 Archivo de credenciales temporales eliminado exitosamente.")

if __name__ == "__main__":
    asyncio.run(test_gsc_connection())
