import boto3
from boto3.dynamodb.conditions import Key
import json
import os

region = os.environ['AWS_REGION']
stage_prefix = os.environ['STAGE_PREFIX']

dynamodb = boto3.resource('dynamodb', region_name=region)
courses_table = dynamodb.Table(stage_prefix+'courses')

def lambda_handler(event, context=None):
    params = event.get('queryStringParameters')
    client = params.get('client')
    courses_data = courses_table.query(IndexName='course_site_index',
                                       KeyConditionExpression=Key("course_site").eq(client))["Items"]
    response = dict()
    response["statusCode"] = 200
    response["headers"] = {"content-type": "application/json"}
    response["body"] = json.dumps(find_courses(courses_data, client))
    return response

def find_courses(courses_data, client):
    print("find courses for {} in {}".format(client, courses_data))
    return [serialize_course(course)
            for course in courses_data if course['is_active'] == True]

def serialize_course(course):
    return {"name": course["course_name"],
            "location": course["location"],
            "location_url" : course["location_url"],
            "date": course["date"],
            "amount": str(course["amount"])}
