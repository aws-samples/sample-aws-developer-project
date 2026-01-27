import os
from aws_cdk import (
    Stack,
    aws_lambda,
    aws_apigateway,
    CfnOutput
)
from constructs import Construct

class InitialApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,  **kwargs) -> None:
      super().__init__(scope, construct_id, **kwargs)

      code_location=os.path.join(os.path.dirname(__file__), "../initial_api")
      ui_code_location=os.path.join(os.path.dirname(__file__), "../ui")
      lambda_runtime=aws_lambda.Runtime.PYTHON_3_12
      default_concurrent_executions = 5

      self.main_ui_lambda= aws_lambda.Function(self, "MainUI",
         runtime=lambda_runtime,
         handler="main_ui.handler",
         code=aws_lambda.Code.from_asset(ui_code_location),
         reserved_concurrent_executions = default_concurrent_executions,
      )

      self.get_product= aws_lambda.Function(self, "GetProduct",
         runtime=lambda_runtime,
         handler="get_product.handler",
         code=aws_lambda.Code.from_asset(code_location),
         reserved_concurrent_executions = default_concurrent_executions
      )

      self.query_products= aws_lambda.Function(self, "QueryProducts",
         runtime=lambda_runtime,
         handler="query_products.handler",
         code=aws_lambda.Code.from_asset(code_location),
         reserved_concurrent_executions = default_concurrent_executions
      )

      self.insert_product= aws_lambda.Function(self, "InsertProduct",
         runtime=lambda_runtime,
         handler="insert_product.handler",
         code=aws_lambda.Code.from_asset(code_location),
         reserved_concurrent_executions = default_concurrent_executions
      )

      self.update_product= aws_lambda.Function(self, "UpdateProduct",
         runtime=lambda_runtime,
         handler="update_product.handler",
         code=aws_lambda.Code.from_asset(code_location),
         reserved_concurrent_executions = default_concurrent_executions,
      )

      self.options_handler= aws_lambda.Function(self, "APIOptions",
         runtime=lambda_runtime,
         handler="options.handler",
         code=aws_lambda.Code.from_asset(code_location),
         reserved_concurrent_executions = default_concurrent_executions,
      )

      api = aws_apigateway.RestApi(
         self, "ProductsAPI",
         rest_api_name="ProductsApi",
         description="Amazon API Gateway for ProductsAPI.",
         deploy_options=aws_apigateway.StageOptions(
               stage_name="dev",
               logging_level=aws_apigateway.MethodLoggingLevel.INFO,
         )
      )
      products_resource = api.root.add_resource("products")
      products_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.query_products))
      products_resource.add_method("POST", aws_apigateway.LambdaIntegration(self.insert_product))
      products_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))
      
      get_product_resource = products_resource.add_resource("{id}")
      get_product_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.get_product))
      get_product_resource.add_method("PUT", aws_apigateway.LambdaIntegration(self.update_product))
      get_product_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))

      ui_resource = api.root.add_resource("ui")
      ui_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.main_ui_lambda))

      self.api=api
      CfnOutput(self, "ProductsApiUrl", value=f'{api.url}products')
      CfnOutput(self, "UIUrl", value=f'{api.url}ui')


