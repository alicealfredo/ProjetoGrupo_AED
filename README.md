PROJETOGRUPO_AED/
├── data/                 # Armazenamento de dados persistentes
│   ├── categorias.txt    # Lista de categorias
│   ├── comentarios.txt   # Registo de comentários
│   ├── imagens.csv       # Imagens
│   └── usuarios.bin      # Dados binários dos utilizadores
├── static/               # Ficheiros estáticos
│   ├── css/
│   │   └── style.css     # Estilização da interface
│   └── imagens_upload/   # Diretório de destino dos uploads
├── templates/            # Ficheiros HTML
│   ├── admin.html
│   ├── categorias.html
│   ├── dashboard.html
│   ├── imagem.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── app.py                # Servidor Flask e rotas principais
└── venv/                 # Ambiente virtual Python

Tecnologias Utilizadas:
 - Python com a framework Flask.
 - HTML5 e CSS3.

Notas de Desenvolvimento:
Atualmente, as rotas básicas de visualização estão configuradas no app.py.
O próximo passo envolve a implementação da lógica de processamento dos formulários(POST)
para gravação real nos ficheiros da pasta data/.
