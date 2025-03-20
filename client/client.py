import socket
import json
import os
import sys
import time
from tkinter import filedialog
from status.protocolError import error_dict
from status.protocolOk import ok_dict


HOST_SRV = sys.argv[1]
PORT_SRV = int(sys.argv[2]) # Porta Padrão esperada: 8080
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def display_status_msg(resposta):
    if "stt" in resposta:
        try:
            codigo = resposta["stt"].split()[1]  
            # Converter para inteiro para garantir compatibilidade com os dicionários
            codigo = int(codigo) if codigo.isdigit() else 22
        except (IndexError, ValueError):
            codigo = 22  # formato não é algo como "ok xx" ou "err xx"
    else:
        codigo = 22  # não tiver stt

    if resposta["stt"].startswith("ok"):
        mensagem = ok_dict.get(codigo, "Operação realizada com sucesso.")
        print(f"ok {codigo}: {mensagem}") 
    else:
        mensagem = error_dict.get(codigo, "Erro desconhecido.")
        print(f"err {codigo}: {mensagem}")

def download_file():
    file_name = input("Nome do arquivo a ser baixado: ")
    
    try:
        # Adaptar handle_duplicate_files para o cliente
        nm, ext = os.path.splitext(file_name)
        nome_local = f"{nm}{ext}"
        contador = 1
        
        while os.path.exists(os.path.join(DOWNLOAD_DIR, nome_local)):
            nome_local = f"{nm}({contador}){ext}"
            contador += 1
            
        caminho_salvo = os.path.join(DOWNLOAD_DIR, nome_local)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps({"comando": "BAIXAR", "arquivo": file_name}).encode())
            
            resposta_inicial = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            if not resposta_inicial["stt"].startswith("ok"):
                display_status_msg(resposta_inicial)
                return
            
            print(f"Baixando arquivo '{file_name}'...")
            
            eof_encontrado = False
            with open(caminho_salvo, "wb") as file:
                while not eof_encontrado and (data := client_socket.recv(BUFFER_SIZE)):
                    if b"<EOF>" in data:
                        partes = data.split(b"<EOF>", 1)
                        file.write(partes[0])
                        eof_encontrado = True
                        break
                    file.write(data)
            
            if eof_encontrado:
                try:
                    # Definir um timeout para evitar bloqueio permanente
                    client_socket.settimeout(2.0)
                    resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
                    if resposta_final["stt"].startswith("ok"):
                        print(f"Arquivo salvo como: {nome_local}")
                    display_status_msg(resposta_final)
                except socket.timeout:
                    print(f"Arquivo baixado e salvo como: {nome_local}")
                except json.JSONDecodeError:
                    print(f"Erro ao processar resposta do servidor")
            else:
                print("Erro: marcador de fim de arquivo não encontrado")
                
    except ConnectionRefusedError:
        print(f"Erro: Não foi possível conectar ao servidor {HOST_SRV}:{PORT_SRV}")
    except PermissionError:
        print(f"Erro: Sem permissão para salvar o arquivo")
    except Exception as e:
        print(f"err 12: {error_dict[12]}")
        print(f"Detalhes: {str(e)}")
        
                
def send_msg(mensagem):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST_SRV, PORT_SRV))
        client_socket.sendall(json.dumps(mensagem).encode())
        try:
            return json.loads(client_socket.recv(BUFFER_SIZE).decode())
        except json.JSONDecodeError:
            return {"stt": "err 22", "msg": error_dict[22]}
        except Exception as e:
            return {"stt": "err 56", "msg": error_dict[56]}
        

def list_files():
    resposta = send_msg({"comando": "LISTAR"})
    if resposta["stt"].startswith("ok"):
        print("\nARQUIVOS NO SERVIDOR:")
        for file in resposta.get("files", []):
            print(f" - {file}")
    display_status_msg(resposta)


def send_file():
    """Envia um arquivo para o servidor com tratamento de duplicação"""
    file_path = filedialog.askopenfilename()
    if not file_path:  # Usuário cancelou a seleção
        print("Operação de envio cancelada.")
        return
        
    if not os.path.exists(file_path):
        print(f"err 53: {error_dict[53]}")  # arquivo não encontrado localmente
        return

    try:
        # Primeiro verifica se o arquivo já existe no servidor
        nome_arquivo = os.path.basename(file_path)
        resposta_listar = send_msg({"comando": "LISTAR"})
        
        if resposta_listar["stt"].startswith("ok") and "files" in resposta_listar:
            arquivos_servidor = resposta_listar.get("files", [])
            if nome_arquivo in arquivos_servidor:
                # Arquivo com mesmo nome já existe
                print(f"Arquivo '{nome_arquivo}' já existe no servidor.")
                print("O servidor vai gerar um nome único para este arquivo.")
        
        with open(file_path, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps({"comando": "ENVIAR", "arquivo": nome_arquivo}).encode())
            
            # Receber resposta inicial do servidor
            resposta_inicial = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            if not resposta_inicial["stt"].startswith("ok"):
                display_status_msg(resposta_inicial)
                return
            
            # Enviar conteúdo do arquivo com barra de progresso
            print(f"Enviando arquivo '{nome_arquivo}'...")
            tamanho_arquivo = os.path.getsize(file_path)
            enviado_total = 0
            
            while chunk := file.read(BUFFER_SIZE):
                client_socket.sendall(chunk)
                enviado_total += len(chunk)
                progresso = (enviado_total / tamanho_arquivo) * 100
                print(f"\rProgresso: {progresso:.1f}%", end="")
                
            client_socket.sendall(b"<EOF>")
            print()  # Nova linha após a barra de progresso
            
            # Receber resposta final
            resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            
            # Extrair o nome que o servidor usou para o arquivo (se foi alterado)
            if "arquivo" in resposta_final:
                nome_salvo = resposta_final["arquivo"]
                print(f"Arquivo salvo no servidor como: {nome_salvo}")
            
            display_status_msg(resposta_final)
    
    except ConnectionRefusedError:
        print(f"err 51: {error_dict[51]}")
    except PermissionError:
        print(f"err 52: {error_dict[52]}")
    except Exception as e:
        print(f"err 11: {error_dict[11]}")
        print(f"Detalhes: {str(e)}")

        
def delete_file():
    try:
        file_name = input("Nome do arquivo a ser excluído: ")
        resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
        display_status_msg(resposta)
    except ConnectionRefusedError:
        print(f"err 51: {error_dict[51]}")
    except PermissionError:
        print(f"err 52: {error_dict[52]}")
    except Exception as e:
        print(f"err 13: {error_dict[13]}")
        print(f"Detalhes: {str(e)}")


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


