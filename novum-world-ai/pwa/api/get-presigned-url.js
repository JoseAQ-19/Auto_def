const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");

module.exports = async (req, res) => {
    // 0. Only POST method allowed
    if (req.method !== "POST") {
        return res.status(405).json({ message: "Método no permitido. Usa POST." });
    }

    const { auth, files } = req.body;

    // 1. Check Master Password
    if (auth !== process.env.PWA_MASTER_PASSWORD) {
        return res.status(401).json({ message: "Acceso Intruso Denegado." });
    }

    if (!files || !Array.isArray(files) || files.length === 0) {
        return res.status(400).json({ message: "Faltan archivos para procesar." });
    }

    // 2. Initialize S3Client mapping to Cloudflare R2
    const s3 = new S3Client({
        region: "auto",
        endpoint: `https://${process.env.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com`,
        credentials: {
            accessKeyId: process.env.R2_ACCESS_KEY_ID,
            secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
        },
    });

    const bucketName = process.env.R2_BUCKET_NAME;

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
                publicUrl: `https://${process.env.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com/${bucketName}/${filename}`
            };
        });

        const urls = await Promise.all(urlPromises);

        return res.status(200).json({ urls });
    } catch (error) {
        console.error("S3 Error:", error);
        return res.status(500).json({ message: "Error conectando a Cloudflare R2." });
    }
};
