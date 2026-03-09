# Guía de Configuración de Credenciales (Fase 2)

Para que el Cerebro (Phase 1) despierte y el Músculo (Phase 4) tenga fuerza, necesitas configurar los siguientes **Repository Secrets** en tu repositorio de GitHub:

Ve a tu repositorio de GitHub -> `Settings` -> `Secrets and variables` -> `Actions` -> **`New repository secret`**.

## 1. Google Search Console (El Cerebro)
* **`GSC_SITE_URL`**: La URL exacta de tu propiedad en Google Search Console.
  * Ej: `https://entrenandolainteligenciaartificial.com` o `sc-domain:tu-dominio.com`
* **`GOOGLE_APPLICATION_CREDENTIALS_JSON`**: El contenido de tu archivo `credentials.json` (la Service Account de Google Cloud con permisos de lectura en GSC) convertido a **Base64**.
  * ¿Por qué Base64? Porque Github Secrets rompe las comillas y saltos de línea de los JSON.
  * *Cómo obtener el Base64 en PC*: En Windows usa Powerhsell con `[convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))` o usa una web como `base64encode.org`.

## 2. El Agente LLM (El Guionista)
* **`LLM_API_KEY`**: Tu API Key (ej. de OpenAI `sk-...` o Groq `gsk_...`).
* **`LLM_BASE_URL`**: Opcional. Si usas OpenAI, déjalo vacío o usa `https://api.openai.com/v1`. Si usas Groq, usa `https://api.groq.com/openai/v1`.
* **`LLM_MODEL`**: El modelo a usar. Mantenlo barato y rápido: `gpt-4o-mini` (OpenAI) o `llama-3.1-8b-instant` (Groq).

## 3. Telegram (Notificaciones)
* **`TOKEN_TELEGRAM`**: El token que te da el BotFather al crear tu bot (Ej: `123456789:ABCdefgHIJKlmnop...`).
* **`TELEGRAM_USER_ID`**: Tu ID de chat personal en Telegram. Búscalo en bots como `@userinfobot`. (Ej: `12345678`).

## 4. Cloudflare R2 (Almacenamiento de Video)
* **`CLOUDFLARE_ACCOUNT_ID`**: El ID de cuenta de tu dashboard de Cloudflare.
* **`R2_ACCESS_KEY_ID`**: La llave de acceso pública de tu API Token para R2.
* **`R2_SECRET_ACCESS_KEY`**: La llave de acceso secreta de tu API Token para R2.
* **`R2_BUCKET_NAME`**: El nombre de tu bucket de R2.

---
> [!IMPORTANT]
> **No lo retrases.** Hasta que no pongas estos 7 Secretos en tu GitHub, la Acción diaria fallará (aunque el código subido esté inmaculado y pase los Unit Tests).
