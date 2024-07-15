import boto3

# use this endpoint for localstack
endpoint_url = "http://localhost.localstack.cloud:4566"

s3 = boto3.client("s3", endpoint_url=endpoint_url)

def bucket_exists(bucket):
  s3res = boto3.resource(service_name='s3', endpoint_url=endpoint_url)
  return s3res.Bucket(bucket) in s3res.buckets.all()

# list all S3 bucket
print(s3.list_buckets())

# create new bucket
bucket_name = 'test-bucket'
bucket_region = 'us-west-1'
if (not bucket_exists(bucket_name)):    
    create_bucket_resp = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
        'LocationConstraint': bucket_region})
    print(create_bucket_resp)

# put object to the new bucket
put_object_resp = s3.put_object(
    Body='test.txt',
    Bucket=bucket_name,
    Key='test.txt',
)
print(put_object_resp)

# list objects in this bucket
list_obj_resp = s3.list_objects_v2(
    Bucket=bucket_name
)
print(list_obj_resp['Contents'])