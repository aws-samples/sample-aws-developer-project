import os
import os.path
from aws_cdk import (
   Stack,
   aws_codebuild,
   aws_codecommit,
   CfnOutput,
   aws_codepipeline,
   aws_codepipeline_actions,
   aws_iam,
   RemovalPolicy
)
from constructs import Construct

build_permissions={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::*:role/cdk-*"
            ]
        }
    ]
}

class CICDStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,  **kwargs) -> None:
      super().__init__(scope, construct_id, **kwargs)
      domain=self.node.try_get_context("domain") or self.account

      repo = aws_codecommit.Repository(self, "Repository",
         repository_name="ProductsCatalog",
         description="Repo for the product catalog",
      )
      CfnOutput(self, "RepositoryUrl", value=repo.repository_clone_url_grc)
      pipeline = aws_codepipeline.Pipeline(self, "Pipeline",
         pipeline_name="ProductsCatalogPipeline",
         restart_execution_on_update=True
      )
      pipeline.artifact_bucket.enforce_ssl = True
      source_output = aws_codepipeline.Artifact("SourceOutput")
      source_stage = pipeline.add_stage(stage_name="Source")
      source_stage.add_action(
         aws_codepipeline_actions.CodeCommitSourceAction(
            action_name="SourceCode",
            repository=repo,
            output=source_output
         )
      )

      stack_name='FullApiStack'
      change_set_name='cdk-deploy-change-set' # default changeset name by cdk-deploy
      project = aws_codebuild.PipelineProject(self, "CreateChangesetProject",
         build_spec=aws_codebuild.BuildSpec.from_source_filename('buildspec.yaml')
      )
      policy_doc=aws_iam.PolicyDocument.from_json(build_permissions)
      policy=aws_iam.Policy(self,"BuildPolicy",document=policy_doc)
      project.role.attach_inline_policy(policy)
      prod_stage = {
         "stage_name": "Deploy",
         "actions": [
            aws_codepipeline_actions.CodeBuildAction(
                  action_name="PrepareChanges",
                  project=project,
                  input=source_output,
                  run_order=1
            ),
            aws_codepipeline_actions.ManualApprovalAction(
                  action_name="ApproveChanges",
                  run_order=2
            ),
            aws_codepipeline_actions.CloudFormationExecuteChangeSetAction(
                  action_name="PerformChanges",
                  stack_name=stack_name,
                  change_set_name=change_set_name,
                  run_order=3
            )
         ]
      }
      pipeline.add_stage(**prod_stage)

