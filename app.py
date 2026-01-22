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
    # Verifica se o utilizador está logado
    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_foto = request.args.get('url')
    autor = request.args.get('autor', 'Anónimo')
    titulo = request.args.get('titulo', 'Foto')
    
    # Cria um nome de ficheiro único por utilizador
    caminho_fav = f'data/favoritos_{email_user}.csv'
    
    with open(caminho_fav, 'a', encoding='utf-8') as f:
        # Guarda URL, Título e Autor separados por TAB
        f.write(f"{url_foto}\t{titulo}\t{autor}\n")
        
    return redirect(url_for('index'))

@app.route("/remover_favorito")
def remover_favorito():
    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_remover = request.args.get('url')
    caminho_fav = f'data/favoritos_{email_user}.csv'
    
    if os.path.exists(caminho_fav):
        # 1. Ler todas as linhas atuais
        linhas_restantes = []
        with open(caminho_fav, 'r', encoding='utf-8') as f:
            for linha in f:
                # Se a URL na linha não for a que queremos remover, mantemos
                if url_remover not in linha:
                    linhas_restantes.append(linha)
        
        # 2. Sobreescrever o ficheiro com a nova lista (sem a imagem removida)
        with open(caminho_fav, 'w', encoding='utf-8') as f:
            for linha in linhas_restantes:
                f.write(linha)
                
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for('login'))

    email_user = session["user"]["email"]
    imagens_dashboard = []
    
    # 1. Carregar Favoritos (Código que já tem)
    caminho_fav = f'data/favoritos_{email_user}.csv'
    if os.path.exists(caminho_fav):
        with open(caminho_fav, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('\t')
                if len(partes) >= 3:
                    imagens_dashboard.append({
                        'photo_image_url': partes[0],
                        'categoria': partes[1],
                        'autor': partes[2],
                        'tipo': 'favorito'
                    })

    # 2. Carregar Uploads Próprios
    caminho_fotos = 'data/photos.csv000'
    if os.path.exists(caminho_fotos):
        with open(caminho_fotos, 'r', encoding='utf-8') as f:
            # Pulamos o cabeçalho se existir ou tratamos erro
            for linha in f:
                partes = linha.strip().split('\t')
                # Verificamos se a linha tem o nosso e-mail no final (campo 5)
                if len(partes) >= 6 and partes[5] == email_user:
                    imagens_dashboard.append({
                        'photo_image_url': partes[0],
                        'categoria': partes[2],
                        'autor': partes[3],
                        'tipo': 'upload'
                    })

    return render_template("dashboard.html", images=imagens_dashboard)

@app.route("/upload", methods=["POST"])
def upload_imagem():
    if "user" not in session:
        return redirect(url_for('login'))
        
    # 1. Identificar o utilizador e definir o caminho da pasta individual
    email_user = session["user"]["email"]
    nome_pasta_user = email_user.replace("@", "_").replace(".", "_") # Limpa caracteres especiais
    caminho_base = 'static/uploads'
    caminho_user = os.path.join(caminho_base, nome_pasta_user)
    
    # 2. Criar a pasta do utilizador se não existir
    if not os.path.exists(caminho_user):
        os.makedirs(caminho_user)
    
    # 3. Processar os dados do formulário
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    autor = request.form.get("autor") or session["user"]["nome"]
    ficheiro = request.files.get("arquivo")

    if ficheiro and ficheiro.filename != '':
        nome_ficheiro = ficheiro.filename.replace(" ", "_")
        # Guardar o ficheiro dentro da pasta do utilizador
        caminho_final_disco = os.path.join(caminho_user, nome_ficheiro)
        ficheiro.save(caminho_final_disco)

        # 4. Guardar no CSV com o caminho relativo correto para o navegador
        with open('data/photos.csv000', 'a', encoding='utf-8') as f:
            # A URL agora inclui a subpasta do utilizador
            url_navegador = f"/static/uploads/{nome_pasta_user}/{nome_ficheiro}"
            f.write(f"\n{url_navegador}\t{descricao}\t{titulo}\t{autor}\tLocal\t{email_user}")

    return redirect(url_for('dashboard'))

@app.route("/remover_upload")
def remover_upload():
    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_remover = request.args.get('url')
    caminho_csv = 'data/photos.csv000'
    
    if os.path.exists(caminho_csv):
        linhas_restantes = []
        foto_apagada = False
        
        with open(caminho_csv, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('\t')
                # Validação: URL coincide e o e-mail (coluna 6) é do dono
                if len(partes) >= 6 and partes[0] == url_remover and partes[5] == email_user:
                    # Remove o ficheiro físico (limpa a barra inicial para o OS)
                    caminho_fisico = partes[0].lstrip('/')
                    if os.path.exists(caminho_fisico):
                        os.remove(caminho_fisico)
                    foto_apagada = True
                    continue 
                linhas_restantes.append(linha)
        
        if foto_apagada:
            with open(caminho_csv, 'w', encoding='utf-8') as f:
                for linha in linhas_restantes:
                    f.write(linha if linha.endswith('\n') else linha + '\n')
                
    return redirect(url_for('dashboard'))

@app.route("/categorias")
def categorias():
    # 1. Obter todas as imagens uma única vez para contar
    todas = obter_imagens(n=15000) 
    
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
            session["user"] = user_data
            
            # NOVO: Se o email for o do admin, vai para o painel de admin
            if user_data['email'] == 'admin@gmail.com':
                return redirect(url_for("admin"))
            
            # Caso contrário, vai para categorias como já estava
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

@app.route("/admin")
def admin():
    if "user" not in session or session["user"]["email"] != "admin@gmail.com":
        return redirect(url_for('login'))

    # 1. Estatísticas de Utilizadores
    users_list = []
    if os.path.exists(UTILIZADORES_BIN):
        with open(UTILIZADORES_BIN, "rb") as f:
            for linha in f:
                dados = linha.decode("utf-8").strip().split("|")
                if len(dados) >= 2:
                    users_list.append({'nome': dados[0], 'email': dados[1]})

    # 2. Estatísticas e Listagem de Fotos (Moderação)
    todas_fotos = []
    caminho_csv = 'data/photos.csv000'
    if os.path.exists(caminho_csv):
        with open(caminho_csv, 'r', encoding='utf-8') as f:
            # Pula o cabeçalho se houver, ou trata como DictReader
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
        
                todas_fotos.append({
                    'url': row.get('photo_image_url'),
                    'titulo': row.get('photo_description', 'Sem título'),
                    'autor': row.get('photographer_username', 'Anónimo'),
                    'dono_email': row.get('email_user', 'Sistema') # Requer que o upload grave o email
                })

                if len(todas_fotos)>=50:
                    break

    return render_template("admin.html", 
                           users=users_list, 
                           photos=todas_fotos,
                           stats={'total_users': len(users_list), 'total_photos': len(todas_fotos)})

@app.route("/admin/banir/<email>")
def banir_utilizador(email):
    if "user" not in session or session["user"]["email"] != "admin@email.com":
        return redirect(url_for('login'))

    linhas_restantes = []
    with open(UTILIZADORES_BIN, "rb") as f:
        for linha in f:
            if email not in linha.decode("utf-8"):
                linhas_restantes.append(linha)
    
    with open(UTILIZADORES_BIN, "wb") as f:
        for linha in linhas_restantes:
            f.write(linha)
    return redirect(url_for('admin_panel'))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)