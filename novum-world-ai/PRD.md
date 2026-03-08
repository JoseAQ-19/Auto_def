# PRD: Novum World AI Director (V1.0)
## Resumen
Orquestador automático en Python + GitHub Actions para generar contenido diario de vídeo.

## Componentes y Requisitos
1. **Data Scan**: Escaneo de artículos/estudiantes con más impresiones para elegir el tema del día.
2. **Scripting**: Generación de un guion de 60 segundos dividido en escenas.
3. **Voice Synth (Estudio A)**: Por cada escena, llamada a la API de ElevenLabs para obtener el .mp3.
4. **Video Prod (Estudio B & Estudio A)**: Bucle de creación vía gradio_client a Hugging Face spaces:
   - "Habla": Conexión enviando el audio -> "Novum-Podcast-Studio" (LTX-2).
   - "Acción": Conexión enviando el prompt visual -> "Novum-Action-Set" (Wan2.2).
5. **Assembly**: Unión de todos los clips `.mp4` vía FFmpeg.
6. **Publishing**: Subida automática a redes a través de Composio.
7. **Secrets Exigidos**: ELEVENLABS_API_KEY, HF_TOKEN_PODCAST, HF_TOKEN_ACTION, HF_SPACE_PODCAST_URL, HF_SPACE_ACTION_URL.
