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

## Testing

```bash
uv run pytest
```

## Notes

- The service currently supports only AWS S3 bucket configuration. Extend `app/main.py` with additional models and template logic for more resource types.
- The default response is a simple string template; consider integrating a templating engine if the Terraform output becomes more complex.
