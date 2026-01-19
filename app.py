from flask import Flask, render_template, request, redirect, url_for, session
import csv
import random
import os

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

UTILIZADORES_BIN = "data/utilizadores.bin"

def guardar_utilizador(nome, email, senha):
    linha = f"{nome}|{email}|{senha}\n"
    with open(UTILIZADORES_BIN, "ab") as f:  # append binário
        f.write(linha.encode("utf-8"))

def email_existe(email):
    if not os.path.exists(UTILIZADORES_BIN):
        return False
    
    with open(UTILIZADORES_BIN, "rb") as f:
        for linha in f:
            dados = linha.decode("utf-8").strip().split("|")
            if len(dados) >= 2 and dados[1] == email:
                return True
    return False

def verificar_login(email, senha):
    if not os.path.exists(UTILIZADORES_BIN):
        return None
    
    with open(UTILIZADORES_BIN, "rb") as f:
        for linha in f:
            nome, em, pw = linha.decode("utf-8").strip().split("|")
            if em == email and pw == senha:
                return {"nome": nome, "email": em}
    
    return None

def obter_imagens(n=9, query=None):
    imagens = []
    caminho = 'data/photos.csv000'  # confirma que o nome está exatamente assim!

    try:
        with open(caminho, 'r', encoding='utf-8') as ficheiro:
            leitor = csv.DictReader(ficheiro, delimiter='\t')  # separador = TAB
            for linha in leitor:
                # O (linha.get(...) or '') evita o erro de NoneType
                url = (linha.get('photo_image_url') or '').strip()
                if not url:
                    continue

                # Descrição com fallback para ai_description
                desc = (linha.get('photo_description') or '').strip()
                if not desc:
                    desc = (linha.get('ai_description') or 'Sem descrição').strip()

                desc = (linha.get('photo_description') or '').strip()
                autor = (linha.get('photographer_username') or 'Anónimo').strip()
                local = (linha.get('photo_location_name') or '').strip()

                if query:
                    q = query.lower()
                    texto_total = f"{desc} {autor} {local}".lower()

                    if q not in texto_total:
                        continue

                # "Categoria" fake: primeira palavra da descrição (ou "Foto" se vazio)
                primeira_palavra = desc.split()[0].capitalize() if desc.split() else 'Foto'

                imagens.append({
                    'photo_image_url': url,
                    'photo_description': desc,
                    'categoria': primeira_palavra,
                    'autor': autor,
                    'local': local
                })

        # Se tiver mais do que precisamos → amostra aleatória
        if len(imagens) > n:
            return random.sample(imagens, n)
        
        return imagens

    except FileNotFoundError:
        return [{'erro': f'Arquivo não encontrado: {caminho}. Verifica o nome e a pasta data/'}]
    except Exception as e:
        return [{'erro': f'Erro ao ler o arquivo: {str(e)}'}]
    
def obter_fotos_por_categoria(slug, quantidade=4):
    # Procura todas as imagens que correspondem ao filtro
    fotos = obter_imagens(n=100, query=slug) 
    
    if len(fotos) >= quantidade:
        return random.sample(fotos, quantidade)
    return fotos # Retorna o que encontrar se houver poucas
    

