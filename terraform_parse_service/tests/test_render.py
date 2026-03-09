from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_render_s3_terraform():
    payload = {
        "payload": {
            "properties": {
                "aws_region": "eu-west-1",
                "acl": "private",
                "bucket_name": "tripla-bucket",
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert 'provider "aws"' in data["terraform"]
    assert 'bucket = "tripla-bucket"' in data["terraform"]
    assert 'acl    = "private"' in data["terraform"]


def test_invalid_acl():
    payload = {
        "payload": {
            "properties": {
                "aws_region": "eu-west-1",
                "acl": "invalid-acl",
                "bucket_name": "tripla-bucket",
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 400
    assert "Invalid ACL" in response.json()["detail"]


def test_invalid_bucket_name():
    payload = {
        "payload": {
            "properties": {
                "aws_region": "eu-west-1",
                "acl": "private",
                "bucket_name": "INVALID_BUCKET_NAME",
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 400
    assert "Invalid S3 bucket name" in response.json()["detail"]