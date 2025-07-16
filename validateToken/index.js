import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET;

/** @param {import('aws-lambda').APIGatewayProxyEventV2} event */
export const handler = async (event) => {
    const cookies = event.cookies;

    const token = cookies.find((c) => c.trim().startsWith("token=")).split("=")[1];

    if (!token) {
        return {
            statusCode: 401,
            body: JSON.stringify("Missing authentication token")
        }
    }

    try {
        const user = jwt.verify(token, JWT_SECRET);

        return {
            statusCode: 200,
            body: JSON.stringify({ user })
        };
    } catch (error) {
        return {
            statusCode: 401,
            body: JSON.stringify("Invalid or expired token")
        };
    }
}