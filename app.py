#!/usr/bin/env python3
import os

import aws_cdk as cdk
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from aws_developer_sample_project.stacks.initial_api_stack import InitialApiStack
from aws_developer_sample_project.stacks.core_api_stack import CoreApiStack
from aws_developer_sample_project.stacks.full_api_stack import FullApiStack
from aws_developer_sample_project.stacks.containers_stack import ContainersStack
from aws_developer_sample_project.stacks.cicd_stack import CICDStack

app = cdk.App()
InitialApiStack(app, "InitialApiStack")
CoreApiStack(app, "CoreApiStack")
FullApiStack(app, "FullApiStack")
ContainersStack(app, "ContainersStack")
CICDStack(app, "CICDStack")

AwsSolutionsChecks().visit(app)
app.synth()
