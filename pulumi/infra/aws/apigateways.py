import pulumi_aws as aws

def create_rest_api(pName: str, pFunction, pBody):

    aws_rest_api = aws.apigateway.RestApi(
        f"{pName}-api",
        body=pBody,
    )

    # deployment
    aws_deployment = aws.apigateway.Deployment(
        f"{pName}-deployment",
        rest_api=aws_rest_api.id,
    )

    # stage
    aws_stage = aws.apigateway.Stage(
        f"{pName}-api-rest-stage",
        rest_api=aws_rest_api.id,
        deployment=aws_deployment.id,
        stage_name=f"{pName}-api",
    )

    # rest-api -> lambda permissions
    aws_rest_invoke_permission = aws.lambda_.Permission(
        f"{pName}-api-rest-lambda-permission",
        action="lambda:invokeFunction",
        function=pFunction.name,
        principal="apigateway.amazonaws.com",
        source_arn=aws_rest_api.execution_arn.apply(lambda execution_arn: f"{execution_arn}/*"),
    )

    return aws_rest_api, aws_stage


   