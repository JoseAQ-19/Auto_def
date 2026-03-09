# PRD: Novum World AI (V2 - Arquitectura Coste Cero)
**Role:** Arquitecto Principal GSD
**Focus:** Fricción Cero en Recepción y Distribución
**Restricciones Tecnológicas:** Plataformas "Always Free", Client-side Uploads, y delegación de distribución en Composio SDK.

## 1. El Objetivo
Automatizar un flujo de trabajo de creación de contenido en formato vertical (Shorts, Reels, TikTok) sin límites de carga para .mp4 (30MB+). El humano únicamente renderiza en CapCut Agent y usa una PWA para la subida final sin tiempos de espera.

## 2. Componentes de la Arquitectura
- **Cerebro (Notificaciones & LLM):** Scripts en Python ejecutados diariamente por un Cronjob de GitHub Actions. Usará Telegram únicamente para enviar de manera asíncrona notificaciones de texto (Mega Prompts) al humano.
- **Recepción (La PWA):** Página Web App ligera protegida por master password y hosted en Cloudflare Pages / Vercel. Sube el vídeo exportado del PC/móvil usando **Client-side Pre-signed URLs** hacia Cloudflare R2 sin tocar el límite Serverless.
- **Músculo (Extracción & Ruteo):** API request de Google Search Console para seleccionar temas. Tras la carga en R2, la PWA gatilla un Webhook a GitHub Actions mediante `repository_dispatch`.
- **Distribución:** GitHub Actions se baja el MP4 ultrarrápido desde R2, lo auto-publica exclusivamente a través de la API oficial de **Composio** en YouTube, Instagram y TikTok, y limpia R2 tras publicarlo. 

## 3. Limitaciones Previas Superadas
- Subidas limitadas a 20MB de Telegram Bots publicas resueltas moviendo la carga a Cloudflare R2 y aislando Telegram solo a texto y notificaciones.
- Los timeouts o límites HTTP de servidores gratuitos se manejan moviendo la carga real al Browser-Side con las SDKs nativas hacia AWS/S3 compatible services como Cloudflare.

---
## Flujos y Faseado en `progress.txt`
Todas las tareas asociadas a estas 4 Fases están detalladas a fuego en la raíz del repositorio y guiadas estrictamente bajo el framework GSD. Ninguna otra tecnología de hosting se va a plantear excepto este pipeline 100% gratuito basado en PWA y Actions.
