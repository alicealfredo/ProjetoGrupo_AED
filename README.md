# Gerenciador de Imagens

## Sobre o Projeto

O **Gerenciador de Imagens** é uma plataforma digital desenvolvida para a gestão e análise de imagens. O sistema permite a organização, pesquisa e visualização de conteúdos visuais categorizados, oferecendo uma experiência personalizada tanto para utilizadores comuns quanto para administradores.

Este projeto foi desenvolvido para a disciplina de **Algoritmia e Estrutura de Dados (TSIW)** pelos autores Clara Mota, Alice Alfredo e Henrique Oliveira.

## Funcionalidades

### Utilizador Comum

* **Página Inicial:** Feed de imagens com funcionalidade de pesquisa (filtro por descrição, autor ou local) baseada em arquivos CSV.
* **Categorias:** Organização dinâmica de imagens por temas (Natureza, Arquitetura, Pessoas, etc.), com contagem automática de itens por categoria.
* **Galeria Privada (Favoritos):** Cada utilizador possui um ficheiro CSV individual para salvar a sua coleção privada de imagens.
* **Dashboard do Utilizador:** Visualização de estatísticas dinâmicas através de gráficos de barras e de ranking, além de gestão de uploads e interesses.

### Administrador

* **Gestão de Utilizadores:** Visualização e controlo dos utilizadores registados na plataforma.
* **Moderação de Conteúdo:** Ferramentas para remover ou gerir as imagens publicadas no sistema.
* **Estatísticas Globais:** Acesso ao total de utilizadores e fotos em todo o sistema.

## Tecnologias Utilizadas

* **Linguagem:** Python 
* **Framework Web:** Flask 
* **Frontend:** HTML5 e CSS3 
* **Visualização de Dados:** Matplotlib 
* **Armazenamento:**
  * Ficheiros binários (`.bin`) para dados de utilizadores.
  * Ficheiros CSV para dados de imagens e favoritos.

## Segurança e Autenticação
* **Diferenciação de Papéis:** O sistema distingue administradores (`admin@gmail.com`) de utilizadores comuns, redirecionando-os para painéis específicos.
* **Gestão de Sessão:** Utiliza o mecanismo de `session` do Flask para manter a autenticação durante a navegação.
* **Persistência:** No login, o sistema percorre e descodifica o ficheiro binário para validar as credenciais.

## Estrutura do Projeto
A organização de pastas segue o padrão Flask:
* `/static`: Arquivos CSS (estilos externos específicos para cada página) e recursos visuais (ícones/gráficos).
* `/templates`: Arquivos HTML das páginas (index, login, dashboard, etc...).
* `/data`: Base de dados em formatos CSV e BIN.
* `app.py`: Arquivo principal da aplicação.
* `graficos.py`: Responsável pela geração dos gráficos visuais.

**Autores:** Clara Mota, Alice Alfredo e Henrique Oliveira
