import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

VALID_ACLS = {
    "private",
    "public-read",
    "public-read-write",
    "authenticated-read",
}

BUCKET_RE = re.compile(r"^[a-z0-9.-]{3,63}$")


class Properties(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    aws_region: str = Field(alias="aws-region")
    acl: str
    bucket_name: str = Field(alias="bucket-name")


class Payload(BaseModel):
    properties: Properties


class RenderRequest(BaseModel):
    payload: Payload


def validate_inputs(bucket_name: str, acl: str):
    if acl not in VALID_ACLS:
        raise HTTPException(status_code=400, detail="Invalid ACL value")

    if not BUCKET_RE.match(bucket_name):
        raise HTTPException(status_code=400, detail="Invalid S3 bucket name")


@app.post("/render", response_class=PlainTextResponse)
def render(request: RenderRequest):
    props = request.payload.properties

    validate_inputs(props.bucket_name, props.acl)

    terraform = f"""
provider "aws" {{
  region = "{props.aws_region}"
}}

resource "aws_s3_bucket" "bucket" {{
  bucket = "{props.bucket_name}"
}}

resource "aws_s3_bucket_acl" "bucket_acl" {{
  bucket = aws_s3_bucket.bucket.id
  acl    = "{props.acl}"
}}
"""

    return terraform.strip()
