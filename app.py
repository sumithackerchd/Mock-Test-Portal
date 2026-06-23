
from flask import Flask,send_from_directory, render_template, request, redirect, session
import sqlite3


app = Flask(__name__)

app.secret_key = "mocktest_secret"


# Home

@app.route("/")
def home():
    return render_template("index.html")


# Student Registration

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("mocktest.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            """,
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# Student Login

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("mocktest.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=? AND password=?
            """,
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["name"] = user[1]

            return redirect("/dashboard")

    return render_template("login.html")


# Student Dashboard

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["name"]
    )


# Admin Login

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin_dashboard")

    return render_template("admin_login.html")


# Logout

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/admin_dashboard")
# Add Category

@app.route("/add_category", methods=["GET", "POST"])
def add_category():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        category_name = request.form["category_name"]

        conn = sqlite3.connect("mocktest.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO categories(category_name)
            VALUES(?)
            """,
            (category_name,)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_category.html")


# Add Test

@app.route("/add_test", methods=["GET", "POST"])
def add_test():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories")

    categories = cursor.fetchall()

    if request.method == "POST":

        test_name = request.form["test_name"]
        category_id = request.form["category_id"]
        duration = request.form["duration"]

        cursor.execute(
            """
            INSERT INTO tests(test_name, category_id, duration)
            VALUES(?,?,?)
            """,
            (test_name, category_id, duration)
        )

        conn.commit()

        return redirect("/")

    conn.close()

    return render_template(
        "add_test.html",
        categories=categories
    )
# Add Questions

@app.route("/add_question", methods=["GET", "POST"])
def add_question():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tests")

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
            (test_id, question, option1, option2, option3, option4, answer)
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

        return redirect("/")

    conn.close()

    return render_template(
        "add_question.html",
        tests=tests
    )
# Available Tests

@app.route("/tests")
def tests():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tests.id,
           tests.test_name,
           categories.category_name,
           tests.duration
    FROM tests
    JOIN categories
    ON tests.category_id = categories.id
    """)

    all_tests = cursor.fetchall()

    conn.close()

    return render_template(
        "tests.html",
        tests=all_tests
    )
# Start Selected Test

@app.route("/start_test/<int:test_id>")
def start_test(test_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM questions
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
# Result

@app.route("/result/<int:test_id>", methods=["POST"])
def result(test_id):

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM questions
        WHERE test_id=?
        """,
        (test_id,)
    )

    questions = cursor.fetchall()

    score = 0

    for q in questions:

        selected = request.form.get(f"q{q[0]}")

        if selected == q[7]:
            score += 1

    total = len(questions)

    cursor.execute(
        """
        INSERT INTO results(user_id,test_id,score)
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
        total=total
    )
# My Results

@app.route("/my_results")
def my_results():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT tests.test_name,
               results.score
        FROM results
        JOIN tests
        ON results.test_id = tests.id
        WHERE results.user_id = ?
        """,
        (session["user_id"],)
    )

    results = cursor.fetchall()

    conn.close()

    return render_template(
        "my_results.html",
        results=results
    )
# Leaderboard

@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT users.name,
               MAX(results.score)
        FROM results
        JOIN users
        ON results.user_id = users.id
        GROUP BY users.id
        ORDER BY MAX(results.score) DESC
        """
    )

    leaders = cursor.fetchall()

    conn.close()

    return render_template(
        "leaderboard.html",
        leaders=leaders
    )

# Admin Dashboard

@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tests")
    total_tests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    total_results = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_tests=total_tests,
        total_questions=total_questions,
        total_results=total_results
    )


# View Students

@app.route("/view_students")
def view_students():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,name,email
        FROM users
        """
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


# View Results

@app.route("/view_results")
def view_results():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT users.name,
               tests.test_name,
               results.score
        FROM results
        JOIN users
        ON results.user_id = users.id
        JOIN tests
        ON results.test_id = tests.id
        """
    )

    results = cursor.fetchall()

    conn.close()

    return render_template(
        "view_results.html",
        results=results
    )


# Delete Student

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view_students")

# View Tests

@app.route("/view_tests")
def view_tests():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tests")

    tests = cursor.fetchall()

    conn.close()

    return render_template(
        "view_tests.html",
        tests=tests
    )


# View Questions

@app.route("/view_questions")
def view_questions():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions")

    questions = cursor.fetchall()

    conn.close()

    return render_template(
        "view_questions.html",
        questions=questions
    )
@app.route("/add_bulk_questions", methods=["GET","POST"])
def add_bulk_questions():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tests")
    tests = cursor.fetchall()

    if request.method == "POST":

        test_id = request.form["test_id"]
        questions_text = request.form["questions"]

        lines = questions_text.strip().split("\n")

        for line in lines:

            data = line.split("|")

            if len(data) == 6:

                cursor.execute("""
                INSERT INTO questions
                (test_id, question, option1, option2, option3, option4, answer)
                VALUES(?,?,?,?,?,?,?)
                """,(
                    test_id,
                    data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    data[5]
                ))

        conn.commit()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template(
        "bulk_questions.html",
        tests=tests
    )
@app.route("/upload_excel", methods=["GET","POST"])
def upload_excel():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("mocktest.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tests")
    tests = cursor.fetchall()

    if request.method == "POST":

        test_id = request.form["test_id"]

        file = request.files["excel_file"]

        df = pd.read_excel(file)

        for index,row in df.iterrows():

            cursor.execute("""
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
            """,(
                test_id,
                row["question"],
                row["option1"],
                row["option2"],
                row["option3"],
                row["option4"],
                row["answer"]
            ))

        conn.commit()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template(
        "upload_excel.html",
        tests=tests
    )
@app.route("/download_template")
def download_template():

    return send_from_directory(
        "static",
        "question_template.xlsx",
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(debug=True, port=5004)

    