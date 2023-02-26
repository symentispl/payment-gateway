import json
from urllib.parse import parse_qsl
import boto3

def lambda_handler(event, context=None):
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    table = dynamodb.Table('payments')
    item= dict()
    for i in parse_qsl(event['body']):
        item[i[0]] = i[1]
    if event['requestContext']['identity']['sourceIp'] in ['195.149.229.109', '148.251.96.163', '178.32.201.77', '46.248.167.59', '46.29.19.106', '176.119.38.175']:
        table.put_item(Item=item)
    print(event)
    response = dict()
    response["statusCode"] = 200
    response["body"] = "TRUE"
    return response