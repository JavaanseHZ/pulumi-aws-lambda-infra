
import pulumi_aws as aws

def create_secret(pName: str, pSecretString: str) -> aws.secretsmanager.Secret:

    aws_secret = aws.secretsmanager.Secret(
        "gcloud_service_account_key_secret",
        name=f"{pName}-api-service_acount_key_secret"
    )

    aws_secret_version = aws.secretsmanager.SecretVersion(
        "gcloud_service_account_key_secret",
        secret_id=aws_secret.id,
        secret_string=pSecretString
    )
    
    return aws_secret