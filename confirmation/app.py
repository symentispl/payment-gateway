import os,boto3,json
from urllib.parse import parse_qsl
from mako.template import Template
from botocore.exceptions import ClientError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

region = os.environ['AWS_REGION']
stage_prefix = os.environ['STAGE_PREFIX']

send_grid_api_key_secret = "send-grid-api-key"
allowed_ip = ['195.149.229.109', '148.251.96.163', '178.32.201.77', '46.248.167.59', '46.29.19.106', '176.119.38.175']

dynamodb = boto3.resource('dynamodb', region_name=region)
payment_table = dynamodb.Table(stage_prefix+'payments')
courses_table = dynamodb.Table(stage_prefix+'courses')
mail_template=Template(filename='mail_template.html', input_encoding='UTF-8')

def lambda_handler(event, context=None):
    item = dict()
    for i in parse_qsl(event['body']):
        item[i[0]] = i[1]
    source_ip = event['requestContext']['identity']['sourceIp']
    if source_ip in allowed_ip or stage_prefix == "test.":
        payment_table.put_item(Item=item)
        if item['tr_status'] == 'TRUE':
            course_name = item['tr_desc']
            response = courses_table.get_item(Key = {'course_name': course_name})
            if "Item" in response:
                course = response['Item']
                send_email(item['tr_email'], course_name, item['tr_amount'], course['date'], course['location'])
    print(event)
    response = dict()
    response["statusCode"] = 200
    response["body"] = "TRUE"
    return response

def send_email(email_to, course_name, amount, date, location):
    print("sending confirmation email to {}".format(email_to))
    html = mail_template.render_unicode(course_name=course_name, amount=amount, date=date, location=location)
    email_from = 'jaroslaw.palka@symentis.pl'  
    message = Mail(
    from_email=email_from,
    to_emails=email_to,
    subject='Zakup szkolenia',
    html_content=html)
    try:
        sendgrid_api_key = get_sendgrid_api_key()
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print("confirmation mail sent with response {}".format(response))
    except Exception as e:
        print("confirmation sent failed with message {}".format(e.message))
    
def get_sendgrid_api_key():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=send_grid_api_key_secret
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)["api-key"]
