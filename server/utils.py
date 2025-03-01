import os

# verifica se o usuario ja baixou esse arquivo e adiciona um contador ao nome do arquivo.
def handle_duplicate_files(nome_arquivo, DOWNLOAD_DIR):
    nm,ext = os.path.splitext(os.path.basename(nome_arquivo))
    nome = f"{nm}{ext}"
    contador = 1

    while os.path.exists(os.path.join(DOWNLOAD_DIR, nome)):
        nome = f"{nm}({contador}){ext}"
        contador += 1
    
    return nome

def read_write_binary(source,destiny):
    with open(source, "rb") as src, open(destiny, "wb") as dst:
        while True:
            bloco = src.read(4096)
            if not bloco:
                break
            dst.write(bloco)