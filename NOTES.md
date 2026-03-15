## Part 1 – API Service

### Stack

The API service is implemented using **FastAPI** with **Pydantic** for request validation and served by **Uvicorn**.  
This stack keeps the service lightweight while providing strong schema validation and clear API documentation.

### Payload Handling

The incoming JSON request is modeled using nested Pydantic schemas:

RenderRequest → Payload → Properties

This structure mirrors the request payload and ensures strict validation before Terraform generation.

Additional validation checks include:

- S3 bucket naming rules
- allowed ACL values

Invalid requests are rejected early with appropriate HTTP responses.

### Terraform Rendering

Terraform configuration is generated using a simple Python template.  
The generated configuration includes:

- `provider "aws"`
- `aws_s3_bucket`
- `aws_s3_bucket_acl`

The Terraform configuration is returned as plain text in the API response so the client can redirect the output directly into a `.tf` file if needed.

### Testing

Tests are implemented using **FastAPI's `TestClient`**.

The test suite covers:

- successful Terraform rendering
- invalid ACL handling
- invalid S3 bucket names

Tests verify both the HTTP response and the generated Terraform content.

---

## Part 2 – Terraform

### Environment Safety

To prevent global S3 bucket name collisions, bucket names now include the environment prefix:

`${var.environment}-${var.cluster_name}-static-assets`

This allows multiple environments (e.g. `dev`, `staging`, `prod`) to coexist safely.

### Security Defaults

Baseline security settings were added for the static assets bucket:

- S3 versioning enabled
- server-side encryption (AES256)
- `BucketOwnerEnforced` ownership
- full S3 public access block configuration

The Kubernetes cluster version is also parameterized through the `cluster_version` variable (default `1.29`) instead of hardcoding deprecated versions.

### State Management

Terraform state is intentionally kept **local** to keep the assignment simple.

In a production environment, the recommended setup would be:

- **S3 backend** for Terraform state
- **DynamoDB locking** to prevent concurrent modifications

### Possible Extensions

Additional improvements that could be implemented:

- remote Terraform backend configuration
- configurable IAM roles for worker nodes
- cluster logging configuration
- separating public and private subnets for worker nodes

---

## Part 3 – Helm

### Service Configuration

The Helm chart now wires `.Values.service.type` into the Service template.  
This allows users to switch between:

- `ClusterIP`
- `NodePort`
- `LoadBalancer`

without modifying the template itself.

### Autoscaling Compatibility

Resource **requests and limits** were added to the container specification.

This ensures the **Horizontal Pod Autoscaler (HPA)** can properly calculate CPU utilization.

### Potential Improvements

Future improvements could include:

- configurable liveness/readiness probes
- environment variables for runtime configuration
- optional HPA enable/disable flags
- Helm naming helpers to support multiple releases

---

## Part 4 – System Behavior

### Load Characteristics

The API service is lightweight and primarily CPU-light. Its main work is request validation and Terraform text generation, so the runtime cost per request is small.

Under burst traffic, the main considerations are:

- concurrent request handling at the application layer
- pod-level CPU and memory sizing
- horizontal scaling if request volume increases

In Kubernetes, this can be handled with:

- horizontal pod autoscaling
- appropriate CPU/memory requests and limits

### Observability

Currently the service relies on:

- FastAPI default logging
- Kubernetes events

A production deployment would typically include:

- structured logs shipped to CloudWatch (or another log sink)
- Prometheus metrics
- alerting on error rates and latency spikes

### Security Considerations

The API currently has **no authentication**, and Terraform state is stored locally.

In a real production setup, improvements would include:

- protecting the API using IAM, API Gateway, or OIDC
- storing Terraform state in encrypted S3 with DynamoDB locking

---

## Part 5 – Development Approach

Development was performed iteratively using:

- **uv + pytest** for Python dependency management and testing
- **helm lint** for Helm chart validation
- manual Terraform code review, terraform validate and plan, (no actual `terraform apply` was executed)

References used:

- FastAPI documentation
- AWS S3 bucket naming rules

AI tooling (Codex) was used for initial scaffolding and documentation assistance, followed by manual review and fixes.

Changes were intentionally kept minimal to stay focused on the assignment requirements while ensuring correctness and basic production readiness.

The repository structure and README were organized around the three main deliverables:

- API Service
- Terraform
- Helm

so reviewers can quickly locate the relevant sections.
