import os, smtplib, ssl, boto3
from urllib.parse import parse_qsl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mako.template import Template

region = os.environ['AWS_REGION']
stage_prefix = os.environ['STAGE_PREFIX']

dynamodb = boto3.resource('dynamodb', region_name=region)
payment_table = dynamodb.Table(stage_prefix+'payments')
courses_table = dynamodb.Table(stage_prefix+'courses')

def send_email(email_to, course_name, amount, date, location):
    html = Template(filename='mail_template.html', input_encoding='UTF-8').render_unicode(course_name, amount, date, location).encode('UTF-8')
    email_from = 'sender_email@gmail.com'  #dajesz email symentis chyba
    password = 'xxx'
    email_message = MIMEMultipart()
    email_message['From'], email_message['To'], email_message['Subject'] = email_from, email_to, "Zakup szkolenia Symentis"
    email_message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server: #tutaj wpisujesz swoj email provider i port(?)
        server.login(email_from, password)
        server.sendmail(email_from, email_to, email_message.as_string())
    
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
