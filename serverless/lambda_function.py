import base64, json, os
from decimal import Decimal

import boto3

tabla = boto3.resource("dynamodb").Table(os.environ.get("TABLA", "condor-scores"))


def lambda_handler(event, context):
    metodo = event["requestContext"]["http"]["method"]

    if metodo == "POST":                       # registrar el resultado de una carrera
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)
        d = json.loads(body)
        tabla.update_item(
            Key={"jugador": d["jugador"]},
            UpdateExpression="ADD puntos :p, partidas :uno",
            ExpressionAttributeValues={":p": Decimal(str(d["puntos"])), ":uno": 1},
        )
        return {"statusCode": 201, "body": "ok"}

    # GET: top 10 (scan sirve para el laboratorio; en producción usar un índice)
    items = tabla.scan(ProjectionExpression="jugador, puntos")["Items"]
    top = sorted(items, key=lambda i: i["puntos"], reverse=True)[:10]
    return {"statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(top, default=int)}
