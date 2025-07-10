import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, ScanCommand } from "@aws-sdk/lib-dynamodb"
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const REGION = "us-east-1";
const BUCKET_NAME = process.env.BUCKET_NAME;
const BLOG_POST_TABLE = process.env.BLOG_POST_TABLE;

const s3 = new S3Client({ region: REGION });
const dynamodb = new DynamoDBClient({ region: REGION });
const dbclient = DynamoDBDocumentClient.from(dynamodb);

export const handler = async (event) => {
    try {
        const scan = new ScanCommand({
            TableName: BLOG_POST_TABLE
        });
        const response = await dbclient.send(scan);
        const items = response.Items;

        try {
            await Promise.all(items.map(async (blogpost) => {
                if (blogpost.thumbnail) {
                    const getobject = new GetObjectCommand({
                        Bucket: BUCKET_NAME,
                        Key: blogpost.thumbnail
                    });
                    blogpost.thumbnail = await getSignedUrl(s3, getobject, { expiresIn: 3600 });
                }
            }));
        } catch (error) {
            console.error("==================== ERROR IN LAMBDA FUNCTION GETALLBLOGPOSTS ====================")
            console.error(error);
            console.error("==================================================================================")
            return {
                statusCode: 500,
                body: JSON.stringify("There was a problem getting a signed URL for the thumbnail.")
            }
        }
        return {
            statusCode: 200,
            body: JSON.stringify(items)
        }
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION GETALLBLOGPOSTS ====================")
        console.error(error);
        console.error("==================================================================================")
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem extracting blog posts from the database.")
        }
    }
}