import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_developer_sample_project.aws_developer_sample_project_stack import DeveloperRbtSampleProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_developer_sample_project/aws_developer_sample_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DeveloperRbtSampleProjectStack(app, "developer-rbt-sample-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
