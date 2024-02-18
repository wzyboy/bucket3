# bucket3

**bucket3** is a basic image hosting service that allows [browser-based uploads to Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-UsingHTTPPOST.html).

The filename is derived from the SHA-256 digest of the file and is guaranteed to be unique. New uploads will never overwrite previously uploaded files.

The service is dead-simple with no database and no built-in authentication. It is not recommended to run the service to the general public without any authentication layer.

![screenshot](screenshot.png)

## Prerequisites

- Create an S3 bucket `example-bucket`.
- Put a domain `example.org` in front of the bucket (e.g. with CloudFront) so that `https://example.org/foo.png` returns `foo.png` in the bucket.

## Setup

```bash
# Install the package
pipx install git+https://github.com/wzyboy/bucket3

# Edit the configuration file
cp server.example.cfg server.cfg
vim server.cfg

# Start the web server (localhost:5333)
s3u-web
```

## Special Thanks

90% of the frontend code is written by ChatGPT.
