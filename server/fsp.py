import os
import json
import threading
import time
import sys
from server.utils import handle_duplicate_files
from status.protocolError import error_dict
from status.protocolOk import ok_dict


HOST = sys.argv[1]
PORT = int(sys.argv[2])

DATA_FILES_DIR = os.path.join(os.path.dirname(__file__), "data/files")
os.makedirs(DATA_FILES_DIR, exist_ok=True)
BUFFER_SIZE = 4096
arquivo_lock = threading.Lock()


def processar_mensagem(mensagem:json, client_socket):
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_FILES_DIR)
            if len(arquivos) == 0:
                resposta = {"stt" : "ok 47", "msg" : ok_dict[47]}
            else:
                resposta = {"stt" : "ok 45", "msg" : ok_dict[45], "files": arquivos}
        
        elif dados["comando"] == "ENVIAR": # Usuario enviando arquivo ao servidor.
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))

            try:
                with arquivo_lock:
                    if os.path.exists(data_arquivo):
                        novo_nome = handle_duplicate_files(nome_arquivo,DATA_FILES_DIR)
                        data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(novo_nome))
                        
                    resposta_inicial = {"stt" : "ok 40", "msg" : ok_dict[40]}
                    client_socket.sendall(json.dumps(resposta_inicial).encode())
                    tamanho_arquivo = dados.get("tamanho", 0)

                    if tamanho_arquivo > 0:
                        with open(data_arquivo,"wb") as arquivo:
                            bytes_recebidos = 0

                            while bytes_recebidos < tamanho_arquivo:
                                dados = client_socket.recv(BUFFER_SIZE)

                                if not dados or bytes_recebidos == tamanho_arquivo:
                                    break

                                arquivo.write(dados)
                                bytes_recebidos += len(dados)

                              
                    resposta_final = {"stt" : "ok 41", "msg" : ok_dict[41],"name":os.path.basename(data_arquivo)}
                    client_socket.sendall(json.dumps(resposta_final).encode())

                    return
                
            except:
                resposta = {"stt" : "err 11", "msg" : error_dict[11]}


        elif dados["comando"] == "DELETAR": # Usuario deletando arquivo do servidor.
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))

            try:
                with arquivo_lock:
                    if not os.path.exists(data_arquivo):
                        resposta = {"stt" : "err 14", "msg" : error_dict[14]}
                    else:
                        os.remove(data_arquivo)
                        resposta = {"stt" : "ok 43", "msg" : ok_dict[43]}
            except:
                resposta = {"stt" : "err 13", "msg" : error_dict[13]}


        elif dados["comando"] == "BAIXAR": # usuario baixando arquivo do servidor.
            nome_arquivo = dados["arquivo"]
            data_arquivo = os.path.join(DATA_FILES_DIR, os.path.basename(nome_arquivo))
            

            try:
                with arquivo_lock:
                    if not os.path.exists(data_arquivo):
                        resposta = {"stt" : "err 14", "msg" : error_dict[14]}
                        client_socket.sendall(json.dumps(resposta).encode())
                        return

                    else:
                        tamanho_arquivo = os.path.getsize(data_arquivo)
                        resposta_inicial = {"stt" : "ok 44", "msg" : ok_dict[44],"size":tamanho_arquivo}
                        client_socket.sendall(json.dumps(resposta_inicial).encode())

                        time.sleep(0.2)

                        bytes_enviados = 0
                        with open(data_arquivo,"rb") as file:
                            while bytes_enviados < tamanho_arquivo:
                                dados = file.read(4096)
                                if not dados or bytes_enviados == tamanho_arquivo:
                                    break
                                client_socket.sendall(dados)
                                bytes_enviados += len(dados)

                        resposta_final = {"stt" : "ok 46", "msg" : ok_dict[46]}
                        client_socket.sendall(json.dumps(resposta_final).encode())

                        return
            
            except:
                resposta = {"stt" : "err 12", "msg" : error_dict[12]}

        else:
            resposta = {"stt" : "err 21", "msg" : error_dict[21]}

    except json.JSONDecodeError:
        resposta = {"stt" : "err 22", "msg" : error_dict[22]}

    client_socket.sendall(json.dumps(resposta).encode())