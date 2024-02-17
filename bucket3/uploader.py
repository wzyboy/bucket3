import mimetypes
from pathlib import Path
from urllib.parse import quote
from email.header import Header

import boto3
from botocore.exceptions import ClientError

from bucket3.hasher import Hasher


class Uploader:

    def __init__(self, domain: str, bucket: str) -> None:
        self.domain = domain
        self.bucket = bucket
        self.s3 = boto3.client('s3')

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise
        else:
            return True
        return False

    def upload_from_fs(self, path: Path, *, prefix: str = '') -> str:
        if prefix and not prefix.endswith('/'):
            raise ValueError('Prefix must have a trailing slash')
        if prefix and prefix.startswith('/'):
            raise ValueError('Prefix must not start with a slash')
        key = Hasher(path).key()
        if prefix:
            key = f'{prefix}{key}'

        if not self.exists(key):
            mtime = str(path.stat().st_mtime)
            content_type = mimetypes.guess_type(path)[0] or 'binary/octet-stream'  # default AWS Content-Type
            self.s3.upload_file(
                str(path), self.bucket, key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ChecksumAlgorithm': 'SHA256',
                    'Metadata': {
                        'mtime': mtime,
                        'filename': Header(path.name).encode(),
                    }
                }
            )

        # Key should already be URL-safe. Invoke quote() to ensure this.
        url = f'https://{self.domain}/{quote(key)}'
        return url

    def get_upload_form_data(self, key: str) -> dict:
        '''Request a presigned POST from AWS. The frontend uses the data to
        build a web form to upload the file directly to AWS.'''
        # https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-UsingHTTPPOST.html

        # The frontend calculates the checksum and derive the key from it. Here
        # we convert the key back to the checksum and attach it to the request
        # so that AWS can verify the integrity of the file.
        checksum = Hasher.from_key(key).checksum()
        fields = {
            'x-amz-checksum-algorithm': 'SHA256',
            'x-amz-checksum-sha256': checksum,
        }

        # Limit what can be done with the generated presigned request.
        # https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
        # These conditions are signed against so they cannot be tempered by the
        # frontend. Boto3 already includes `bucket` and `key` in the conditions,
        # but it won't automatically add custom fields added above.
        conditions = [
            ["starts-with", "$Content-Type", "image/"],
            {'x-amz-checksum-algorithm': 'SHA256'},
            {'x-amz-checksum-sha256': checksum},
        ]

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_post.html
        response = self.s3.generate_presigned_post(
            self.bucket,
            key,
            Fields=fields,
            Conditions=conditions,
        )

        # The response contains the presigned URL and required fields
        return response
