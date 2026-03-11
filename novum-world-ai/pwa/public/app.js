document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("videoFile");
    const dropArea = document.getElementById("dropZ");
    const fileMsg = document.querySelector(".file-msg");
    const form = document.getElementById("uploadForm");
    const submitBtn = document.getElementById("submitBtn");
    const consoleDiv = document.getElementById("statusConsole");
    const modeRadios = document.querySelectorAll('input[name="uploadType"]');

    let currentFiles = [];

    // Toggle single vs multiple
    modeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'batch') {
                fileInput.setAttribute('multiple', true);
                fileMsg.textContent = "Arrastra tus videos aquí (Múltiples)";
            } else {
                fileInput.removeAttribute('multiple');
                fileMsg.textContent = "Arrastra tu video aquí (Único)";
            }
            currentFiles = [];
            fileInput.value = '';
        });
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            currentFiles = Array.from(e.target.files);
            const sizeMB = currentFiles.reduce((acc, f) => acc + f.size, 0) / (1024 * 1024);
            fileMsg.textContent = `${currentFiles.length} archivo(s) seleccionados (${sizeMB.toFixed(2)} MB total)`;
        } else {
            currentFiles = [];
            fileMsg.textContent = "Toca o arrastra tus videos aquí";
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

        if (currentFiles.length === 0) {
            logMsg("ERROR: No se detectaron archivos. Abortando.", "err");
            return;
        }

        const authKey = document.getElementById("password").value;
        const uploadType = document.querySelector('input[name="uploadType"]:checked').value;
        const titleText = document.getElementById("videoTitle").value;

        // Metadata extendida
        const descriptionText = document.getElementById("videoDescription").value;
        const hashtagsText = document.getElementById("videoHashtags").value;
        const privacyVal = document.getElementById("videoPrivacy").value;

        // Redes objetivo
        const destYoutube = document.getElementById("destYoutube").checked;
        const destInstagram = document.getElementById("destInstagram").checked;
        const destTiktok = document.getElementById("destTiktok").checked;

        submitBtn.disabled = true;
        submitBtn.textContent = "UPLOADING...";

        try {
            const filesPayload = currentFiles.map(f => ({
                filename: `novum_${Date.now()}_${f.name.replace(/[^a-zA-Z0-9.\-_]/g, '')}`,
                contentType: f.type
            }));

            // 1. Obtener Presigned URL
            logMsg(`Solicitando Presigned URLs a Cloudflare R2 para ${currentFiles.length} archivo(s)...`);
            const res = await fetch("/api/get-presigned-url", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    auth: authKey,
                    files: filesPayload
                })
            });

            if (!res.ok) throw new Error("Acceso DENEGADO o Fallo de Servidor.");
            const data = await res.json();
            logMsg("Enlaces encriptados recibidos. Iniciando PUSH paralelo...");

            // 2. Subida paralela (Client-Side Upload hacia R2)
            const uploadPromises = currentFiles.map((file, index) => {
                const { url, publicUrl, filename } = data.urls[index];
                return fetch(url, {
                    method: "PUT",
                    headers: { "Content-Type": file.type },
                    body: file
                }).then(uploadRes => {
                    if (!uploadRes.ok) throw new Error(`Fallo subiendo: ${file.name}`);
                    return { filename, publicUrl, size: file.size };
                });
            });

            const uploadedFilesData = await Promise.all(uploadPromises);
            logMsg("Push completado. Archivos anclados en Cloudflare.");

            // 3. Disparar a GitHub Actions webhook JSON ligero
            logMsg("Enviando señal de ejecución a GitHub Actions...");
            const triggerRes = await fetch("/api/trigger-github", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    auth: authKey,
                    type: uploadType,
                    title: titleText,
                    description: descriptionText,
                    hashtags: hashtagsText,
                    privacy: privacyVal,
                    destinations: {
                        youtube: destYoutube,
                        instagram: destInstagram,
                        tiktok: destTiktok
                    },
                    uploadedFiles: uploadedFilesData
                })
            });

            if (!triggerRes.ok) throw new Error("GitHub rechazó la señal dispatch.");

            logMsg("✓ SECUENCIA EXITOSA. GitHub Automation despierto.");
            submitBtn.textContent = "SISTEMA OK";
            form.reset();
            currentFiles = [];
            fileMsg.textContent = "Toca o arrastra tus videos aquí";

        } catch (error) {
            logMsg(`X ERROR CRÍTICO: ${error.message}`, "err");
            submitBtn.textContent = "REINTENTAR";
            submitBtn.disabled = false;
        }
    });
});
