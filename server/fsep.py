#ToDo: Implementar Exceções para os casos de erro.
#Considerar criar um novo campo: AUTOR.
#ToDo: procurar alternativas para importação de módulos.

import os
import json
import threading
from client.client import DOWNLOAD_DIR
from server.data_log import save_log

DATA_DIR = os.path.join(os.path.dirname(__file__), "data/files")
arquivo_lock = threading.Lock()

def processar_mensagem(mensagem, client_socket):
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_DIR)
            resposta = {"status": "ok", "arquivos": arquivos}
        
        elif dados["comando"] == "ENVIAR":
            nome_arquivo = dados["arquivo"]
            caminho_arquivo = os.path.join(DATA_DIR, os.path.basename(nome_arquivo))
            conteudo = dados["conteudo"]
            try:
                with arquivo_lock:
                    with open(caminho_arquivo, "w") as f:
                        f.write(conteudo)
                    resposta = {"status": "ok", "mensagem": f"Arquivo '{nome_arquivo}' salvo no servidor."}
                    save_log(nome_arquivo,client_socket)
            except FileExistsError:
                resposta = {"status": "erro", "mensagem": "Arquivo já existe."}

        elif dados["comando"] == "BAIXAR":
            nome_arquivo = dados["arquivo"]
            caminho_arquivo = os.path.join(DATA_DIR, os.path.basename(nome_arquivo))
            caminho_cliente = os.path.join(DOWNLOAD_DIR, os.path.basename(nome_arquivo))
            try:
                with arquivo_lock:
                    with open(caminho_arquivo, "rb") as src, open(caminho_cliente, "wb") as dst:
                        while True:
                            bloco = src.read(4096)
                            if not bloco:
                                break
                            dst.write(bloco)
                    resposta = {"status": "ok", "mensagem": f"Arquivo '{nome_arquivo}' baixado com sucesso."}
            except FileNotFoundError:
                resposta = {"status": "erro", "mensagem": "Arquivo não encontrado."}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}

    # client_socket.sendall(json.dumps(resposta).encode()) #Comentar em caso de TESTES RÁPIDOS onde o cliente não é necessário.
    print(resposta)

# Testes rápidos
if __name__ == "__main__":
    print(os.listdir(DATA_DIR))

    processar_mensagem('{"comando": "BAIXAR", "arquivo": "test_image.jpg"}', None)