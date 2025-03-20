import socket
import json
import os
import sys
import time
from tkinter import filedialog
from status.protocolError import error_dict
from status.protocolOk import ok_dict


# Constantes para cores (compatível com a maioria dos terminais)
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
AZUL = "\033[94m"
RESET = "\033[0m"
NEGRITO = "\033[1m"


HOST_SRV = sys.argv[1]
PORT_SRV = int(sys.argv[2])  # Porta Padrão esperada: 8080
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_message(tipo, codigo, mensagem_personalizada=None):
    """Exibe mensagens padronizadas com cores"""
    if tipo == "ok":
        mensagem = ok_dict.get(codigo, "Operação realizada com sucesso")
        if mensagem_personalizada:
            print(f"{VERDE}✓ {mensagem_personalizada}{RESET}")
        else:
            print(f"{VERDE}ok {codigo}: {mensagem}{RESET}")
    else:  # tipo == "err"
        mensagem = error_dict.get(codigo, "Erro desconhecido")
        if mensagem_personalizada:
            print(f"{VERMELHO}✗ {mensagem_personalizada}{RESET}")
        else:
            print(f"{VERMELHO}err {codigo}: {mensagem}{RESET}")


def display_status_msg(resposta):
    """Processa e exibe mensagens de status do servidor"""
    if "stt" in resposta:
        try:
            partes = resposta["stt"].split()
            tipo = partes[0]  # "ok" ou "err"
            codigo = int(partes[1]) if partes[1].isdigit() else 22
        except (IndexError, ValueError):
            tipo = "err"
            codigo = 22  # formato não é algo como "ok xx" ou "err xx"
    else:
        tipo = "err"
        codigo = 22  # resposta não tem campo 'stt'

    display_message(tipo, codigo)


def download_file():
    """Baixa um arquivo do servidor"""
    limpar_tela()
    print(f"{NEGRITO}{AZUL}=== DOWNLOAD DE ARQUIVO ==={RESET}\n")
    
    # Primeiro lista arquivos disponíveis
    resposta = send_msg({"comando": "LISTAR"})
    if resposta["stt"].startswith("ok") and "files" in resposta and resposta["files"]:
        print(f"{AZUL}Arquivos disponíveis:{RESET}")
        for i, file in enumerate(resposta["files"], 1):
            print(f"{AZUL}{i}.{RESET} {file}")
        print()
    
    file_name = input(f"{AMARELO}Nome do arquivo a ser baixado:{RESET} ")
    if not file_name:
        display_message("err", 50)  # Operação cancelada pelo usuário
        return
    
    try:
        # Tratamento para nomes duplicados
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
            
            print(f"{AMARELO}Baixando arquivo '{file_name}'...{RESET}")
            
            eof_encontrado = False
            with open(caminho_salvo, "wb") as file:
                bytes_recebidos = 0
                while not eof_encontrado and (data := client_socket.recv(BUFFER_SIZE)):
                    if b"<EOF>" in data:
                        partes = data.split(b"<EOF>", 1)
                        file.write(partes[0])
                        bytes_recebidos += len(partes[0])
                        print(f"\r{AMARELO}Progresso: {bytes_recebidos} bytes{RESET}", end="")
                        eof_encontrado = True
                        break
                    file.write(data)
                    bytes_recebidos += len(data)
                    print(f"\r{AMARELO}Progresso: {bytes_recebidos} bytes{RESET}", end="")
            
            print()  # Nova linha depois da barra de progresso
            
            if eof_encontrado:
                try:
                    client_socket.settimeout(2.0)
                    resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
                    if resposta_final["stt"].startswith("ok"):
                        display_message("ok", 46, f"Arquivo salvo como: {nome_local}")
                    else:
                        display_status_msg(resposta_final)
                except socket.timeout:
                    display_message("ok", 46, f"Arquivo baixado e salvo como: {nome_local}")
                except json.JSONDecodeError:
                    display_message("err", 56)  # Resposta inválida do servidor
            else:
                display_message("err", 57)  # Marcador de fim de arquivo não encontrado
                
    except ConnectionRefusedError:
        display_message("err", 51, f"Não foi possível conectar ao servidor {HOST_SRV}:{PORT_SRV}")
    except PermissionError:
        display_message("err", 52)  # Sem permissão para acessar o arquivo
    except Exception as e:
        display_message("err", 12, f"Detalhes: {str(e)}")
    
    input(f"\n{AMARELO}Pressione ENTER para continuar...{RESET}")


