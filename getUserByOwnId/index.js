import jwt from "jsonwebtoken";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const REGION = "us-east-1";
const ADMIN_USER_TABLE = process.env.ADMIN_USER_TABLE;
const BUCKET_NAME = process.env.BUCKET_NAME;
const JWT_SECRET = process.env.JWT_SECRET;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));
const s3 = new S3Client({ region: REGION });

/**  @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    try {
        const token = event.cookies.find((cookie) => cookie.trim().startsWith("token")).split("=")[1];
        const { id } = jwt.verify(token, JWT_SECRET);

        if (!id) {
            return {
                statusCode: 401,
                body: JSON.stringify("Unauthorized access"),
            };
        }
        const userData = await dbclient.send(new GetCommand({
            TableName: ADMIN_USER_TABLE,
            Key: { id: id }
        }));

        if (!userData.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: "User not found" }),
            };
        }

        const user = userData.Item;

        if (user.profilePicture) {
            const getObjectCmd = new GetObjectCommand({
                Bucket: BUCKET_NAME,
                Key: user.profilePicture,
            });

            user.profilePicture = await getSignedUrl(s3, getObjectCmd, { expiresIn: 3600 });
        }

        return {
            statusCode: 200,
            body: JSON.stringify(user),
            headers: {
                "Content-Type": "application/json",
            },
        };
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION GETUSERBYOWNID ====================");
        console.error(error);
        console.error("============================================ =================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem getting the user from the database.")
        }
    }
};
