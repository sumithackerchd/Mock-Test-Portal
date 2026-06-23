import sqlite3
import smtplib
import random

from email.mime.text import MIMEText

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_from_directory
)
app = Flask(__name__)

app.secret_key = "mocktest_secret"
EMAIL_ADDRESS = "sumitgiri.chandausi@gmail.com"
EMAIL_PASSWORD = "zvzzwpbkbwesrgrc"

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.secret_key = "mocktest_secret"


# ==========================
# HOME
# ==========================

@app.route("/")
def home():
    return render_template("index.html")

#password reset route

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        conn = sqlite3.connect("mocktest.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if not user:
            return "Email Not Registered"

        otp = random.randint(100000, 999999)

        session["reset_otp"] = str(otp)
        session["reset_email"] = email

        msg = MIMEText(
            f"Your ExamMaster Password Reset OTP is: {otp}"
        )

        msg["Subject"] = "ExamMaster Password Reset OTP"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.send_message(msg)

        server.quit()

        return redirect("/verify_otp")

    return render_template("forgot_password.html")

#verify otp route

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        otp = request.form["otp"]

        if otp == session.get("reset_otp"):

            return redirect("/reset_password")

        return "Invalid OTP"

    return render_template("verify_otp.html")


#temp route to test email sending functionality

@app.route("/test_email")
def test_email():

    otp = random.randint(
        100000,
        999999
    )

    msg = MIMEText(
        f"Your OTP is {otp}"
    )

    msg["Subject"] = "ExamMaster OTP"

    msg["From"] = EMAIL_ADDRESS

    msg["To"] = EMAIL_ADDRESS

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        EMAIL_ADDRESS,
        EMAIL_PASSWORD
    )

    server.send_message(msg)

    server.quit()

    return "Email Sent"
# ==========================
# STUDENT REGISTER
# ==========================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]

        password = generate_password_hash(
            request.form["password"]
        )

        conn = sqlite3.connect(
    "mocktest.db",
    timeout=30,
    check_same_thread=False
)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            conn.close()

            return "Email Already Registered"

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                mobile,
                password
            )
            VALUES(?,?,?,?)
            """,
            (
                name,
                email,
                mobile,
                password
            )
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")
#=========================
# All users route for debugging
#=========================
@app.route("/all_users")
def all_users():

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id,name,email,mobile FROM users"
    )

    data = cursor.fetchall()

    conn.close()

    return str(data)
# ==========================
# STUDENT LOGIN
# ==========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(
    "mocktest.db",
    timeout=30
)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            OR mobile=?
            """,
            (
                username,
                username
            )
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user[4],
            password
        ):

            session["user_id"] = user[0]
            session["name"] = user[1]

            return redirect("/dashboard")

        return "Invalid Email/Mobile or Password"

    return render_template("login.html")


#=========================
#check users route for debugging
#=========================

@app.route("/check_users")
def check_users():

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")

    data = cursor.fetchall()

    conn.close()

    return str(data)
# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return """
<h2 style='color:green'>
Registration Successful ✅
</h2>
<a href='/login'>Login Now</a>
"""

    return render_template(
        "dashboard.html",
        name=session["name"]
    )


# ==========================
# ADMIN LOGIN
# ==========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin_dashboard")

    return render_template(
        "admin_login.html"
    )


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================
# ADD CATEGORY
# ==========================

@app.route(
    "/add_category",
    methods=["GET", "POST"]
)
def add_category():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        category_name = request.form[
            "category_name"
        ]

        conn = sqlite3.connect(
            "mocktest.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO categories
            (category_name)
            VALUES(?)
            """,
            (category_name,)
        )

        conn.commit()
        conn.close()

        return redirect(
            "/admin_dashboard"
        )

    return render_template(
        "add_category.html"
    )


# ==========================
# ADD TEST
# ==========================

