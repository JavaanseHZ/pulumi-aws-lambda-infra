# Description

An AWS lambda function in python that takes a text parameter and translates it to Danish using the google translate API.

The lambda function is deployed on AWS infrastructure on an API Gateway with a documented REST endpoint and set up via pulumi.

# Project

## Setup

### Git

The project is devided into two repositories:

**pulumi-aws-lamda-infra**

- infrastructure code in python using pulumi.

- deployment pipeline

**pulumi-aws-lamda-app**

- AWS lambda application code in python using aws lambda library
- build pipeline

Both repositories have a protected main branch.

### Pulumi

The project is structured as follows:

- infra
  - apigateways
    - config.yaml
    - translate:
      - config.yaml
      - openapi.json
  - lambdas
    - config.yaml
    - translate:
       - config.yaml
  - iam
    - config.yaml
    - translate:
       - config.yaml

### Secrets

Secrets are configured in the pulumi cloud.
Access to the pulumi cloud is configured in the deployment pipeline.

## Infrastructure

![infra-](infra.drawio.svg)

### Stages

The setup is divided into a dev & a prod stage.
The dev stage runs the newest version, the prod stage runs a dedicated version.

### API Gateway

The API Gateway is accessible via the following URL:

#### REST endpoint

- access control
- documentation via open api spec
- example request

### AWS Lambda

THe Lambda is deployed via pulumi , the release artifact is the release generated on github.

### Google Cloud Translate

Access to the google translate andpoint is configured via pulumi and injected as an environment variable into the AWS lambda application.

## Application

### Python (AWS Lambda)

The application takes in two parameters:
- source-language
- source-text

It translates the text using the gcloud python library abstracting the "projects.locations.translateText" method of the "Cloud Translation".


### Validation

not implemented

Examples:
- src-language field, as google provides an api which languages it supports
- src-text , restriction on 

### Error Handling

not implemented

The google api errors are abstracted into a unified custom error handling.

## Build

The build is run on feature branches as a quality gate for merging.
On the main branch, it will create a new versioned application release using Lambda Layers.
The release is versioned using semantic versioning and conventional commits (not implemented).

### Github Actions

The build is separated in 4 stages:

- build code
- static code analysis (not implemeted)
- unit tests  (not implemeted)
- reporting (not implemeted)
- create version (only on main branch) (not implemeted)
- release (only on main branch)

### Release Artifact

The relase artfact is uploaded to the Github repos release page, including an auto-generated release note.

## Deployment

The deployment is done via pulumi and automated via github actions.

### Github Actions

The deployment is separated in 2 stages, both for dev and prod:

- deploy pulumi
- short integration test (not implemented)

### Secrets

The secrets for AWS and Google Cloud are are managed in the Pulumi cloud