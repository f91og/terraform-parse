from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_render_s3_terraform():
    payload = {
        "payload": {
            "properties": {
                "aws_region": "eu-west-1",
                "acl": "private",
                "bucket_name": "tripla-bucket"
            }
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 200

    data = response.json()
    terraform = data["terraform"]

    assert 'provider "aws"' in terraform
    assert 'bucket = "tripla-bucket"' in terraform
    assert 'acl    = "private"' in terraform
