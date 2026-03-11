module.exports = async (req, res) => {
    if (req.method !== "POST") {
        return res.status(405).json({ message: "Metodo no soportado" });
    }

    const { auth, type, title, description, hashtags, privacy, destinations, uploadedFiles } = req.body;

    // 1. Validar password
    if (auth !== process.env.PWA_MASTER_PASSWORD) {
        return res.status(401).json({ message: "Unauthorized" });
    }

    // 2. Disparador hacia GitHub
    const GITHUB_TOKEN = process.env.GITHUB_PAT;
    const GITHUB_REPO = process.env.GITHUB_REPO; // ej: JoseAQ-19/Auto_def

    if (!GITHUB_TOKEN || !GITHUB_REPO) {
        return res.status(500).json({ message: "Configuracion de GitHub faltante en Vercel." });
    }

    // Adaptamos el cliente payload según sea unitario o batch para no romper compatibilidad opcional
    // Enviamos el payload moderno indicando "type" y el arreglo de "files"
    try {
        // Busqueda infalible del vídeo final ensamblado (Evitando fragmentos o escenas):
        // El vídeo completo (merged) siempre será el que tenga el mayor peso en bytes de toda la tanda subida.
        const mainVideo = [...uploadedFiles].sort((a, b) => (b.size || 0) - (a.size || 0))[0];

        const githubRes = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
            method: "POST",
            headers: {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": `token ${GITHUB_TOKEN}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                event_type: "video_upload_ready",
                client_payload: {
                    metadata: {
                        type: type || "single",
                        title: title,
                        description: description || "",
                        hashtags: hashtags || "",
                        privacy: privacy || "private",
                        dest_youtube: destinations?.youtube ? "true" : "false",
                        dest_instagram: destinations?.instagram ? "true" : "false",
                        dest_tiktok: destinations?.tiktok ? "true" : "false",
                        files: uploadedFiles,

                        // Legacy compatibility mapeando el archivo ganador
                        video_url: mainVideo?.publicUrl || "",
                        file_key: mainVideo?.filename || ""
                    }
                }
            })
        });

        if (!githubRes.ok) {
            const errorText = await githubRes.text();
            console.error("Github Error:", errorText);
            return res.status(502).json({ message: "Fallo apuntando al Actions V2." });
        }

        return res.status(200).json({ success: true, message: "GitHub Despierto" });
    } catch (err) {
        console.error("Serverless crash:", err);
        return res.status(500).json({ message: "Fallo crudo al disparar Github." });
    }
};
