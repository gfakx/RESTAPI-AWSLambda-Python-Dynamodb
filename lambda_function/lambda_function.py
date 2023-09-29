import json
import boto3
import logging
from custom_encoder import DecimalEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Notes')


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    http_method = event['httpMethod']

    if http_method == 'POST':
        return create_note(event)
    elif http_method == 'GET':
        return get_note(event)
    elif http_method == 'PUT':
        return update_note(event)
    elif http_method == 'DELETE':
        return delete_note(event)
    else:
        return build_response(400, {"message": "Invalid HTTP Method"})


def create_note(event):
    body = event.get('body')
    if not body:
        return build_response(400, {"message": "Missing request body"})

    try:
        body = json.loads(body)
        response = table.put_item(Item=body)
        return build_response(200, {"message": "Note added successfully!"})
    except json.JSONDecodeError:
        return build_response(400, {"message": "Invalid JSON format"})
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return build_response(500, {"message": "Error creating note"})


def get_note(event):
    try:
        path_params = event.get('pathParameters', {})
        noteId = path_params.get('noteId')
        if not noteId:
            return build_response(400, {"message": "Missing noteId in path parameters"})

        response = table.get_item(Key={'noteId': noteId})
        if 'Item' in response:
            return build_response(200, response['Item'])
        else:
            return build_response(404, {"message": "Note not found"})
    except Exception as e:
        logger.error(f"Error getting note: {str(e)}")
        return build_response(500, {"message": "Error getting note"})


def update_note(event):
    try:
        noteId = event['pathParameters']['noteId']
        body = event.get('body')
        if not body:
            return build_response(400, {"message": "Missing request body"})

        body = json.loads(body)
        response = table.update_item(
            Key={'noteId': noteId},
            UpdateExpression="set content = :c",
            ExpressionAttributeValues={":c": body['content']},
            ReturnValues="UPDATED_NEW"
        )
        return build_response(200, response['Attributes'])
    except json.JSONDecodeError:
        return build_response(400, {"message": "Invalid JSON format"})
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        return build_response(500, {"message": "Error updating note"})


def delete_note(event):
    try:
        noteId = event['pathParameters']['noteId']
        table.delete_item(Key={'noteId': noteId})
        return build_response(200, {"message": "Note deleted successfully!"})
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        return build_response(500, {"message": "Error deleting note"})


def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body, cls=DecimalEncoder),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
