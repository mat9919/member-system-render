from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///members.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")

db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "member_number": self.member_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return """<!doctype html><meta charset="utf-8">
<title>Member System</title>
<h1>Member System (Ultra-lite)</h1>
<form method="post" action="/api/members">
  <input name="member_number" placeholder="Member No." required>
  <input name="first_name"  placeholder="First name">
  <input name="last_name"   placeholder="Last name">
  <input name="phone_number" placeholder="Phone">
  <button type="submit">Add</button>
</form>
<p><a href="/api/members" target="_blank">ดูรายการสมาชิก (JSON)</a></p>
"""

@app.route("/api/members", methods=["GET"])
def list_members():
    return jsonify([m.to_dict() for m in Member.query.order_by(Member.id.desc()).all()])

@app.route("/api/members", methods=["POST"])
def create_member():
    data = request.form or request.json or {}
    mn = data.get("member_number")
    if not mn:
        return jsonify({"error": "member_number required"}), 400
    m = Member(
        member_number=mn,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        phone_number=data.get("phone_number"),
    )
    db.session.add(m)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
