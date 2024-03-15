from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'vyuvbyubugYUVKFVKUFV7678vk'
db = SQLAlchemy(app)

class Main(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    ph = db.Column(db.Float)
    hardness = db.Column(db.Float)
    cost = db.Column(db.Integer)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        row = Main.query.filter_by(username=username).first()

        if row and sha256_crypt.verify(password, row.password):
            session['username'] = username

            return redirect("/home_stud")
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
    
@app.route('/details')
def details():
    if 'username' in session:
        # Fetch all rows from the Main table
        all_rows = Main.query.all()
        return render_template('details.html', rows=all_rows)
    else:
        return redirect(url_for('login'))