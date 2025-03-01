import socket
import threading
from fsep import processar_mensagem

HOST = "127.0.0.1"
PORT = 8080

def cliente_thread(client_socket, addr):
    print(f"Conexão recebida de {addr}")
    try:
        while True:
            mensagem = client_socket.recv(4096).decode()
            if not mensagem:
                break
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