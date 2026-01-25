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

def gerar_ranking_categorias(stats_categorias, email_user):
    # Filtrar apenas categorias que têm pelo menos 1 favorito
    labels = [cat for cat, qtd in stats_categorias.items() if qtd > 0]
    valores = [qtd for cat, qtd in stats_categorias.items() if qtd > 0]

    if not valores:
        return None

    plt.figure(figsize=(8, 6))
    
    # Cores personalizadas (podes adicionar mais se tiveres muitas categorias)
    cores = ['#F4D35E', '#540B0E', '#E9724C', '#255F85', '#A32858', '#49111C']
    
    # Criar o gráfico de pizza
    # autopct='%1.1f%%' adiciona a percentagem automaticamente nas fatias
    plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140, colors=cores, 
            textprops={'fontweight': 'bold'})
    
    plt.title('Distribuição de Categorias Favoritas', fontsize=14, pad=20)
    plt.axis('equal')  # Garante que o gráfico seja um círculo perfeito
    
    # Guardar ficheiro
    user_id = email_user.replace('@', '_').replace('.', '_')
    caminho = f'static/imagens/graficos/pizza_{user_id}.png'
    os.makedirs('static/imagens/graficos', exist_ok=True)
    
    plt.savefig(caminho, transparent=True) # transparent=True ajuda a integrar no design
    plt.close()
    return f'imagens/graficos/pizza_{user_id}.png'