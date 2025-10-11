variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lambda_path" {
  type = string
  default = "../lambda"
}

variable "dist_path" {
    type = string
    default = "../dist"
}

variable "policies" {
    type = map(string)
    default = {
        HQDynamoAccess = "arn:aws:iam::657506130101:policy/HQDynamoAccess"
        HQObjectAccess = "arn:aws:iam::657506130101:policy/HQObjectAccess"
    }
}