import uuid
import hashlib
import json

def lambda_handler(event, context=None):
    code = 'GqtXpYSEk160KOW9'
    id=31744
    params = event.get('queryStringParameters')
    amount = params.get('amount')
    description = params.get('description')
    crc = uuid.uuid4()
    md5string = '&'.join([str(id),str(amount),str(crc),code])
    url = f'https://secure.tpay.com?id=31744&amount={amount}&description={description}&crc={crc}&md5sum={hashlib.md5(md5string.encode("utf-8")).hexdigest()}'
    response = dict()
    response["statusCode"] = 303
    response["body"] = json.dumps(dict())
    response["headers"] = {"Location": url}
    return response