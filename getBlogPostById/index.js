import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

const REGION = "us-east-1";
const BUCKET_NAME = process.env.BUCKET_NAME;
const BLOG_POST_TABLE = process.env.BLOG_POST_TABLE;

const s3 = new S3Client({ region: REGION });
const dynamodb = new DynamoDBClient({ region: REGION });
const dbclient = DynamoDBDocumentClient.from(dynamodb);

const streamToString = async (stream) => {
    return await new Promise((resolve, reject) => {
        const chunks = [];
        stream.on("data", (chunk) => chunks.push(chunk));
        stream.on("error", reject);
        stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    });
};

/**
 * @param {import('aws-lambda').APIGatewayProxyEventV2} event 
 */
export const handler = async (event) => {
    const id = event.pathParameters?.id;
    if (!id) {
        return {
            statusCode: 400,
            body: JSON.stringify("An acceptable ID was not sent.")
        }
    }
    try {
        const get = new GetCommand({
            TableName: BLOG_POST_TABLE,
            Key: { id }
        });

        const response = await dbclient.send(get);
        const post = response.Item;

        if (!post || !post.path) {
            return {
                statusCode: 404,
                body: JSON.stringify("No file was found under this post.")
            }
        }

        try {
            const getobject = new GetObjectCommand({
                Bucket: BUCKET_NAME,
                Key: post.path,
            });

            const s3response = await s3.send(getobject);
            post.content = await streamToString(s3response.Body);
            
            return {
                statusCode: 200,
                body: JSON.stringify(post)
            }

        } catch (error) {
            console.error("==================== ERROR IN LAMBDA FUNCTION GETBLOGPOSTBYID ====================");
            console.error(error);
            console.error("==================================================================================");
            return {
                statusCode: 500,
                body: JSON.stringify("There was a problem getting the blog post info from the bucket.")
            }
        }

    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION GETBLOGPOSTBYID ====================");
        console.error(error);
        console.error("==================================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem getting the blog post info from the database.")
        }
    }
}
