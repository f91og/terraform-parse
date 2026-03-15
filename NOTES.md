## Part 1 – API Service
- **Stack**: FastAPI + Pydantic for schema validation, packaged behind Uvicorn. This keeps the service lightweight and quick to extend.  
- **Payload handling**: `RenderRequest` → `Properties` models mirror the incoming JSON; ACL/bucket names are validated against AWS requirements before any generation happens.  
- **Terraform rendering**: A simple f-string template builds provider + `aws_s3_bucket` + `aws_s3_bucket_acl`. After validation the rendered content is returned as plain text so callers can redirect it straight into a `.tf` file.  
- **Tests**: FastAPI´s `TestClient` covers happy-path rendering plus invalid ACL/bucket scenarios; tests assert the Terraform body contains the expected resources.

## Part 2 – Terraform
- **Version hygiene**: Introduced a `cluster_version` variable (default 1.29) so we stay on supported EKS versions instead of the deprecated 1.25 pin.  
- **Remote state**: Added an S3 backend (with DynamoDB locking) for separation/locking across environments; prevents dev/staging/prod state collisions.  
- **Next ideas**: Bucket names should include environment/region to ensure uniqueness, add server-side encryption + block-public-access, and parameterize the backend bucket so each tenant/environment can inject their own state store.

## Part 3 – Helm
- **Service routing**: Wired `.Values.service.type` through the Service manifest so switching between ClusterIP/NodePort/LB actually works.  
- **HPA readiness**: Added container `resources` (requests/limits) in the Deployment to satisfy autoscaling requirements.  
- **Follow-ups**: Could add configurable liveness/readiness probes and optional HPA enable/disable toggle when running in Kind or clusters without metrics-server.

## Part 4 – System Behavior
- **Load considerations**: The service is CPU-light but disk IO (writing /tmp files per request) can spike on bursty workloads; pod autoscaling + adequate node disk throughput mitigate it.  
- **Failure scenarios**: If /tmp fills or becomes read-only, requests will fail—surface those errors and consider pushing artifacts to durable storage (S3) instead. Terraform backend outages (S3/Dynamo) would block deployments; enabling retries and alerting on state backend errors would help resilience.

## Part 5 – Approach & Tools
- Iterated locally with uv/pytest for Python, `helm lint` for chart validation, and manual Terraform code review (no apply).  
- Used FastAPI docs and AWS naming rules as references; no AI tools used beyond editor assistance.  
- Alignments kept minimal per requirement hints—only the necessary fixes/validations were implemented to stay focused on deliverables.