def send_msg(mensagem):
    """Envia uma mensagem para o servidor e retorna a resposta"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps(mensagem).encode())
            try:
                return json.loads(client_socket.recv(BUFFER_SIZE).decode())
            except json.JSONDecodeError:
                return {"stt": "err 56"}  # Resposta inválida do servidor
    except ConnectionRefusedError:
        return {"stt": "err 51"}  # Não foi possível conectar ao servidor
    except Exception:
        return {"stt": "err 31"}  # Erro ao processar mensagem


def list_files():
    """Lista os arquivos disponíveis no servidor"""
    limpar_tela()
    print(f"{NEGRITO}{AZUL}=== ARQUIVOS NO SERVIDOR ==={RESET}\n")
    
    print(f"{AMARELO}Obtendo lista de arquivos...{RESET}")
    resposta = send_msg({"comando": "LISTAR"})
    
    if resposta["stt"].startswith("ok"):
        if "files" in resposta and resposta["files"]:
            print(f"\n{AZUL}Arquivos disponíveis:{RESET}")
            for i, file in enumerate(resposta["files"], 1):
                print(f"{AZUL}{i}.{RESET} {file}")
        else:
            print(f"{AMARELO}Nenhum arquivo encontrado no servidor{RESET}")
    else:
        display_status_msg(resposta)
    
    input(f"\n{AMARELO}Pressione ENTER para continuar...{RESET}")


def send_file():
    """Envia um arquivo para o servidor"""
    limpar_tela()
    print(f"{NEGRITO}{AZUL}=== ENVIO DE ARQUIVO ==={RESET}\n")
    
    print(f"{AMARELO}Selecione o arquivo para enviar...{RESET}")
    file_path = filedialog.askopenfilename()
    
    if not file_path:
        display_message("err", 50)  # Operação cancelada pelo usuário
        return
        
    if not os.path.exists(file_path):
        display_message("err", 53)  # Arquivo não encontrado localmente
        return

    try:
        with open(file_path, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps({"comando": "ENVIAR", "arquivo": os.path.basename(file_path)}).encode())
            
            # Receber resposta inicial do servidor
            resposta_inicial = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            if not resposta_inicial["stt"].startswith("ok"):
                display_status_msg(resposta_inicial)
                return
                
            # Enviar conteúdo do arquivo
            print(f"{AMARELO}Enviando arquivo '{os.path.basename(file_path)}'...{RESET}")
            total_enviado = 0
            tamanho_arquivo = os.path.getsize(file_path)
            
            while chunk := file.read(BUFFER_SIZE):
                client_socket.sendall(chunk)
                total_enviado += len(chunk)
                porcentagem = (total_enviado / tamanho_arquivo) * 100
                print(f"\r{AMARELO}Progresso: {porcentagem:.1f}%{RESET}", end="")
                
            client_socket.sendall(b"<EOF>")
            print()  # Nova linha após a barra de progresso
            
            # Receber resposta final
            resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            display_status_msg(resposta_final)
    
    except ConnectionRefusedError:
        display_message("err", 51, f"Não foi possível conectar ao servidor {HOST_SRV}:{PORT_SRV}")
    except PermissionError:
        display_message("err", 52)  # Sem permissão para acessar o arquivo
    except Exception as e:
        display_message("err", 11, f"Detalhes: {str(e)}")
    
    input(f"\n{AMARELO}Pressione ENTER para continuar...{RESET}")


def delete_file():
    """Exclui um arquivo do servidor"""
    limpar_tela()
    print(f"{NEGRITO}{AZUL}=== EXCLUSÃO DE ARQUIVO ==={RESET}\n")
    
    # Primeiro lista arquivos disponíveis
    resposta = send_msg({"comando": "LISTAR"})
    if resposta["stt"].startswith("ok") and "files" in resposta and resposta["files"]:
        print(f"{AZUL}Arquivos disponíveis:{RESET}")
        for i, file in enumerate(resposta["files"], 1):
            print(f"{AZUL}{i}.{RESET} {file}")
        print()
    
    file_name = input(f"{AMARELO}Nome do arquivo a ser excluído:{RESET} ")
    if not file_name:
        display_message("err", 50)  # Operação cancelada pelo usuário
        return
    
    confirmacao = input(f"{VERMELHO}Tem certeza que deseja excluir '{file_name}'? (s/n):{RESET} ")
    if confirmacao.lower() != 's':
        display_message("err", 50)  # Operação cancelada pelo usuário
        return
    
    resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
    display_status_msg(resposta)
    
    input(f"\n{AMARELO}Pressione ENTER para continuar...{RESET}")


def exibir_cabecalho():
    """Exibe o cabeçalho do programa"""
    print(f"{NEGRITO}{AZUL}╔══════════════════════════════════════╗{RESET}")
    print(f"{NEGRITO}{AZUL}║           {RESET}{NEGRITO}CLIENTE FSP{RESET}              {NEGRITO}{AZUL}║{RESET}")
    print(f"{NEGRITO}{AZUL}║    {RESET}File Sharing Protocol - v1.0      {NEGRITO}{AZUL}║{RESET}")
    print(f"{NEGRITO}{AZUL}╚══════════════════════════════════════╝{RESET}")
    print(f"{AMARELO}Conectado a: {HOST_SRV}:{PORT_SRV}{RESET}\n")


def main():
    """Função principal do cliente FSP"""
    try:
        while True:
            limpar_tela()
            exibir_cabecalho()
            
            print(f"{NEGRITO}MENU PRINCIPAL:{RESET}")
            print(f"{AZUL}1.{RESET} Listar arquivos")
            print(f"{AZUL}2.{RESET} Enviar arquivo")
            print(f"{AZUL}3.{RESET} Baixar arquivo")
            print(f"{AZUL}4.{RESET} Excluir arquivo")
            print(f"{VERMELHO}0.{RESET} Sair")
            print()
            
            opcao = input(f"{AMARELO}Digite sua opção:{RESET} ")
            
            if opcao == "1":
                list_files()
            elif opcao == "2":
                send_file()
            elif opcao == "3":
                download_file()
            elif opcao == "4":
                delete_file()
            elif opcao == "0":
                print(f"{VERDE}Encerrando cliente...{RESET}")
                time.sleep(1)
                limpar_tela()
                break
            else:
                display_message("err", 21)
                time.sleep(1)
    except KeyboardInterrupt:
        limpar_tela()
        print(f"{VERDE}Cliente encerrado pelo usuário.{RESET}")
    except Exception as e:
        print(f"{VERMELHO}Erro fatal: {str(e)}{RESET}")
        input(f"{AMARELO}Pressione ENTER para sair...{RESET}")


if __name__ == "__main__":
    main()