CATEGORIAS_FIXAS = [
    {"nome": "Natureza", "slug": "nature", "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80"},
    {"nome": "Arquitetura", "slug": "architecture", "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80"},
    {"nome": "Pessoas", "slug": "people", "img": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80"},
    {"nome": "Paisagens", "slug": "landscape", "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80"},
    {"nome": "Animais", "slug": "animal", "img": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400&q=80"},
    {"nome": "Arte", "slug": "art", "img": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&q=80"}
]

@app.route("/")
def index():
    # Sincronizando com o name="search" que está no seu index.html
    query = request.args.get('search', '').strip()
    
    # Se não houver pesquisa, 'obter_imagens' retorna aleatórias (conforme seu código)
    imagens = obter_imagens(n=60, query=query if query else None)
    
    return render_template(
        "index.html",
        images=imagens,
        query=query,
        categorias=CATEGORIAS_FIXAS # Passando a lista para o HTML
    )


# No app.py, substitua a função favoritar por esta:
@app.route("/favoritar")
def favoritar():
    url_foto = request.args.get('url')
    autor = request.args.get('autor', 'Anónimo')
    titulo = request.args.get('titulo', 'Foto')
    
    caminho_fav = 'data/favoritos.csv'
    
    # Salvamos os dados separados por TAB para manter o padrão
    with open(caminho_fav, 'a', encoding='utf-8') as f:
        f.write(f"{url_foto}\t{titulo}\t{autor}\n")
        
    return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    favoritos_urls = []
    caminho_fav = 'data/favoritos.csv'
    
    # 1. Carregar URLs das imagens favoritadas
    try:
        if os.path.exists(caminho_fav):
            with open(caminho_fav, 'r', encoding='utf-8') as f:
                favoritos_urls = [linha.strip() for linha in f.readlines()]
    except Exception:
        pass

    # 2. Obter todas as imagens do sistema
    todas_imagens = obter_imagens(n=1000) 

    if todas_imagens and 'erro' in todas_imagens[0]:
        return render_template("dashboard.html", images=[], erro=todas_imagens[0]['erro'])

    # 3. FILTRAGEM DUPLA:
    # Mostramos se a imagem está nos favoritos OU se foi carregada pelo "Admin"
    imagens_dashboard = [
        img for img in todas_imagens 
        if img.get('photo_image_url') in favoritos_urls or img.get('autor') == "Admin"
    ]

    return render_template("dashboard.html", images=imagens_dashboard)

@app.route("/upload", methods=["POST"])
def upload_imagem():
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    # Capturamos o nome inserido no formulário (ou "Anónimo" se estiver vazio)
    autor = request.form.get("autor") or "Anónimo" 
    ficheiro = request.files.get("arquivo")

    if ficheiro and ficheiro.filename != '':
        nome_ficheiro = ficheiro.filename.replace(" ", "_")
        caminho_pasta = 'static/uploads'
        
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            
        ficheiro.save(os.path.join(caminho_pasta, nome_ficheiro))

        # Guarda no CSV usando a variável 'autor' em vez de "Admin"
        with open('data/photos.csv000', 'a', encoding='utf-8') as f:
            url = "/static/uploads/" + nome_ficheiro
            # A ordem deve seguir: URL \t Descrição \t Categoria \t Autor \t Local
            f.write(f"\n{url}\t{descricao}\t{titulo}\t{autor}\tLocal")

    return redirect(url_for('dashboard'))

@app.route("/categorias")
def categorias():
    # 1. Obter todas as imagens uma única vez para contar
    todas = obter_imagens(n=5000) 
    
    categorias_processadas = []
    for cat in CATEGORIAS_FIXAS:
        nova_cat = cat.copy()
        
        # Filtra as fotos que pertencem a esta categoria
        fotos_da_cat = [img for img in todas if cat['slug'] in img['photo_description'].lower()]
        
        # Define o contador real
        nova_cat['total'] = len(fotos_da_cat)
        
        # Define as imagens de capa e miniaturas (como fizemos antes)
        if len(fotos_da_cat) >= 4:
            amostra = random.sample(fotos_da_cat, 4)
            nova_cat['capa'] = amostra[0]['photo_image_url']
            nova_cat['thumbs'] = [f['photo_image_url'] for f in amostra[1:4]]
        else:
            nova_cat['capa'] = cat['img']
            nova_cat['thumbs'] = [cat['img']] * 3
            
        categorias_processadas.append(nova_cat)
        
    return render_template("categorias.html", categorias=categorias_processadas)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        user_data = verificar_login(email, senha)

        if user_data:
            session["user"] = user_data # Guarda nome e interesses na sessão
            return redirect(url_for("categorias"))
        else:
            return "Login inválido!"

    return render_template("login.html")

@app.route("/registo", methods=["GET","POST"])
def registo():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        interesses = request.form.getlist("interesses")

        if email_existe(email):
            return "Email já registado!"

        guardar_utilizador(nome, email, senha)
        return redirect(url_for("login"))

    return render_template("registo.html")

@app.route("/perfil")
def perfil():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("perfil.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)