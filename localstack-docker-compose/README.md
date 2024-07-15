# Simulating AWS environment locally with AWS Localstack

# Configure AWS CLI

```
$ aws configure
```

# Create docker-compose.yaml file

Copying the entire [docker-compose.yml from LocalStack github repository](https://github.com/localstack/localstack/blob/master/docker-compose.yml) from

* [docker-compose.yaml](./docker-compose.yaml)
 

# Run AWS Localstack with Docker-Compose

Start services to see the logs
```
$ docker compose up
```

Start services running on background
```
$ docker compose up -d
```

Check container
```
$ docker ps -a
```

Stop services
```
$ docker compose down
```


# Connection to LocalStack

After start services, LocalStack container will start an endpoint URL as `https://localhost:4566` or `https://localhost.localstack.cloud:4566`, which is being used by AWS CLI or SDK to emulate AWS services. There are also pre-defined external services port set to `4510-4599`. 

Note: Starting with version 0.11.0, all APIs are exposed via a single edge service, which is accessible on `http://localhost:4566` by default (customizable via EDGE_PORT, see further below). Please use the single port 4566 (edge service) to access all LocalStack APIs from now on

Verify the endpoint `info`:
```bash
$ curl --silent https://localhost.localstack.cloud:4566/_localstack/info | jq
{
  "version": "3.5.1.dev:b58b0f8ef",
  "edition": "community",
  "is_license_activated": false,
  "session_id": "7e4bdece-0893-40cd-9ced-18d99a3e603e",
  "machine_id": "dkr_2e4ab4757fd5",
  "system": "linux",
  "is_docker": true,
  "server_time_utc": "2024-07-12T08:46:09",
  "uptime": 2515
}
```

Verify the endpoint `health`:
```bash
$ curl --silent https://localhost.localstack.cloud:4566/_localstack/health | jq
{
  "services": {
    "acm": "disabled",
    "apigateway": "disabled",
    "cloudformation": "available",
    "cloudwatch": "running",
    "config": "disabled",
    "dynamodb": "available",
    "dynamodbstreams": "available",
    "ec2": "disabled",
    "es": "disabled",
    "events": "disabled",
    "firehose": "disabled",
    "iam": "disabled",
    "kinesis": "available",
    "kms": "disabled",
    "lambda": "disabled",
    "logs": "disabled",
    "opensearch": "disabled",
    "redshift": "disabled",
    "resource-groups": "disabled",
    "resourcegroupstaggingapi": "disabled",
    "route53": "disabled",
    "route53resolver": "disabled",
    "s3": "available",
    "s3control": "disabled",
    "scheduler": "disabled",
    "secretsmanager": "disabled",
    "ses": "disabled",
    "sns": "running",
    "sqs": "running",
    "ssm": "available",
    "stepfunctions": "disabled",
    "sts": "available",
    "support": "disabled",
    "swf": "disabled",
    "transcribe": "disabled"
  },
  "edition": "community",
  "version": "3.5.1.dev"
}
```

# Create Profile for LocalStack

Now we can configure AWS profile and start using LocalStack:

1 - Append these lines into your `~/.aws/config`:
```ini
[profile localstack]
output = json
region = us-east-1
endpoint_url = https://localhost.localstack.cloud:4566
cli_pager=
```

2 - Add the default AWS Access and Secret key of LocalStack into `~/.aws/credentials`:
```ini
[localstack]
aws_access_key_id=test
aws_secret_access_key=test
```

We are going to test Profile for LocalStack. The first example is creating a static website hosted in S3:
1 - Created new S3 bucket:
```bash
$ AWS_PROFILE=localstack aws s3api create-bucket --bucket james-bucket
{
    "Location": "/james-bucket"
}
$ AWS_PROFILE=localstack aws s3 ls s3://
2024-07-12 15:55:59 james-bucket
```
2 - Create a sample `index.html` with following content:
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Welcome to James' home</title>
    </head>
    <body>
        <p>This is an example webpage to test a S3 static webapp in LocalStack.</p>
    </body>
</html>
```
3 - Upload the file into S3 and make it as static website:
```bash
$ AWS_PROFILE=localstack aws s3 cp bucketsamples/index.html s3://james-bucket
upload: bucketsamples/index.html to s3://james-bucket/index.html
```

Make static website:
```bash
$ AWS_PROFILE=localstack aws s3 website s3://james-bucket --index-document index.html
```

Now we can test the website by opening this URL `https://james.s3-website.localhost.localstack.cloud:4566`:
```bash
$ curl https://james-bucket.s3-website.localhost.localstack.cloud:4566
<!DOCTYPE html>
<html>
    <head>
        <title>Welcome to James' home</title>
    </head>
    <body>
        <p>This is an example webpage to test a S3 static webapp in LocalStack.</p>
    </body>
</html>
```

# Test LocalStack with SQS queue

Append the `sqs` to the `SERVICES` varbiable in the file `.env`, then start services again.

Let's create a SQS queue
```bash
$ aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name hello-world
{
    "QueueUrl": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/hello-world"
}
```

Let’s send a message to the new queue:
```bash
$ aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/hello-world --message-body "My first Message"
{
    "MD5OfMessageBody": "f34fac8f20963dabd7a76a2f0ea7b3bc",
    "MessageId": "59b27acb-ae97-4b16-89ee-e7e272511200"
}
```

We can also see the messages from our new queue:
```bash
$ aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/hello-world --max-number-of-messages 10
{
    "Messages": [
        {
            "MessageId": "59b27acb-ae97-4b16-89ee-e7e272511200",
            "ReceiptHandle": "NTI5ZjAwMmQtNWVmZS00ZjdkLTk4ZDktMDU3NDNlZjM5N2ZmIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6aGVsbG8td29ybGQgNTliMjdhY2ItYWU5Ny00YjE2LTg5ZWUtZTdlMjcyNTExMjAwIDE3MjA3NjgxMDIuNDE2OTg0OA==",
            "MD5OfBody": "f34fac8f20963dabd7a76a2f0ea7b3bc",
            "Body": "My first Message"
        }
    ]
}
```

# Test LocalStack with S3 bucket

Create a S3 Bucket:
```bash
$ aws --endpoint-url=http://localhost:4566 s3 mb s3://avatar-bucket
make_bucket: avatar-bucket
```

List all S3 buckets
```bash
$ aws --endpoint-url http://localhost:4566 s3 ls
2024-07-12 11:25:37 avatar-bucket
```

Create another S3 bucket
```bash
$ aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
```

List all S3 bucket again
```bash
$ aws --endpoint-url http://localhost:4566 s3 ls
2024-07-12 11:25:37 avatar-bucket
2024-07-12 11:29:57 test-bucket
```

Create a text file:
```bash
$ mkdir bucketsamples
$ touch bucketsamples/foobar.txt
$ echo -e "sentence1 \nsentence2 \nsentence3" >> bucketsamples/foobar.txt
```

Upload file to your bucket
```bash
$ aws --endpoint-url=http://localhost:4566 s3 cp bucketsamples/foobar.txt s3://test-bucket
```

List objects in your bucket:
```bash
$ aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket
2024-07-12 13:47:10         32 foobar.txt
```

Delete this file
```bash
$ aws --endpoint-url=http://localhost:4566 s3 rm s3://test-bucket/foobar.txt
```

# Test LocalStack with DynamoDB

## Create Table

```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name test_table  --attribute-definitions AttributeName=first,AttributeType=S AttributeName=second,AttributeType=N --key-schema AttributeName=first,KeyType=HASH AttributeName=second,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
{
   "TableDescription": {
       "TableArn": "arn:aws:dynamodb:us-east-1:000000000000:table/test_table",
       "AttributeDefinitions": [
           {
               "AttributeName": "first",
               "AttributeType": "S"
           },
           {
               "AttributeName": "second",
               "AttributeType": "N"
           }
       ],
       "ProvisionedThroughput": {
           "NumberOfDecreasesToday": 0,
           "WriteCapacityUnits": 5,
           "ReadCapacityUnits": 5
       },
       "TableSizeBytes": 0,
       "TableName": "test_table",
       "TableStatus": "CREATING",
       "KeySchema": [
           {
               "KeyType": "HASH",
               "AttributeName": "first"
           },
           {
               "KeyType": "RANGE",
               "AttributeName": "second"
           }
       ],
       "ItemCount": 0,
       "CreationDateTime": 1491818083.66
   }
}
```

We can verify our created table
```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb list-tables
{
    "TableNames": [
        "test_table"
    ]
}
```

and describe it too
```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb describe-table --table-name test_table
```

## Put item
```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb put-item --table-name test_table  --item '{"first":{"S":"Jack"},"second":{"N":"42"}}'
$ aws --endpoint-url=http://localhost:4566 dynamodb put-item --table-name test_table  --item '{"first":{"S":"Manish"},"second":{"N":"40"}}'
```

## Scan Table
```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name test_table
{
    "Items": [
        {
            "first": {
                "S": "Jack"
            },
            "second": {
                "N": "42"
            }
        },
        {
            "first": {
                "S": "Manish"
            },
            "second": {
                "N": "40"
            }
        }
    ],
    "Count": 2,
    "ScannedCount": 2,
    "ConsumedCapacity": null
}
```


## Get item
```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb get-item --table-name test_table  --key '{"first":{"S":"Manish"},"second":{"N":"40"}}'
{
    "Item": {
        "first": {
            "S": "Manish"
        },
        "second": {
            "N": "40"
        }
    }
}
```

## Query

I hate to query over CLI, and you can see why. Hope this can help you realize that the best way to deal with DynamoDB is via an SDK.

```bash
$ aws --endpoint-url=http://localhost:4566 dynamodb query --table-name test_table --projection-expression "#first, #second" --key-condition-expression "#first = :value" --expression-attribute-values '{":value" : {"S":"Manish"}}' --expression-attribute-names '{"#first":"first", "#second":"second"}'
{
    "Items": [
        {
            "first": {
                "S": "Manish"
            },
            "second": {
                "N": "40"
            }
        }
    ],
    "Count": 1,
    "ScannedCount": 1,
    "ConsumedCapacity": null
}
```

# Test LocalStack with SNS

## Create a topic

List all topics
```bash
$ aws --endpoint-url=http://localhost:4566 sns list-topics
```

Create new topic
```bash
$ aws --endpoint-url=http://localhost:4566 sns create-topic --name test-topic
{
    "TopicArn": "arn:aws:sns:us-east-1:000000000000:test-topic"
}
```

List topics again to verify
```bash
$ aws --endpoint-url=http://localhost:4566 sns list-topics
{
    "Topics": [
        {
            "TopicArn": "arn:aws:sns:us-east-1:000000000000:test-topic"
        }
    ]
}
```


## Subscribe to the topic

(use any random email)

```bash
$ aws --endpoint-url=http://localhost:4566 sns subscribe --topic-arn arn:aws:sns:us-east-1:000000000000:test-topic --protocol email --notification-endpoint favtuts@gmail.com
{
    "SubscriptionArn": "arn:aws:sns:us-east-1:000000000000:test-topic:568e05b4-a34d-43e5-9bab-39d59b6fb10d"
}
```


## Publish to this topic

```bash
$ aws --endpoint-url=http://localhost:4566 sns publish  --topic-arn arn:aws:sns:us-east-1:000000000000:test-topic --message 'Test Message!'
{
    "MessageId": "fa345427-a0a4-48e3-9a09-b8b482eae1f8"
}
```

## SNS-SQS Fanout
* https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html

When you subscribe an Amazon SQS queue to an Amazon SNS topic, you can publish a message to the topic and Amazon SNS sends an Amazon SQS message to the subscribed queue.


Create a SQS first
```bash
$ aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name fan-out-sqs
{
    "QueueUrl": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/fan-out-sqs"
}
```
Get QueueArn attribute
```bash
$ aws sqs get-queue-attributes --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/fan-out-sqs --attribute-names QueueArn --endpoint-url=http://localhost:4566
{
    "Attributes": {
        "QueueArn": "arn:aws:sqs:us-east-1:000000000000:fan-out-sqs"
    }
}
```

Create a SNS topic
```bash
$ aws --endpoint-url=http://localhost:4566 sns create-topic --name fan-out-topic
{
    "TopicArn": "arn:aws:sns:us-east-1:000000000000:fan-out-topic"
}
```

Subscribe SQS with QueueArn to SNS topic
```bash
$ aws --endpoint-url=http://localhost:4566 sns subscribe --protocol sqs --topic-arn "arn:aws:sns:us-east-1:000000000000:fan-out-topic"  --notification-endpoint "arn:aws:sqs:us-east-1:000000000000:fan-out-sqs"
{
    "SubscriptionArn": "arn:aws:sns:us-east-1:000000000000:fan-out-topic:da814fd5-448b-4ad4-bf48-34c2e447385f"
}
```

Verify the list of subscriptions
```bash
$ aws --endpoint-url=http://localhost:4566 sns list-subscriptions
{
    "Subscriptions": [
        {
            "SubscriptionArn": "arn:aws:sns:us-east-1:000000000000:test-topic:568e05b4-a34d-43e5-9bab-39d59b6fb10d",
            "Owner": "000000000000",
            "Protocol": "email",
            "Endpoint": "favtuts@gmail.com",
            "TopicArn": "arn:aws:sns:us-east-1:000000000000:test-topic"
        },
        {
            "SubscriptionArn": "arn:aws:sns:us-east-1:000000000000:fan-out-topic:da814fd5-448b-4ad4-bf48-34c2e447385f",
            "Owner": "000000000000",
            "Protocol": "sqs",
            "Endpoint": "arn:aws:sqs:us-east-1:000000000000:fan-out-sqs",
            "TopicArn": "arn:aws:sns:us-east-1:000000000000:fan-out-topic"
        }
    ]
}
```

Publish a message to SNS
```bash
$ aws --endpoint-url=http://localhost:4566 sns  publish --topic-arn "arn:aws:sns:us-east-1:000000000000:fan-out-topic" --message "for fanout"
{
    "MessageId": "c6413aef-e739-4846-8b26-b39a1df9f939"
}
```

Final, you can receive the message on SQS
```bash
$ aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/fan-out-sqs
{
    "Messages": [
        {
            "MessageId": "557bfbb7-921f-421e-b5b7-bda2358ba055",
            "ReceiptHandle": "ZTUzZTNhNWYtM2ZlZS00MGM2LWJmODUtMzhiMThhNDdiYTA1IGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6ZmFuLW91dC1zcXMgNTU3YmZiYjctOTIxZi00MjFlLWI1YjctYmRhMjM1OGJhMDU1IDE3MjA3NzM0MTguMzk5NTg1Nw==",
            "MD5OfBody": "ba4044a34e66748b78600dc4fb5615cf",
            "Body": "{\"Type\": \"Notification\", \"MessageId\": \"c6413aef-e739-4846-8b26-b39a1df9f939\", \"TopicArn\": \"arn:aws:sns:us-east-1:000000000000:fan-out-topic\", \"Message\": \"for fanout\", \"Timestamp\": \"2024-07-12T08:35:13.408Z\", \"UnsubscribeURL\": \"http://localhost.localstack.cloud:4566/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:000000000000:fan-out-topic:da814fd5-448b-4ad4-bf48-34c2e447385f\", \"SignatureVersion\": \"1\", \"Signature\": \"NLGMBnblch3NJn+49kkh+GhZ52/Uqg6McvsdsnVoHGflCs+X9qN4ZIkY3dEXkScI4TnD0OavelT+lFX+o+4FihWMS0GD2ZeAwA3JIMQy8kfhsUifNJyR/WZmNEKhYq0jYqZ9DetpSrzzsaX2+WBXJ7aX6GwnZlaD5z/PEc/kmEwquPyny0dKO3/Q7mXq0q0cbX4QFwR2S51wYsFoNoLaF6uV5N4mgtX7A3LFVkRC/v1OPQRxinKhfdD2F+NMO4fzticMfedfAHanUJBJYyLpYDfR6xqS/5Cexv8iCJKlav6hjWLTj/1W9LF0S9pIgmR9sqZsrxts3XQnlJbfCu7oOg==\", \"SigningCertURL\": \"http://localhost.localstack.cloud:4566/_aws/sns/SimpleNotificationService-6c6f63616c737461636b69736e696365.pem\"}"
        }
    ]
}
```


# LocalStack peristentce

From now, Persistent is the feature only on LocalStack pro. For the community edition, can consider to user the open source image: https://hub.docker.com/r/gresau/localstack-persist

# Reference
* https://github.com/localstack/localstack/issues/3080
* https://github.com/kevinadhiguna/jiyu/tree/master/aws-localstack
* https://gist.github.com/davidmerrick/db6cf82a279d59485ffc2d5de368940e
* https://lobster1234.github.io/2017/04/05/working-with-localstack-command-line/
* https://github.com/localstack/localstack/issues/510
* https://www.devlo.io/run-localstack-with-docker-compose.html
* https://medium.com/wearesinch/simulating-aws-environment-locally-with-aws-localstack-ad5a80413d71
* https://tunguyen9889.medium.com/localstack-getting-started-85b5d2699eef
* https://github.com/localstack/localstack/issues/6398