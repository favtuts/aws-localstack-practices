# Using LocalStack to test AWS services locally
* https://tuts.heomi.net/using-localstack-to-test-aws-services-locally/

# Setting up LocalStack

Create `docker-compose.yml` file which contains the Localstack and Elasticsearch:
```yaml
version: "3.9"

services:
  elasticsearch:
    container_name: elasticsearch
    image: docker.elastic.co/elasticsearch/elasticsearch:7.10.2 # Max version supported by LocalStack
    environment:
      - node.name=elasticsearch
      - cluster.name=es-docker-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - data01:/usr/share/elasticsearch/data

  localstack:
    container_name: "${LOCALSTACK_DOCKER_NAME-localstack_main}"
    image: localstack/localstack
    ports:
      - "4566:4566" # Edge port
    depends_on:
      - elasticsearch
    environment:
      - DEBUG=1
      - OPENSEARCH_ENDPOINT_STRATEGY=port # port, path, domain
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"

volumes:
  data01:
    driver: local
```

To run the stack:
```
$ docker compose up
```

To stop the stack
```
$ docker compose down
```

# Key tools required:
* Node.js (brew install node)
* LocalStack (brew install localstack)
* Python (brew install python) this is required to install `awscli-local`
* `awscli-local` (`pip install awscli-local`) this avoids having to define the endpoint-url on each command

# Creating a Lambda function

Open terminal and run, Accept all the defaults when running through the wizard as it doesn’t really matter.
```
$ npm init
```

Once created run:
```
$ npm install aws-sdk
```
This will install the `aws-sdk` package for the lambda so that it can consume the services hosted within LocalStack.

Create an `index.js` file containing the below code:
```js
const aws = require('aws-sdk');

const s3 = new aws.S3({ 
    apiVersion: '2006-03-01',
    endpoint: `http://${process.env.LOCALSTACK_HOSTNAME}:4566`, // This two lines are
    s3ForcePathStyle: true,                                     // only needed for LocalStack. 
});

module.exports.handler = async event => {
    // Get the object from the event and show its content type
    const bucket = event.Records[0].s3.bucket.name;
    const key = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, ' '));
    const params = {
        Bucket: bucket,
        Key: key,
    };
    try {
        const { ContentType } = await s3.getObject(params).promise();
        console.log('Lambda executed outputting content-type')
        console.log('CONTENT TYPE:', ContentType);
        return ContentType;
    } catch (err) {
        console.log(err);
        const message = `Error getting object ${key} from bucket ${bucket}. Make sure they exist and your bucket is in the same region as this function.`;
        console.log(message);
        throw new Error(message);
    }
};
```

The above code will check the S3 bucket and output the content-type of a dummy file that we will push into the bucket.

Now that we have a Lambda function we now need to package the directory into a zip file so we can upload it to the Lambda service.
```bash
$ zip lambda.zip index.js
```

We will create the lambda function using the below script. Ensure your terminal is pointing to the directory in which your .zip file is held.
```bash
$ awslocal \
lambda create-function --function-name my-lambda \
--region eu-west-1 \
--zip-file fileb://lambda.zip \
--handler index.handler --runtime nodejs12.x \
--role arn:aws:iam::000000000000:role/lambda-role


{
    "FunctionName": "my-lambda",
    "FunctionArn": "arn:aws:lambda:eu-west-1:000000000000:function:my-lambda",
    "Runtime": "nodejs12.x",
    "Role": "arn:aws:iam::000000000000:role/lambda-role",
    "Handler": "index.handler",
    "CodeSize": 755,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2024-07-16T06:54:20.066971+0000",
    "CodeSha256": "hL13DXjEbJdPKG8PLvHuK1NWNdErWhf3Lff8fzIdFX4=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "bdb0c267-0eb0-4260-840e-8e36e06285a9",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Zip",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    },
    "SnapStart": {
        "ApplyOn": "None",
        "OptimizationStatus": "Off"
    },
    "RuntimeVersionConfig": {
        "RuntimeVersionArn": "arn:aws:lambda:eu-west-1::runtime:8eeff65f6809a3ce81507fe733fe09b835899b99481ba22fd75b5a7338290ec1"
    },
    "LoggingConfig": {
        "LogFormat": "Text",
        "LogGroup": "/aws/lambda/my-lambda"
    }
}
```

# Running the demo

To get this demo running, the first is a `dummy txt` file and the second is a json file to setup an event trigger.

Create a `dummy.txt` file within the root of your project.
```bash
$ echo "dummy text" >> dummyfile.txt
```

Create a json file within the root of your project called `‘s3-notif-config.json’` and paste the below code into that file:
```json
{
    "LambdaFunctionConfigurations": [
        {
            "Id": "s3eventtriggerslambda",
            "LambdaFunctionArn": "arn:aws:lambda:eu-west-1:000000000000:function:my-lambda",
            "Events": ["s3:ObjectCreated:*"]
        }
    ]
}
```

Next, we will create a bucket within S3 to hold the dummy txt file.
```bash
$ awslocal s3 mb s3://my-bucket --region eu-west-1
make_bucket: my-bucket
```

We will also push the notification configuration we’ve created earlier so that the Lambda is executed when an item is pushed to the bucket.
```bash
$ awslocal \
s3api put-bucket-notification-configuration --bucket my-bucket \
--notification-configuration file://s3-notif-config.json
```

We can now push the dummy txt file to the bucket 
```bash
$ awslocal \
s3api put-object --bucket my-bucket \
--key dummyfile.txt --body=dummyfile.txt

{
    "ETag": "\"721855327e5b8c8a11f7eb7631e865fa\"",
    "ServerSideEncryption": "AES256"
}
```

Next we need to run up Cloudwatch Logs to monitor the execution of the Lambda when we push a file to the S3 bucket.
```bash
$ awslocal --region=eu-west-1 logs tail '/aws/lambda/my-lambda'

2024-07-16T07:01:55.323000+00:00 2024/07/16/[$LATEST]150a1101a64aaaa70dc7aaa04054e78c START RequestId: c03bb203-0035-43b2-b899-4352eb333e1f Version: $LATEST
2024-07-16T07:01:55.325000+00:00 2024/07/16/[$LATEST]150a1101a64aaaa70dc7aaa04054e78c 2024-07-16T07:01:55.315Zc03bb203-0035-43b2-b899-4352eb333e1f    INFO    Lambda executed outputting content-type
2024-07-16T07:01:55.328000+00:00 2024/07/16/[$LATEST]150a1101a64aaaa70dc7aaa04054e78c 2024-07-16T07:01:55.315Zc03bb203-0035-43b2-b899-4352eb333e1f    INFO    CONTENT TYPE: binary/octet-stream
2024-07-16T07:01:55.331000+00:00 2024/07/16/[$LATEST]150a1101a64aaaa70dc7aaa04054e78c END RequestId: c03bb203-0035-43b2-b899-4352eb333e1f
2024-07-16T07:01:55.333000+00:00 2024/07/16/[$LATEST]150a1101a64aaaa70dc7aaa04054e78c REPORT RequestId: c03bb203-0035-43b2-b899-4352eb333e1f  Duration: 22.56 ms      Billed Duration: 23 ms  Memory Size: 128 MB     Max Memory Used: 128 MB
```