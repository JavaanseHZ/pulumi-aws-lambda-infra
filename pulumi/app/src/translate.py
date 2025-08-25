import json
import boto3
import logging
import os
import base64
from google.oauth2.service_account import Credentials
from google.cloud import translate_v3



def handler(event, context):
    aws_secrets_client = boto3.client('secretsmanager')
    aws_secret_name = os.environ['GCLOUD_SERVICE_ACCOUNT_KEY']
    glcoud_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    
    gcloud_service_account_key = aws_secrets_client.get_secret_value(SecretId=aws_secret_name).get('SecretString')

    gcloud_credentials = Credentials.from_service_account_info(json.loads(gcloud_service_account_key))

    glcoud_translation_client = translate_v3.TranslationServiceClient(project=glcoud_project_id, credentials=gcloud_credentials)
    
    
    text = "hello world",
    source_language_code = "en-US",
    target_language_code = "dk",
    mime_type = "text/plain"
    parent = f"projects/{glcoud_project_id}/locations/global"

    glcoud_translation_client_response = glcoud_translation_client.translate_text(
        contents=[text],
        parent=parent,
        mime_type=mime_type,
        source_language_code=source_language_code,
        target_language_code=target_language_code,
    )

    #return {"statusCode": 200, "body": json.dumps("translate test --- " + secret_name + " --- " + base64.b64decode(gcloud_credentials)[:10]}

    return {"statusCode": 200, "body": json.dumps("translate test --- " + secret_name + " --- " + base64.b64decode(gcloud_credentials)[:10] + " --- " + glcoud_translation_client_response)}


def translate_text(
    text: str = "hello world",
    source_language_code: str = "en-US",
    target_language_code: str = "dk",
    creds: str = "",
    project_id: str = ""
    ) -> translate_v3.TranslationServiceClient:
        client = translate_v3.TranslationServiceClient(project=project_id, credentials=creds)
        mime_type = "text/plain"
        response = client.translate_text(
            contents=[text],
            parent=parent,
            mime_type=mime_type,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
        )
        return response
