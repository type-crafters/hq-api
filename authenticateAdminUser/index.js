import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand } from "@aws-sdk/lib-dynamodb";

const REGION = "us-east-1";
const JWT_SECRET = process.env.JWT_SECRET;
const ADMIN_USER_TABLE = process.env.ADMIN_USER_TABLE;

const dbclient = DynamoDBDocumentClient.from(new DynamoDBClient({ region: REGION }));

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    const { email, password } = JSON.parse(event.body);

    if (!email || !password) {
        return {
            statusCode: 400,
            body: JSON.stringify("Missing required credentials")
        };
    }

    const result = await dbclient.send(new QueryCommand({
        TableName: ADMIN_USER_TABLE,
        IndexName: "email-index",
        KeyConditionExpression: "email = :email",
        ExpressionAttributeValues: {
            ":email": email
        }
    }));

    const user = result.Items?.[0];

    if (!user) {
        return {
            statusCode: 401,
            body: JSON.stringify("Invalid email or password.")
        };
    }

    const passwordsMatch = await bcrypt.compare(password, user.password);

    if (passwordsMatch) {
        const token = jwt.sign({
            id: user.id,
            email: user.email,
            role: user.role
        },
            JWT_SECRET,
            { expiresIn: "1h" }
        );

        return {
            statusCode: 200,
            headers: {
                "Set-Cookie": `token=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify("Login successful")
        };
    } else {
        return {
            statusCode: 401,
            body: JSON.stringify("Invalid email or password.")
        };
    }
};