from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "my_secret_key"

# ใช้ SQLite (Render จะสร้างไฟล์ในโฟลเดอร์โปรเจกต์)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///members.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ตารางสมาชิก
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# หน้าแรก
@app.route("/")
def home():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    return redirect(url_for("login"))

# สมัครสมาชิก
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            return "ชื่อผู้ใช้นี้มีอยู่แล้ว"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

# เข้าสู่ระบบ
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            return redirect(url_for("home"))
        return "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
    return render_template("login.html")

# ออกจากระบบ
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    if not os.path.exists("members.db"):
        with app.app_context():
            db.create_all()
    app.run(host="0.0.0.0", port=5000)
