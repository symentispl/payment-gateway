# payment gateway

## Environment

This project needs:

* Python 3.9, because AWS lambda requires specific Python
* (AWS SAM CLI)[https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html], to manage infrastructure
* access to AWS account

The best way to manage the environment and dependencies is to use (Conda)[https://docs.conda.io/en/latest/miniconda.html].

Once you have conda installed you need to create a virtual environment:

    conda create -n payment-gateway python=3.9

once this is done you can activate your environment:

    conda activate payment-gateway

and install AWS SAM (we are using pip, there is something wrong with conda package):

    pip install aws-sam-cli

If you want to see if SAM template works, you can run sync of lambda code with AWS.REMEMBER: you need to configure access to AWS, https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

    sam sync --stack-name sam-app --watch

This will deploy lambda and redeploy it every time you change lambda code. HTTP URL
lambda will be printed out in command output:

    Key                 HelloWorldApi                                                               
    Description         API Gateway endpoint URL for Prod stage for Hello World function            
    Value               https://jfeln3n803.execute-api.eu-north-1.amazonaws.com/Prod/hello/ 

Enter URL in browser to see if it works.