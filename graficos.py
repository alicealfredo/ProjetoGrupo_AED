import matplotlib
matplotlib.use('Agg') # Necessário para rodar no servidor sem interface gráfica
import matplotlib.pyplot as plt
import os

def gerar_grafico_barras(favs, uploads, email_user):
    # Criar a figura e os eixos (Anatomia da Figura)
    plt.figure(figsize=(6, 4))
    categorias = ['Favoritos', 'Uploads']
    valores = [favs, uploads]
    
    # Criar barras com as cores do tema
    plt.bar(categorias, valores, color=['#F4D35E', '#540B0E'])
    
    plt.title(f'Atividade Geral do Utilizador')
    plt.ylabel('Quantidade')
    
    # Guardar ficheiro
    user_id = email_user.replace('@', '_').replace('.', '_')
    caminho = f'static/imagens/gráficos/barras_{user_id}.png'
    os.makedirs('static/imagens/gráficos', exist_ok=True)
    
    plt.savefig(caminho)
    plt.close() # Limpar memória
    return f'static/imagens/graficos/barras_{user_id}.png'

def gerar_ranking_categorias(stats_categorias, email_user):
    # 1. Ordenar os dados para o ranking (do maior para o menor)
    # stats_categorias deve ser um dicionário: {"Natureza": 5, "Arte": 2, ...}
    categorias_ordenadas = sorted(stats_categorias.items(), key=lambda x: x[1], reverse=False)
    
    labels = [item[0] for item in categorias_ordenadas if item[1] > 0]
    valores = [item[1] for item in categorias_ordenadas if item[1] > 0]

    if not valores:
        return None

    # 2. Anatomia da Figura
    plt.figure(figsize=(8, 5))
    
    # Criar barras horizontais
    barras = plt.barh(labels, valores, color='#F4D35E')
    
    # Adicionar os valores exatos à frente das barras para facilitar a leitura
    plt.bar_label(barras, padding=3, fontsize=10, fontweight='bold')

    # Customização de rótulos e títulos
    plt.title('O Teu Ranking de Categorias Favoritas', fontsize=14, pad=15)
    plt.xlabel('Quantidade de Favoritos', fontsize=12)
    plt.xlim(0, max(valores) + 1) # Dá um pequeno espaço extra no fim do eixo X
    
    # Ajustar o layout para os nomes das categorias não serem cortados
    plt.tight_layout()

    # 3. Guardar a Imagem
    user_id = email_user.replace('@', '_').replace('.', '_')
    nome_ficheiro = f"ranking_{user_id}.png"
    caminho = os.path.join('static', 'imagens','gráficos', nome_ficheiro)
    
    plt.savefig(caminho)
    plt.close()
    
    return f"static/imagens/gráficos/{nome_ficheiro}"