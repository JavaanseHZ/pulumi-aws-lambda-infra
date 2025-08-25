import json
import pulumi
import pulumi_aws as aws
import pulumi_gcp as gcp
import subprocess
import infra.gcloud.apikeys as infra_gcloud_apikeys
import infra.aws.secrets as infra_aws_secrets
import infra.aws.lambdas as infra_aws_lambdas
import infra.aws.apigateways as infra_aws_apigateways
import infra.aws.apikeys as infra_aws_apikeys

######################
## Config Variables ##
######################

gcloud_config = pulumi.Config("gcp")
gcloud_project_id = gcloud_config.require("project")


#########################
## Google Cloud Access ##
#########################

gcloud_translate_service_account_key = infra_gcloud_apikeys.create_api_key(
    pName="translate",
    pRole="roles/cloudtranslate.user",
    pProject=gcloud_project_id
)

aws_translate_secret = infra_aws_secrets.create_secret(
    pName="translate",
    pSecretString=gcloud_translate_service_account_key.private_key
)


#####################
## Lambda Function ##
#####################

# install python deps before deployment
result = subprocess.run(
    ["pip", "install", "-r", "requirements.txt", "--target", ".", "--upgrade"],
    stdout=subprocess.PIPE,
    cwd="./app/src",
    check=True,
)

aws_translate_lambda_func = infra_aws_lambdas.create_lambda(
    pName="translate",
    pSecret=aws_translate_secret,
    pEnvironment={
                "variables": {
                    "GCLOUD_SERVICE_ACCOUNT_KEY": aws_translate_secret.id,
                    "GCLOUD_PROJECT_ID": gcloud_project_id,
                }
            }
)


#################
## API Gateway ##
#################

aws_translate_rest_api, aws_translate_stage = infra_aws_apigateways.create_rest_api(

    pName="translate",
    pFunction=aws_translate_lambda_func,
    pBody=pulumi.Output.json_dumps(
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
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/TranslateBodyRequest"
                                        }
                                    }
                                }
                            },
                            "responses": {
                                "200": {
                                    "description": "successful translation and transletd text as return value",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/TranslateBodyResponse"
                                            },
                                            
                                            }
                                        }
                                    },
                                "400": {
                                    "description": "the text field is missing in request"
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
                        "TranslateBodyRequest": {
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
                        },
                        "TranslateBodyResponse": {
                            "type": "string",
                            "description": "the translated text"
                        },
                    }
                }
            }
        )
)


#############
## API Key ##
#############

aws_translate_rest_api_key = infra_aws_apikeys.create_api_key(
    pName="translate",
    pRestApi=aws_translate_rest_api,
    pStage=aws_translate_stage

)


############
## Export ##
############

pulumi.export(
    "translate-rest-endpoint",
    aws_translate_stage.invoke_url.apply(lambda url: url + "/translate"),
)

pulumi.export(
    "translate-rest-api-key (x-api-key header)",
    aws_translate_rest_api_key.value,
)