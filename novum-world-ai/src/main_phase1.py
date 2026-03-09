import sys
import os
from src.gsc_client import get_top_performing_topic
from src.llm_agent import generate_novum_prompt
from src.telegram_notifier import send_telegram_message

def run_phase1():
    print("▶ Iniciando Fase 1: Extracción y Guionización (El Cerebro) 🧠")
    
    # GSC Data config
    site_url = os.getenv("GSC_SITE_URL", "https://novum.world") # URL de fallback por defecto para GSC
    creds_path = os.getenv("GSC_CREDENTIALS_PATH", "credentials.json")
    
    print(f"📡 1/4 - Analizando el dominio [{site_url}] en GSC...")
    try:
        top_topic = get_top_performing_topic(site_url, creds_path, days=3)
        print(f"✅ {top_topic.upper()} fue coronado como tema tendencia.")
    except Exception as e:
        print(f"⚠️ Aviso: Conexión con GSC falló. Iniciando fallback por defecto. Detalle técnico: {e}")
        top_topic = "tendencia actual disruptiva en el sector IA"
        
    print(f"🧠 2/4 - Contactando al modelo de Lenguaje LLM para redactar el guion de Novum...")
    try:
        mega_prompt = generate_novum_prompt(top_topic)
        print(f"✅ Mega Prompt de Novum generado exitosamente ({len(mega_prompt)} caracteres).")
    except Exception as e:
        print(f"❌ Error Crítico: Fallo en el módulo LLM. Verifique sus llaves o límite de tokens. Detalle: {e}")
        sys.exit(1)
        
    print("📲 3/4 - Empujando alerta vía Telegram Server al humano asignado...")
    success = send_telegram_message(mega_prompt)
    if success:
        print("✅ Telegram payload enviado a destino. Fricción cero lograda.")
    else:
        print("❌ Error en envío de Telegram. (Recuerde configurar los secretos y el BOTID).")
        
    print("🏁 4/4 - Fase 1 Finalizada.")
    print("El Flujo queda a la espera de que el humano complete la Fase de Subida en la PWA (Phase 3).")

if __name__ == "__main__":
    run_phase1()
