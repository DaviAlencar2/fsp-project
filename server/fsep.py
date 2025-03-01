import os
import json
import threading
import time
from server.data_log import save_log


DATA_FILES_DIR = os.path.join(os.path.dirname(__file__), "data/files")
arquivo_lock = threading.Lock()

def processar_mensagem(mensagem, client_socket):
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_FILES_DIR)
            resposta = {"status": "ok", "arquivos": arquivos}
        
        elif dados["comando"] == "ENVIAR": # usuario enviando arquivo ao servidor
            ... 

        elif dados["comando"] == "DELETAR": # usuario deletando arquivo do servidor
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))

            try:
                with arquivo_lock:
                    if not os.path.exists(data_arquivo):
                        resposta = {"status":"erro", "mensagem":"Arquivo não encontrado."}
                    else:
                        os.remove(data_arquivo)
                        resposta = {"status":"ok", "mensagem":"Arquivo deletado com sucesso."}
            except:
                resposta = {"status":"erro", "mensagem":"Erro ao deletar arquivo."}


        elif dados["comando"] == "BAIXAR": # usuario baixando arquivo do servidor
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))
            try:
                with arquivo_lock:
                    if not os.path.exists(data_arquivo):
                        resposta = {"status":"erro", "mensagem":"Arquivo não encontrado."}

                    else:
                        resposta_inicial = {"status":"ok", "mensagem":"iniciando transferencia"}
                        client_socket.sendall(json.dumps(resposta_inicial).encode())

                        time.sleep(0.2)

                        with open(data_arquivo,"rb") as file:
                            while True:
                                dados = file.read(4096)
                                if not dados:
                                    break
                                client_socket.sendall(dados)
                        client_socket.sendall(b"<EOF>")
                return
            except:
                resposta = {"status":"erro", "mensagem":"Erro ao enviar arquivo"}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}

    client_socket.sendall(json.dumps(resposta).encode())