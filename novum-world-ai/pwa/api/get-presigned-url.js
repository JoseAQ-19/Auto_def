const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

// Vercel Serverless Function - Generador de Firma para Cloudflare R2
module.exports = async (req, res) => {
    // Configuración CORS simple
    res.setHeader('Access-Control-Allow-Credentials', true)
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS,POST')

    // Preflight request handler
    if (req.method === 'OPTIONS') {
        res.status(200).end()
        return
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { auth, filename, contentType } = req.body || {};

    // Seguridad Básica: Master Password
    const MASTER_PASS = process.env.PWA_MASTER_PASSWORD || 'novum666';
    if (!auth || auth !== MASTER_PASS) {
        return res.status(401).json({ error: 'Fallo de Autorización (Master Password Incorrecto)' });
    }

    if (!filename || !contentType) {
        return res.status(400).json({ error: 'Se requiere archivo y tipo' });
    }

    // Credenciales leídas de Vercel/Cloudflare Variables de Entorno (mismos nombres que en GitHub como pidió el Auditor)
    const accessKeyId = process.env.R2_ACCESS_KEY_ID;
    const secretAccessKey = process.env.R2_SECRET_ACCESS_KEY;
    const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const bucketName = process.env.R2_BUCKET_NAME;

    if (!accessKeyId || !secretAccessKey || !accountId || !bucketName) {
        return res.status(500).json({ error: 'Configuración R2 faltante en el servidor.' });
    }

    const s3 = new S3Client({
        region: 'auto',
        endpoint: `https://${accountId}.r2.cloudflarestorage.com`,
        credentials: {
            accessKeyId,
            secretAccessKey,
        },
    });

    try {
        const command = new PutObjectCommand({
            Bucket: bucketName,
            Key: filename,
            ContentType: contentType,
        });

        const signedUrl = await getSignedUrl(s3, command, { expiresIn: 3600 }); // Válido 1 hora

        // El R2 custom domain o url de descarga para pasar a GitHub luego, en caso de ser estática
        const R2_PUBLIC_URL_BASE = process.env.R2_PUBLIC_URL_BASE || `https://${bucketName}.${accountId}.r2.cloudflarestorage.com`;

        res.status(200).json({
            url: signedUrl,
            publicUrl: `${R2_PUBLIC_URL_BASE}/${filename}`
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Error generando clave de subida R2' });
    }
};
