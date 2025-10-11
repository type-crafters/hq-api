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