@app.route(
    "/add_test",
    methods=["GET", "POST"]
)
def add_test():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM categories"
    )

    categories = cursor.fetchall()

    if request.method == "POST":

        test_name = request.form[
            "test_name"
        ]

        category_id = request.form[
            "category_id"
        ]

        duration = request.form[
            "duration"
        ]

        cursor.execute(
            """
            INSERT INTO tests
            (
                test_name,
                category_id,
                duration
            )
            VALUES(?,?,?)
            """,
            (
                test_name,
                category_id,
                duration
            )
        )

        conn.commit()

        return redirect(
            "/admin_dashboard"
        )

    conn.close()

    return render_template(
        "add_test.html",
        categories=categories
    )


# ==========================
# ADD QUESTION
# ==========================

@app.route(
    "/add_question",
    methods=["GET", "POST"]
)
def add_question():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tests"
    )

    tests = cursor.fetchall()

    if request.method == "POST":

        test_id = request.form["test_id"]
        question = request.form["question"]

        option1 = request.form["option1"]
        option2 = request.form["option2"]
        option3 = request.form["option3"]
        option4 = request.form["option4"]

        answer = request.form["answer"]

        cursor.execute(
            """
            INSERT INTO questions
            (
                test_id,
                question,
                option1,
                option2,
                option3,
                option4,
                answer
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                test_id,
                question,
                option1,
                option2,
                option3,
                option4,
                answer
            )
        )

        conn.commit()

        return redirect(
            "/admin_dashboard"
        )

    conn.close()

    return render_template(
        "add_question.html",
        tests=tests
    )


# ==========================
# AVAILABLE TESTS
# ==========================

@app.route("/tests")
def tests():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT tests.id,
           tests.test_name,
           categories.category_name,
           tests.duration
    FROM tests
    JOIN categories
    ON tests.category_id =
       categories.id
    """)

    all_tests = cursor.fetchall()

    conn.close()

    return render_template(
        "tests.html",
        tests=all_tests
    )


# ==========================
# START TEST
# ==========================

@app.route(
    "/start_test/<int:test_id>"
)
def start_test(test_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE test_id=?
        """,
        (test_id,)
    )

    questions = cursor.fetchall()

    cursor.execute(
        """
        SELECT duration
        FROM tests
        WHERE id=?
        """,
        (test_id,)
    )

    duration = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "exam.html",
        questions=questions,
        test_id=test_id,
        duration=duration
    )
# ==========================
# RESULT
# ==========================

@app.route(
    "/result/<int:test_id>",
    methods=["POST"]
)
def result(test_id):

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM questions
        WHERE test_id=?
        """,
        (test_id,)
    )

    questions = cursor.fetchall()

    score = 0

    for q in questions:

        selected = request.form.get(
            f"q{q[0]}"
        )

        if selected == q[7]:
            score += 1

    total = len(questions)

    percentage = 0

    if total > 0:
        percentage = round(
            (score / total) * 100,
            2
        )

    cursor.execute(
        """
        INSERT INTO results
        (
            user_id,
            test_id,
            score
        )
        VALUES(?,?,?)
        """,
        (
            session["user_id"],
            test_id,
            score
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage
    )


# ==========================
# MY RESULTS
# ==========================

@app.route("/my_results")
def my_results():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT tests.test_name,
               results.score
        FROM results

        JOIN tests
        ON results.test_id =
           tests.id

        WHERE results.user_id=?
        """,
        (session["user_id"],)
    )

    results = cursor.fetchall()

    conn.close()

    return render_template(
        "my_results.html",
        results=results
    )


# ==========================
# LEADERBOARD
# ==========================

@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT users.name,
               MAX(results.score)

        FROM results

        JOIN users
        ON results.user_id =
           users.id

        GROUP BY users.id

        ORDER BY
        MAX(results.score) DESC
        """
    )

    leaders = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        leaders=leaders
    )


# ==========================
# ADMIN DASHBOARD
# ==========================

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )
    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tests"
    )
    total_tests = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM questions"
    )
    total_questions = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM results"
    )
    total_results = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_tests=total_tests,
        total_questions=total_questions,
        total_results=total_results
    )


