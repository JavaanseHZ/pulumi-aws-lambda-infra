# Description

An AWS lambda function in python that takes a text parameter and translates it to Danish using the google translate API.

The lambda function is deployed on AWS infrastructure, accessible via an API Gateway with a documented REST endpoint.

The infrastructure is set up via pulumi.

# Project

## Setup

### Git

The project is divided into two repositories:

**pulumi-aws-lambda-infra** ([repo](https://github.com/JavaanseHZ/pulumi-aws-lambda-infra))
- infrastructure code in python using pulumi
- deployment pipeline (not implemented yet)
- 
*pulumi-aws-lambda-app* ([repo](https://github.com/JavaanseHZ/pulumi-aws-lambda-app))
- AWS lambda application code in python using aws lambda library
- build pipeline

Currently the deployment artifact used is generated directly in the infrastructure code. This means the application repo is not really used yet.

In a prodcution setup, the main branches would be protected.

### Pulumi

The pulumi project is structured as follows: [pulumi/app/src]:
```
- app
  - src
    - translate.py (lambda function)
    - requirements.txt (lambda python dependencies)
- infra
  - aws (pulimi aws entities)
    - apigateways.py
    - apikeys.py
    - lambdas.py
    - secrets.py
  - gcloud (pulimi google cloud entities)
    - apikeys.py 
- __main__.py (pulimi main)
- requirements.py (pulimi python dependencies)
- Pulumi.yaml (pulimi config)
- Pulumi.dev.yaml (pulumi dev stage config)
```
It is located in the [pulumi](https://github.com/JavaanseHZ/pulumi-aws-lambda-infra/tree/main/pulumi/) subfolder.

## Infrastructure

![infra-](infra.drawio.svg)

### API Gateway & Rest Endpoint

The API Gateway is accessible via via an URL and securfed via an api key.

Example curl request:
```
curl --request POST \
  --url [URL] \
  --header 'Content-Type: application/json' 
  --header 'x-api-key: [APIKEY]' \
  --data '{
	"text": "My car is red"
}'
```

The openapi spec is located in the [openapi-spec.json](https://github.com/JavaanseHZ/pulumi-aws-lambda-infra/blob/main/openapi-spec.json) file.

### AWS Lambda

The lambda code is located in the [pulumi/app/src](https://github.com/JavaanseHZ/pulumi-aws-lambda-infra/tree/main/pulumi/app/src) subfolder.

The dependecies are listed in the ```requirements.txt``` file, the function itself in the ```translate.py``` file.

The Lambda is deployed via pulumi and directly from the app folder.

In a production setup the release artifact is created via [github actions in the app repository](https://github.com/JavaanseHZ/pulumi-aws-lambda-app/blob/main/.github/workflows/build.yaml).

### Google Cloud Translate

Access to the google translate endpoint api key is configured via pulumi and injected as an AWS secret variable into the AWS lambda.

### Stages

The setup is currently has a dev stage.

A prod stage could be configured to e.g. use different versions.

## Application

### Python (AWS Lambda)

The application takes in two parameters:
- language
- text

It translates the text using the gcloud python library abstracting the ```projects.locations.translateText``` method of the ```Cloud Translation``` API.

It returns the translated text.

### Secrets

The google api key secret is configured in the AWS.

### Validation

Currently there's only some minor input validation, e.g if the text field is missing.

Additional validation could be done:
- checking the request against the OpenApi schema in the gateway
- checking the language field, as google provides an api which languages it supports
- text, restriction on chars or length

### Error Handling

While there's a try/catch clause, error handling is not implemented.

The google api errors should be abstracted into a unified custom error handling.

## Build

The build can run on feature branches as a quality gate for merging.

On the main branch, it creates a new versioned application release using AWS Lambda layers.

The release could be versioned using semantic versioning and conventional commits (not implemented).

### Github Actions

The build is separated in the following stages:

- build code
- configure access to AWS
- deploy to AWS (only on main branch)

In a production setup, additional step could be:
- static code analysis
- unit tests
- reporting

### Secrets

The secrets for the AWS cli are managed in the Github Actions settings.

### Release Artifact

The release artfact is uploaded to AWS as a lambda layer.

Additionally it could be uploaded to the Github repos release page, including an auto-generated release note.

## Deployment

The deployment is done via pulumi and could be automated via github actions.

### Secrets

The secrets for the Pulumi Cloud, AWS and Google Cloud could be managed in the Github Actions settings.
