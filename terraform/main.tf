terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  lambda_src = toset(distinct([
    for f in fileset(var.lambda_path, "**/lambda_function.py") : dirname(f)
  ]))

  lambda_config = {
    for f in local.lambda_src :
    f => yamldecode(file("${var.lambda_path}/${f}/service.yml"))
  }

  lambda_env = {
    for f in local.lambda_src :
    f => (fileexists("${var.lambda_path}/${f}/.env") ?
      { for line in split("\n", file("${var.lambda_path}/${f}/.env")) :
        split("=", line)[0] => split("=", line)[1] if length(split("=", line)) == 2
      } : {}
    )
  }
}

# Create a Lambda role for each function
resource "aws_iam_role" "exec_role" {
  for_each = local.lambda_src

  name = "lambda_${each.value}_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach the AWSLambdaBasicExecutionRole policy to each role created
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  for_each = aws_iam_role.exec_role

  role       = each.value.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach additional required policies, as declared by the policies array of service.yml
resource "aws_iam_role_policy_attachment" "additional_policies" {
  for_each = merge([
    for lambda, config in local.lambda_config : {
      for policy in lookup(config, "policies", []) :
      "${lambda}:${policy}" => {
        lambda = lambda
        policy = policy
      }
      if contains(keys(var.policies), policy)
    }
  ]...)

  role       = aws_iam_role.exec_role[each.value.lambda].name
  policy_arn = var.policies[each.value.policy]
}

# Compress each lambda function into a .zip file in dist/
data "archive_file" "lambda_zip" {
  for_each = { for f in local.lambda_src : f => f }

  type       = "zip"
  source_dir = "${var.lambda_path}/${each.key}"

  excludes = [".env", "service.yml", "requirements.txt", ".venv"]

  output_path = "${var.dist_path}/${each.key}.zip"
}

# Create the lambda function resource in AWS
resource "aws_lambda_function" "lambda" {
  for_each = data.archive_file.lambda_zip

  function_name = each.key
  description   = "[${replace(timestamp(), "T", " ")}] Terraform-generated Lambda function ${each.key}"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"
  role          = aws_iam_role.exec_role[each.key].arn
  filename      = each.value.output_path
  environment {
    variables = local.lambda_env[each.key]
  }
}


# Create the ApiGatewayV2 HTTP API
resource "aws_apigatewayv2_api" "hq-api" {
  name          = "hq-api"
  protocol_type = "HTTP"
}

# Add invoke pemission to all lambdas for API Gateway
resource "aws_lambda_permission" "api_invoke" {
  for_each = aws_lambda_function.lambda

  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.hq-api.execution_arn}/*/*"
}

# Create a Lambda Function integration for each route
resource "aws_apigatewayv2_integration" "lambda_integration" {
  for_each = local.lambda_config

  api_id                 = aws_apigatewayv2_api.hq-api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.lambda[each.key].invoke_arn
  payload_format_version = "2.0"
}

# Create a route with the method and path specified on each lambda function's service.yml 
# Attach each integration
resource "aws_apigatewayv2_route" "api_route" {
  for_each = local.lambda_config

  api_id    = aws_apigatewayv2_api.hq-api.id
  route_key = "${each.value.method} ${each.value.path}"


  target = "integrations/${aws_apigatewayv2_integration.lambda_integration[each.key].id}"
}

# Create an ApiGatewayV2 deployment resource
resource "aws_apigatewayv2_deployment" "hq_api_deployment" {
  api_id = aws_apigatewayv2_api.hq-api.id

  triggers = {
    redeployment = sha1(jsonencode({
      routes       = aws_apigatewayv2_route.api_route
      integrations = aws_apigatewayv2_integration.lambda_integration
    }))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Add the $default stage to the deployment
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.hq-api.id
  name        = "$default"
  auto_deploy = true

  deployment_id = aws_apigatewayv2_deployment.hq_api_deployment.id
}

output "api_endpoint" {
  value = aws_apigatewayv2_stage.default.invoke_url
}