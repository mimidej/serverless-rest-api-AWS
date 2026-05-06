import json
import boto3
import uuid
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "tasks"


def get_table():
    return dynamodb.Table(TABLE_NAME)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    http_method = event.get("httpMethod", "")
    path_params = event.get("pathParameters") or {}
    task_id = path_params.get("id")

    try:
        if http_method == "GET" and not task_id:
            return get_all_tasks()
        elif http_method == "GET" and task_id:
            return get_task(task_id)
        elif http_method == "POST":
            body = json.loads(event.get("body") or "{}")
            return create_task(body)
        elif http_method == "PUT" and task_id:
            body = json.loads(event.get("body") or "{}")
            return update_task(task_id, body)
        elif http_method == "DELETE" and task_id:
            return delete_task(task_id)
        else:
            return response(400, {"error": "Invalid request"})
    except Exception as e:
        return response(500, {"error": str(e)})


def get_all_tasks():
    table = get_table()
    result = table.scan()
    return response(200, {"tasks": result.get("Items", [])})


def get_task(task_id):
    table = get_table()
    result = table.get_item(Key={"id": task_id})
    item = result.get("Item")
    if not item:
        return response(404, {"error": "Task not found"})
    return response(200, item)


def create_task(body):
    if "title" not in body:
        return response(400, {"error": "Field 'title' is required"})

    table = get_table()
    task = {
        "id": str(uuid.uuid4()),
        "title": body["title"],
        "description": body.get("description", ""),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    table.put_item(Item=task)
    return response(201, task)


def update_task(task_id, body):
    table = get_table()

    # Verify task exists
    result = table.get_item(Key={"id": task_id})
    if not result.get("Item"):
        return response(404, {"error": "Task not found"})

    # Build update expression dynamically
    allowed_fields = {"title", "description", "status"}
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return response(400, {"error": "No valid fields to update"})

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
    names = {f"#{k}": k for k in updates}
    values = {f":{k}": v for k, v in updates.items()}

    result = table.update_item(
        Key={"id": task_id},
        UpdateExpression=expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ReturnValues="ALL_NEW",
    )
    return response(200, result.get("Attributes", {}))


def delete_task(task_id):
    table = get_table()

    result = table.get_item(Key={"id": task_id})
    if not result.get("Item"):
        return response(404, {"error": "Task not found"})

    table.delete_item(Key={"id": task_id})
    return response(200, {"message": f"Task {task_id} deleted successfully"})
