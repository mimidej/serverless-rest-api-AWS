# serverless-rest-api

A production-ready serverless REST API built with AWS Lambda, API Gateway, and DynamoDB. Implements full CRUD operations for a task manager using Python and Infrastructure as Code with AWS SAM.

---

## Architecture

```
Client (HTTP)
    │
    ▼
API Gateway  ──────────────────► CloudWatch Logs
    │
    ▼
Lambda (Python 3.12)
    │
    ▼
DynamoDB
```

| Service | Role |
|---|---|
| **API Gateway** | Exposes REST endpoints, handles routing and CORS |
| **Lambda** | Business logic, stateless function triggered by HTTP events |
| **DynamoDB** | NoSQL database, on-demand billing |
| **IAM Role** | Least-privilege permissions for Lambda → DynamoDB |
| **CloudWatch** | Automatic logs and metrics for every invocation |

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/tasks` | List all tasks |
| `GET` | `/tasks/{id}` | Get a single task |
| `POST` | `/tasks` | Create a new task |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

---

## Request & Response Examples

### Create a task
```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk and eggs"}'
```

```json
{
  "id": "a3f1c2d4-...",
  "title": "Buy groceries",
  "description": "Milk and eggs",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00+00:00",
  "updated_at": "2025-01-15T10:30:00+00:00"
}
```

### Update a task
```bash
curl -X PUT https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/tasks/a3f1c2d4-... \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Delete a task
```bash
curl -X DELETE https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/tasks/a3f1c2d4-...
```

---

## Project Structure

```
serverless-rest-api/
├── src/
│   └── handler.py              # Lambda function (Python 3.12)
├── infra/
│   └── template.yaml           # AWS SAM infrastructure template
├── tests/
│   └── test_handler.py         # Unit tests with mocked AWS services
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline (GitHub Actions)
└── README.md
```

---

## Local Development

### Prerequisites
- Python 3.12+
- AWS SAM CLI
- AWS CLI configured with credentials

### Run tests locally
```bash
python -m pytest tests/ -v
```

### Deploy to AWS
```bash
# Build
sam build -t infra/template.yaml

# Deploy (first time)
sam deploy --guided

# Deploy (subsequent times)
sam deploy
```

---

## CI/CD Pipeline

Every push to `main` triggers the GitHub Actions workflow:

1. **Test** — runs unit tests with mocked DynamoDB
2. **Deploy** — builds and deploys via SAM to AWS

To enable deployment, add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

---

## AWS Free Tier

This project runs entirely within the AWS Free Tier:

| Service | Free Tier Limit |
|---|---|
| Lambda | 1M requests/month |
| API Gateway | 1M requests/month (first 12 months) |
| DynamoDB | 25 GB storage, 25 WCU/RCU |
| CloudWatch | 5 GB logs ingestion/month |

---

## Skills Demonstrated

- Serverless architecture on AWS
- Infrastructure as Code (AWS SAM / CloudFormation)
- RESTful API design
- Python (boto3, unit testing with mocks)
- CI/CD with GitHub Actions
- IAM least-privilege security
- NoSQL data modeling with DynamoDB

---

## Author

Built as part of an AWS Cloud Practitioner & AI Practitioner portfolio.
