import os
import json
import threading
from server.data_log import save_log
from server.utils import handle_duplicate_files,read_write_binary

DATA_FILES_DIR = os.path.join(os.path.dirname(__file__), "data/files")
arquivo_lock = threading.Lock()

def processar_mensagem(mensagem, client_socket):
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_FILES_DIR)
            resposta = {"status": "ok", "arquivos": arquivos}
        
        elif dados["comando"] == "ENVIAR": # usuario enviando arquivo ao servidor
            ... # Nova Lógica precisa ser implementada levando em consideração as novas caracteristicas do projeto.

        elif dados["comando"] == "BAIXAR":
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))
           
            try:
                with arquivo_lock:
                    if not os.path.exists(data_arquivo):
                        resposta = {"status":"erro", "mensagem":"Arquivo não encontrado."}
                    else:
                        resposta_inicial = {"status":"ok", "mensagem":"iniciando transferencia"}
                        client_socket.sendall(json.dumps(resposta_inicial).encode())

                        with open(data_arquivo,"rb") as file:
                            while True:
                                dados = file.read(4096)
                                if not dados:
                                    break
                                client_socket.sendall(dados)
                        save_log(nome_arquivo,client_socket)
                        resposta = {"status":"ok", "mensagem":"Arquivo enviado com sucesso."}
            except:
                resposta = {"status":"erro", "mensagem":"Erro ao enviar arquivo: {e}"}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}

    client_socket.sendall(json.dumps(resposta).encode())