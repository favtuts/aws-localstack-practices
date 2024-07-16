# LocalStack – Mock AWS in local development
* https://tuts.heomi.net/localstack-mock-aws-in-local-development

# Installation & Setup

Create a `docker-compose.yml` file and paste the following contents.
```yaml
    version: "3.8"

    services:
      localstack:
        image: localstack/localstack
        ports:
          - "127.0.0.1:4566:4566"
          - "127.0.0.1:4510-4559:4510-4559"
        environment:
          - DEBUG=${DEBUG-}
          - DOCKER_HOST=unix:///var/run/docker.sock
        volumes:
          - "${LOCALSTACK_VOLUME_DIR:-./volume}:/var/lib/localstack"
          - "/var/run/docker.sock:/var/run/docker.sock"
```

Start the container by running:
```bash
docker compose up
```
LocalStack should be started at `http://localhost:4566`. To check it’s running properly, check the health by visiting `https://localhost:4566/health`.
```
$ curl --silent https://localhost.localstack.cloud:4566/_localstack/health | jq
```


# Install AWS CLI

AWS CLI will communicate with LocalStack by using specific endpoint `--endpoint-url=http://localhost:4566`. Example:

```bash
$ aws s3api list-buckets --endpoint-url=http://localhost:4566
{
    "Buckets": [],
    "Owner": {
        "DisplayName": "webfile",
        "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
    }
}
```

AWS SDK communicate with LocalStack using JavaScript `aws-sdk` package:
```js
const AWS = require('aws-sdk');

const s3 = new AWS.S3({
  endpoint: 'http://localhost:4566', // Only needed for localstack
  s3ForcePathStyle: true, // Only needed for localstack
});
```

# Create the Lambda function

Create a new file `package.json` and paste the following code:
```json
{
  "main": "index.js",
  "dependencies": {
    "aws-sdk": "^2.1376.0",
    "sharp": "^0.32.1"
  }
}
```

Then run `npm install` to install the dependencies.
```bash
$ npm install
```

Create a new file `index.js` and paste the following code:
```js
onst AWS = require('aws-sdk');
const sharp = require('sharp');

const WIDTH = 64;

const s3 = new AWS.S3({
  endpoint: `http://${process.env.LOCALSTACK_HOSTNAME}:${process.env.EDGE_PORT}`, // Only needed for localstack
  s3ForcePathStyle: true, // Only needed for localstack
});

exports.handler = async (event) => {
  try {
    const srcBucket = event.Records[0].s3.bucket.name;
    const srcKey = decodeURIComponent(
      event.Records[0].s3.object.key.replace(/\+/g, ' ')
    );

    if (srcKey.includes(`${WIDTH}x${WIDTH}`)) {
      console.info('Skipping processed image.');
      return;
    }

    const destinationKey = srcKey.replace(
      /(\.[^.]*)?$/,
      `-${WIDTH}x${WIDTH}$1`
    ); // output will be name-200x200.png

    const typeMatch = srcKey.match(/\.([^.]*)$/);
    if (!typeMatch) {
      console.error('Could not determine the image type.');
      return;
    }

    const imageType = typeMatch[1].toLowerCase();
    if (imageType != 'jpg' && imageType != 'png' && imageType != 'jpeg') {
      console.error(`Unsupported image type: ${imageType}`);
      return;
    }

    const params = {
      Bucket: srcBucket,
      Key: srcKey,
    };

    const originalImage = await s3.getObject(params).promise();

    const buffer = await sharp(originalImage.Body).resize(WIDTH).toBuffer();

    const destinationParams = {
      Bucket: srcBucket,
      Key: destinationKey,
      Body: buffer,
      ContentType: 'image',
    };

    await s3.putObject(destinationParams).promise();

    console.log('Successfully resized ' + srcBucket + '/' + srcKey +
        ' and uploaded to ' + srcBucket + '/' + destinationKey
    );
  } catch (error) {
    console.error(error);
    return;
  }
};
```

Then zip the directory
```bash
$ zip -r function.zip .
```

Create the Lambda function by running:
```bash
$ aws --endpoint-url=http://localhost:4566 \
lambda create-function --function-name CreateThumbnail \
--zip-file fileb://function.zip --handler index.handler --runtime nodejs16.x \
--role arn:aws:iam::000000000000:role/lambda-s3-role


{
    "FunctionName": "CreateThumbnail",
    "FunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:CreateThumbnail",
    "Runtime": "nodejs16.x",
    "Role": "arn:aws:iam::000000000000:role/lambda-s3-role",
    "Handler": "index.handler",
    "CodeSize": 22479332,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2024-07-16T08:04:54.188742+0000",
    "CodeSha256": "Hl+nt2EcORc5tSUNIeNgpCn4GdlbWqf2jQfxMW2YQiQ=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "79665e0f-32b5-439b-bc7d-f8980d047922",
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
        "RuntimeVersionArn": "arn:aws:lambda:us-east-1::runtime:8eeff65f6809a3ce81507fe733fe09b835899b99481ba22fd75b5a7338290ec1"
    },
    "LoggingConfig": {
        "LogFormat": "Text",
        "LogGroup": "/aws/lambda/CreateThumbnail"
    }
}
```


Create a S3 bucket:
```bash
$ aws --endpoint-url=http://localhost:4566 s3 mb s3://avatar-bucket
make_bucket: avatar-bucket
```

Create a file `notification-configuration.json`:
```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:CreateThumbnail",
      "Events": ["s3:ObjectCreated:*"]
    }
  ]
}
```

Configure Amazon S3 to publish events:
```bash
$ aws --endpoint-url=http://localhost:4566 \
s3api put-bucket-notification-configuration --bucket avatar-bucket \
--notification-configuration file://notification-configuration.json
```

Copy an image to the directory and upload the image to the S3 bucket:
```bash
$ aws --endpoint-url=http://localhost:4566 \
s3api put-object --bucket avatar-bucket \
--key test-image.png --body=test-image.png

{
    "ETag": "\"e9f292d6cd3b22dfc539125798a5ab63\"",
    "ServerSideEncryption": "AES256"
}
```

Check the log:
```bash
$ aws --endpoint-url=http://localhost:4566 logs tail '/aws/lambda/CreateThumbnail' --follow
```