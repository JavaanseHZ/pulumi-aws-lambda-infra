import json
import pulumi
import pulumi_aws as aws
import pulumi_gcp as gcp

#########################
## Google Cloud Access ##
#########################
## gcloud service account and api key saved in aws secret
gcloud_translate_service_account = gcp.serviceaccount.Account(
    "translate-service-account",
    account_id="translate-service-account",
    display_name="translate-service-account"
)

gcloud_translate_iam_binding = gcp.projects.IAMBinding(
    "translate-service-account-iam-binding",
    project=gcp.config.project,
    role="roles/cloudtranslate.user",
    members=[gcloud_translate_service_account.member]
)

gcloud_translate_service_account_key = gcp.serviceaccount.Key(
    "translate-service-account-api-key",
    service_account_id=gcloud_translate_service_account.name
)

aws_translate_secret = aws.secretsmanager.Secret(
    "gcloud_service_account_key",
    name="translate-secret"
)

aws_translate_secret_version = aws.secretsmanager.SecretVersion(
    "gcloud_service_account_key",
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

## function
aws_translate_lambda_func = aws.lambda_.Function(
    "translate-lambda",
    role=aws_translate_lamda_role.arn,
    runtime="python3.12",
    handler="translate.handler",
    environment={
        "variables": {
            "GCLOUD_SERVICE_ACCOUNT_KEY": aws_translate_secret.id,
            "GCLOUD_PROJECT_ID": gcp.config.project,
        },
    },
    code=pulumi.AssetArchive({".": pulumi.FileArchive("./app/src")}),
)

#################
## API Gateway ##
#################
## rest api with openapi spec
aws_translate_rest_api = aws.apigateway.RestApi(
    "translate-api",
    body=pulumi.Output.json_dumps(
        {
            "swagger": "2.0",
            "info": {"title": "translate-api", "version": "1.0"},
            "paths": {
                "/translate": {
                    "x-amazon-apigateway-any-method": {
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
                    },
                },
            },
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
    stage_name="translate",
)

# rest-api -> lambda permissions
aws_translate_rest_invoke_permission = aws.lambda_.Permission(
    "translate-api-rest-lambda-permission",
    action="lambda:invokeFunction",
    function=aws_translate_lambda_func.name,
    principal="apigateway.amazonaws.com",
    source_arn=aws_translate_stage.execution_arn.apply(lambda arn: arn + "*/*"),
)

# export endpoint
pulumi.export(
    "translate-rest-endpoint",
    aws_translate_stage.invoke_url.apply(lambda url: url + "/translate"),
)