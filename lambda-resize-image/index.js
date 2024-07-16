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