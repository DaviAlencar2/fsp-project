import socket; import json; import os; import datetime; import csv
from tkinter import filedialog


HOST_SRV = "192.168.0.6" #meu notebook linux
PORT_SRV = 8080
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True) # checando se o diretorio ja existe


def send_msg(mensagem):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))  
        client_socket.sendall(json.dumps(mensagem).encode())  
        try:
            resposta = client_socket.recv(BUFFER_SIZE).decode()
            return json.loads(resposta)
        except json.JSONDecodeError:
            return {"status": "erro", "mensagem": "Resposta inválida do servidor."}


def list_files():
    resposta = send_msg({"comando": "LISTAR"})
    if resposta["status"] == "ok":
        print("\nARQUIVOS NO SERVIDOR:")
        for file in resposta["arquivos"]:
            print(f" - {file}")
    else:
        print("ERRO:", resposta["mensagem"])


def send_file():
    file_name = filedialog.askopenfilename()
    if not os.path.exists(file_name):
        print("ERRO: ARQUIVO NÃO ENCONTRADO!")
        return
    
    with open(file_name, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))
        client_socket.sendall(json.dumps({"comando": "ENVIAR", "arquivo": os.path.basename(file_name)}).encode())
        
        resposta = client_socket.recv(BUFFER_SIZE).decode()
        resposta_json = json.loads(resposta)
        if resposta_json.get("status") != "ok":
            print("ERRO:", resposta_json.get("mensagem"))
            return
        
        while chunk := file.read(BUFFER_SIZE):
            client_socket.sendall(chunk)
        client_socket.sendall(b"<EOF>")
        
        resposta_final = client_socket.recv(BUFFER_SIZE).decode()
        print(json.loads(resposta_final).get("mensagem", "Erro desconhecido."))
        if resposta["status"] == "ok": # tentativa de solucionar erro do log (se a operação tiver ok)
            transfer_log(os.path.basename(file_name))transfer_log(os.path.basename(file_name)) # colocando log


def download_file():
    file_name = input("Nome do arquivo a ser baixado: ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))  
        client_socket.sendall(json.dumps({"comando": "BAIXAR", "arquivo": file_name}).encode())
        
        metadado = json.loads(client_socket.recv(BUFFER_SIZE).decode())
        if metadado.get("status") != "ok":
            print("ERRO:", metadado.get("mensagem"))
            return
        
        caminho_salvo = os.path.join(DOWNLOAD_DIR, file_name)
        
        with open(caminho_salvo, "wb") as file:
            # b"" em python == str no formato bytes
            dado_total = b""
            while True:
                dado = client_socket.recv(BUFFER_SIZE)
                if not dado or b"<EOF>" in dado:
                    dado_total += dado.split(b"<EOF>")[0]  # Garante que o EOF não fique no arquivo
                    break
                dado_total += dado
            file.write(dado_total)
        
        print(f"Arquivo baixado com sucesso em {caminho_salvo}!")


def delete_file():
    file_name = input("Nome do arquivo a ser excluído: ")
    resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
    print(resposta["mensagem"])
    if resposta["status"] == "ok": # tentativa de solucionar erro do log
            transfer_log(os.path.basename(file_name))


def transfer_log(file_name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dados = [file_name, now]
    with open("client/log_transferencia.csv", mode="a", newline="") as f:
        escritor = csv.writer(f)
        if f.tell() == 0:
                escritor.writerow(["Nome do Arquivo:", "Data, Hora:"])
        escritor.writerow(log_dados)


def main():
    print("==== Cliente FSEP ====")
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
            print("Opção inválida!")


if __name__ == "__main__":
    main()
