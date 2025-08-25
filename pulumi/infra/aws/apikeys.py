import pulumi_aws as aws

def create_api_key(pName: str, pRestApi, pStage) -> aws.apigateway.ApiKey:
     # set api key for rest api endpoint to secure reest api
    aws_rest_api_key = aws.apigateway.ApiKey(f"{pName}-api-rest-key")

    aws_rest_plan = aws.apigateway.UsagePlan(f"{pName}-api-rest-plan", aws.apigateway.UsagePlanArgs(
        api_stages=[
            aws.apigateway.UsagePlanApiStageArgs(
                api_id=pRestApi.id,
                stage=pStage.stage_name,
            ),
        ],
    ))

    aws_rest_plan_key = aws.apigateway.UsagePlanKey(f"{pName}-api-rest-plan-key", aws.apigateway.UsagePlanKeyArgs(
        key_id=aws_rest_api_key.id,
        key_type="API_KEY",
        usage_plan_id=aws_rest_plan.id,
    ))
    
    return aws_rest_api_key
