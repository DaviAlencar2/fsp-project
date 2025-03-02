import os

# verifica se o usuario ja baixou esse arquivo e adiciona um contador ao nome do arquivo.
def handle_duplicate_files(nome_arquivo, FILES_DIR):
    nm,ext = os.path.splitext(os.path.basename(nome_arquivo))
    nome = f"{nm}{ext}"
    contador = 1

    while os.path.exists(os.path.join(FILES_DIR, nome)):
        nome = f"{nm}({contador}){ext}"
        contador += 1
    
    return nome