from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import boto3
import os

load_dotenv()

app = Flask(__name__)

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_REGION = 'ap-south-1'

# Initialize S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


@app.route('/')
def index():
    # List all buckets
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return render_template('index.html', buckets=buckets)


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    s3.create_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))


@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form['bucket_name']
    s3.delete_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))


@app.route('/list_objects/<bucket_name>')
def list_objects(bucket_name):
    # List all objects in a bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    objects = [obj['Key'] for obj in response.get('Contents', [])]
    return render_template('objects.html', bucket_name=bucket_name, objects=objects)


@app.route('/upload_file/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
    file = request.files['file']
    file_name = file.filename
    s3.upload_fileobj(file, bucket_name, file_name)
    return redirect(url_for('list_objects', bucket_name=bucket_name))


@app.route('/delete_file/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
    s3.delete_object(Bucket=bucket_name, Key=file_name)
    return redirect(url_for('list_objects', bucket_name=bucket_name))


@app.route('/copy_file/<bucket_name>/<source>/<destination>')
def copy_file(bucket_name, source, destination):
    s3.copy_object(Bucket=bucket_name, CopySource=f"{bucket_name}/{source}", Key=destination)
    return redirect(url_for('list_objects', bucket_name=bucket_name))


@app.route('/move_file/<bucket_name>/<source>/<destination>')
def move_file(bucket_name, source, destination):
    s3.copy_object(Bucket=bucket_name, CopySource=f"{bucket_name}/{source}", Key=destination)
    s3.delete_object(Bucket=bucket_name, Key=source)
    return redirect(url_for('list_objects', bucket_name=bucket_name))


if __name__ == '__main__':
    app.run(debug=True)
