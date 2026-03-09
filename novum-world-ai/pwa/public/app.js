document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("videoFile");
    const dropArea = document.getElementById("dropZ");
    const fileMsg = document.querySelector(".file-msg");
    const form = document.getElementById("uploadForm");
    const submitBtn = document.getElementById("submitBtn");
    const consoleDiv = document.getElementById("statusConsole");

    let currentFile = null;

    // Drag & Drop logic
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            currentFile = e.target.files[0];
            fileMsg.textContent = `${currentFile.name} (${(currentFile.size / (1024 * 1024)).toFixed(2)} MB)`;
        } else {
            currentFile = null;
            fileMsg.textContent = "Toca o arrastra tu video aquí";
        }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('is-active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('is-active'), false);
    });

    // Logging utility
    function logMsg(msg, type = "info") {
        consoleDiv.classList.remove('hidden');
        const p = document.createElement('p');
        p.textContent = `> ${msg}`;
        if (type === 'err') p.className = 'err';
        if (type === 'warn') p.className = 'warn';
        consoleDiv.appendChild(p);
        consoleDiv.scrollTop = consoleDiv.scrollHeight;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!currentFile) {
            logMsg("ERROR: No se detectó archivo. Abortando.", "err");
            return;
        }

        if (currentFile.size > 55 * 1024 * 1024) { // Límite de seguridad 55MB
            logMsg(`ERROR: Archivo sobrepasa los 50MB (${(currentFile.size / 1024 / 1024).toFixed(2)}MB).`, "err");
            return;
        }

        const authKey = document.getElementById("password").value;
        const titleText = document.getElementById("videoTitle").value;
        const safeFileName = `novum_${Date.now()}_${currentFile.name.replace(/[^a-zA-Z0-9.\-_]/g, '')}`;

        submitBtn.disabled = true;
        submitBtn.textContent = "UPLOADING...";

        try {
            // 1. Obtener Presigned URL
            logMsg("Solicitando Presigned URL a Cloudflare R2...");
            const res = await fetch("/api/get-presigned-url", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    auth: authKey,
                    filename: safeFileName,
                    contentType: currentFile.type
                })
            });

            if (!res.ok) throw new Error("Acceso DENEGADO o Fallo de Servidor.");
            const { url, publicUrl } = await res.json();
            logMsg("Enlace encriptado recibido. Iniciando PUSH...");

            // 2. Subida directa (Client-Side Upload hacia R2)
            const uploadRes = await fetch(url, {
                method: "PUT",
                headers: {
                    "Content-Type": currentFile.type
                },
                body: currentFile
            });

            if (!uploadRes.ok) throw new Error("Fallo la subida a Cloudflare R2.");
            logMsg("Push completado. Archivo anclado en Cloudflare.");

            // 3. Disparar a GitHub Actions
            logMsg("Enviando señal de ejecución a GitHub Actions...");
            const triggerRes = await fetch("/api/trigger-github", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    auth: authKey,
                    videoUrl: publicUrl || `https://${safeFileName}`, // Ajustar según domain
                    videoTitle: titleText,
                    filename: safeFileName
                })
            });

            if (!triggerRes.ok) throw new Error("GitHub rechazó la señal dispatch.");

            logMsg("✓ SECUENCIA EXITOSA. El Agente 04 asume control del video.");
            submitBtn.textContent = "SISTEMA OK";
            form.reset();
            currentFile = null;
            fileMsg.textContent = "Toca o arrastra tu video aquí";

        } catch (error) {
            logMsg(`X ERROR CRÍTICO: ${error.message}`, "err");
            submitBtn.textContent = "REINTENTAR";
            submitBtn.disabled = false;
        }
    });
});
