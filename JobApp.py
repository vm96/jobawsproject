from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'job'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddJob.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addjob", methods=['POST'])
def AddJob():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    position = request.form['position']
    pri_skill = request.form['pri_skill']
    last_companyname = request.form['last_companyname']
    salary = request.form['salary']
    years_of_exp = request.form['years_of_exp']
    dateofjoin = request.form['dateofjoin']
    gender = request.form['gender']
    marital_status = request.form['marital_status']
    Resume_file = request.files['Resume_file']

    insert_sql = "INSERT INTO job VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if Resume_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (first_name, last_name, address, phone, email, position, pri_skill, last_companyname, salary, years_of_exp, dateofjoin, gender, maritalstatus))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        Resume_file_in_s3 = "first_name-" + str(first_name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=Resume_file_in_s3, Body=Resume_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                Resume_file_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddJobOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
