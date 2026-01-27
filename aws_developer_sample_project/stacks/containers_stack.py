from aws_cdk import (
   Stack,
   aws_apigateway as apigw,
   aws_ecr_assets,
   aws_ec2,
   aws_elasticloadbalancingv2,
   aws_elasticache,
   aws_s3,
   aws_s3_notifications,
   aws_dynamodb,
   Duration,
   CfnOutput,
   RemovalPolicy,
   aws_ecs,
   aws_ecs_patterns,
   aws_iam,
   aws_cognito,
   aws_logs,
   aws_ecr_assets
)
from constructs import Construct
import os.path

class ContainersStack(Stack):

   def create_vpc(self):
      self.vpc = aws_ec2.Vpc(self, "ServiceVPC",
         max_azs=2,  # Deploy across multiple availability zones
         nat_gateways=0, # No NAT gateways neededfor ElastiCache
         gateway_endpoints={
            "DynamoDbEndpoint": aws_ec2.GatewayVpcEndpointOptions(
               service=aws_ec2.GatewayVpcEndpointAwsService.DYNAMODB
            ),
            "S3Endpoint": aws_ec2.GatewayVpcEndpointOptions(
               service=aws_ec2.GatewayVpcEndpointAwsService.S3
            )
         },
         subnet_configuration=[
               aws_ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    # This enables auto-assign public IP
                    map_public_ip_on_launch=False 
                )
            ]
      )
      self.vpc.add_interface_endpoint("EcrEndpoint",
         service=aws_ec2.InterfaceVpcEndpointAwsService.ECR
      )      
      self.vpc.add_interface_endpoint("EcrDockerEndpoint",
         service=aws_ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
      )      
      self.vpc.add_interface_endpoint("SecretsManager",
         service=aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER
      )      
      self.vpc.add_interface_endpoint("KMSEndpoint",
         service=aws_ec2.InterfaceVpcEndpointAwsService.KMS
      )      
      self.vpc.add_interface_endpoint("LogsEndpoint",
         service=aws_ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS
      )      

      self.ecs_security_group = aws_ec2.SecurityGroup(
         self, "ECSSecurityGroup",
         vpc=self.vpc,
         allow_all_outbound=True,
         description="Security group for the ECS service"
      )

      self.alb_security_group = aws_ec2.SecurityGroup(
         self, "ALBSecurityGroup",
         vpc=self.vpc,
         allow_all_outbound=True,
         description="Security group for the ALB"
      )

   def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
      super().__init__(scope, construct_id, **kwargs)

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

      docker_image_asset = aws_ecr_assets.DockerImageAsset(self, 'MyDockerImage', 
         directory= 'aws_developer_sample_project/containers',
         asset_name='m10-app',
         platform=aws_ecr_assets.Platform.LINUX_ARM64
      )
      container_image = aws_ecs.ContainerImage.from_docker_image_asset(docker_image_asset)
      self.create_vpc()
      cluster = aws_ecs.Cluster(
         self, 'fargate-service-autoscaling',
         vpc=self.vpc
      )

      fargate_task_definition = aws_ecs.FargateTaskDefinition(
            self,
            "ProductCatalogTask",
            memory_limit_mib=512, # 512 MiB of memory
            cpu=256,              # 0.25 vCPU
            runtime_platform=aws_ecs.RuntimePlatform(
                  cpu_architecture=aws_ecs.CpuArchitecture.ARM64,
                  operating_system_family=aws_ecs.OperatingSystemFamily.LINUX
            )            
      )
      self.products_table.grant_read_write_data(fargate_task_definition.task_role)
      container_definition = fargate_task_definition.add_container(
            "MyContainer",
            image = container_image,
            logging=aws_ecs.LogDrivers.aws_logs(
               stream_prefix="MyEcsLogGroup",
               log_retention=aws_logs.RetentionDays.ONE_DAY
            ),
            environment = {
               "PRODUCTS_TABLE_NAME": self.products_table.table_name
            }
      )     
      container_definition.add_port_mappings(
            aws_ecs.PortMapping(container_port=5000, host_port=5000)
      ) 

      service=aws_ecs.FargateService(
            self,
            "MyFargateService",
            cluster=cluster,
            task_definition=fargate_task_definition,
            desired_count=1
      )

      lb = aws_elasticloadbalancingv2.ApplicationLoadBalancer(self, "LB",
         vpc=self.vpc,
         internet_facing=True,
         security_group=self.alb_security_group
      )
      listener = lb.add_listener("Listener",
         port=80,
         open=True
      )
      listener.add_targets("ApplicationFleet",
         port=8080,
         targets=[service]
      )
      lb.set_attribute(
            key="routing.http.drop_invalid_header_fields.enabled",
            value="true" # Set to "true" to drop invalid headers
      )

      alb=lb.load_balancer_dns_name
      CfnOutput(self, "ProductsApiUrl", value=f'{alb}/products')
      CfnOutput(self, "UIUrl", value=f'{alb}')


