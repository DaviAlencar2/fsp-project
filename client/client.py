import socket
import json
import os


HOST_SRV = "127.0.0.1"
PORT_SRV = 8080
# BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")



def send_msg(mensagem):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))  
        client_socket.sendall(json.dumps(mensagem).encode())  
        try:
            resposta = client_socket.recv(4096).decode()  
            return json.loads(resposta)
        except json.JSONDecodeError:
            return {"status": "ERROR", "mensagem": "RESPOSTA INVÁLIDA DO SERVIDOR"}
        
def list_files(): # não precisa fazer a conexao com o servidor
    resposta  = send_msg({"comando": "LISTAR"})
    if resposta["status"] == "ok":
        print("\nARQUIVOS NO SERVIDOR:")
        for file in resposta["arquivos"]:
            print(f" - {file}")
    else:
        print("ERROR", resposta["mensagem"])
    
def send_file():
    file_name = input("DIGITE O CAMINHO DO ARQUIVO A SER ENVIADO: ")
    if not os.path.exists(file_name):
        print("ERROR: ARQUIVO NÃO ENCONTRADO!")
        return
    
    else:
       with open(file_name, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))

        client_socket.sendall(json.dumps({
                "comando": "ENVIAR",
                "arquivo": os.path.basename(file_name)
            }).encode())
        
        client_socket.recv(1024)
        while dado := file.read(4069):
            client_socket.sendall(dado)

        print("ARQUIVO ENVIADO COM SUCESSO!")

def download_file():
    file_name = input("NOME DO ARQUIVO A SER BAIXADO: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV)) # estabelece a conexao cliente c o serv
    # enviando a solicitacao de baixar o arquivo  
    client_socket.sendall(json.dumps({
            "comando": "BAIXAR",
            "arquivo": file_name
        }).encode())
    # recebendo o metadata
    metadado = json.loads(client_socket.recv(1024).decode())
    if metadado.get("status") != "ok":
            return print("ERROR:", metadado.get("mensagem"))
    # se n n tiver pasta para salvar o arquivo cria a pasta
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    caminho_salvo = os.path.join(DOWNLOAD_DIR, file_name)
    # recebendo o arquivo
    with open(caminho_salvo, "wb") as file:
            while dado := client_socket.recv(4069):
                file.write(dado)
    
    print(f"ARQUIVO BAIXADO COM SUCESSO EM {caminho_salvo}!")

def delete_file():
    file_name = input("NOME DO ARQUIVO A SER EXCLUIDO: ")
    resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
    print(resposta["mensagem"])
