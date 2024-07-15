import boto3

# use this endpoint for localstack
endpoint_url = "http://localhost.localstack.cloud:4566"

s3 = boto3.client("s3", endpoint_url=endpoint_url)

# list all S3 bucket
print(s3.list_buckets())

# create new bucket
create_bucket_resp = s3.create_bucket(Bucket='test-bucket', CreateBucketConfiguration={
    'LocationConstraint': 'us-west-1'})
print(create_bucket_resp)