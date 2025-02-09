'''
O servidor espera que o cliente envie uma mensagem em formato JSON com o seguinte formato:
{"comando": "COMANDO", "arquivo": "NOME_ARQUIVO", "conteudo": "CONTEUDO"}.

Onde: COMANDO é uma string que pode ser "LISTAR", "ENVIAR" ou "BAIXAR";
NOME_ARQUIVO é o nome do arquivo que será manipulado;
e CONTEUDO é o conteúdo do arquivo que será enviado ao servidor(usado apenas no comando "ENVIAR").
'''

import os
import json
import socket
import threading

HOST = "127.0.0.1"
PORT = 8080
DATA_DIR = "data/"

def processar_mensagem(mensagem, client_socket): # Considerar colocar essa função em um arquivo separado chamdo fsep.py.
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_DIR)
            resposta = {"status": "ok", "arquivos": arquivos}
        
        elif dados["comando"] == "ENVIAR":
            nome_arquivo = dados["arquivo"]
            caminho_arquivo = os.path.join(DATA_DIR, os.path.basename(nome_arquivo))
            conteudo = dados["conteudo"]
            with open(caminho_arquivo, "w") as f:
                f.write(conteudo)
            resposta = {"status": "ok", "mensagem": f"Arquivo '{nome_arquivo}' salvo no servidor."}
        
        elif dados["comando"] == "BAIXAR":
            nome_arquivo = dados["arquivo"]
            try:
                with open(caminho_arquivo, "r") as f:
                    conteudo = f.read()
                resposta = {"status": "ok", "conteudo": conteudo}
            except FileNotFoundError:
                resposta = {"status": "erro", "mensagem": "Arquivo não encontrado."}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}

    client_socket.sendall(json.dumps(resposta).encode())

def cliente_thread(client_socket, addr):
    print(f"Conexão recebida de {addr}")
    try:
        mensagem = client_socket.recv(4096).decode()
        processar_mensagem(mensagem,client_socket)
    except Exception as e:
        print(f"Erro ao processar mensagem de {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Fim da conexão com {addr}")

def iniciar_servidor():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Servidor rodando em {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=cliente_thread, args=(client_socket, addr)).start()

if __name__ == "__main__":
    iniciar_servidor()