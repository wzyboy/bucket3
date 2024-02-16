import argparse
from pathlib import Path

from bucket3.uploader import Uploader


def cli():

    ap = argparse.ArgumentParser()
    ap.add_argument('file_path', type=Path)
    ap.add_argument('--domain', required=True)
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--prefix', default='')
    ap.add_argument('--tmp', action='store_true', help='shorthand of --prefix tmp/')
    args = ap.parse_args()

    if args.tmp:
        prefix = 'tmp/'
    else:
        prefix = args.prefix

    uploader = Uploader(args.domain, args.bucket)
    url = uploader.upload_from_fs(args.file_path, prefix=prefix)

    print(url)


if __name__ == '__main__':
    cli()
