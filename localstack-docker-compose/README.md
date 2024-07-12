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