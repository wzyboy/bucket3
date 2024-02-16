import base64
import hashlib
from pathlib import Path


class Hasher:
    '''Hash a local file and converts between checksum and S3 key'''

    def __init__(self, file_path, digest=None) -> None:
        self.file_path = Path(file_path)
        if digest:
            self.digest = digest
        else:
            with open(file_path, 'rb') as f:
                hash_obj = hashlib.sha256()
                while chunk := f.read(1024 * 1024 * 10):  # 10 MiB
                    hash_obj.update(chunk)
                self.digest = hash_obj.digest()

    def __str__(self) -> str:
        return self.key()

    def key(self) -> str:
        '''URL-safe Base64-encoded hash digest less padding plus suffix'''
        stem = base64.urlsafe_b64encode(self.digest).decode('ascii').rstrip('=')
        key = self.file_path.with_stem(stem).name
        return key

    def checksum(self) -> str:
        '''Base64-encoded hash digest'''
        return base64.b64encode(self.digest).decode('ascii')

    @classmethod
    def from_checksum(cls, checksum: str, fn: str):
        digest = base64.b64decode(checksum.encode('ascii'))
        return cls(fn, digest)

    @classmethod
    def from_key(cls, key: str):
        path = Path(key)
        # Pad the string to a multiple of 4 for Base64
        len_str = len(path.stem)
        if len_str % 4 == 0:
            len_pad = len_str
        else:
            len_pad = ((len_str // 4) + 1) * 4
        encoded = path.stem.ljust(len_pad, '=').encode('ascii')
        digest = base64.urlsafe_b64decode(encoded)

        return cls(path.name, digest)
