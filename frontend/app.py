# Importation du module Flask pour créer une application web
from flask import Flask, render_template, redirect, url_for

# Création de l'application Flask
# template_folder : dossier où se trouvent les fichiers HTML
# static_folder : dossier pour les fichiers statiques (CSS, JS, images)
app = Flask(__name__, template_folder="templates", static_folder="static")

# Route pour la racine du site (redirige vers la page de connexion)
@app.route("/")
def home():
    return redirect(url_for("login"))

# Route pour la page de connexion
@app.route("/login")
def login():
    return render_template("login.html")

# Route pour la page des projets
@app.route("/projects")
def projects():
    return render_template("projects.html")

# Route pour la page du diagramme de Gantt
@app.route("/gantt")
def gantt():
    return render_template("gantt.html")

# Route pour la page de suivi du temps
@app.route("/time")
def time():
    return render_template("time.html")

# Point d'entrée de l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
