import boto3
import json


def lambda_handler(event, context=None):
    params = event.get('queryStringParameters')
    client = params.get('client')
    print("client is {}".format(client))
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    courses_table = dynamodb.Table('courses')
    print("courses table {}".format(courses_table))
    courses_data = courses_table.scan()['Items']
    print("courses data {}".format(courses_data))
    response = dict()
    response["statusCode"] = 200
    response["headers"] = {"content-type": "application/json"}
    response["body"] = json.dumps(find_courses(courses_data, client))
    return response


def find_courses(courses_data, client):
    print("find courses for {} in {}".format(client, courses_data))
    return [serialize_course(course)
            for course in courses_data if course['host_site'] == client and course['is_active'] == True]


def serialize_course(course):
    return {"name": course["course_name"],
            "location": course["location"],
            "date": course["date"],
            "amount": str(course["amount"])}
