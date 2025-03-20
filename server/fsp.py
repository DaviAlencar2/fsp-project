import socket
import json
import os
import datetime
import csv
from tkinter import filedialog
from status.clientError import error_dict
from status.clienteOK import ok_dict

HOST_SRV = "192.168.0.5"
PORT_SRV = 8080
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def processar_mensagem(resposta):
    print(json.dumps(resposta, indent=4))


def send_msg(mensagem):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps(mensagem).encode())
            return json.loads(client_socket.recv(BUFFER_SIZE).decode())
    except (socket.error, json.JSONDecodeError):
        return {"stt": "err 60", "msg": error_dict.get(60, "Erro de conexão ou resposta inválida.")}


def executar_comando(comando, arquivo=None):
    mensagem = {"comando": comando}
    if arquivo:
        mensagem["arquivo"] = arquivo
    return send_msg(mensagem)


def list_files():
    resposta = executar_comando("LISTAR")
    processar_mensagem(resposta)


def send_file():
    file_name = filedialog.askopenfilename()
    if not os.path.isfile(file_name):
        processar_mensagem({"stt": "err 51", "msg": error_dict.get(51, "Arquivo não encontrado.")})
        return

    resposta = executar_comando("ENVIAR", os.path.basename(file_name))
    processar_mensagem(resposta)

    if not resposta["stt"].startswith("ok"):
        return

    try:
        with open(file_name, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            while chunk := file.read(BUFFER_SIZE):
                client_socket.sendall(chunk)
            client_socket.sendall(b"<EOF>")
        transfer_log(os.path.basename(file_name))
        processar_mensagem({"stt": "ok 61", "msg": ok_dict.get(61, "Arquivo enviado com sucesso.")})
    except socket.error:
        processar_mensagem({"stt": "err 60", "msg": error_dict.get(60, "Erro de conexão ao enviar arquivo.")})


def download_file():
    file_name = input("Nome do arquivo a ser baixado: ")
    resposta = executar_comando("BAIXAR", file_name)

    if not resposta["stt"].startswith("ok"):
        processar_mensagem(resposta)
        return

    caminho_salvo = os.path.join(DOWNLOAD_DIR, file_name)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket, open(caminho_salvo, "wb") as file:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps({"comando": "BAIXAR", "arquivo": file_name}).encode())

            while (data := client_socket.recv(BUFFER_SIZE)):
                if b"<EOF>" in data:
                    file.write(data.split(b"<EOF>")[0])
                    break
                file.write(data)

        processar_mensagem({"stt": "ok 62", "msg": ok_dict.get(62, "Arquivo baixado com sucesso.")})
    except socket.error:
        processar_mensagem({"stt": "err 60", "msg": error_dict.get(60, "Erro de conexão ao baixar arquivo.")})


def delete_file():
    file_name = input("Nome do arquivo a ser excluído: ")
    resposta = executar_comando("DELETAR", file_name)
    processar_mensagem(resposta)


def transfer_log(file_name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("client/log_transferencia.csv", mode="a", newline="") as f:
        csv.writer(f).writerow([file_name, now] if f.tell() != 0 else ["Nome do Arquivo:", "Data, Hora:"])


def main():
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
            break
        else:
            processar_mensagem({"stt": "err 99", "msg": "Opção inválida."})


if __name__ == "__main__":
    main()
