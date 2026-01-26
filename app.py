from flask import Flask, render_template, request, redirect, url_for, session
import csv
import random
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from graficos import gerar_grafico_barras, gerar_pizza_autores_favoritos

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

# --- CONFIGURAÇÕES DE DADOS ---
UTILIZADORES_BIN = "data/utilizadores.bin"

# --- FUNÇÕES DE PERSISTÊNCIA (FICHEIRO BINÁRIO) ---

def guardar_utilizador(nome, email, senha):
    """Guarda um novo utilizador no ficheiro binário com codificação UTF-8."""
    linha = f"{nome}|{email}|{senha}\n"
    with open(UTILIZADORES_BIN, "ab") as f:
        f.write(linha.encode("utf-8"))

def email_existe(email):
    """Verifica se um email já está registado no sistema."""
    if not os.path.exists(UTILIZADORES_BIN):
        return False
    
    with open(UTILIZADORES_BIN, "rb") as f:
        for linha in f:
            dados = linha.decode("utf-8").strip().split("|")
            if len(dados) >= 2 and dados[1] == email:
                return True
    return False

def verificar_login(email, senha):
    """Valida as credenciais do utilizador percorrendo o ficheiro binário."""
    if not os.path.exists(UTILIZADORES_BIN):
        return None
    
    with open(UTILIZADORES_BIN, "rb") as f:
        for linha in f:
            nome, em, pw = linha.decode("utf-8").strip().split("|")
            if em == email and pw == senha:
                return {"nome": nome, "email": em}
    
    return None

# --- LÓGICA DE GESTÃO DE IMAGENS E CATEGORIAS ---

def obter_imagens(n=9, query=None):
    """Lê o ficheiro photos.csv e aplica filtros de pesquisa ou categoria."""
    imagens = []
    caminho = 'data/photos.csv'  

    try:
        with open(caminho, 'r', encoding='utf-8') as ficheiro:
            leitor = csv.DictReader(ficheiro, delimiter='\t')  
            for linha in leitor:
                url = (linha.get('photo_image_url') or '').strip()
                if not url:
                    continue

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

                primeira_palavra = desc.split()[0].capitalize() if desc.split() else 'Foto'

                imagens.append({
                    'photo_image_url': url,
                    'photo_description': desc,
                    'categoria': primeira_palavra,
                    'autor': autor,
                    'local': local
                })

        if len(imagens) > n:
            return random.sample(imagens, n)
        
        return imagens

    except FileNotFoundError:
        return [{'erro': f'Arquivo não encontrado: {caminho}. Verifica o nome e a pasta data/'}]
    except Exception as e:
        return [{'erro': f'Erro ao ler o arquivo: {str(e)}'}]
    
def obter_fotos_por_categoria(slug, quantidade=4):
    fotos = obter_imagens(n=100, query=slug) 
    
    if len(fotos) >= quantidade:
        return random.sample(fotos, quantidade)
    return fotos 

def obter_comentarios(url_foto):
    comentarios = []
    caminho = 'data/comentarios.csv'
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('|')
                if len(partes) >= 3 and partes[0] == url_foto:
                    comentarios.append({
                        'autor': partes[1],
                        'texto': partes[2]
                    })
    return comentarios
    

