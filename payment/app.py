import boto3, uuid, hashlib, json, os
from botocore.exceptions import ClientError

region = os.environ['AWS_REGION']
stage_prefix = os.environ['STAGE_PREFIX']
tpay_secret_name = "tpay-creds"

dynamodb = boto3.resource('dynamodb', region_name=region)
courses_table = dynamodb.Table(stage_prefix+'courses')
discounts_table = dynamodb.Table(stage_prefix+'discounts')

def lambda_handler(event, context=None):
    params = event.get('queryStringParameters')
    course_name = params.get('course_name')
    discount = params.get('discount')
    tpay_secret = get_tpay_secret()
    
    amount = courses_table.get_item(Key = {'course_name': course_name})['Item']['amount']
    if type(amount) == int:
        amount = float(amount)
    if discount:
        if discounts_table.get_item(Key = {'discount_code': discount})['Item']['is_active'] == True:
            amount -= amount * (discounts_table.get_item(Key = {'discount_code': discount})['Item']['discount_percentage'])/100

    description = encode_description(course_name)
    crc = uuid.uuid4()
    
    md5string = '&'.join([str(tpay_secret['tpay-id']),str(round(amount, 2)),str(crc),tpay_secret['tpay-code']])
    
    url = f'https://secure.tpay.com?id=31744&amount={round(amount, 2)}&description={description}&crc={crc}&md5sum={hashlib.md5(md5string.encode("utf-8")).hexdigest()}&return_url=https://jvmperformance.pl/confirmation&return_error_url=https://jvmperformance.pl/payment_failed'
    response = dict()
    response["statusCode"] = 303
    response["body"] = json.dumps(dict())
    response["headers"] = {"Location": url}
    return response

def encode_description(description):
    result = ""
    for i in description:
        if i.isupper():
            result=result+"%20"+i.upper()
        else:
            result=result+i
    return result[3:]

def get_tpay_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=tpay_secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)