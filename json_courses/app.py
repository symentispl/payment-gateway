import boto3

def lambda_handler(event, context=None):
    params = event.get('queryStringParameters')
    client = params.get('client')
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    courses_table = dynamodb.Table('courses')
    courses_data = courses_table.scan()['Items']
    response = dict()
    response["statusCode"] = 200
    if client == 'jvmperformance':
        response["body"] = [course for course in courses_data if course['host_site'] == 'jvmperformance' and course['is_active'] == True]
    elif client == 'symentis':
        response["body"] = [course for course in courses_data if course['host_site'] == 'symentis' and course['is_active'] == True]
    elif client == 'concurrency':
        response["body"] = [course for course in courses_data if course['host_site'] == 'concurrency' and course['is_active'] == True]
    return response