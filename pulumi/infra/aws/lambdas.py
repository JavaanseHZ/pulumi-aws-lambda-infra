import json
import pulumi
import pulumi_aws as aws

def create_lambda(pName: str, pSecret:aws.secretsmanager.Secret , pEnvironment) -> aws.lambda_.Function:
    
    aws_lamda_role = aws.iam.Role(
        f"{pName}-role",
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

    aws_lamda_role_policy = aws.iam.RolePolicy(
        f"{pName}-role-policy",
        role=aws_lamda_role.id,
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
                    "Resource": pSecret.id
                }
            ]
        }),
    )

    ## function
    aws_lambda_func = aws.lambda_.Function(
        f"{pName}-lambda",
        role=aws_lamda_role.arn,
        runtime="python3.12",
        handler=f"{pName}.handler",
        environment=pEnvironment,
        code=pulumi.AssetArchive({".": pulumi.FileArchive("./app/src")}),
        timeout=10,
        memory_size=256
    )

    return aws_lambda_func