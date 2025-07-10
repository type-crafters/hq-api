import Busboy from "busboy";
import { Buffer } from "buffer";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { randomUUID } from "crypto";

const REGION = "us-east-1";
const HQ_BUCKET = process.env.HQ_BUCKET;
const BLOG_POSTS_TABLE = process.env.BLOG_POSTS_TABLE;

const s3 = new S3Client({ region: REGION });
const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

/** @param {string} text */
const clipPreview = (text) => {
    const words = text.split(/\s+/);
    let preview = "";

    for (let word of words) {
        if ((preview + " " + word).trim().length <= 197) {
            preview += " " + word;
        } else {
            break;
        }
    }

    return preview.trim() + "...";
}

/** @param {import("aws-lambda").APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    const buffer = Buffer.from(event.body, (event.isBase64Encoded ? "base64" : "utf-8"));

    const fields = {};
    const files = [];

    await new Promise((resolve, reject) => {
        try {
            const busboy = Busboy({
                headers: {
                    "content-type": event.headers["content-type"] || event.headers["Content-Type"]
                }
            });

            busboy.on("file", (name, stream, info) => {
                const { filename, encoding, mimetype } = info;
                const chunks = [];
                stream.on("data", chunk => chunks.push(chunk));
                stream.on("end", () => {
                    files.push({
                        fieldname: name,
                        filename,
                        contentType: mimetype,
                        encoding,
                        buffer: Buffer.concat(chunks),
                    });
                });
            });

            busboy.on("field", (name, value) => {
                fields[name] = value;
            });

            busboy.on("close", resolve);
            busboy.on("error", reject);

            busboy.write(buffer);
            busboy.end();
        } catch (err) {
            reject(err);
        }
    });

    const required = ["title", "author", "content", "featured"];

    if (required.some((key) => !(key in fields))) {
        return {
            statusCode: 422,
            body: JSON.stringify("Missing required keys in body.")
        }
    }

    const image = files.find((file) => file.fieldname === "thumbnail");

    const uuid = randomUUID();
    const filename = uuid.split("-").slice(2).join("-");
    const mdpath = `blog-posts/article_${filename}.md`;

    const markdown = Buffer.from(fields.content, "utf-8");

    try {
        await s3.send(new PutObjectCommand({
            Bucket: HQ_BUCKET,
            Key: mdpath,
            Body: markdown,
            ContentType: "text/markdown"
        }));
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION SAVEBLOGPOST ====================");
        console.error(error);
        console.error("===============================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem saving the post's markdown file to the bucket.")
        }
    }

    let thumbpath = "";

    if (image) {
        const ext = image.filename.split(".").pop();
        thumbpath = `thumbnails/thumb_${filename}.${ext}`;

        try {
            await s3.send(new PutObjectCommand({
                Bucket: HQ_BUCKET,
                Key: thumbpath,
                Body: image.buffer,
                ContentType: image.contentType
            }));
        } catch (error) {
            console.error("==================== ERROR IN LAMBDA FUNCTION SAVEBLOGPOST ====================");
            console.error(error);
            console.error("===============================================================================");
            return {
                statusCode: 500,
                body: JSON.stringify("There was a problem saving the post's thumbnail to the bucket.")
            }
        }
    }

    try {
        await dbclient.send(new PutCommand({
            TableName: BLOG_POSTS_TABLE,
            Item: {
                id: uuid,
                title: fields.title,
                author: fields.author,
                creationDate: new Date().toISOString(),
                path: mdpath,
                thumbnail: thumbpath,
                preview: clipPreview(fields.content),
                featured: ["true", "on", "1"].includes(fields.featured) ? true : false
            }
        }));
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION SAVEBLOGPOST ====================");
        console.error(error);
        console.error("===============================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem saving the post's data to the database.")
        }
    }

    return {
        statusCode: 201,
        body: JSON.stringify("Post created")
    };
}