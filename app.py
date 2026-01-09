from flask import Flask, render_template
import os

app = Flask(__name__)

def get_categorias():
    categorias = []
    caminho = 'categorias.txt'
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            # Lendo todas as linhas e removendo espaços em branco
            linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
            # Ignora a primeira linha que contém o título do arquivo 
            categorias = linhas[1:]
    return categorias

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/categorias")
def categorias():
    lista = get_categorias()
    # Tabela
    tabela_html = '<table class="table-custom"><thead><tr><th>Categoria</th></tr></thead><tbody>'
    for item in lista:
        tabela_html += f'<tr><td>{item}</td></tr>'
    tabela_html += '</tbody></table>'

    return render_template('categorias.html', categoryTable=tabela_html)

@app.route("/login")
def login():
    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True)
