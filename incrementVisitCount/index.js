import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, UpdateCommand } from "@aws-sdk/lib-dynamodb";

const REGION = "us-east-1";
const VISIT_TABLE = process.env.VISIT_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    try {
        await dbclient.send(new UpdateCommand({
            TableName: VISIT_TABLE,
            Key: {
                year: new Date().getFullYear(),
                month: new Date().getMonth() + 1
            },
            UpdateExpression: "SET #v = if_not_exists(#v, :zero) + :i",
            ExpressionAttributeNames: { "#v": "visits" },
            ExpressionAttributeValues: {
                ":zero": 0,
                ":i": 1
            }
        }));

        return {
            statusCode: 204
        };
    } catch (error) {
        if (error.name === "ConditionalCheckFailedException") {
            return;
        } else {
            console.error("==================== ERROR IN LAMBDA FUNCTION INCREMENTVISITCOUNT ====================");
            console.error(error);
            console.error("======================================================================================");
            return {
                statusCode: 500,
                body: JSON.stringify("There was a problem getting the visit count from the database.")
            }
        }
    }
}