from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'vyuvbyubugYUVKFVKUFV7678vk'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(120))
    dob = db.Column(db.Date)
    subject = db.Column(db.String(120))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    mot = db.Column(db.String(120)) #Mode of teaching

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    rating = db.Column(db.Float)
    points = db.Column(db.Integer)
    subject = db.Column(db.String(120))
    mot = db.Column(db.String(120))

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'))
    subjects = db.Column(db.String(120))
    medium = db.Column(db.String(120))
    date_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    student = db.relationship('Student', backref='sessions')
    tutor = db.relationship('Tutor', backref='sessions')

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        print("post HIII")

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if role == "tutor":
            row = Tutor.query.filter_by(username=username).first()
        elif role == "student":
            row = Student.query.filter_by(username=username).first()

        if row and sha256_crypt.verify(password, row.password):
            session['username'] = username
            session['role'] = role

            if role=="tutor":
                return redirect("/home_tut")
            elif role=="student":
                return redirect("/home_stud")
        else:
            return render_template('login.html')
            
    else:
        return render_template('login.html')

@app.route('/reg_stud', methods=['GET', 'POST'])
def reg_stud():

    if request.method == 'POST':
        print("stud POST")

        name = request.form['name']
        username = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dob = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        mot = request.form.getlist('mot')[0]
        password = request.form['password']
        confirm_password = request.form['check']

        if password!=confirm_password:
            return render_template('reg_stud.html')

        hashed_password = sha256_crypt.hash(password)

        stu1 = Student(name=name, username=username, password=hashed_password, phone=phone,\
                       address=address, dob=dob, mot=mot)
        db.session.add(stu1)
        db.session.commit()

        print("commited")
        
        session['username'] = username
        session['role'] = 'student'

        return redirect('/home_stud')
    
    else:
        return render_template('reg_stud.html')

@app.route('/reg_tut', methods=['GET', 'POST'])
def reg_tut():

    if request.method == 'POST':
        name = request.form['name']
        username = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['date']
        mot = request.form.getlist('mot')
        password = request.form['password']
        confirm_password = request.form['check']

        if password!=confirm_password: 
            return render_template('reg_tut.html')

        hashed_password = sha256_crypt.hash(password)

        stu1 = Tutor(name=name, username=username, password=hashed_password, phone=phone,\
                       address=address, dob=dob, mot=mot)
        db.session.add(stu1)
        db.session.commit()
        
        session['username'] = username
        session['role'] = 'tutor'
        return redirect('/home_tut')
    
    else:
        return render_template('reg_tut.html')

@app.route("/home_stud", methods=['GET', 'POST'])
def home_stud():
    if request.method=="POST":
        pass
    else:
        return render_template("home_stud.html")

@app.route("/home_tut", methods=['GET', 'POST'])
def home_tut():
    if request.method=="POST":
        pass
    else:
        return render_template("home_tut.html")

@app.route("/stud_vc", methods=['GET', 'POST'])
def studvc():
    if request.method == 'POST':
        subject = request.form['Subject']
        date = request.form['date']
        time = request.form['time']
        Student.query.filter_by(username=session['username']).update(subject=subject, date=date, time=time)
        return redirect('/home_stud')
    else:
        return render_template('stud_vc.html')

@app.route("/tut_vc", methods=['GET', 'POST'])
def tutvc():
    if request.method == 'POST':
        row = Tutor.query.filter_by(username=session['username']).first()
        subject = row.subject
        mot = row.mot
        rows = Student.query.filter_by(subject=subject, mot=mot).all()
    else:
        return render_template('tut_vc.html', rows=rows)
    
@app.route("/feedback", methods=['GET', 'POST'])
def feedme():
    if request.method == 'POST':
        und = request.form['und']
        app = request.form['app']
        cle = request.form['cle']
        eng = request.form['eng']
        kno = request.form['kno']
        name = request.form['name']
        avg = (int(und)+int(app)+int(cle)+int(eng)+int(kno))/5

        #code for rating and points.
        #Tutor.query.filter_by(username=name).update(score=score+avg)
    else:
        return render_template('feedback.html')


if __name__ == '__main__':
    app.run()