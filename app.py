from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import date
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret_key_123"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM teachers WHERE username=? AND password=?",
                (username, password)
            ).fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    with get_db() as db:

        # Total students
        students = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]

        # Present students (today)
        today = str(date.today())
        present = db.execute(
            "SELECT COUNT(*) FROM attendance WHERE status='Present' AND date=?",
            (today,)
        ).fetchone()[0]

        # Absent students
        absent = students - present

    return render_template(
        "dashboard.html",
        students=students,
        present=present,
        absent=absent
    )


# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if "user" not in session:
        return redirect("/")

    with get_db() as db:

        if request.method == "POST":
            name = request.form.get("name")
            roll = request.form.get("roll")
            phone = request.form.get("phone")

            if name and roll and phone:
                db.execute(
                    "INSERT INTO students(name, roll, phone) VALUES (?, ?, ?)",
                    (name, roll, phone)
                )
                db.commit()

        students = db.execute("SELECT * FROM students").fetchall()

    return render_template("add_student.html", students=students)


# ---------------- ATTENDANCE ----------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "user" not in session:
        return redirect("/")

    with get_db() as db:

        students = db.execute("SELECT * FROM students").fetchall()

        if request.method == "POST":

            today = str(date.today())

            for s in students:
                status = request.form.get(str(s["id"]))

                if status:
                    db.execute(
                        "INSERT INTO attendance(student_id, status, date) VALUES (?, ?, ?)",
                        (s["id"], status, today)
                    )

            db.commit()

            return redirect("/records")

    return render_template("attendance.html", students=students)


# ---------------- MANAGE STUDENTS ----------------
@app.route("/manage_students")
def manage_students():

    if "user" not in session:
        return redirect("/")

    with get_db() as db:
        students = db.execute("SELECT * FROM students").fetchall()

    return render_template("manage_students.html", students=students)


# ---------------- RECORDS ----------------
@app.route("/records")
def records():

    if "user" not in session:
        return redirect("/")

    selected_date = request.args.get("date")

    with get_db() as db:

        if selected_date:
            records = db.execute("""
                SELECT students.name, attendance.status, attendance.date
                FROM attendance
                JOIN students ON students.id = attendance.student_id
                WHERE attendance.date=?
                ORDER BY attendance.date DESC
            """, (selected_date,)).fetchall()

        else:
            records = db.execute("""
                SELECT students.name, attendance.status, attendance.date
                FROM attendance
                JOIN students ON students.id = attendance.student_id
                ORDER BY attendance.date DESC
            """).fetchall()

    return render_template("records.html", records=records)


# ---------------- EXPORT EXCEL ----------------
@app.route("/export")
def export():

    if "user" not in session:
        return redirect("/")

    with get_db() as db:
        data = db.execute("""
            SELECT students.name, attendance.status, attendance.date
            FROM attendance
            JOIN students ON students.id = attendance.student_id
        """).fetchall()

    df = pd.DataFrame([dict(row) for row in data])

    file = "attendance.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)


# ---------------- ADMIN PANEL ----------------
@app.route("/control-panel-987")
def admin():

    if "user" not in session:
        return redirect("/")

    if session["user"] != "admin":
        return "Unauthorized Access"

    with get_db() as db:
        students = db.execute("SELECT * FROM students").fetchall()

    return render_template("admin.html", students=students)


# ---------------- DELETE STUDENT ----------------
@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "user" not in session:
        return redirect("/")

    with get_db() as db:
        db.execute("DELETE FROM attendance WHERE student_id=?", (id,))
        db.execute("DELETE FROM students WHERE id=?", (id,))
        db.commit()

    return redirect("/manage_students")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
