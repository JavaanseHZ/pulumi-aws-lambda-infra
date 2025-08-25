import json
import boto3
import logging
import os
import base64
from google.oauth2.service_account import Credentials
from google.cloud import translate_v3



def handler(event, context):

    ## VALIDATION not implmeneted - could also be separate lambda, e.g. supported languages. some stuff should also be done in api gateway


    ##get google api secret from aws secret manager
    aws_secrets_client = boto3.client('secretsmanager')
    aws_secret_name = os.environ['GCLOUD_SERVICE_ACCOUNT_KEY']
    gcloud_service_account_key = base64.b64decode(aws_secrets_client.get_secret_value(SecretId=aws_secret_name).get('SecretString'))
    
    ##google translate text api request
    gcloud_project_id = os.environ.get("GCLOUD_PROJECT_ID")
    gcloud_credentials = Credentials.from_service_account_info(json.loads(gcloud_service_account_key))
    glcoud_translation_client = translate_v3.TranslationServiceClient(credentials=gcloud_credentials)
    glcoud_translation_client_request = {
            "contents": ['hello world'],
            "target_language_code": "da",
            "source_language_code": "en-US",
            "parent": f"projects/{gcloud_project_id}/locations/global",
            "mime_type": "text/plain",
    }
    glcoud_translation_client_response = glcoud_translation_client.translate_text(**glcoud_translation_client_request)

    ## ERROR HANDLING not implmeneted - could also be separate lambda, should be conform to own domain

    return {"statusCode": 200, "body": glcoud_translation_client_response.translations[0].translated_text}
