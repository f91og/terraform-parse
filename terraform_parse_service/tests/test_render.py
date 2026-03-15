from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_render_s3_terraform():
    payload = {
        "payload": {
            "properties": {
                "aws-region": "eu-west-1",
                "acl": "private",
                "bucket-name": "tripla-bucket",
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 200
    body = response.text

    assert 'provider "aws"' in body
    assert 'bucket = "tripla-bucket"' in body
    assert 'acl    = "private"' in body


def test_invalid_acl():
    payload = {
        "payload": {
            "properties": {
                "aws-region": "eu-west-1",
                "acl": "invalid-acl",
                "bucket-name": "tripla-bucket",
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
                "aws-region": "eu-west-1",
                "acl": "private",
                "bucket-name": "INVALID_BUCKET_NAME",
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 400
    assert "Invalid S3 bucket name" in response.json()["detail"]


def test_bucket_name_edge_cases():
    invalid_names = [
        "-leadingdash",
        "trailingdot.",
        "double..dots",
        "dot.-combo",
        "192.168.0.1",
    ]

    for name in invalid_names:
        payload = {
            "payload": {
                "properties": {
                    "aws-region": "eu-west-1",
                    "acl": "private",
                    "bucket-name": name,
                }
            }
        }
        response = client.post("/render", json=payload)

        assert response.status_code == 400
        assert "Invalid S3 bucket name" in response.json()["detail"]
