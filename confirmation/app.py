import os, smtplib, ssl, boto3,json
from urllib.parse import parse_qsl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.template import Template
from botocore.exceptions import ClientError


region = os.environ['AWS_REGION']
stage_prefix = os.environ['STAGE_PREFIX']

smtp_secret_name = "ses-smtp-user"

dynamodb = boto3.resource('dynamodb', region_name=region)
payment_table = dynamodb.Table(stage_prefix+'payments')
courses_table = dynamodb.Table(stage_prefix+'courses')

def lambda_handler(event, context=None):
    item = dict()
    for i in parse_qsl(event['body']):
        item[i[0]] = i[1]
    if event['requestContext']['identity']['sourceIp'] in ['195.149.229.109', '148.251.96.163', '178.32.201.77', '46.248.167.59', '46.29.19.106', '176.119.38.175']:
        payment_table.put_item(Item=item)
        if item['tr_status'] == 'TRUE':
            course_name = item['tr_desc']
            course = courses_table.get_item(Key = {'course_name': course_name})['Item']
            send_email(item['tr_email'], course_name, item['tr_amount'], course['date'], course['location'])
    print(event)
    response = dict()
    response["statusCode"] = 200
    response["body"] = "TRUE"
    return response

def send_email(email_to, course_name, amount, date, location):
    smtp_secret = get_smtp_secret()
    html = Template(filename='mail_template.html', input_encoding='UTF-8').render_unicode(course_name, amount, date, location).encode('UTF-8')
    email_from = 'no-replay@payment.jvmperformance.pl'  
    email_message = MIMEMultipart()
    email_message['From'], email_message['To'], email_message['Subject'] = email_from, email_to, "Zakup szkolenia Symentis"
    email_message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("email-smtp.eu-central-1.amazonaws.com", 587, context=context) as server: #tutaj wpisujesz swoj email provider i port(?)
        server.login(smtp_secret["smtp-username"], smtp_secret["smtp-password"])
        server.sendmail(email_from, email_to, email_message.as_string())
    
def get_smtp_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=smtp_secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
