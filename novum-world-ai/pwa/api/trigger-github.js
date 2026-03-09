// Vercel Serverless Function - Gatillo para GitHub Actions
module.exports = async (req, res) => {
    // CORS Headers
    res.setHeader('Access-Control-Allow-Credentials', true)
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS,POST')

    if (req.method === 'OPTIONS') {
        return res.status(200).end()
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { auth, videoUrl, videoTitle, filename } = req.body || {};

    // Seguridad: Master Password
    const MASTER_PASS = process.env.PWA_MASTER_PASSWORD || 'novum666';
    if (!auth || auth !== MASTER_PASS) {
        return res.status(401).json({ error: 'Acceso Denegado' });
    }

    const GITHUB_PAT = process.env.GITHUB_PAT;
    const GITHUB_REPO = process.env.GITHUB_REPO; // ej: "JoseAQ-19/Auto_def" o "usuario/novum-world-ai"

    if (!GITHUB_PAT || !GITHUB_REPO) {
        console.error("Falta PAT o REPO en vars");
        return res.status(500).json({ error: 'Configuración de GitHub faltante en servidor' });
    }

    try {
        // Ejecuta workflow_dispatch o repository_dispatch en el repo
        const githubRes = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/dispatches`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${GITHUB_PAT}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_type: 'video_upload_ready',
                client_payload: {
                    title: videoTitle,
                    video_url: videoUrl,
                    file_key: filename
                }
            })
        });

        if (!githubRes.ok) {
            const errorText = await githubRes.text();
            console.error("Fallo GitHub:", errorText);
            throw new Error(`GitHub Api status: ${githubRes.status}`);
        }

        res.status(200).json({ success: true, message: 'Señal Github Action enviada con éxito' });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Error enviando señal al Músculo (Fase 4)' });
    }
};
