import os
from flask import Flask, render_template, url_for, flash, redirect, request
import git
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy

# Optional toolbar import only for development
if os.environ.get("FLASK_ENV") == "development":
    from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '7c9b91ed34545cd307fadd60f26be6ff'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

with app.app_context():
    db.create_all()


# Only enable DebugToolbar in development
if os.environ.get("FLASK_ENV") == "development":
    app.debug = True
    toolbar = DebugToolbarExtension(app)
else:
    app.debug = False  # production mode

@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/Knowmebetter/KnowMe-website')  # 👈 UPDATE to your real path
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', subtitle='Home', text='This is the home page')

@app.route("/second_page")
def second_page():
    return render_template('second_page.html', subtitle='Introduction', text='This is the second page')

@app.route("/third_page")
def third_page():
    return render_template('third_page.html', subtitle='About me', text='This is my page')

@app.route("/success")
def success_page():
    return render_template("success.html", subtitle="Registration Complete", show_navbar=False)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data  # ⚠️ We'll hash this later
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('success_page'))
    return render_template('register.html', title='Register', form=form, show_navbar=False)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")