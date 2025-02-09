import os
import json
DATA_DIR = "data/"

def processar_mensagem(mensagem, client_socket):
    try:
        dados = json.loads(mensagem)

        if dados["comando"] == "LISTAR":
            arquivos = os.listdir(DATA_DIR)
            resposta = {"status": "ok", "arquivos": arquivos}
        
        elif dados["comando"] == "ENVIAR":
            nome_arquivo = dados["arquivo"]
            caminho_arquivo = os.path.join(DATA_DIR, os.path.basename(nome_arquivo))
            conteudo = dados["conteudo"]
            with open(caminho_arquivo, "w") as f:
                f.write(conteudo)
            resposta = {"status": "ok", "mensagem": f"Arquivo '{nome_arquivo}' salvo no servidor."}
        
        elif dados["comando"] == "BAIXAR":
            nome_arquivo = dados["arquivo"]
            try:
                with open(caminho_arquivo, "r") as f:
                    conteudo = f.read()
                resposta = {"status": "ok", "conteudo": conteudo}
            except FileNotFoundError:
                resposta = {"status": "erro", "mensagem": "Arquivo não encontrado."}

        else:
            resposta = {"status": "erro", "mensagem": "Comando inválido."}

    except json.JSONDecodeError:
        resposta = {"status": "erro", "mensagem": "Formato de mensagem inválido."}

    client_socket.sendall(json.dumps(resposta).encode())
