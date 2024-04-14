import boto3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
import os

#Loading Enviornment Variables
load_dotenv()

#Creates a Flask application instance. __name__
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for flash messages

# AWS credentials
try:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Initialize S3 client
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

except Exception as e:
    print(f"Error initializing S3 client: {e}")
    # Handle the exception as per your application's requirements

@app.route('/')
def index():
    try:
        # List all buckets
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return render_template('index.html', buckets=buckets)

    except Exception as e:
        flash(f"Error listing buckets: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    try:
        bucket_name = request.form['bucket_name']
        s3.create_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' created successfully!", 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error creating bucket: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    try:
        bucket_name = request.form['bucket_name']
        s3.delete_bucket(Bucket=bucket_name)
        flash(f"Bucket '{bucket_name}' deleted successfully!", 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error deleting bucket: {e}", 'error')
        return redirect(url_for('index'))

@app.route('/list_objects/<bucket_name>', methods=['GET'])
def list_objects(bucket_name):
    try:
        # List all objects in a bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = [obj['Key'] for obj in response.get('Contents', [])]
        return render_template('objects.html', bucket_name=bucket_name, objects=objects)

    except Exception as e:
        flash(f"Error listing objects: {e}", 'error')
        return redirect(url_for('index'))


@app.route('/create_folder/<bucket_name>', methods=['POST'])
def create_folder(bucket_name):
    try:
        if request.method == 'POST':
            folder_name = request.form['folder_name']
            s3.put_object(Bucket=bucket_name, Key=f"{folder_name}/")
            flash(f"Folder '{folder_name}' created successfully!", 'success')
            return redirect(url_for('list_objects', bucket_name=bucket_name))

    except Exception as e:
        flash(f"Error creating folder: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

@app.route('/delete_folder/<bucket_name>', methods=['POST'])
def delete_folder(bucket_name):
    try:
        folder_name = request.form.get('folder_name')

        if folder_name:
            # Delete all objects inside the folder
            objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder_name}/").get('Contents', [])
            for obj in objects:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

            # Delete the folder itself
            s3.delete_object(Bucket=bucket_name, Key=f"{folder_name}/")

            flash(f"Folder '{folder_name}' deleted successfully!", 'success')
        else:
            flash("Please select a folder to delete.", 'error')

        return redirect(url_for('list_objects', bucket_name=bucket_name))
    except Exception as e:
        flash(f"Error deleting folder: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

# ... (previous code remains unchanged)

@app.route('/upload_file/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
    try:
        file = request.files['file']

        # Check if a file is selected
        if not file:
            flash("Please select a file to upload.", 'error')
            return redirect(url_for('list_objects', bucket_name=bucket_name))

        file_name = file.filename
        s3.upload_fileobj(file, bucket_name, file_name)
        flash(f"File '{file_name}' uploaded successfully!", 'success')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

    except Exception as e:
        flash(f"Error uploading file: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

# ... (rest of the code remains unchanged)

@app.route('/delete_file/<bucket_name>/<file_name>')
def delete_file(bucket_name, file_name):
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        flash(f"File '{file_name}' deleted successfully!", 'success')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

    except Exception as e:
        flash(f"Error deleting file: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

@app.route('/copy_file/<bucket_name>/<source>/<destination>')
def copy_file(bucket_name, source, destination):
    try:
        s3.copy_object(Bucket=bucket_name, CopySource=f"{bucket_name}/{source}", Key=destination)
        flash(f"File '{source}' copied to '{destination}' successfully!", 'success')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

    except Exception as e:
        flash(f"Error copying file: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

@app.route('/move_file/<bucket_name>/<source>/<destination>')
def move_file(bucket_name, source, destination):
    try:
        s3.copy_object(Bucket=bucket_name, CopySource=f"{bucket_name}/{source}", Key=destination)
        s3.delete_object(Bucket=bucket_name, Key=source)
        flash(f"File '{source}' moved to '{destination}' successfully!", 'success')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

    except Exception as e:
        flash(f"Error moving file: {e}", 'error')
        return redirect(url_for('list_objects', bucket_name=bucket_name))

if __name__ == '__main__':
    app.run(debug=True)
