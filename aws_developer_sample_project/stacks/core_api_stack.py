import os
from aws_cdk import (
   Stack,
   aws_lambda,
   aws_apigateway,
   aws_dynamodb,
   CfnOutput,
   aws_logs,
   aws_kms,
   Duration,
   RemovalPolicy,
   aws_iam
)
from constructs import Construct

class CoreApiStack(Stack):
    
   def create_api_gateway(self):
      log_group = aws_logs.LogGroup(self, "ApiGWLogGroup",
         encryption_key = self.key,
         retention = aws_logs.RetentionDays.ONE_DAY
      )
      api = aws_apigateway.RestApi(
         self, "ProductsAPI",
         rest_api_name="ProductsApi",
         description="Amazon API Gateway for ProductsAPI.",
         deploy_options=aws_apigateway.StageOptions(
               stage_name="dev",
               access_log_destination=aws_apigateway.LogGroupLogDestination(log_group),
               logging_level=aws_apigateway.MethodLoggingLevel.INFO,
               data_trace_enabled=True
         ),
      )
      products_resource = api.root.add_resource("products")
      products_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.query_products))
      products_resource.add_method("POST", aws_apigateway.LambdaIntegration(self.insert_product))
      products_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))
      
      get_product_resource = products_resource.add_resource("{id}")
      get_product_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.get_product))
      get_product_resource.add_method("PUT", aws_apigateway.LambdaIntegration(self.update_product))
      get_product_resource.add_method("DELETE", aws_apigateway.LambdaIntegration(self.delete_product))
      get_product_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))

      main_ui=api.root.add_resource("ui")
      main_ui.add_method("GET", aws_apigateway.LambdaIntegration(self.main_ui_lambda))

      self.api=api
      CfnOutput(self, "ProductsApiUrl", value=f'{api.url}products')
      CfnOutput(self, "UIUrl", value=f'{api.url}ui')

   def create_lambda(self,name, code_file, code_location=None):
      function_name = self.lambda_prefix + "_" + name
      log_group = aws_logs.LogGroup(self, f'lg_{name}',
         log_group_name = f'/aws/lambda/{function_name}',
         encryption_key = self.key
      )
      
      return aws_lambda.Function(self, name,
         runtime=self.lambda_runtime,
         architecture=aws_lambda.Architecture.ARM_64,
         environment={
            "PRODUCTS_TABLE_NAME": self.products_table.table_name
         },
         environment_encryption = self.key,
         handler=f"{code_file}.handler",
         code=aws_lambda.Code.from_asset(code_location or self.code_location),
         timeout=Duration.seconds(10),
         reserved_concurrent_executions = self.default_concurrent_executions,
         function_name = function_name,
         log_group=log_group,
      )


   def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
      super().__init__(scope, construct_id, **kwargs)

      self.code_location=os.path.join(os.path.dirname(__file__), "../core_api")
      self.ui_code_location=os.path.join(os.path.dirname(__file__), "../ui")
      self.lambda_runtime=aws_lambda.Runtime.PYTHON_3_12
      self.default_concurrent_executions=5
      self.lambda_prefix="CoreApi"
      self.key=aws_kms.Key(self, self.lambda_prefix+"Key", 
            enable_key_rotation=True,
      )
      self.key.grant_encrypt_decrypt(
            grantee=aws_iam.ServicePrincipal(f"logs.{self.region}.amazonaws.com")
      )
      self.products_table=aws_dynamodb.Table(self,"ProductsTable",            
         partition_key=aws_dynamodb.Attribute(
               name="id", 
               type=aws_dynamodb.AttributeType.STRING
         ),
         # WARNING - This is for testing ONLY, not for PROD
         removal_policy=RemovalPolicy.DESTROY,
         # Default, but let's make explicit
         encryption=aws_dynamodb.TableEncryption.AWS_MANAGED,
         billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
      )

      self.products_table.add_global_secondary_index(
         index_name="category-index",
         partition_key=aws_dynamodb.Attribute(
               name="category", type=aws_dynamodb.AttributeType.STRING
         )
      )

      self.main_ui_lambda= self.create_lambda( "MainUI", code_file="main_ui",code_location=self.ui_code_location)

      self.get_product= self.create_lambda("GetProduct", code_file="get_product")
      self.products_table.grant_read_data(self.get_product)

      self.query_products= self.create_lambda("QueryProducts", code_file="query_products")
      self.products_table.grant_read_data(self.query_products)

      self.insert_product= self.create_lambda("InsertProduct", code_file="insert_product")
      self.products_table.grant_read_write_data(self.insert_product)

      self.update_product= self.create_lambda("UpdateProduct", code_file="update_product")
      self.products_table.grant_read_write_data(self.update_product)

      self.delete_product= self.create_lambda("DeleteProduct", code_file="delete_product")
      self.products_table.grant_read_write_data(self.delete_product)

      self.options_handler= self.create_lambda("APIOptions", code_file="options")
      self.create_api_gateway()

