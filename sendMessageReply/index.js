import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, UpdateCommand } from "@aws-sdk/lib-dynamodb";
import nodemailer from "nodemailer";

const REGION = "us-east-1";
const GMAIL_ADDRESS = process.env.GMAIL_ADDRESS;
const GMAIL_APP_PASSWORD = process.env.GMAIL_APP_PASSWORD;
const MESSAGE_TABLE = process.env.MESSAGE_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }))

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    const { id, message, replyTo } = JSON.parse(event.body);

    const transporter = nodemailer.createTransport({
        service: "gmail",
        auth: {
            user: GMAIL_ADDRESS,
            pass: GMAIL_APP_PASSWORD
        }
    });

    try {
        await transporter.sendMail({
            from: `TypeCrafters <${GMAIL_ADDRESS}>`,
            to: replyTo,
            subject: "Your inquiry through TypeCrafters HQ",
            text: message
        });

        try {
            await dbclient.send(new UpdateCommand({
                TableName: MESSAGE_TABLE,
                Key: { id },
                UpdateExpression: "set replied = :value",
                ExpressionAttributeValues: {
                    ":value": true
                }
            }));

            return {
                statusCode: 204
            }
        } catch (error) {
            console.error("==================== ERROR IN LAMBDA FUNCTION SENDMESSAGEREPLY ====================");
            console.error(error);
            console.error("===================================================================================");
            return {
                statusCode: 500,
                body: JSON.stringify("There was a problem updating the message's reply status.")
            }
        }


    } catch (error) {
        console.error("==================== ERROR IN LAMBDA FUNCTION SENDMESSAGEREPLY ====================");
        console.error(error);
        console.error("===================================================================================");
        return {
            statusCode: 500,
            body: JSON.stringify("There was a problem sending a reply.")
        }
    }
}