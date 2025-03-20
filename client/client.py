import socket
import json
import os
import sys
from tkinter import filedialog
from status.protocolError import error_dict
from status.protocolOk import ok_dict


HOST_SRV = sys.argv[1]
PORT_SRV = sys.argv[2]
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def processar_mensagem(resposta):
    codigo = int(resposta.get("stt", "err 22").split()[1]) if "stt" in resposta else 22 # erro desconhecido
    if resposta["stt"].startswith("ok"):
        print (f"ok {codigo}: {ok_dict.get(codigo, 'Mensagem de sucesso desconhecida')}")
    else:
        print (f"err {codigo}: {error_dict.get(codigo, 'Erro desconhecido')}")


def send_msg(mensagem):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))
        client_socket.sendall(json.dumps(mensagem).encode())
        try:
            return json.loads(client_socket.recv(BUFFER_SIZE).decode())
        except json.JSONDecodeError:
            return {"stt": "err 22", "msg": error_dict[22]}  # resposta inválida do servidor


def list_files():
    resposta = send_msg({"comando": "LISTAR"})
    if resposta["stt"].startswith("ok"):
        print("\nARQUIVOS NO SERVIDOR:")
        for file in resposta.get("files", []):
            print(f" - {file}")
    processar_mensagem(resposta)


def send_file():
    file_name = filedialog.askopenfilename()
    if not os.path.exists(file_name):
        print(f"err 14: {error_dict[14]}")  # arquivo não encontrado
        return

    with open(file_name, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))
        client_socket.sendall(json.dumps({"comando": "ENVIAR", "arquivo": os.path.basename(file_name)}).encode())

        # if not send_msg({"comando": "ENVIAR", "arquivo": os.path.basename(file_name)})["stt"].startswith("ok"):
        #     print(f"err 55: {error_dict[55]}")  # erro desconhecido
        #     return

        while chunk := file.read(BUFFER_SIZE):
            client_socket.sendall(chunk)
        client_socket.sendall(b"<EOF>")

        processar_mensagem(json.loads(client_socket.recv(BUFFER_SIZE).decode()))


def download_file():
    file_name = input("Nome do arquivo a ser baixado: ")
    resposta = send_msg({"comando": "BAIXAR", "arquivo": file_name})

    if not resposta["stt"].startswith("ok"):
        processar_mensagem(resposta)
        return

    caminho_salvo = os.path.join(DOWNLOAD_DIR, file_name)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket, open(caminho_salvo, "wb") as file:
        client_socket.connect((HOST_SRV, PORT_SRV))
        client_socket.sendall(json.dumps({"comando": "BAIXAR", "arquivo": file_name}).encode())

        while (data := client_socket.recv(BUFFER_SIZE)):
            if b"<EOF>" in data:
                file.write(data.split(b"<EOF>")[0])
                break
            file.write(data)

    print(f"ok 46: {ok_dict[46]}")  # Arquivo baixado com sucesso


def delete_file():
    file_name = input("Nome do arquivo a ser excluído: ")
    resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
    processar_mensagem(resposta)

def main():
    print("==== Cliente FSP ====")
    while True:
        print("\nEscolha uma opção:")
        print("1 - Listar arquivos")
        print("2 - Enviar arquivo")
        print("3 - Baixar arquivo")
        print("4 - Excluir arquivo")
        print("0 - Sair")
        
        opcao = input("Opção: ")
        
        if opcao == "1":
            list_files()
        elif opcao == "2":
            send_file()
        elif opcao == "3":
            download_file()
        elif opcao == "4":
            delete_file()
        elif opcao == "0":
            print("Encerrando cliente...")
            break
        else:
            print("err 21: " + error_dict[21])  # comando inválido


if __name__ == "__main__":
    main()


