# Description

An AWS lambda function in python that takes a text parameter and translates it to Danish using the google translate API.

The lambda function is deployed on AWS infrastructure on an API Gateway with a documented REST endpoint and set up via pulumi.

# Project

## Setup

### Git

The project is devided into two repositories:

**pulumi-aws-lamda-infra**([repo](https://github.com/JavaanseHZ/pulumi-aws-lambda-infra))
- infrastructure code in python using pulumi
- for now, also application code
- deployment pipeline (not implemented yet)

**pulumi-aws-lamda-app** ([repo](https://github.com/JavaanseHZ/pulumi-aws-lambda-app))
- AWS lambda application code in python using aws lambda library
- build pipeline (not implemented yet)

Both repositories have a protected main branch.

### Pulumi

The pulumi project is structured as follows:

- infra
  - aws (pulimi aws entities)
    - apigateways.py
    - apikeys.py
    - lambdas.py
    - secrets.py
  - gcloud (pulimi google cloud entities)
    - apikeys.py 
- \_\_main\_\_.py (pulimi main)
- requirements.py (pulimi python dependencies)
- Pulumi.yaml (pulimi config)
- Pulumi.dev.yaml (pulumi dev stage config)

### Secrets

The google api key secret is configured in the AWS.

## Infrastructure

![infra-](infra.drawio.svg)

### Stages
(not implemented)

The setup is divided into a dev & a prod stage.

The dev stage runs the newest version, the prod stage runs a dedicated version.

### API Gateway

The API Gateway is accessible via via an URL and an api key.
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

#### REST endpoint

- access control
- documentation via open api spec
- example request

### AWS Lambda
(not implemented - lambda code directly in infra repo)

The Lambda is deployed via pulumi, the release artifact is the release generated via github actions.

### Google Cloud Translate

Access to the google translate endpoint is configured via pulumi and injected as an AWS secret variable into the AWS lambda.

## Application

### Python (AWS Lambda)

The application takes in two parameters:
- language
- text

It translates the text using the gcloud python library abstracting the ```projects.locations.translateText``` method of the ```Cloud Translation``` API.

It returns the translated text.


### Validation

(not implemented)

Examples:
- language field, as google provides an api which languages it supports
- text, restriction on 

### Error Handling

(not implemented)

The google api errors could be abstracted into a unified custom error handling.

## Build

(not implemented)

The build can run on feature branches as a quality gate for merging.
On the main branch, it could create a new versioned application release using AWS Lambda layers.
The release should be versioned using semantic versioning and conventional commits (not implemented).

### Github Actions

(not implemented)

The build is separated in 4 stages:

- build code
- static code analysis (not implemeted)
- unit tests  (not implemeted)
- reporting (not implemeted)
- create version (only on main branch) (not implemeted)
- release (only on main branch)

### Release Artifact

(not implemented)

The release artfact is uploaded to the Github repos release page, including an auto-generated release note.

It is also uploaded AWS as a lambda layer.

## Deployment

(not implemented)

The deployment is done via pulumi and automated via github actions.

### Github Actions

(not implemented)

The deployment is separated in 2 stages, both for dev and prod:

- deploy pulumi
- short integration test (not implemented)

### Secrets

The secrets for the Pulumi CLoud, AWS and Google Cloud are are managed in the Github Actions