# Simulating AWS environment locally with AWS Localstack

# Configure AWS CLI

```
$ aws configure
```

# Create docker-compose.yaml file
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
```
$ aws --endpoint-url=http://localhost:4566 s3 mb s3://avatar-bucket
make_bucket: avatar-bucket
```

List all S3 buckets
```
$ aws --endpoint-url http://localhost:4566 s3 ls
2024-07-12 11:25:37 avatar-bucket
```

Create another S3 bucket
```
$ aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
```

List all S3 bucket again
```
$ aws --endpoint-url http://localhost:4566 s3 ls
2024-07-12 11:25:37 avatar-bucket
2024-07-12 11:29:57 test-bucket
```

Create a text file:
```
$ touch foobar.txt
$ echo -e "sentence1 \nsentence2 \nsentence3" >> foobar.txt
```

Upload file to your bucket
```
$ aws --endpoint-url=http://localhost:4566 s3 cp foobar.txt s3://test-bucket
```

List objects in your bucket:
```
$ aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket
2024-07-12 13:47:10         32 foobar.txt
```

# Reference
* https://github.com/localstack/localstack/issues/3080
* https://github.com/kevinadhiguna/jiyu/tree/master/aws-localstack
* https://gist.github.com/davidmerrick/db6cf82a279d59485ffc2d5de368940e