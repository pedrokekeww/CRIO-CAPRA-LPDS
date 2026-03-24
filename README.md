# CRIO-CAPRA-LPDS
#LPDS project

##Passos para rodar o projeto:

1 - Instale o Python 3.10 e o Git
(Se for Linux - Ubuntu/Debian): O OpenCV (cv2) exige algumas bibliotecas de sistema para processar imagens. Rode no terminal do servidor:

`sudo apt update`
`sudo apt install python3 python3-venv python3-pip git -y`
`sudo apt install libgl1 libglib2.0-0 -y`

2 - Clone o repositório.

3 - Criar e Ativar o Ambiente Virtual(venv):

# Criar a pasta do venv
`python -m venv venv`

# Ativar o venv (No Linux):
`source venv/bin/activate`

# Ativar o venv (No Windows):
`venv\Scripts\activate`

4 - Instalar as Bibliotecas do Python

Com o venv ativado, instale todas as dependências que estão no arquivo (FastAPI, Uvicorn, SQLAlchemy, OpenCV, Supervision, etc.):

`pip install -r requirements.txt`

5 - Iniciar o Servidor
Para ligar a aplicação, rode o comando:

`uvicorn main:app --host 0.0.0.0 --port 8000`
