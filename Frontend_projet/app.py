from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/gantt")
def gantt():
    return render_template("gantt.html")

@app.route("/time")
def time():
    return render_template("time.html")

if __name__ == "__main__":
    app.run(debug=True)
