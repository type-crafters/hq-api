import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, ScanCommand } from "@aws-sdk/lib-dynamodb"

const REGION = "us-east-1";
const MESSAGE_TABLE = process.env.MESSAGE_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

export const handler = async (event) => {
    try {
        const scan = new ScanCommand({
            TableName: MESSAGE_TABLE
        });
        const response = await dbclient.send(scan);
        const messages = response.Items;
        return {
            statusCode: 200,
            body: JSON.stringify(messages)
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