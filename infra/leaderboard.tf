resource "aws_dynamodb_table" "scores" {
  name         = "condor-scores"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "jugador"

  attribute {
    name = "jugador"
    type = "S"
  }
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../serverless/lambda_function.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_iam_role" "lambda" {
  name = "condor-leaderboard-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "dynamo" {
  name = "dynamo-scores"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:UpdateItem", "dynamodb:Scan"]
      Resource = aws_dynamodb_table.scores.arn
    }]
  })
}

resource "aws_lambda_function" "leaderboard" {
  function_name    = "condor-leaderboard"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  environment {
    variables = { TABLA = aws_dynamodb_table.scores.name }
  }
}

resource "aws_lambda_function_url" "leaderboard" {
  function_name      = aws_lambda_function.leaderboard.function_name
  authorization_type = "NONE"
}

# Permisos para invocar la Function URL públicamente (AWS exige ambos)
resource "aws_lambda_permission" "url" {
  statement_id           = "AllowPublicFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.leaderboard.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "invoke" {
  statement_id  = "AllowPublicInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.leaderboard.function_name
  principal     = "*"
}
