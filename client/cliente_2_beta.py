import os
import sys
import time
import socket
import json
from tkinter import filedialog
from status.protocolError import error_dict
from status.protocolOk import ok_dict




HOST_SRV = sys.argv[1]
PORT_SRV = int(sys.argv[2]) # Porta Padrão esperada: 8080
BUFFER_SIZE = 4096
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Constantes para cores (compatível com a maioria dos terminais)
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
AZUL = "\033[94m"
RESET = "\033[0m"
NEGRITO = "\033[1m"


def limpar_tela():
    """Limpa a tela do terminal de forma compatível com diferentes sistemas"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_status_msg(resposta, mostrar_prefixo=True):
    """Exibe mensagens de status com formatação por cores"""
    if "stt" not in resposta:
        print(f"{VERMELHO}Erro: Resposta do servidor inválida{RESET}")
        return
    
    try:
        codigo = resposta["stt"].split()[1]
        codigo = int(codigo) if codigo.isdigit() else 22
    except (IndexError, ValueError):
        codigo = 22
    
    if resposta["stt"].startswith("ok"):
        mensagem = ok_dict.get(codigo, "Operação realizada com sucesso.")
        if mostrar_prefixo:
            print(f"{VERDE}✓ {mensagem}{RESET}")
        else:
            print(f"{VERDE}{mensagem}{RESET}")
    else:
        mensagem = error_dict.get(codigo, "Erro desconhecido.")
        if mostrar_prefixo:
            print(f"{VERMELHO}✗ {mensagem}{RESET}")
        else:
            print(f"{VERMELHO}{mensagem}{RESET}")


def exibir_cabecalho():
    """Exibe o cabeçalho do cliente FSP"""
    print(f"{NEGRITO}{AZUL}╔════════════════════════════════════╗{RESET}")
    print(f"{NEGRITO}{AZUL}║{RESET}         {NEGRITO}CLIENTE FSP{RESET}                {NEGRITO}{AZUL}║{RESET}")
    print(f"{NEGRITO}{AZUL}║{RESET} File Sharing Protocol - v1.0         {NEGRITO}{AZUL}║{RESET}")
    print(f"{NEGRITO}{AZUL}╚════════════════════════════════════╝{RESET}")
    print(f"{AMARELO}Conectado a: {HOST_SRV}:{PORT_SRV}{RESET}")
    print()


def exibir_menu():
    """Exibe as opções do menu principal"""
    print(f"{NEGRITO}MENU PRINCIPAL:{RESET}")
    print(f"{AZUL}1{RESET} - Listar arquivos no servidor")
    print(f"{AZUL}2{RESET} - Enviar arquivo para o servidor")
    print(f"{AZUL}3{RESET} - Baixar arquivo do servidor")
    print(f"{AZUL}4{RESET} - Excluir arquivo do servidor")
    print(f"{VERMELHO}0{RESET} - Sair")
    print()


def list_files():
    """Lista os arquivos disponíveis no servidor"""
    print(f"{AMARELO}Obtendo lista de arquivos...{RESET}")
    resposta = send_msg({"comando": "LISTAR"})
    
    if resposta["stt"].startswith("ok"):
        if "files" in resposta and resposta["files"]:
            print(f"\n{NEGRITO}ARQUIVOS DISPONÍVEIS:{RESET}")
            for i, file in enumerate(resposta["files"], 1):
                print(f"{AZUL}  {i}.{RESET} {file}")
            print()
        else:
            print(f"{AMARELO}Nenhum arquivo encontrado no servidor.{RESET}\n")
    else:
        display_status_msg(resposta)
    
    input(f"{AMARELO}Pressione ENTER para continuar...{RESET}")


def send_file():
    """Envia um arquivo para o servidor"""
    print(f"{AMARELO}Selecione o arquivo para enviar...{RESET}")
    file_path = filedialog.askopenfilename()
    
    if not file_path:
        print(f"{AMARELO}Operação cancelada pelo usuário.{RESET}")
        time.sleep(1)
        return
    
    if not os.path.exists(file_path):
        print(f"{VERMELHO}Arquivo não encontrado: {file_path}{RESET}")
        time.sleep(1.5)
        return
    
    try:
        print(f"{AMARELO}Enviando {os.path.basename(file_path)}...{RESET}")
        
        with open(file_path, "rb") as file, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST_SRV, PORT_SRV))
            client_socket.sendall(json.dumps({"comando": "ENVIAR", "arquivo": os.path.basename(file_path)}).encode())
            
            resposta_inicial = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            if not resposta_inicial["stt"].startswith("ok"):
                display_status_msg(resposta_inicial)
                time.sleep(1.5)
                return
            
            total_enviado = 0
            tamanho_arquivo = os.path.getsize(file_path)
            
            while chunk := file.read(BUFFER_SIZE):
                client_socket.sendall(chunk)
                total_enviado += len(chunk)
                porcentagem = (total_enviado / tamanho_arquivo) * 100
                print(f"\r{AMARELO}Progresso: {porcentagem:.1f}%{RESET}", end="")
                
            client_socket.sendall(b"<EOF>")
            print()  # Nova linha após a barra de progresso
            
            resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            display_status_msg(resposta_final)
    
    except ConnectionRefusedError:
        print(f"{VERMELHO}Erro: Não foi possível conectar ao servidor {HOST_SRV}:{PORT_SRV}{RESET}")
    except Exception as e:
        print(f"{VERMELHO}Erro ao enviar arquivo: {str(e)}{RESET}")
    
    time.sleep(1.5)


def download_file():
    """Baixa um arquivo do servidor"""
    # Primeiro, lista os arquivos disponíveis
    resposta = send_msg({"comando": "LISTAR"})
    
    if resposta["stt"].startswith("ok") and "files" in resposta and resposta["files"]:
        print(f"\n{NEGRITO}ARQUIVOS DISPONÍVEIS PARA DOWNLOAD:{RESET}")
        for i, file in enumerate(resposta["files"], 1):
            print(f"{AZUL}  {i}.{RESET} {file}")
        print()
        
        file_name = input(f"{AMARELO}Digite o nome do arquivo a ser baixado: {RESET}")
        
        if not file_name:
            print(f"{AMARELO}Operação cancelada.{RESET}")
            time.sleep(1)
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
                    time.sleep(1.5)
                    return
                
                print(f"{AMARELO}Baixando '{file_name}'...{RESET}")
                
                with open(caminho_salvo, "wb") as file:
                    dados_recebidos = 0
                    while True:
                        data = client_socket.recv(BUFFER_SIZE)
                        if not data:
                            break
                            
                        if b"<EOF>" in data:
                            partes = data.split(b"<EOF>", 1)
                            file.write(partes[0])
                            dados_recebidos += len(partes[0])
                            print(f"\r{AMARELO}Recebidos: {dados_recebidos} bytes{RESET}", end="")
                            break
                            
                        file.write(data)
                        dados_recebidos += len(data)
                        print(f"\r{AMARELO}Recebidos: {dados_recebidos} bytes{RESET}", end="")
                
                print()  # Nova linha após a barra de progresso
                
                try:
                    client_socket.settimeout(2.0)
                    resposta_final = json.loads(client_socket.recv(BUFFER_SIZE).decode())
                    print(f"{VERDE}Arquivo salvo como: {nome_local}{RESET}")
                    display_status_msg(resposta_final)
                except socket.timeout:
                    print(f"{VERDE}Arquivo baixado e salvo como: {nome_local}{RESET}")
                except json.JSONDecodeError:
                    print(f"{VERMELHO}Erro ao processar resposta do servidor{RESET}")
                    
        except ConnectionRefusedError:
            print(f"{VERMELHO}Erro: Não foi possível conectar ao servidor {HOST_SRV}:{PORT_SRV}{RESET}")
        except PermissionError:
            print(f"{VERMELHO}Erro: Sem permissão para salvar o arquivo{RESET}")
        except Exception as e:
            print(f"{VERMELHO}Erro ao baixar arquivo: {str(e)}{RESET}")
    else:
        print(f"{AMARELO}Nenhum arquivo disponível para download.{RESET}")
    
    time.sleep(1.5)


def delete_file():
    """Exclui um arquivo do servidor"""
    # Primeiro, lista os arquivos disponíveis
    resposta = send_msg({"comando": "LISTAR"})
    
    if resposta["stt"].startswith("ok") and "files" in resposta and resposta["files"]:
        print(f"\n{NEGRITO}ARQUIVOS DISPONÍVEIS PARA EXCLUSÃO:{RESET}")
        for i, file in enumerate(resposta["files"], 1):
            print(f"{AZUL}  {i}.{RESET} {file}")
        print()
        
        file_name = input(f"{AMARELO}Digite o nome do arquivo a ser excluído: {RESET}")
        
        if not file_name:
            print(f"{AMARELO}Operação cancelada.{RESET}")
            time.sleep(1)
            return
            
        confirmacao = input(f"{VERMELHO}Tem certeza que deseja excluir '{file_name}'? (s/n): {RESET}")
        if confirmacao.lower() != 's':
            print(f"{AMARELO}Exclusão cancelada.{RESET}")
            time.sleep(1)
            return
            
        resposta = send_msg({"comando": "DELETAR", "arquivo": file_name})
        display_status_msg(resposta)
    else:
        print(f"{AMARELO}Nenhum arquivo disponível para exclusão.{RESET}")
    
    time.sleep(1.5)


def main():
    """Função principal do cliente FSP"""
    try:
        while True:
            limpar_tela()
            exibir_cabecalho()
            exibir_menu()
            
            opcao = input(f"{AMARELO}Digite sua opção: {RESET}")
            
            if opcao == "1":
                limpar_tela()
                list_files()
            elif opcao == "2":
                limpar_tela()
                send_file()
            elif opcao == "3":
                limpar_tela()
                download_file()
            elif opcao == "4":
                limpar_tela()
                delete_file()
            elif opcao == "0":
                limpar_tela()
                print(f"{VERDE}Encerrando cliente FSP...{RESET}")
                time.sleep(1)
                limpar_tela()
                break
            else:
                print(f"{VERMELHO}Opção inválida. Tente novamente.{RESET}")
                time.sleep(1)
    except KeyboardInterrupt:
        limpar_tela()
        print(f"{VERDE}Cliente FSP encerrado pelo usuário.{RESET}")
    except Exception as e:
        print(f"{VERMELHO}Erro fatal: {str(e)}{RESET}")
        input(f"{AMARELO}Pressione ENTER para sair...{RESET}")