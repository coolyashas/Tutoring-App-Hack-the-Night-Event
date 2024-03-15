from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'vyuvbyubugYUVKFVKUFV7678vk'
db = SQLAlchemy(app)
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='your_google_client_id',
    consumer_secret='your_google_client_secret',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

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


@app.route('/google_login')
def google_login():
    return google.authorize(callback=url_for('google_authorized', _external=True))

@app.route('/google_authorized')
def google_authorized():
    resp = google.authorized_response()

    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (resp['access_token'], '')

    user_info = google.get('userinfo')
    email = user_info.data['email']

    # Check if user with this email exists in your database
    user = Main.query.filter_by(username=email).first()
    if user:
        session['username'] = email
        session['role'] = user.role
        return redirect(url_for('details'))

    # If user does not exist, you can redirect to a registration page
    # or automatically create a new user with default credentials

    return redirect(url_for('register'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run()
