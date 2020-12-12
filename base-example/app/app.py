import sys
import json

def handler(event, context): 

    # prediction = model.predict(url)
    response = {
        "statusCode": 200,
        "body": json.dumps(event['body'])
    }

    return response