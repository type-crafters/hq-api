import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand, ScanCommand } from "@aws-sdk/lib-dynamodb";

const REGION = "us-east-1";
const VISIT_TABLE = process.env.VISIT_TABLE;
const BLOG_POST_TABLE = process.env.BLOG_POST_TABLE;
const MESSAGE_TABLE = process.env.MESSAGE_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    try {
        const pageVisits = await dbclient.send(new GetCommand({
            TableName: VISIT_TABLE,
            Key: {
                year: new Date().getFullYear(),
                month: new Date().getMonth() + 1
            }
        }));

        const featuredPosts = await dbclient.send(new ScanCommand({
            TableName: BLOG_POST_TABLE,
            FilterExpression: "#r = :val",
            ExpressionAttributeNames: { "#r": "featured" },
            ExpressionAttributeValues: { ":val": true },
            Select: "COUNT",
        }));

        const newMessages = await dbclient.send(new ScanCommand({
            TableName: MESSAGE_TABLE,
            FilterExpression: "#r = :val",
            ExpressionAttributeNames: { "#r": "replied" },
            ExpressionAttributeValues: { ":val": false },
            Select: "COUNT",
        }));

        return {
            statusCode: 200,
            body: JSON.stringify({
                visits: pageVisits.Item?.visits || 0,
                featuredPosts: featuredPosts.Count || 0,
                newMessages: newMessages.Count || 0
            })
        };
    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION GETALLSTATS ====================");
        console.error(error);
        console.error("==============================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem getting the page's stats.")
        }
    }
}