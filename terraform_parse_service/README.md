# Terraform Parse Service

A minimal FastAPI service that turns a JSON payload describing an AWS S3 bucket into a Terraform snippet. It is intended as a building block for tools that need to generate infrastructure templates programmatically.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`

## Setup

```bash
# Recommended install using uv
uv sync --all-groups

# or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running the API

Start the development server with reload support:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The app exposes a single endpoint: `POST /render`.

### Sample request

```bash
curl -X POST http://localhost:8000/render \
  -H "Content-Type: application/json" \
  -d '{
        "payload": {
          "properties": {
            "aws_region": "ap-southeast-1",
            "acl": "private",
            "bucket_name": "my-generated-bucket"
          }
        }
      }'
```

### Sample response

```json
{
  "terraform": "\nprovider \"aws\" {\n  region = \"ap-southeast-1\"\n}\n\nresource \"aws_s3_bucket\" \"bucket\" {\n  bucket = \"my-generated-bucket\"\n}\n\nresource \"aws_s3_bucket_acl\" \"bucket_acl\" {\n  bucket = aws_s3_bucket.bucket.id\n  acl    = \"private\"\n}\n"
}
```

## Project layout

- `app/main.py` # FastAPI application with the `/render` endpoint.
- `pyproject.toml` # project metadata and dependencies.
- `tests/` # unit tests
- `uv.lock` # dependency lock file

## Run test cases

```bash
uv run pytest
```

## Local Testing with Kind
```
# 1 Create Kubernetes cluster
kind create cluster --name tripla-test

# 2 Build Docker image under folder root
export IMAGE_TAG=$(date +%Y%m%d%H%M%S)
docker build -t terraform-parse:$IMAGE_TAG terraform_parse_service


### 3 Load image into kind or push to your image repository
kind load docker-image terraform-parse:$IMAGE_TAG --name tripla-test

### 4 Deploy Helm chart
helm lint ./helm
helm install terraform-parse ./helm \
  --set image.repository=terraform-parse \
  --set image.tag=$IMAGE_TAG

### 5 Verify deployment
kubectl get pods
kubectl get svc

### 6 Access the API
kubectl port-forward svc/terraform-parse 8000:8000

Then open:
http://localhost:8000/docs
```

## Notes

- The service currently supports only AWS S3 bucket configuration. Extend `app/main.py` with additional models and template logic for more resource types.
- The default response is a simple string template; consider integrating a templating engine if the Terraform output becomes more complex.
