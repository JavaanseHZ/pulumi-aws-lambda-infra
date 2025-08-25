import pulumi
import pulumi_gcp as gcp

def create_api_key(pName: str, pRole: str, pProject: str) -> gcp.projects.ApiKey:

    # create api key for google translate api
    gcloud_service_account = gcp.serviceaccount.Account(
        f"{pName}-service-account",
        account_id=f"{pName}-service-account",
        display_name=f"{pName}-service-account"
    )

    gcloud_iam_binding = gcp.projects.IAMBinding(
        f"{pName}-service-account-iam-binding",
        project=pProject,
        role=pRole,
        members=[gcloud_service_account.member]
    )

    gcloud_service_account_key = gcp.serviceaccount.Key(
        f"{pName}-service-account-api-key",
        service_account_id=gcloud_service_account.name
    )

    return gcloud_service_account_key
