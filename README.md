# Terraform Parse Service

A minimal FastAPI service that turns a JSON payload describing an AWS S3 bucket into a Terraform snippet. It is intended as a building block for tools that need to generate infrastructure templates programmatically.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Project layout

- `terraform_parse_service/` – FastAPI application with the `/render` endpoint.
- `helm/` – Helm chart to deploy the API.
- `terraform/` – Terraform code for the EKS cluster and static assets bucket.

## Local setup

```bash
cd terraform_parse_service

# install dependencies (uv recommended)
uv sync --all-groups

# run tests
uv run pytest

# start the API locally
uv run uvicorn app.main:app --reload --port 8000
```

The app exposes a single endpoint: `POST /render`.

Sample request
```bash
# render response to yaml file
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{
        "payload": {
          "properties": {
            "aws-region": "ap-southeast-1",
            "acl": "private",
            "bucket-name": "my-generated-bucket"
          }
        }
      }' > main.tf
```

## Local Testing with Kind

Run these commands from the repository root (where the Dockerfile and Helm chart live):

```
# Create Kubernetes cluster
kind create cluster --name tripla-test

# Build Docker image under folder root
export IMAGE_TAG=$(date +%Y%m%d%H%M%S)
docker build -t terraform-parse:$IMAGE_TAG terraform_parse_service


# Load image into kind or push to your image repository
kind load docker-image terraform-parse:$IMAGE_TAG --name tripla-test

# Deploy Helm chart
helm lint ./helm
helm upgrade -i terraform-parse-dev ./helm \
  --set image.repository=terraform-parse \
  --set image.tag=$IMAGE_TAG

# Verify deployment
kubectl get pods
kubectl get svc

# Access the API
kubectl port-forward svc/terraform-parse-dev 8000:8000

# Then open:
http://localhost:8000/
```

## Terraform infrastructure

The `terraform/` directory provisions an EKS cluster (via the official terraform-aws-modules/eks module) plus an S3 bucket for static assets. Prerequisites:

- Terraform ≥ 1.0
- AWS credentials with permissions for EKS, EC2, IAM, and S3

Typical workflow:

```bash
cd terraform

# initialize providers/modules
terraform init

# validate terraform
terraform validate

# review changes (set your own IDs)
terraform plan \
  -var 'vpc_id=vpc-0123456789abcdef0' \
  -var 'subnet_ids=["subnet-0aaaa","subnet-0bbbb","subnet-0cccc"]'

# apply when ready
terraform apply \
  -var 'vpc_id=vpc-0123456789abcdef0' \
  -var 'subnet_ids=["subnet-0aaaa","subnet-0bbbb","subnet-0cccc"]'
```

## Notes

- The service currently supports only AWS S3 bucket configuration. Extend `app/main.py` with additional models and template logic for more resource types.
- Terraform uses the default local backend; configure an S3/DynamoDB backend if you plan to share state across teammates or environments.
