def create_api_key(key_name: str, target_service: str) -> gcp.projects.ApiKey:
    return gcp.projects.ApiKey(key_name,
        name="{key_name}-key",
        display_name="{key_name}-key",
        restrictions={
            "api_targets": [{
                "service": target_service,
                "methods": ["GET*, POST*"],
            }],
            "browser_key_restrictions": {
                "allowed_referrers": [".*"],
            },
        })