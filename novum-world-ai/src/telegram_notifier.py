import os
import requests

def send_telegram_message(text: str) -> bool:
    """
    Usa la API de Telegram para enviar un mensaje directamente al humano 
    (notificación de texto = fricción cero).
    """
    bot_token = os.getenv("TOKEN_TELEGRAM")
    chat_id = os.getenv("TELEGRAM_USER_ID")
    
    if not bot_token or not chat_id:
        print("Advertencia: TOKEN_TELEGRAM o TELEGRAM_USER_ID no configurados.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Formateo con markdown para facilitar "un toque para copiar" en clientes de mensajería (móvil)
    formatted_text = f"🦑 *Alerta de Novum*\nSe detectó el tema clave de GSC.\nAquí tienes tu Mega Prompt del día:\n\n```\n{text}\n```"
    
    payload = {
        "chat_id": chat_id,
        "text": formatted_text,
        "parse_mode": "MarkdownV2"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Mensaje enviado a Telegram correctamente.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error enviando notificación a Telegram: {e}")
        # Intento como texto plano en caso de fallo de parseo MarkdownV2
        fallback_payload = {
            "chat_id": chat_id,
            "text": f"🦑 Alerta de Novum\n\n{text}"
        }
        fallback_req = requests.post(url, json=fallback_payload)
        if fallback_req.status_code == 200:
            print("Fallback de Telegram exitoso.")
            return True
        return False
