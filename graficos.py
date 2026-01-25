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
    caminho = f'static/imagens/graficos/barras_{user_id}.png'
    os.makedirs('static/imagens/graficos', exist_ok=True)
    
    plt.savefig(caminho)
    plt.close() # Limpar memória
    return f'imagens/graficos/barras_{user_id}.png'

def gerar_pizza_autores_favoritos(stats_autores, email_user):
    if not stats_autores:
        # Caso não haja favoritos
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, 'Sem favoritos\npara mostrar\nautores preferidos!', 
                 ha='center', va='center', fontsize=14, fontweight='bold',
                 transform=plt.gca().transAxes)
        plt.axis('off')
    else:
        # Ordenar por quantidade (descendente) → top autores primeiro
        autores_ordenados = sorted(stats_autores.items(), key=lambda x: x[1], reverse=True)
        labels = [autor for autor, qtd in autores_ordenados]
        valores = [qtd for autor, qtd in autores_ordenados]

        # Limitar a exibição (ex: top 8) para não ficar confuso
        if len(labels) > 8:
            outros = sum(valores[8:])
            labels = labels[:8] + ['Outros']
            valores = valores[:8] + [outros]

        plt.figure(figsize=(8, 6))
        
        cores = ['#F4D35E', '#540B0E', '#E9724C', '#255F85', '#A32858', 
                 '#49111C', '#6B7280', '#9CA3AF', '#D1D5DB']  # + cinzentos para "Outros"

        wedges, texts, autotexts = plt.pie(
            valores,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=cores[:len(valores)],
            textprops={'fontsize': 10, 'fontweight': 'bold'},
            pctdistance=0.78
        )

        # Melhorar legibilidade das percentagens
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        plt.title('Autores Mais Favoritados', fontsize=14, pad=20)
        plt.axis('equal')

    # Guardar
    user_id = email_user.replace('@', '_').replace('.', '_')
    caminho_base = 'static/imagens/graficos'
    os.makedirs(caminho_base, exist_ok=True)
    caminho = f'{caminho_base}/pizza_autores_{user_id}.png'
    
    plt.savefig(caminho, transparent=True, bbox_inches='tight', dpi=110)
    plt.close()

    return f'imagens/graficos/pizza_autores_{user_id}.png'