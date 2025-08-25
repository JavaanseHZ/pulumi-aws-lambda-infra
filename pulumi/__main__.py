import json
import pulumi
import pulumi_aws as aws
import pulumi_gcp as gcp
import subprocess

#########################
## Google Cloud Access ##
#########################
## gcloud service account and api key saved in aws secret

gcloud_config = pulumi.Config("gcp")
gcloud_project_id = gcloud_config.require("project")

gcloud_translate_service_account = gcp.serviceaccount.Account(
    "translate-service-account",
    account_id="translate-service-account",
    display_name="translate-service-account"
)

gcloud_translate_iam_binding = gcp.projects.IAMBinding(
    "translate-service-account-iam-binding",
    project=gcloud_project_id,
    role="roles/cloudtranslate.user",
    members=[gcloud_translate_service_account.member]
)

gcloud_translate_service_account_key = gcp.serviceaccount.Key(
    "translate-service-account-api-key",
    service_account_id=gcloud_translate_service_account.name
)

aws_translate_secret = aws.secretsmanager.Secret(
    "gcloud_service_account_key_secret",
    name="translate-api-service_acount_key_secret"
)

aws_translate_secret_version = aws.secretsmanager.SecretVersion(
    "gcloud_service_account_key_secret",
    secret_id=aws_translate_secret.id,
    secret_string=gcloud_translate_service_account_key.private_key
)

#####################
## Lambda Function ##
#####################
## lambda access to logging and gogle api secret - roles and policy
aws_translate_lamda_role = aws.iam.Role(
    "translate-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }),
)

aws_translate_lamda_role_policy = aws.iam.RolePolicy(
    "translate-role-policy",
    role=aws_translate_lamda_role.id,
    policy=pulumi.Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "secretsmanager:ListSecrets",
                    "secretsmanager:GetSecretValue",
                ],
                "Resource": aws_translate_secret.id
            }
        ]
    }),
)



# python deps
result = subprocess.run(
    ["pip", "install", "-r", "requirements.txt", "--target", ".", "--upgrade"],
    stdout=subprocess.PIPE,
    cwd="./app/src",
    check=True,
)

## function
aws_translate_lambda_func = aws.lambda_.Function(
    "translate-lambda",
    role=aws_translate_lamda_role.arn,
    runtime="python3.12",
    handler="translate.handler",
    environment={
        "variables": {
            "GCLOUD_SERVICE_ACCOUNT_KEY": aws_translate_secret.id,
            "GCLOUD_PROJECT_ID": gcloud_project_id,
        },
    },
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./app/src")}),
    timeout=10,
    memory_size=256
)

#################
## API Gateway ##
#################
## rest api with openapi spec
aws_translate_rest_api = aws.apigateway.RestApi(
    "translate-api",
    body=pulumi.Output.json_dumps(
        {
            "openapi" : "3.0.1",
            "info" : {
                "title" : "translate-api",
                "version" : "1.0"
            },
            "servers" : [ {
                "url" : "/",
                "variables" : {
                    "basePath" : {
                        "default" : "translate-api"
                    }
                }
            } ],
            "paths" : {
                "/translate" : {
                    "post" : {
                        "security" : [ {
                            "api_key" : [ ]
                        } ],
                        "x-amazon-apigateway-integration": {
                            "uri": pulumi.Output.format(
                                "arn:aws:apigateway:{0}:lambda:path/2015-03-31/functions/{1}/invocations",
                                aws.config.region,
                                aws_translate_lambda_func.arn,
                            ),
                            "passthroughBehavior": "when_no_match",
                            "httpMethod": "POST",
                            "type": "aws_proxy",
                        },
                        "requestBody": {
                            "required": "true",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TranslateBody"
                                    }
                                }
                            }
                        }
                    },                    
                }
            },
            "components" : {
                "securitySchemes" : {
                    "api_key" : {
                        "type" : "apiKey",
                        "name" : "x-api-key",
                        "in" : "header"
                    }
                },
                "schemas": {
                    "TranslateBody": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "the source text to translate"
                            },
                            "language": {
                                "type": "string",
                                "description": "the source language (optional)"
                            }
                        }
                    }
                }
            }
        }
    ),
)




# deployment
aws_translate_deployment = aws.apigateway.Deployment(
    "translate-deployment",
    rest_api=aws_translate_rest_api.id,
)

# stage
aws_translate_stage = aws.apigateway.Stage(
    "translate-api-rest-stage",
    rest_api=aws_translate_rest_api.id,
    deployment=aws_translate_deployment.id,
    stage_name="translate-api",
)

# rest-api -> lambda permissions
aws_translate_rest_invoke_permission = aws.lambda_.Permission(
    "translate-api-rest-lambda-permission",
    action="lambda:invokeFunction",
    function=aws_translate_lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=aws_translate_rest_api.execution_arn.apply(lambda execution_arn: f"{execution_arn}/*"),
)


# set api key for rest api endpoint
aws_translate_rest_api_key = aws.apigateway.ApiKey("translate-api-rest-key")

aws_translate_rest_plan = aws.apigateway.UsagePlan("translate-api-rest-plan", aws.apigateway.UsagePlanArgs(
    api_stages=[
        aws.apigateway.UsagePlanApiStageArgs(
            api_id=aws_translate_rest_api.id,
            stage=aws_translate_stage.stage_name,
        ),
    ],
))

aws_translate_rest_plan_key = aws.apigateway.UsagePlanKey("translate-api-rest-plan-key", aws.apigateway.UsagePlanKeyArgs(
    key_id=aws_translate_rest_api_key.id,
    key_type="API_KEY",
    usage_plan_id=aws_translate_rest_plan.id,
))

# export endpoint
pulumi.export(
    "translate-rest-endpoint",
    aws_translate_stage.invoke_url.apply(lambda url: url + "/translate"),
)
pulumi.export(
    "translate-rest-api-key (x-api-key header)",
    aws_translate_rest_api_key.value,
)