import json
import boto3
import logging
import os
import base64
from google.oauth2.service_account import Credentials
from google.cloud import translate_v3

logger = logging.getLogger()
logger.setLevel("INFO")

def handler(event, context):

    ## VALIDATION not really implemented - could also be separate lambda, e.g. supported languages. some stuff should also be done in api gateway
    try:
        eventBody = json.loads(event['body'])
        
        logger.info(f"incoming event body: {eventBody}")
 
        if 'text' in eventBody:
            source_text = eventBody['text']
        else:
            return {"statusCode": 400, "body": "missing the field [text] in request"}

        if 'language' in eventBody:
            source_language_code = eventBody['language']
        else:
            source_language_code = "en-US"

        target_language_code = "da"

        ##get google api secret from aws secret manager
        aws_secrets_client = boto3.client('secretsmanager')
        aws_secret_name = os.environ['GCLOUD_SERVICE_ACCOUNT_KEY']
        gcloud_service_account_key = base64.b64decode(aws_secrets_client.get_secret_value(SecretId=aws_secret_name).get('SecretString'))
        
        ##google translate text api request
        gcloud_project_id = os.environ.get("GCLOUD_PROJECT_ID")
        gcloud_credentials = Credentials.from_service_account_info(json.loads(gcloud_service_account_key))
        glcoud_translation_client = translate_v3.TranslationServiceClient(credentials=gcloud_credentials)
        glcoud_translation_client_request = {
                "contents": [source_text],
                "target_language_code": target_language_code,
                "source_language_code": source_language_code,
                "parent": f"projects/{gcloud_project_id}/locations/global",
                "mime_type": "text/plain",
        }
        glcoud_translation_client_response = glcoud_translation_client.translate_text(**glcoud_translation_client_request)

        logger.info(f"successfully translated text from [{source_language_code}] to [{target_language_code}] on event: {event}")
        
        return {"statusCode": 200, "body": glcoud_translation_client_response.translations[0].translated_text}

    ## ERROR HANDLING not really implemented - could also be separate lambda, should be conform to own domain
    except Exception as e:
        logger.error(f"error translating: {str(e)}")
        raise
