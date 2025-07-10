import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { randomUUID } from "crypto";

const REGION = "us-east-1";
const MESSAGE_TABLE = process.env.MESSAGE_TABLE;

const dynamodb = new DynamoDBClient({ region: REGION });
const dbclient = DynamoDBDocumentClient.from(dynamodb);

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {

    let data;

    try {
        data = JSON.parse(event.body);

        const requiredKeys = ["name", "email", "subject", "message"];

        for (let key of requiredKeys) {
            if (!(key in data)) {
                return {
                    statusCode: 422,
                    body: JSON.stringify("Missing required field '" + key + "' in body.")
                }
            }
        }
    } catch {
        return {
            statusCode: 400,
            body: JSON.stringify("Request was sent without an appropriate body.")
        }
    }

    const put = new PutCommand({
        TableName: MESSAGE_TABLE,
        Item: {
            id: randomUUID(),
            name: data.name,
            replyTo: data.email,
            subject: data.subject,
            message: data.message,
            receivedAt: new Date().toISOString()
        }
    });

    try {
        await dbclient.send(put);
        return {
            statusCode: 201,
            body: JSON.stringify("Message sent!")
        }
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION SENDMESSAGE ====================");
        console.error(error);
        console.error("==============================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem saving the message to the database.")
        }
    }
}