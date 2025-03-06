import socket
import threading
import signal
import sys
from server.fsp import processar_mensagem

HOST = "0.0.0.0"
PORT = 8080

servidor_ativo = True


def encerrar_servidor(sig, frame):
    """Manipulador para o sinal de Ctrl+C"""
    global servidor_ativo
    print("\nEncerrando o servidor...")
    servidor_ativo = False


def cliente_thread(client_socket, addr):
    print(f"Conexão recebida de {addr}")
    try:
        while True:
            mensagem = client_socket.recv(4096).decode()
            if not mensagem:
                break
            processar_mensagem(mensagem, client_socket)
    except Exception as e:
        print(f"Erro ao processar mensagem de {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Fim da conexão com {addr}")
        print()


def iniciar_servidor():
    signal.signal(signal.SIGINT, encerrar_servidor)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print("=== Servidor FSEP iniciado. ===")
        print(f"Servidor rodando em {HOST}:{PORT}")
        print("Pressione Ctrl+C para encerrar o servidor")
        print()
        
        server_socket.settimeout(1.0)
        
        while servidor_ativo:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=cliente_thread, args=(client_socket, addr)).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erro no servidor: {e}")
                break
        
        print("Servidor encerrado.")


if __name__ == "__main__":
    iniciar_servidor()