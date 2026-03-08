import os
import json
import logging
import asyncio
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Se requiere `pip install mcp`
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    pass

logger = logging.getLogger(__name__)

class DataScanner:
    def __init__(self):
        # El JSON de la Service Account a setear en Secrets como cadena de texto
        self.gcp_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        # El domino a revisar, ej: sc-domain:tudominio.com
        self.site_url = os.environ.get("GSC_SITE_URL", "sc-domain:midominio.com")
        
        if not self.gcp_json:
            logger.warning("Falta GOOGLE_APPLICATION_CREDENTIALS_JSON. El escaneo MCP fallará en producción.")

    async def _fetch_from_mcp(self) -> List[Dict[str, Any]]:
        """
        Conecta vía Protocolo MCP a Google Search Console.
        """
        tmp_cred_path = None
        env_vars = os.environ.copy()
        
        if self.gcp_json:
            fd, tmp_cred_path = tempfile.mkstemp(suffix=".json")
            with os.fdopen(fd, 'w') as f:
                f.write(self.gcp_json)
            env_vars["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_cred_path

        # Parametros de servidor STDIO (Node.js) para conectar al MCP de GSC
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "mcp-server-gsc"], # Usamos el paquete oficial/estable
            env=env_vars
        )
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        logger.info(f"Conectando a GSC MCP ({start_str} - {end_str})...")

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Llamada a la herramienta de analíticas del MCP
                    # Este payload mapea a GSC API
                    result = await session.call_tool("search_analytics", arguments={
                        "siteUrl": self.site_url,
                        "startDate": start_str,
                        "endDate": end_str,
                        "dimensions": ["PAGE"],
                        "rowLimit": 3
                    })
                    
                    logger.info("Métricas leídas exitosamente del MCP.")
                    
                    # Normalización robusta del output de text
                    text_content = result.content[0].text if hasattr(result, 'content') and result.content else "[]"
                    
                    try:
                        data = json.loads(text_content)
                        # El servidor mcp-server-gsc devuelve el objeto directo de la API de Google
                        # que contiene la propiedad 'rows'.
                        if isinstance(data, dict):
                            return data.get("rows", [])
                        return data if isinstance(data, list) else []
                    except json.JSONDecodeError:
                        logger.error(f"GSC devolvió un string no-JSON: {text_content}")
                        return []
                    
        except Exception as e:
            logger.error(f"Error conectando al MCP de GSC: {e}")
            raise
        finally:
            if tmp_cred_path and os.path.exists(tmp_cred_path):
                os.remove(tmp_cred_path)

    def get_top_article(self) -> str:
        """
        Sincrónico: Extrae de GSC y devuelve la URL Top 1 por impresiones.
        """
        try:
           # Forzamos event loop en scripts sincronos
           analytics = asyncio.run(self._fetch_from_mcp())
           
           if analytics and len(analytics) > 0:
               # La estructura típica del json es [{"keys": ["url"], "clicks": X, "impressions": Y}]
               top_url = analytics[0].get("keys", [""])[0] 
               logger.info(f"🏆 Top 1 URL encontrada: {top_url}")
               return top_url
           else:
               logger.warning("No se encontraron analíticas en GSC (JSON vacío). Activa fallback.")
               return "https://novum.world/articulos/tendencias-ia-default"
        except Exception as e:
           logger.error(f"Fallo escaneando datos GSC. Fallback activado. Error: {e}")
           return "https://novum.world/articulos/tendencias-ia-default"

    def compose_prompt_for_script(self, top_url: str) -> str:
         """
         Puente de IA: Toma la URL y genera el prompt semilla.
         """
         slug = top_url.strip("/").split("/")[-1].replace("-", " ")
         if not slug:
             slug = "noticia clave"
         
         prompt = f"El artículo ganador del día (Más impresiones en GSC) es sobre '{slug}'. Redacta un guion dinámico para Novum de 60 segundos enfocado en este logro."
         logger.info(f"🧠 Prompt Puente Generado: {prompt}")
         return prompt
