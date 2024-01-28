from flask import Flask, render_template, request, flash, redirect, url_for, json
import secrets
import pymysql.cursors
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Connect to MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='company',
    cursorclass=pymysql.cursors.DictCursor
)

jobs = ["Job1", "Job2", "Job3"]
students = []  # Initialize as an empty list to fetch from the database
interviews = []
job_postings = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post_job', methods=['POST', 'GET'])
def post_job():
    if request.method == 'POST':
        job_role = request.form['job_role']
        job_type = request.form['job_type']
        skills_required = request.form['skills_required']
        num_employees = request.form['num_employees']
        num_openings = request.form['num_openings']
        company_description = request.form['company_description']
        responsibilities = request.form['responsibilities']

        try:
            with connection.cursor() as cursor:
                # SQL query to insert data into the job_postings table
                sql = "INSERT INTO job_postings (job_role, job_type, skills_required, num_employees, num_openings, company_description, responsibilities) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (job_role, job_type, skills_required, num_employees, num_openings, company_description, responsibilities))
                connection.commit()

                # Notify all students about the new job posting
                notify_students_about_job_posting(job_role)

                flash('Job posting added successfully', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')

        return redirect(url_for('job_listings'))

    return render_template('post_job.html')

# Function to send notifications to all students about the new job posting
def notify_students_about_job_posting(job_role):
    try:
        with connection.cursor() as cursor:
            # Fetch all student emails from the database
            sql = "SELECT email FROM students"
            cursor.execute(sql)
            student_emails = [student['email'] for student in cursor.fetchall()]

        # Send email notifications to students
        subject = 'New Job Opening'
        body = f'There is a new job opening for the position of {job_role}. Check your dashboard for more details.'
        send_email(subject, body, student_emails)
    except Exception as e:
        flash(f'Error notifying students: {e}', 'danger')

# Function to send email
def send_email(subject, body, recipients):
    try:
        # SMTP Configuration (Update with your SMTP server details)
        smtp_server = 'smtp.gmail.com'  # Assuming you are using Gmail
        smtp_port = 587
        smtp_username = 'Projectdemo65@gmail.com'  # Your Gmail username
        smtp_password = 'nbknetqtvnrgwnjv'  # Your Gmail password

        # Create the email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'Projectdemo65@gmail.com'  # Replace with your sender email address
        msg['To'] = ', '.join(recipients)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(msg['From'], recipients, msg.as_string())

    except Exception as e:
        flash(f'Error sending email: {e}', 'danger')

@app.route('/view_students')
def view_students():
    # Fetch all records of students from the database
    try:
        with connection.cursor() as cursor:
            # Replace this query with your actual query to fetch all students
            sql = "SELECT id, name , email FROM students"
            cursor.execute(sql)
            fetched_students = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching students: {e}', 'danger')
        fetched_students = []

    return render_template('view_students.html', students=fetched_students)

@app.route('/placement_analytics')
def placement_analytics():
    data = {
        "year_wise_companies_visited": {
            2017: 0.7,
            2016: 0.7,
            2015: 0.7,
            2014: 0.55,
        },
        "top_packages_last_5_years": {
            "correct_answers": [100, 100, 100, 100, 100],
            "incorrect_answers": [2, 2, 2, 2, 2],
            "unattempted_questions": [30, 30, 30, 30, 30],
        },
        "top_recruiter": {
            "2015": "C",
            "2014": {"Mar": 20, "Apr": 15},
        },
        "year_wise_placements": {
            "2017": "Outcome 10",
            "2016": "Outcome 10",
            "2015": "Outcome 10",
            "2014": "Outcome 10",
        }
    }
    return render_template('placement_analytics.html', data=data, json_data=json.dumps(data))

@app.route('/schedule_interview', methods=['GET', 'POST'])
def schedule_interview():
    # Fetch the list of students from the database
    try:
        with connection.cursor() as cursor:
            # Replace this query with your actual query to fetch students
            sql = "SELECT id, name FROM students"
            cursor.execute(sql)
            fetched_students = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching students: {e}', 'danger')
        fetched_students = []

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']

        selected_student = next((student for student in fetched_students if student['id'] == student_id), None)

        if selected_student:
            interview_details = {
                'student_name': selected_student['name'],
                'date': date,
                'time': time,
                'location': location
            }

            interviews.append(interview_details)

            try:
                with connection.cursor() as cursor:
                    # SQL query to insert data into the interviews table
                    sql = "INSERT INTO interviews (student_id, date, time, location) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (student_id, date, time, location))
                    connection.commit()
                    flash('Interview scheduled successfully', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'danger')

        else:
            flash('Selected student not found', 'danger')

    return render_template('schedule_interview.html', students=fetched_students, interviews=interviews)

# Check if you have an endpoint like this in your Flask app



@app.route('/admin_all_records')
def admin_all_records():
    # Fetch all records of students, interviews, and job postings from the database
    try:
        with connection.cursor() as cursor:
            # Fetch students
            sql_students = "SELECT id, name, email FROM students"
            cursor.execute(sql_students)
            fetched_students = cursor.fetchall()

            # Fetch interviews
            sql_interviews = "SELECT id, student_id, date, time, location FROM interviews"
            cursor.execute(sql_interviews)
            fetched_interviews = cursor.fetchall()

            # Fetch job postings
            sql_job_postings = "SELECT id, job_role, job_type, skills_required, num_employees, num_openings, company_description, responsibilities FROM job_postings"
            cursor.execute(sql_job_postings)
            fetched_job_postings = cursor.fetchall()

    except Exception as e:
        flash(f'Error fetching records: {e}', 'danger')
        fetched_students = []
        fetched_interviews = []
        fetched_job_postings = []

    return render_template('all_records.html', students=fetched_students, interviews=fetched_interviews, job_postings=fetched_job_postings)
@app.route('/job_listings')
def job_listings():
    # Fetch all job postings from the database
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, job_role, job_type, skills_required, num_employees, num_openings, company_description, responsibilities FROM job_postings"
            cursor.execute(sql)
            job_postings = cursor.fetchall()
    except Exception as e:
        flash(f'Error fetching job postings: {e}', 'danger')
        job_postings = []

    return render_template('job_listings.html', job_postings=job_postings)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