CATEGORIAS_FIXAS = [
    {"nome": "Natureza", "slug": "nature", "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80"},
    {"nome": "Arquitetura", "slug": "architecture", "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80"},
    {"nome": "Pessoas", "slug": "people", "img": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80"},
    {"nome": "Paisagens", "slug": "landscape", "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&q=80"},
    {"nome": "Animais", "slug": "animal", "img": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=400&q=80"},
    {"nome": "Arte", "slug": "art", "img": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&q=80"}
]

# --- ROTAS PRINCIPAIS E NAVEGAÇÃO ---

@app.route("/")
def index():
    """Página Inicial: Exibe feed de imagens e barra de pesquisa."""

    query = request.args.get('search', '').strip()
    
    imagens = obter_imagens(n=60, query=query if query else None)
    
    return render_template(
        "index.html",
        images=imagens,
        query=query,
        categorias=CATEGORIAS_FIXAS,
        obter_comentarios=obter_comentarios
    )

@app.route("/favoritar")
def favoritar():
    """Adiciona uma imagem ao ficheiro CSV individual de favoritos do utilizador."""

    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_foto = request.args.get('url')
    autor = request.args.get('autor', 'Anónimo')
    
    categoria = request.args.get('categoria', 'Sem categoria') 
    
    caminho_fav = f'data/favoritos_{email_user}.csv'

    # Gravação utilizando tabulação (\t) como separador conforme a estrutura do projeto
    with open(caminho_fav, 'a', encoding='utf-8') as f:
        f.write(f"{url_foto}\t{categoria}\t{autor}\n")
        
    return redirect(url_for('index'))

@app.route("/remover_favorito")
def remover_favorito():
    """Remove uma entrada específica do ficheiro de favoritos do utilizador."""

    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_remover = request.args.get('url')
    caminho_fav = f'data/favoritos_{email_user}.csv'
    
    if os.path.exists(caminho_fav):
        linhas_restantes = []
        with open(caminho_fav, 'r', encoding='utf-8') as f:
            for linha in f:
                if url_remover not in linha:
                    linhas_restantes.append(linha)

        # Reescreve o ficheiro apenas com os itens que não foram removidos
        with open(caminho_fav, 'w', encoding='utf-8') as f:
            for linha in linhas_restantes:
                f.write(linha)
                
    return redirect(url_for('dashboard'))

# --- DASHBOARD E ESTATÍSTICAS ---

@app.route("/dashboard")
def dashboard():
    """Painel do Utilizador: Reúne favoritos, uploads e gera gráficos estatísticos."""

    if "user" not in session:
        return redirect(url_for('login'))

    email_user = session["user"]["email"]
    count_favs = 0
    count_uploads = 0
    imagens_dashboard = []
    stats_autores = {}  
    
    # 1. Carregar Favoritos do utilizador
    caminho_fav = f'data/favoritos_{email_user}.csv'
    if os.path.exists(caminho_fav):
        with open(caminho_fav, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('\t')
                if len(partes) >= 3:
                    url = partes[0]
                    autor = partes[2].strip()

                    imagens_dashboard.append({
                        'photo_image_url': url,
                        'categoria': partes[1] if len(partes)>1 else "—",
                        'autor': autor,
                        'tipo': 'favorito'
                    })

                    stats_autores[autor] = stats_autores.get(autor, 0) + 1
                    count_favs += 1
    
    # 2. Carregar Uploads feitos pelo utilizador (filtrados por email no photos.csv)
    caminho_fotos = 'data/photos.csv'
    if os.path.exists(caminho_fotos):
        with open(caminho_fotos, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('\t')
                if len(partes) >= 6 and partes[5] == email_user:
                    imagens_dashboard.append({
                        'photo_image_url': partes[0],
                        'categoria': partes[2],
                        'autor': partes[3],
                        'tipo': 'upload'
                    })
                    count_uploads += 1

    # 3. Gerar ficheiros de imagem dos gráficos (usando graficos.py)
    url_barras = gerar_grafico_barras(count_favs, count_uploads, email_user)
    url_pizza = gerar_pizza_autores_favoritos(stats_autores, email_user)

    return render_template("dashboard.html",
                           count_favs=count_favs,
                           count_uploads=count_uploads,
                           images=imagens_dashboard,
                           url_barras=url_barras,
                           url_pizza=url_pizza)

# --- SISTEMA DE UPLOAD ---

@app.route("/upload", methods=["POST"])
def upload_imagem():
    """Gere o upload físico de ficheiros e o registo dos metadados no CSV global."""

    if "user" not in session:
        return redirect(url_for('login'))
        
    email_user = session["user"]["email"]

    # Cria pasta específica para o utilizador se não existir
    nome_pasta_user = email_user.replace("@", "_").replace(".", "_") 
    caminho_base = 'static/imagens/uploads'
    caminho_user = os.path.join(caminho_base, nome_pasta_user)
    
    if not os.path.exists(caminho_user):
        os.makedirs(caminho_user)
    
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    autor = request.form.get("autor") or session["user"]["nome"]
    ficheiro = request.files.get("arquivo")

    if ficheiro and ficheiro.filename != '':
        nome_ficheiro = ficheiro.filename.replace(" ", "_")
        caminho_final_disco = os.path.join(caminho_user, nome_ficheiro)
        ficheiro.save(caminho_final_disco)

        # Regista a nova imagem no photos.csv para aparecer no feed global
        with open('data/photos.csv', 'a', encoding='utf-8') as f:
            url_navegador = f"static/imagens/uploads/{nome_pasta_user}/{nome_ficheiro}"
            f.write(f"\n{url_navegador}\t{descricao}\t{titulo}\t{autor}\tLocal\t{email_user}")

    return redirect(url_for('dashboard'))

# --- PERFIL E ADMINISTRAÇÃO ---

@app.route("/admin")
def admin():
    """Painel de Administração: Estatísticas totais e moderação de utilizadores/comentários."""

    if "user" not in session or session["user"]["email"] != "admin@gmail.com":
        return redirect(url_for('login'))

    # Carrega lista de utilizadores para gestão
    users_list = []
    if os.path.exists(UTILIZADORES_BIN):
        with open(UTILIZADORES_BIN, "rb") as f:
            for linha in f:
                dados = linha.decode("utf-8").strip().split("|")
                if len(dados) >= 2:
                    users_list.append({'nome': dados[0], 'email': dados[1]})

    # Carrega fotos (limitado a 50 para performance) e comentários
    todas_fotos = []
    caminho_csv = 'data/photos.csv'
    if os.path.exists(caminho_csv):
        with open(caminho_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
        
                todas_fotos.append({
                    'url': row.get('photo_image_url'),
                    'titulo': row.get('photo_description', 'Sem título'),
                    'autor': row.get('photographer_username', 'Anónimo'),
                    'dono_email': row.get('email_user', 'Sistema') 
                })

                if len(todas_fotos)>=50:
                    break

    todos_comentarios = []
    caminho_com = 'data/comentarios.csv'
    if os.path.exists(caminho_com):
        with open(caminho_com, 'r', encoding='utf-8') as f:
            for i, linha in enumerate(f):
                partes = linha.strip().split('|')
                if len(partes) >= 3:
                    todos_comentarios.append({
                        'id': i,
                        'url_foto': partes[0],
                        'autor': partes[1],
                        'texto': partes[2],
                    })

    return render_template("admin.html", 
                           users=users_list, 
                           photos=todas_fotos,
                           comentarios=todos_comentarios,
                           stats={'total_users': len(users_list),'total_photos': len(todas_fotos)})

@app.route("/comentar", methods=["POST"])
def comentar():
    """Regista comentários associados a uma URL de imagem no ficheiro comentarios.csv."""

    if "user" not in session:
        return redirect(url_for('login'))
    
    utilizador = session["user"]["nome"]
    url_foto = request.form.get("url_foto")
    texto = request.form.get("comentario").strip()
        
    if texto:
        caminho_comentarios = 'data/comentarios.csv'
        with open(caminho_comentarios, 'a', encoding='utf-8') as f:
            f.write(f"{url_foto}|{utilizador}|{texto}\n")
            
    return redirect(request.referrer or url_for('index'))

# --- MODERAÇÃO E GESTÃO DE CONTEÚDO ---

@app.route("/remover_upload")
def remover_upload():
    """
    Remove uma imagem do sistema:
    1. Elimina o ficheiro físico da pasta static/imagens/uploads.
    2. Remove a entrada correspondente no ficheiro photos.csv.
    """

    if "user" not in session:
        return redirect(url_for('login'))
    
    email_user = session["user"]["email"]
    url_remover = request.args.get('url')
    caminho_csv = 'data/photos.csv'
    
    if os.path.exists(caminho_csv):
        linhas_restantes = []
        foto_apagada = False
        
        with open(caminho_csv, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('\t')
                # Valida se a foto pertence ao utilizador antes de apagar
                if len(partes) >= 6 and partes[0] == url_remover and partes[5] == email_user:
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

# --- NAVEGAÇÃO POR CATEGORIAS ---

@app.route("/categorias")
def categorias():
    """
    Processa as categorias fixas e seleciona dinamicamente imagens de amostra
    baseadas na descrição das fotos no CSV.
    """

    todas = obter_imagens(n=15000) 
    
    categorias_processadas = []
    for cat in CATEGORIAS_FIXAS:
        nova_cat = cat.copy()
        
        # Filtra fotos que contenham o 'slug' na descrição
        fotos_da_cat = [img for img in todas if cat['slug'] in img['photo_description'].lower()]
        
        nova_cat['total'] = len(fotos_da_cat)
        
        # Define a imagem de capa e as miniaturas (thumbs)
        if len(fotos_da_cat) >= 4:
            amostra = random.sample(fotos_da_cat, 4)
            nova_cat['capa'] = amostra[0]['photo_image_url']
            nova_cat['thumbs'] = [f['photo_image_url'] for f in amostra[1:4]]
        else:
            nova_cat['capa'] = cat['img']
            nova_cat['thumbs'] = [cat['img']] * 3
            
        categorias_processadas.append(nova_cat)
        
    return render_template("categorias.html", categorias=categorias_processadas)

# --- GESTÃO DE UTILIZADORES E PERFIL ---

@app.route("/login", methods=["GET","POST"])
def login():
    """Gere o acesso ao sistema e redireciona admin ou user comum para as suas áreas."""

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        user_data = verificar_login(email, senha)

        if user_data:
            session["user"] = user_data
            
            if user_data['email'] == 'admin@gmail.com':
                return redirect(url_for("admin"))
            
            return redirect(url_for("categorias"))
        else:
            return "Login inválido!"

    return render_template("login.html")

@app.route("/registo", methods=["GET","POST"])
def registo():
    """
    Processa o registo de novos utilizadores.
    Verifica a existência do email no ficheiro binário antes de guardar.
    """

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Lista de interesses capturada do formulário (para personalização futura)
        interesses = request.form.getlist("interesses")

        # Validação de duplicados no ficheiro utilizadores.bin
        if email_existe(email):
            return "Email já registado!"

        # Persistência dos dados em formato binário
        guardar_utilizador(nome, email, senha)
        return redirect(url_for("login"))

    return render_template("registo.html")

# --- ÁREA PESSOAL E HISTÓRICO ---

@app.route("/perfil")
def perfil():
    """
    Apresenta os dados do perfil e o histórico de comentários do utilizador logado.
    Filtra o ficheiro comentarios.csv pelo nome do utilizador em sessão.
    """

    if "user" not in session:
        return redirect(url_for("login"))
    
    meus_comentarios = []
    caminho_com = 'data/comentarios.csv'
    if os.path.exists(caminho_com):
        with open(caminho_com, 'r', encoding='utf-8') as f:
            for linha in f:
                partes = linha.strip().split('|')
                # Verifica se o comentário pertence ao utilizador atual (índice 1 do CSV)
                if len(partes) >= 3 and partes[1] == session["user"]["nome"]:
                    meus_comentarios.append({
                        'url_foto': partes[0],
                        'texto': partes[2],
                        'data': "sem data"
                    })

    return render_template("perfil.html", user=session["user"], meus_comentarios=meus_comentarios)

@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    """
    Atualiza os dados do utilizador no ficheiro binário.
    Reescreve o ficheiro mantendo os outros utilizadores intactos.
    """
    
    if "user" not in session:
        return redirect(url_for('login'))

    email_atual = session["user"]["email"]

    if request.method == "POST":
        novo_nome = request.form.get("nome")
        nova_senha = request.form.get("senha")

        linhas_atualizadas = []
        utilizador_encontrado = False

        if os.path.exists(UTILIZADORES_BIN):
            with open(UTILIZADORES_BIN, "rb") as f:
                for linha in f:
                    nome, email, senha = linha.decode("utf-8").strip().split("|")
                    if email == email_atual:
                        # Mantém a senha antiga se o campo estiver vazio
                        senha_final = nova_senha if nova_senha else senha
                        nova_linha = f"{novo_nome}|{email}|{senha_final}\n"
                        linhas_atualizadas.append(nova_linha.encode("utf-8"))
                        session["user"]["nome"] = novo_nome
                    else:
                        linhas_atualizadas.append(linha)

        with open(UTILIZADORES_BIN, "wb") as f:
            for l in linhas_atualizadas:
                f.write(l)

        return redirect(url_for('perfil'))

    return render_template("editar_perfil.html")

# --- FUNÇÕES ADMINISTRATIVAS ---

@app.route("/admin/banir/<email>")
def banir_utilizador(email):
    """Remove um utilizador permanentemente do ficheiro binário (Acesso Restrito)."""

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

@app.route("/admin/comentario/apagar/<int:comment_id>")
def apagar_comentario_admin(comment_id):
    """
    Permite ao administrador apagar comentários inadequados.
    Lê o CSV, ignora a linha pelo índice (ID) e reescreve o ficheiro atualizado.
    """

    # Proteção de rota: apenas o email de admin tem acesso
    if "user" not in session or session["user"]["email"] != "admin@gmail.com":
        return redirect(url_for('login'))

    caminho = 'data/comentarios.csv'
    linhas = []
    
    # Carrega todas as linhas, exceto a que deve ser eliminada
    with open(caminho, 'r', encoding='utf-8') as f:
        for i, linha in enumerate(f):
            if i != comment_id:
                linhas.append(linha)

    # Atualiza o ficheiro comentarios.csv no disco
    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(linhas)

    return redirect(url_for('admin'))

@app.route("/logout")
def logout():
    """Encerra a sessão do utilizador e limpa os dados da memória."""

    session.pop("user", None)
    return redirect(url_for("login"))

# --- INICIALIZAÇÃO ---

if __name__ == "__main__":
    # O modo debug=True permite ver erros detalhados e reinicia o servidor ao alterar código
    app.run(debug=True)
