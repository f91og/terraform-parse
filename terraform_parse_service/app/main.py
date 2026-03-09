from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Properties(BaseModel):
    aws_region: str
    acl: str
    bucket_name: str


class Payload(BaseModel):
    properties: Properties


class RenderRequest(BaseModel):
    payload: Payload


@app.post("/render")
def render(request: RenderRequest):
    props = request.payload.properties

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

    return {"terraform": terraform}
