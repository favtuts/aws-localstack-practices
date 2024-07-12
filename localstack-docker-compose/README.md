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


Note: Starting with version 0.11.0, all APIs are exposed via a single edge service, which is accessible on `http://localhost:4566` by default (customizable via EDGE_PORT, see further below). Please use the single port 4566 (edge service) to access all LocalStack APIs from now on


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
$ touch foobar.txt
$ echo -e "sentence1 \nsentence2 \nsentence3" >> foobar.txt
```

Upload file to your bucket
```bash
$ aws --endpoint-url=http://localhost:4566 s3 cp foobar.txt s3://test-bucket
```

List objects in your bucket:
```bash
$ aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket
2024-07-12 13:47:10         32 foobar.txt
```

Delete this file
```bash
$ aws --endpoint-url=http://localhost:4566 s3 rm s3://test-bucket/foobar.txt
delete: s3://mytestbucket/mongo.log
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

# LocalStack peristentce

From now, Persistent is the feature only on LocalStack pro. For the community edition, can consider to user the open source image: https://hub.docker.com/r/gresau/localstack-persist

# Reference
* https://github.com/localstack/localstack/issues/3080
* https://github.com/kevinadhiguna/jiyu/tree/master/aws-localstack
* https://gist.github.com/davidmerrick/db6cf82a279d59485ffc2d5de368940e
* https://lobster1234.github.io/2017/04/05/working-with-localstack-command-line/