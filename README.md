# Boardgame API

Esta é uma API Flask para gerenciar boardgames e partidas, incluindo funcionalidades para adicionar, listar, pesquisar e excluir boardgames e partidas. A API também permite adicionar jogos diretamente da BoardGameGeek API.

## Para Usar sem Docker

1. Clone o repositório:
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Inicie a aplicação Flask:

    ```bash
    python app.py
    ```

​    A aplicação estará disponível em `http://localhost:5000`.

## Para Usar com Docker

1. Construa a imagem Docker:
    ```bash
    docker build -t boardgame-api .
    ```

2. Execute o container Docker:
    ```bash
    docker run -p 5000:5000 boardgame-api
    ```
   A aplicação estará disponível em `http://localhost:5000`.

## Endpoints

### Home
- **GET /**: Retorna a página principal.

### Adicionar Boardgame
- **POST /add_game**:
    - Parâmetros:
      - `nome` (string): Nome do Boardgame.
      - `playerage` (integer): Idade mínima sugerida.
      - `playtime` (integer): Tempo médio de uma partida (minutos).
      - `min_players` (integer): Número mínimo de jogadores.
      - `max_players` (integer): Número máximo de jogadores.
      - `ano_publi` (integer): Ano da publicação.
    - Respostas:
      - 200: Jogo adicionado com sucesso.
      - 400: Erro se alguma informação faltar ou alguma constraint for desrespeitada.

### Listar Boardgames
- **GET /list_all**: Retorna uma lista de todos os Boardgames.

### Excluir Boardgame
- **DELETE /boardgames/<int:id>**:
    - Parâmetros:
      - `id` (integer): ID do Boardgame para ser deletado.
    - Respostas:
      - 200: Boardgame deletado com sucesso.
      - 404: Boardgame não encontrado.

### Pesquisar Boardgame na BoardGameGeek API
- **GET /search_game**:
    - Parâmetros:
      - `name` (string): Nome do Boardgame para ser pesquisado.
    - Respostas:
      - 200: Retorna os resultados da pesquisa.
      - 400: Erro se o nome do jogo estiver faltando.
      - 500: Erro ao buscar dados na API BoardGameGeek.

### Adicionar Boardgame da BoardGameGeek API
- **POST /add_game_bgg**:
    - Parâmetros:
      - `id` (integer): ID do jogo na BoardGameGeek API.
    - Respostas:
      - 200: Jogo adicionado com sucesso.
      - 400: Erro se o ID do jogo estiver faltando.
      - 404: Jogo não encontrado.
      - 500: Erro ao buscar dados na API BoardGameGeek.

### Retornar todos os Boardgames
- **GET /get_boardgames**: Retorna todos os Boardgames para preencher o select para registrar partidas

### Registrar Partida
- **POST /register_match**:
    - Parâmetros:
      - `boardgame_id` (integer): ID do Boardgame.
      - `data_partida` (string): Data da partida no formato YYYY-MM-DD.
      - `vencedor` (string): Nome do vencedor da partida.
      - `jogador1` a `jogador10` (string): Nomes dos jogadores.
    - Respostas:
      - 200: Partida registrada com sucesso.
      - 400: Faltam informações obrigatórias ou a data é inválida.

### Listar Partidas
- **GET /list_matches**: Retorna uma lista de todas as partidas.

### Excluir Partida
- **DELETE /matches/<int:match_id>**:
    - Parâmetros:
      - `match_id` (integer): ID da partida para ser deletada.
    - Respostas:
      - 200: Partida deletada com sucesso.
      - 404: Partida não encontrada.
