import os
from aws_cdk import (
   Stack,
   aws_lambda,
   aws_apigateway,
   aws_ec2,
   aws_elasticache,
   aws_s3,
   aws_s3_notifications,
   aws_dynamodb,
   aws_lambda_event_sources,
   aws_cognito,
   Duration,
   CfnOutput,
   RemovalPolicy,
   aws_kinesis,
   aws_iam,
   aws_kms,
   aws_logs
)
from constructs import Construct

class FullApiStack(Stack):    
   def create_vpc_etc(self):
      vpc = aws_ec2.Vpc(self, "ValkeyVPC",
         max_azs=2,  # Deploy across multiple availability zones
         nat_gateways=0, # No NAT gateways needed for ElastiCache
         gateway_endpoints={
            "DynamoDbEndpoint": aws_ec2.GatewayVpcEndpointOptions(
               service=aws_ec2.GatewayVpcEndpointAwsService.DYNAMODB
            ),
            "S3Endpoint": aws_ec2.GatewayVpcEndpointOptions(
               service=aws_ec2.GatewayVpcEndpointAwsService.S3
            )
         }
      )
      cache_subnets = vpc.select_subnets(subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED)

      # Create a Subnet Group for ElastiCache
      subnet_group = aws_elasticache.CfnSubnetGroup(
         self, "CacheSubnetGroup",
         description="Subnet group for ElastiCache cluster",
         cache_subnet_group_name="CacheSubnetGroup",
         subnet_ids=cache_subnets.subnet_ids
      )

      cache_security_group = aws_ec2.SecurityGroup(
         self, "CacheSecurityGroup",
         vpc=vpc,
         allow_all_outbound=True,
         description="Security group for ElastiCache"
      )
      # Create the ElastiCache Replication Group (Valkey Cluster)
      valkey_cluster = aws_elasticache.CfnReplicationGroup(
         self, "CacheCluster",
         replication_group_description="My Redis/Valkey Cluster",
         transit_encryption_enabled=True,
         cache_subnet_group_name="CacheSubnetGroup",
         engine="redis",  # Specify the engine as Redis
         cache_node_type="cache.t3.micro",  # Choose an appropriate instance type
         num_cache_clusters=2,  # Number of nodes in the cluster (primary + replicas)
         automatic_failover_enabled=True,
         # engine_version="7.2",  # Specify the Valkey/Redis engine version
         port=6379,
         security_group_ids=[cache_security_group.security_group_id] # Assign a security group
      )      
      
      lambda_security_group = aws_ec2.SecurityGroup(
         self, "CacheLambdaSecurityGroup",
         vpc=vpc,
         allow_all_outbound=True,
         description="Security group for get product lambda"
      )
      cache_security_group.connections.allow_from(lambda_security_group, aws_ec2.Port.tcp(6379))  
      return (vpc,valkey_cluster,lambda_security_group,cache_subnets)

   def create_gateway_only(self):
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
      return api
   def create_api_gateway(self):
      api = self.create_gateway_only()
      products_resource = api.root.add_resource("products")
      products_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.query_products))
      products_resource.add_method("POST", aws_apigateway.LambdaIntegration(self.insert_product))
      products_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))
      
      get_product_resource = products_resource.add_resource("{id}")
      get_product_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.get_product))
      get_product_resource.add_method("PUT", aws_apigateway.LambdaIntegration(self.update_product))
      get_product_resource.add_method("DELETE", aws_apigateway.LambdaIntegration(self.delete_product))
      get_product_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))

      product_images_resource = get_product_resource.add_resource("images")
      product_images_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.download))
      product_images_resource.add_method("POST", aws_apigateway.LambdaIntegration(self.upload))

      main_ui=api.root.add_resource("ui")
      main_ui.add_method("GET", aws_apigateway.LambdaIntegration(self.main_ui_lambda))


      self.api=api
      CfnOutput(self, "ProductsApiUrl", value=f'{api.url}products')
      CfnOutput(self, "UIUrl", value=f'{api.url}ui')

   def make_authorizer(self,url,cognito_domain_prefix):
      self.pool=aws_cognito.UserPool(self, "myuserpool",
         self_sign_up_enabled=True,
         auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
         password_policy=aws_cognito.PasswordPolicy(
            min_length=8,
            require_digits=True,
            require_lowercase=True,
            require_uppercase=True,
            require_symbols=True
         ),
         user_invitation=aws_cognito.UserInvitationConfig(
            email_subject="Access the product catalog!",
            email_body="Hello {username}, you have been invited to look at our product catalog! Your temporary password is {####}",
            sms_message="Hello {username}, your temporary password for ou product catalog is {####}"
         ),
         standard_attributes=aws_cognito.StandardAttributes(
            email=aws_cognito.StandardAttribute(required=True, mutable=False),
         )
      )
      self.pool.add_domain("CognitoDomain",
         cognito_domain=aws_cognito.CognitoDomainOptions(
            domain_prefix=cognito_domain_prefix.lower()
         )
      )

      self.pool_client = self.pool.add_client("MyUserPoolClient",
            auth_flows=aws_cognito.AuthFlow(user_srp=True, admin_user_password=True),
            o_auth=aws_cognito.OAuthSettings(
               flows=aws_cognito.OAuthFlows(
                  authorization_code_grant=True,
                  implicit_code_grant=True
               ),
               scopes=[aws_cognito.OAuthScope.OPENID],
               callback_urls=[url]
            ),
            prevent_user_existence_errors=True
      )
      region=Stack.of(self).region
      CfnOutput(self, "CognitoLoginUrl", value=f'https://{cognito_domain_prefix.lower()}.auth.{region}.amazoncognito.com/login?client_id={self.pool_client.user_pool_client_id}&response_type=token&redirect_uri='+url)
      CfnOutput(self, "CognitoSignupUrl", value=f'https://{cognito_domain_prefix.lower()}.auth.{region}.amazoncognito.com/signup?client_id={self.pool_client.user_pool_client_id}&response_type=token&redirect_uri='+url)
      self.authorizer=aws_apigateway.CognitoUserPoolsAuthorizer(self, 'CognitoAuthorizer', 
         cognito_user_pools=[self.pool],
      )


   def create_authenticated_api_gateway(self):
      api = self.create_gateway_only()
      cognito_domain_prefix=self.node.try_get_context("cognito_domain") or os.getenv('CDK_DEFAULT_ACCOUNT','sample_app')
      print(f"{cognito_domain_prefix=}")
      self.make_authorizer(api.url+"ui",cognito_domain_prefix)
      products_resource = api.root.add_resource("products")
      products_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.query_products))
      products_resource.add_method("POST", 
         aws_apigateway.LambdaIntegration(self.insert_product),
         authorizer=self.authorizer,
         authorization_type=aws_apigateway.AuthorizationType.COGNITO
      )
      products_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))
      
      get_product_resource = products_resource.add_resource("{id}")
      get_product_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.get_product))
      get_product_resource.add_method("PUT", aws_apigateway.LambdaIntegration(self.update_product),authorizer=self.authorizer,authorization_type=aws_apigateway.AuthorizationType.COGNITO)
      get_product_resource.add_method("DELETE", aws_apigateway.LambdaIntegration(self.delete_product),authorizer=self.authorizer,authorization_type=aws_apigateway.AuthorizationType.COGNITO)
      get_product_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))

      product_images_resource = get_product_resource.add_resource("images")
      product_images_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.download))
      product_images_resource.add_method("POST", aws_apigateway.LambdaIntegration(self.upload),authorizer=self.authorizer,authorization_type=aws_apigateway.AuthorizationType.COGNITO)

      ui_resource = api.root.add_resource("ui")
      ui_resource.add_method("GET", aws_apigateway.LambdaIntegration(self.main_ui_lambda))
      ui_resource.add_method("OPTIONS", aws_apigateway.LambdaIntegration(self.options_handler))

      self.api=api
      CfnOutput(self, "ProductsApiUrl", value=api.url)


   def create_redis_lambda(self,name,cache_url,code_file,vpc,cache_subnets,lambda_security_group):
      if vpc:
         return aws_lambda.Function(self, name,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            architecture=aws_lambda.Architecture.ARM_64,
            handler=f"{code_file}.handler",
            code=aws_lambda.Code.from_asset(self.code_location),
            environment={
               "CACHE_CLUSTER_URL": cache_url,
               "PRODUCTS_TABLE_NAME": "full_api_products"
            },
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=cache_subnets.subnets),
            layers=[self.redis_layer],
            security_groups=[lambda_security_group],
            timeout=Duration.seconds(30)
         )
      else:
         return aws_lambda.Function(self, name,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            architecture=aws_lambda.Architecture.ARM_64,
            handler=f"{code_file}.handler",
            code=aws_lambda.Code.from_asset(self.code_location),
            environment={
               "CACHE_CLUSTER_URL": "",
               "PRODUCTS_TABLE_NAME": "full_api_products"
            },
            layers=[self.redis_layer],
            timeout=Duration.seconds(30)
         )


   def create_lambda(self,name, code_file,layers=[]):
      return aws_lambda.Function(self, name,
         runtime=aws_lambda.Runtime.PYTHON_3_12,
         architecture=aws_lambda.Architecture.ARM_64,
         layers=layers,
         handler=f"{code_file}.handler",
         code=aws_lambda.Code.from_asset(self.code_location),
         timeout=Duration.seconds(10)
      )


   def create_image_lambda(self,name, code_file,s3_bucket):
      return aws_lambda.Function(self, name,
         runtime=aws_lambda.Runtime.PYTHON_3_12,
         architecture=aws_lambda.Architecture.ARM_64,
         handler=f"{code_file}.handler",
         code=aws_lambda.Code.from_asset(self.code_location),
         timeout=Duration.seconds(10),
         environment={
            "BUCKET_NAME": s3_bucket.bucket_name,
            "PRODUCTS_TABLE_NAME": "full_api_products"
         }
      )

   def create_stream_and_processing(self):
      stream=aws_kinesis.Stream(self, "ProductPricesStream",stream_name='ProductPricesStream')

      self.process_price_updates= aws_lambda.Function(self, "ProcessPriceUpdates",
         runtime=self.lambda_runtime,
         handler="process_stream_prices.handler",
         code=aws_lambda.Code.from_asset(self.code_location),
         environment={
            "PRODUCTS_TABLE_NAME": "full_api_products"
         },         
      )
      self.process_price_updates.add_event_source(aws_lambda_event_sources.KinesisEventSource(stream,
         batch_size=100,
         starting_position=aws_lambda.StartingPosition.LATEST
      ))

   def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
      super().__init__(scope, construct_id, **kwargs)
      self.lambda_prefix="FullApi"
      self.key=aws_kms.Key(self, self.lambda_prefix+"Key", 
            enable_key_rotation=True,
      )
      self.key.grant_encrypt_decrypt(
            grantee=aws_iam.ServicePrincipal(f"logs.{self.region}.amazonaws.com")
      )

      bucket=aws_s3.Bucket(self, "ImagesBucket",
               versioned=True, 
               block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
               encryption=aws_s3.BucketEncryption.S3_MANAGED,
               object_ownership=aws_s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
               removal_policy=RemovalPolicy.DESTROY,
               auto_delete_objects=True,
               enforce_ssl= True,
      )
      products_table=aws_dynamodb.Table(self,"ProductsTable",            
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

      products_table.add_global_secondary_index(
         index_name="category-index",
         partition_key=aws_dynamodb.Attribute(
               name="category", type=aws_dynamodb.AttributeType.STRING
         )
      )

      self.code_location=os.path.join(os.path.dirname(__file__), "../full_api")
      self.lambda_runtime=aws_lambda.Runtime.PYTHON_3_12
      ui_code_location=os.path.join(os.path.dirname(__file__), "../ui")

      if self.node.try_get_context("create_cache")=="true":
         print("FullApiStack creating with cache")
         (vpc,valkey_cluster,lambda_security_group,cache_subnets)=self.create_vpc_etc()
      else:
         (vpc,valkey_cluster,lambda_security_group,cache_subnets)=(None,None,None,None)

      self.redis_layer=aws_lambda.LayerVersion(self, "RedisLayer",
         removal_policy=RemovalPolicy.DESTROY,
         code=aws_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "../layers/redis-layer-python.zip")),
         compatible_architectures=[aws_lambda.Architecture.ARM_64]
      )

      pillow_layer=aws_lambda.LayerVersion(self, "PillowLayer",
         removal_policy=RemovalPolicy.DESTROY,
         code=aws_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "../layers/pil-layer-python.zip")),
         compatible_architectures=[aws_lambda.Architecture.ARM_64]
      )
      cache_url = valkey_cluster.attr_primary_end_point_address if valkey_cluster else ""
      self.query_products= self.create_redis_lambda(
         name="QueryProducts", 
         cache_url = cache_url, 
         code_file="query_products", 
         vpc=vpc, 
         cache_subnets=cache_subnets,
         lambda_security_group=lambda_security_group
      ) 
      products_table.grant_read_data(self.query_products)

      self.insert_product= self.create_redis_lambda(
         name="InsertProduct", 
         cache_url = cache_url, 
         code_file="insert_product", 
         vpc=vpc, 
         cache_subnets=cache_subnets,
         lambda_security_group=lambda_security_group
      )
      products_table.grant_read_write_data(self.insert_product)

      self.update_product= self.create_redis_lambda(
         name="UpdateProduct", 
         cache_url = cache_url, 
         code_file="update_product", 
         vpc=vpc, 
         cache_subnets=cache_subnets,
         lambda_security_group=lambda_security_group
      )
      products_table.grant_read_write_data(self.update_product)

      self.options_handler= self.create_lambda(
         name="Options", 
         code_file="options", 
      )


      self.upload = self.create_image_lambda(
         name="GenerateUploadUrl", 
         s3_bucket=bucket,
         code_file="generate_upload_url", 
      )
      bucket.grant_read_write(self.upload)

      self.download = self.create_image_lambda(
         name="GenerateDownloadUrl",
         s3_bucket=bucket, 
         code_file="generate_download_url", 
      )
      bucket.grant_read(self.download)


      self.delete_product=self.create_redis_lambda(
         name="DeleteProduct", 
         cache_url = cache_url, 
         code_file="delete_product", 
         vpc=vpc, 
         cache_subnets=cache_subnets,
         lambda_security_group=lambda_security_group
      ) 
      products_table.grant_read_write_data(self.delete_product)


      self.get_product= self.create_redis_lambda(
         name="GetProduct", 
         cache_url = cache_url, 
         code_file="get_product", 
         vpc=vpc, 
         cache_subnets=cache_subnets,
         lambda_security_group=lambda_security_group
      )
      products_table.grant_read_data(self.get_product)
      # self.get_product.connections.allow_internally(aws_ec2.Port.tcp(6379)) # Allow access to Redis

      self.main_ui_lambda= aws_lambda.Function(self, "MainUI",
         runtime=self.lambda_runtime,
         handler="main_ui.handler",
         code=aws_lambda.Code.from_asset(ui_code_location)
      )

      if self.node.try_get_context("authenticated")=="true":
         self.create_authenticated_api_gateway()
      else:
         self.create_api_gateway()

      self.process_images= self.create_lambda(
         name="ProcessImages", 
         code_file="process_uploaded_images",
         layers=[pillow_layer]
      )
      products_table.grant_read_write_data(self.process_images)
      bucket.grant_read_write(self.process_images)

      bucket.add_event_notification(
         aws_s3.EventType.OBJECT_CREATED_PUT,
         aws_s3_notifications.LambdaDestination(self.process_images),
         aws_s3.NotificationKeyFilter(prefix="incoming_product_images/", suffix=".png")
      )

      if self.node.try_get_context("create_stream")=="true":
         print("FullApiStack creating streams")
         self.create_stream_and_processing()



