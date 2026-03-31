from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# DATABASE MODELS
# --------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():
    return render_template("index.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", tasks=tasks)

# ADD TASK
@app.route("/add-task", methods=["POST"])
def add_task():
    title = request.form["title"]

    new_task = Task(title=title, user_id=session["user_id"])
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for("dashboard"))

# COMPLETE TASK
@app.route("/complete-task/<int:id>")
def complete_task(id):
    task = Task.query.get(id)
    task.completed = True
    db.session.commit()
    return redirect(url_for("dashboard"))

# DELETE TASK
@app.route("/delete-task/<int:id>")
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard"))

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# --------------------
import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))