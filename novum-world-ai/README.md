# Novum World AI Director (V1.0)
Orquestador automático para generación de contenido diario (vídeos) usando ElevenLabs, LTX-2 (Hugging Face) y Wan2.2.

## Arquitectura
- **Motor de Audio:** `src/audio_engine.py` se conecta con la API de ElevenLabs para generar TTS.
- **Motor de Vídeo:** `src/video_engine.py` utiliza Gradio Client para mandar comandos a los Spaces "Novum-Podcast-Studio" y "Novum-Action-Set", procesando Lip-Sync y generación visual respectivamente.
- **Orquestador:** `src/main.py` genera un guion simulado, llama a ambos estudios, y ensambla finalmente el `.mp4`.

## Configuración de GitHub Secrets
Para ejecutar el bot automáticamente (`.github/workflows/daily_video.yml`) debes setear la siguiente lista de secretos:
* `ELEVENLABS_API_KEY`: API Key de texto-a-voz.
* `HF_TOKEN_PODCAST`: Token con permisos "Write" para interactuar con "Novum-Podcast-Studio".
* `HF_SPACE_PODCAST_URL`: URL remota del Space de podcast (ej: `https://...hf.space/`).
* `HF_TOKEN_ACTION`: Token con permisos "Write" para interactuar con "Novum-Action-Set".
* `HF_SPACE_ACTION_URL`: URL remota del Space de acción.

## Desarrollo Local
1. Instala las dependencias: `pip install -r requirements.txt`.
2. Ejecuta los tests: `python -m unittest discover tests/`.
3. Crea un archivo `assets/novum_master_image.png`.

## Deploy (Composio)
Esta versión simula todo el recorrido hasta generar `final_video.mp4` que automáticamente sube a artifacts. Para integrar Composio basta con inyectar el Composio Node al final del archivo `main.py`.
