import boto3
import uuid
import hashlib
import json

def encode_description(description):
    result = ""
    for i in description:
        if i.isupper():
            result=result+"%20"+i.upper()
        else:
            result=result+i
    return result[3:]

def lambda_handler(event, context=None):
    code = 'GqtXpYSEk160KOW9'
    id=31744
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    table = dynamodb.Table('courses')
    params = event.get('queryStringParameters')
    course_name = params.get('course_name')
    discount = params.get('discount')
    amount = table.get_item(Key = {'course_name': course_name})['Item']['amount']
    if type(amount) == int:
        amount = float(amount)
    description = encode_description(course_name)
    crc = uuid.uuid4()
    md5string = '&'.join([str(id),str(amount),str(crc),code])
    url = f'https://secure.tpay.com?id=31744&amount={amount}&description={description}&crc={crc}&md5sum={hashlib.md5(md5string.encode("utf-8")).hexdigest()}'
    response = dict()
    response["statusCode"] = 303
    response["body"] = json.dumps(dict())
    response["headers"] = {"Location": url}
    return response
