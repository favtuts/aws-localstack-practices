import boto3
import os

endpoint_url = "http://localhost.localstack.cloud:4566"
lambda_client = boto3.client('lambda', endpoint_url=endpoint_url)

# creating function from zip file
current_dir = os.path.dirname(os.path.realpath(__file__))
print(current_dir)
zip_filename = current_dir+"/consumer.zip"
with open(zip_filename, 'rb') as f:
    create_resp = lambda_client.create_function(
        FunctionName="consumer",
        Runtime="python3.10",
        Role="arn:aws:iam::000000000000:role/lambda-role",
        Handler="consumer.handler",
        Code={'ZipFile': f.read()},
        MemorySize=128,
    )

# creating event source mapping, which allows read last 20 inputs to the SQS queue
event_source_resp = lambda_client.create_event_source_mapping(
    EventSourceArn='arn:aws:sqs:us-east-1:000000000000:app-queue',
    FunctionName='consumer',
    Enabled=True,
    BatchSize=20,
    MaximumBatchingWindowInSeconds=60,   
)