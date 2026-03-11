const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");
const crypto = require("crypto");

module.exports = async (req, res) => {
    const MASTER_PASSWORD = process.env.PWA_MASTER_PASSWORD;
    const CLOUDFLARE_ACCOUNT_ID = process.env.CLOUDFLARE_ACCOUNT_ID;
    const R2_ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID;
    const R2_SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY;
    const R2_BUCKET_NAME = process.env.R2_BUCKET_NAME;

    // Check environment variables early
    if (!MASTER_PASSWORD || !CLOUDFLARE_ACCOUNT_ID || !R2_ACCESS_KEY_ID || !R2_SECRET_ACCESS_KEY || !R2_BUCKET_NAME) {
        return res.status(500).json({ message: "Configuracion faltante en el servidor." });
    }

    // 0. Only POST method allowed
    if (req.method !== "POST") {
        return res.status(405).json({ message: "Método no permitido. Usa POST." });
    }

    const { auth, files } = req.body;

    // 1. Check Master Password with timingSafeEqual
    const authBuffer = Buffer.from(auth || "");
    const masterBuffer = Buffer.from(MASTER_PASSWORD);

    if (authBuffer.length !== masterBuffer.length || !crypto.timingSafeEqual(authBuffer, masterBuffer)) {
        return res.status(401).json({ message: "Acceso Intruso Denegado." });
    }

    if (!files || !Array.isArray(files) || files.length === 0) {
        return res.status(400).json({ message: "Faltan archivos para procesar." });
    }

    // 2. Initialize S3Client mapping to Cloudflare R2
    const s3 = new S3Client({
        region: "auto",
        endpoint: `https://${CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`,
        credentials: {
            accessKeyId: R2_ACCESS_KEY_ID,
            secretAccessKey: R2_SECRET_ACCESS_KEY,
        },
    });

    const bucketName = R2_BUCKET_NAME;

    try {
        const urlPromises = files.map(async (fileData) => {
            const { filename, contentType } = fileData;
            const command = new PutObjectCommand({
                Bucket: bucketName,
                Key: filename,
                ContentType: contentType,
            });

            const preSignedUrl = await getSignedUrl(s3, command, { expiresIn: 3600 });
            return {
                filename: filename,
                url: preSignedUrl,
                publicUrl: `https://${CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com/${bucketName}/${filename}`
            };
        });

        const urls = await Promise.all(urlPromises);

        return res.status(200).json({ urls });
    } catch (error) {
        console.error("S3 Error:", error);
        return res.status(500).json({ message: "Error conectando a Cloudflare R2." });
    }
};
