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
