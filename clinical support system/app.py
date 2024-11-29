from flask import Flask, render_template, request, redirect, url_for, session,flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'hospital_management'
}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change to your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'clinicss24@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'pzakrsxeouffzrsf'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'clinicss24@gmail.com'  # Default sender

def get_db_connection():
    return mysql.connector.connect(**db_config)
mail = Mail(app)


#-------------------------------------------------------------------------------
@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html')
        # return redirect(url_for('index'))
        # return f"Hello, {session['username']}! Welcome to the index page."
    else:
        return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, password FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            #return redirect(url_for('index'))
            # return render_template('index.html')
            error = 'Invalid username or password'
            flash('Invalid username or password', 'error')
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            error = "Passwords do not match"
            return render_template('signup.html', error=error)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user:
            error = "Username already exists"
            return render_template('signup.html', error=error)

        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                       (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

# @app.route('/manage_patients')
# def manage_patients():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patients/manage_patients.html', patients=patients)

@app.route('/manage_patients')
def manage_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch patients and check if each has any associated appointments
    cursor.execute("""
        SELECT p.*, EXISTS(
            SELECT 1 FROM appointments a WHERE a.patient_id = p.id
        ) AS has_appointment
        FROM patients p
    """)
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patients/manage_patients.html', patients=patients)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        contact = request.form['contact']
        mail = request.form['mail']


        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, gender, contact, mail) VALUES (%s, %s, %s, %s, %s)", (name, age, gender, contact, mail))
        conn.commit()
        cursor.close()
        return redirect(url_for('manage_patients'))

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        gender = request.form['gender']
        contact = request.form['contact']
        mail = request.form['mail']

        cursor.execute("""
            UPDATE patients
            SET name = %s, age = %s, gender = %s, contact = %s,mail = %s
            WHERE id = %s""", (name, age, gender, contact,mail, id))
        conn.commit()
        cursor.close()
        return redirect(url_for('manage_patients'))

    else:
        cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
        patient = cursor.fetchone()
        cursor.close()
        return render_template('patients/edit_patient.html', patient=patient)

@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_patients'))


# @app.route('/manage_doctors')
# def manage_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM doctors')
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctors/manage_doctors.html', doctors=doctors)

@app.route('/manage_doctors')
def manage_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch doctors and check if each has any associated appointments
    cursor.execute("""
        SELECT d.*, EXISTS(
            SELECT 1 FROM appointments a WHERE a.doctor_id = d.id
        ) AS has_appointment
        FROM doctors d
    """)
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctors/manage_doctors.html', doctors=doctors)


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    name = request.form['name']
    specialty = request.form['specialty']
    contact = request.form['contact']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO doctors (name, specialty, contact) VALUES (%s, %s, %s)", (name, specialty, contact))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_doctors'))

@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
def edit_doctor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        specialty = request.form['specialty']
        contact = request.form['contact']
        cursor.execute("UPDATE doctors SET name=%s, specialty=%s, contact=%s WHERE id=%s", (name, specialty, contact, id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_doctors'))
    else:
        cursor.execute("SELECT * FROM doctors WHERE id=%s", (id,))
        doctor = cursor.fetchone()
        conn.close()
        return render_template('doctors/edit_doctor.html', doctor=doctor)

@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_doctors'))


@app.route('/manage_appointments')
def manage_appointments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT a.id, p.name AS patient_name, d.name AS doctor_name, a.date, a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    ''')
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('appointment/manage_appointments.html', appointments=appointments)

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']  # Get the appointment date
        time = request.form['time']  # Get the appointment time

        appointment_date = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')


        conn = get_db_connection()
        cursor=conn.cursor()
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, date, time,appointment_date) VALUES (%s, %s, %s, %s,%s)",
                    (patient_id, doctor_id, date, time,appointment_date))
        conn.commit()
        cursor.execute("SELECT mail FROM patients WHERE id = %s", (patient_id,))
        patient_mail = cursor.fetchone()

        # If the patient's email exists, send the appointment email
        if patient_mail:
            send_email_to_patient(patient_mail[0], appointment_date)
        cursor.close()
        return redirect(url_for('manage_appointments'))


# Edit Appointment Route
@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        cursor=conn.cursor()
        cursor.execute("""
            UPDATE appointments
            SET patient_id = %s, doctor_id = %s, date = %s, time = %s
            WHERE id = %s
        """, (patient_id, doctor_id, date,time, id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_appointments'))
    else:
        cursor.execute("SELECT * FROM appointments WHERE id=%s", (id,))
        appointment = cursor.fetchone()
        conn.close()
        return render_template('appointment/edit_appointment.html', appointment=appointment)

# Delete Appointment Route
@app.route('/delete_appointment/<int:id>',)
def delete_appointment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_appointments'))

@app.route('/send_appointment_email/<int:appointment_id>', methods=['POST'])
def send_appointment_email(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the appointment details
    cursor.execute("""
        SELECT a.appointment_date, p.mail
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = %s
    """, (appointment_id,))
    appointment_data = cursor.fetchone()

    if appointment_data:
        appointment_datetime, patient_email = appointment_data
        send_email_to_patient(patient_email, appointment_datetime)
        flash("Appointment email sent successfully!")
    else:
        flash("Appointment not found or email could not be sent!")

    cursor.close()
    conn.close()

    return redirect(url_for('manage_appointments'))

def send_email_to_patient(patient_email, appointment_date):
    msg = Message("Appointment Confirmation", recipients=[patient_email])

    # Format the appointment date to a readable format
    formatted_appointment_date = appointment_date.strftime('%Y-%m-%d %H:%M')  # Include time if necessary

    # Email body content
    msg.body =f"""
    Dear Patient,

    Your appointment has been scheduled as follows:

    Appointment Date and Time: {formatted_appointment_date}

    Thank you for choosing our hospital.

    Best regards,
    The Hospital Team
    """

    try:
        # Send the email using Flask-Mail
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/about_us',)
def about_us():
    return render_template('/about_us.html')


if __name__ == '__main__':
    app.run(debug=True)
