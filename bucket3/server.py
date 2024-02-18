#!/usr/bin/env python

from flask import Flask
from flask import abort
from flask import request
from flask import render_template

from bucket3.uploader import Uploader


app = Flask('bucket3')
app.config.from_prefixed_env('BUCKET3')
uploader = Uploader(app.config['DOMAIN'], app.config['BUCKET'])


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/get_upload_form_data')
def get_upload_form_data():
    if key := request.args.get('key'):
        return uploader.get_upload_form_data(key)
    else:
        abort(400)


def runserver(port: int = 5333):
    app.run(port=port)


if __name__ == '__main__':
    runserver()
