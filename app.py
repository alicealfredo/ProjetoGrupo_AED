from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Lista das imagens existentes na pasta static/imagens
IMAGES = [
    {"arquivo": "imagemBeleza_01.jpg", "categoria": "Beleza"},
    {"arquivo": "imagemBeleza_02.jpg", "categoria": "Beleza"},
    {"arquivo": "imagemCidade_01.jpg", "categoria": "Cidade"},
    {"arquivo": "imagemDesporto_01.jpg", "categoria": "Desporto"},
    {"arquivo": "imagemGastronomia_01.jpg", "categoria": "Gastronomia"},
    {"arquivo": "imagemNatureza_01.jpg", "categoria": "Natureza"},
    {"arquivo": "imagemTecnologia_01.jpg", "categoria": "Tecnologia"},
    {"arquivo": "imagemTecnologia_02.jpg", "categoria": "Tecnologia"},
    {"arquivo": "imagemGastronomia_02.jpg", "categoria": "Gastronomia"},
]

@app.route("/")
def index():
    return render_template("index.html", imagens=IMAGES)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/categorias")
def categorias():
    return render_template('categorias.html')

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
