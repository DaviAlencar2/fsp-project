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
        
def list_files():
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
        with open(file_name, "r") as file:
            content =  file.read()

    resposta = send_msg({
        "comando": "ENVIAR",
        "arquivo": os.path.basename(file_name),
        "conteudo": content
    })
    print(resposta["mensagem"])

def download_file():
    file_name = input("NOME DO ARQUIVO A SER BAIXADO: ")
    resposta =  send_msg({
        "comando": "BAIXAR",
        "arquivo": file_name
    })
    if resposta["status"] == "ok":
        caminho_salvo = os.path.join("downloads", file_name)
        os.makedirs("downloads", exist_ok=True)

        with open(caminho_salvo, "w") as file:
            file.write(resposta.get("conteudo", ""))

        print(f"ARQUIVO SALVO NO: {caminho_salvo}")
    else:
        print("ERROR:", resposta["mensagem"])