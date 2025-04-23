# Documentação do Projeto

## Descrição do Projeto
Este projeto configura um contêiner Docker que executa dois serviços simultaneamente:

- **Flask**: Backend para processar dados, utilizando SQLite como banco de dados.
- **Streamlit**: Frontend para criar uma interface de usuário interativa.

## Requisitos
- **Docker**: Certifique-se de ter o Docker instalado (Docker Desktop no Windows).
- **Python**: Utilizado na imagem base do Docker.
- **Bibliotecas Python**: Listadas no arquivo `requerimentos.txt`. Essas dependências serão instaladas automaticamente ao iniciar o contêiner.

## Geração da imagem e contêiner
- docker build -t quest04redes2 .
- docker run --name quest04redes2 -p 5000:5000 -p 8501:8501 quest04redes2

## Serviços e Portas
- **Flask (Backend)**: Acesse em (http://localhost:5000/devices).
- **Streamlit (Frontend)**: Acesse em (http://localhost:8501).

## Observações
- O banco de dados SQLite será criado automaticamente caso não exista ao iniciar o contêiner.
- O script `start.sh` garante a execução simultânea do Flask e do Streamlit no mesmo contêiner.

---