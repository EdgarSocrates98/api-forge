resource "aws_api_gateway_rest_api" "orders" {
  name = "orders-api"
}

resource "aws_api_gateway_method" "create" {
  rest_api_id   = aws_api_gateway_rest_api.orders.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "create" {
  http_method             = "POST"
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  timeout_milliseconds    = 29000
  uri                     = aws_lambda_function.orders.invoke_arn
}

resource "aws_api_gateway_stage" "prod" {
  stage_name    = "prod"
  xray_tracing_enabled = true
}

resource "aws_lambda_function" "orders" {
  function_name = "orders-api"
  runtime       = "python3.12"
  memory_size   = 256
  timeout       = 30
  handler       = "app.handler"
  reserved_concurrent_executions = 10
  environment {
    variables = {
      ORDERS_TABLE = "value-not-read"
      LOG_LEVEL    = "INFO"
    }
  }
}

resource "aws_lambda_permission" "apigw" {
  function_name = aws_lambda_function.orders.function_name
  principal     = "apigateway.amazonaws.com"
  action        = "lambda:InvokeFunction"
  source_arn    = "${aws_api_gateway_rest_api.orders.execution_arn}/*/*"
}
