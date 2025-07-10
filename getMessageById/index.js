import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const REGION = "us-east-1";
const MESSAGE_TABLE = process.env.MESSAGE_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

/**  @param {import('aws-lambda').APIGatewayProxyEventV2} event */
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
            TableName: MESSAGE_TABLE,
            Key: { id }
        });

        const response = await dbclient.send(get);
        const message = response.Item;

        if (!message) {
            return {
                statusCode: 404,
                body: JSON.stringify("No message was found for this id.")
            }
        }

        return {
            statusCode: 200,
            body: JSON.stringify(message)
        }
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION GETMESSAGEBYID ====================");
        console.error(error);
        console.error("==================================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem getting message from the database.")
        }
    }
}