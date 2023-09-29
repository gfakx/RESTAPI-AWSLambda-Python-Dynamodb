import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Notes')

def lambda_handler(event, context):
    noteId = event['noteId']
    title = event['title']
    content = event['content']
    
    response = table.put_item(
        Item={
            'noteId': noteId,
            'title': title,
            'content': content
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Note added successfully!')
    }
