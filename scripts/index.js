import fs from "fs";
import path from "path";
import { execSync } from "child_process";

const LAMBDA_ROOT = path.resolve(path.join(import.meta.dirname, "..", "lambda"));

console.log(LAMBDA_ROOT)

const npm = () => process.platform === "win32" ? "npm.cmd" : "npm";

/** @param {string} str */
const splitCamel = (str) => {
    let i = 0;
    let words = [];

    str.split("").forEach((char, index) => {
        if (index > 0 && char === char.toUpperCase() && char !== char.toLowerCase()) {
            words.push(str.slice(i, index));
            i = index;
        }
    });

    words.push(str.slice(i));
    return words.join(" ");
};


function testAll() {
    try {
        fs.readdirSync(LAMBDA_ROOT, { withFileTypes: true }).forEach((entry) => {
            if (entry.isDirectory()) {
                const lambda = path.resolve(path.join(LAMBDA_ROOT, entry.name));

                if (fs.existsSync(path.join(lambda, "package.json"))) {

                    try {
                        const { stdout, stderr } = execSync(`${npm()} run test`, { cwd: lambda });
                        if (stderr) console.error(stderr);
                        console.log(stdout);
                    } catch (error) {
                        console.error("Tests failed in %s: %s", lambda, error);
                    }
                }
            }
        });
    } catch (error) {
        console.error(error);
    }
}

function restoreAll() {
    try {
        fs.readdirSync(LAMBDA_ROOT, { withFileTypes: true }).forEach((entry) => {
            if (entry.isDirectory()) {
                const lambda = path.resolve(path.join(LAMBDA_ROOT, entry.name));

                if (fs.existsSync(path.join(lambda, "package.json"))) {
                    try {
                        const { stdout, stderr } = execSync(`${npm()} install`, { cwd: lambda });
                        if (stderr) console.error(stderr);
                        console.log(stdout);
                    } catch (error) {
                        console.error("Tests failed in %s: %s", lambda, error);
                    }
                }
            }
        });
    } catch (error) {
        console.error(error);
    }
}

/** @param {string} name */
function createLambda(name) {
    const indexJs = () => [
        "/** @param {import(\"aws-lambda\").APIGatewayProxyEventV2} event */",
        "export const handler = async (event) => {",
        " ".repeat(4) + "return {",
        " ".repeat(8) + "statusCode: 200,",
        " ".repeat(8) + "body: JSON.stringify(\"Hello from Lambda!\")",
        " ".repeat(4) + "}",
        "}"
    ].join("\n");

    const packageJson = () => JSON.stringify({
        name: splitCamel(name).toLowerCase().replaceAll(" ", "-"),
        version: "0.1.0",
        description: `Lambda function project for ${name}`,
        keywords: ["AWS", "Lambda", "Serverless", "Functions"],
        private: true,
        type: "module",
        main: "index.js",
        author: {
            name: "TypeCrafters Web Division (TWD)",
            email: "typecrafters0@gmail.com",
            url: "https://www.typecrafters.org/"
        },
        scripts: {
            test: "echo \"Error: no test specified\" && exit 1"
        }
    }, null, 4);

    const dirpath = path.resolve(path.join(LAMBDA_ROOT, name));
    if (fs.existsSync(dirpath)) {
        console.error("Directory '%s' already exists at lambda path %s", name, LAMBDA_ROOT);
        process.exit(1);
    }

    fs.mkdirSync(dirpath);
    fs.writeFileSync(path.join(dirpath, "package.json"), packageJson());
    fs.writeFileSync(path.join(dirpath, "index.js"), indexJs());
}

const args = process.argv.slice(2);

switch (args[0]) {
    case "test":
        testAll();
        break;
    case "install":
        restoreAll();
        break;
    case "lambda":
        const name = args[1];
        if (!name) {
            console.error("Required option 'name' not provided. Usage: node index.js lambda <pascalName>");
            process.exit(1);
        }
        createLambda(name);
        break;
    default:
        console.error("Unknown command '%s'. Usage: node index.js <test | install | lambda> <...options>", args[0]);
        process.exit(1);
}