# ==========================
# VIEW STUDENTS
# ==========================

@app.route("/view_students")
def view_students():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,
               name,
               email
        FROM users
        """
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


# ==========================
# VIEW RESULTS
# ==========================

@app.route("/view_results")
def view_results():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT users.name,
               tests.test_name,
               results.score

        FROM results

        JOIN users
        ON results.user_id =
           users.id

        JOIN tests
        ON results.test_id =
           tests.id
        """
    )

    results = cursor.fetchall()

    conn.close()

    return render_template(
        "view_results.html",
        results=results
    )


# ==========================
# DELETE STUDENT
# ==========================

@app.route(
    "/delete_student/<int:id>"
)
def delete_student(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM results
        WHERE user_id=?
        """,
        (id,)
    )

    cursor.execute(
        """
        DELETE FROM users
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        "/view_students"
    )


# ==========================
# VIEW TESTS
# ==========================

@app.route("/view_tests")
def view_tests():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tests"
    )

    tests = cursor.fetchall()

    conn.close()

    return render_template(
        "view_tests.html",
        tests=tests
    )


# ==========================
# VIEW QUESTIONS
# ==========================

@app.route("/view_questions")
def view_questions():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM questions"
    )

    questions = cursor.fetchall()

    conn.close()

    return render_template(
        "view_questions.html",
        questions=questions
    )# ==========================
# BULK QUESTIONS
# ==========================

@app.route(
    "/add_bulk_questions",
    methods=["GET", "POST"]
)
def add_bulk_questions():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tests"
    )

    tests = cursor.fetchall()

    if request.method == "POST":

        test_id = request.form["test_id"]

        questions_text = request.form[
            "questions"
        ]

        lines = questions_text.strip().split(
            "\n"
        )

        for line in lines:

            data = line.split("|")

            if len(data) == 6:

                cursor.execute(
                    """
                    INSERT INTO questions
                    (
                        test_id,
                        question,
                        option1,
                        option2,
                        option3,
                        option4,
                        answer
                    )
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        test_id,
                        data[0],
                        data[1],
                        data[2],
                        data[3],
                        data[4],
                        data[5]
                    )
                )

        conn.commit()
        conn.close()

        return redirect(
            "/admin_dashboard"
        )

    return render_template(
        "bulk_questions.html",
        tests=tests
    )


# ==========================
# EXCEL UPLOAD
# ==========================


# ==========================
# DOWNLOAD TEMPLATE
# ==========================

@app.route("/download_template")
def download_template():

    return send_from_directory(
        "static",
        "question_template.xlsx",
        as_attachment=True
    )


# ==========================
# DELETE QUESTION
# ==========================

@app.route(
    "/delete_question/<int:id>"
)
def delete_question(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM questions
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        "/view_questions"
    )


# ==========================
# DELETE TEST
# ==========================

@app.route(
    "/delete_test/<int:id>"
)
def delete_test(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM questions
        WHERE test_id=?
        """,
        (id,)
    )

    cursor.execute(
        """
        DELETE FROM results
        WHERE test_id=?
        """,
        (id,)
    )

    cursor.execute(
        """
        DELETE FROM tests
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        "/view_tests"
    )


# ==========================
# ANALYTICS
# ==========================

@app.route("/analytics")
def analytics():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect(
        "mocktest.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )
    total_students = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM tests"
    )
    total_tests = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM questions"
    )
    total_questions = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM results"
    )
    total_attempts = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(score) FROM results"
    )
    avg_score = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT MAX(score) FROM results"
    )
    highest_score = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT MIN(score) FROM results"
    )
    lowest_score = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "analytics.html",
        total_students=total_students,
        total_tests=total_tests,
        total_questions=total_questions,
        total_attempts=total_attempts,
        avg_score=round(avg_score, 2),
        highest_score=highest_score,
        lowest_score=lowest_score
    )


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5004)