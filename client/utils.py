import os

def handle_duplicate_files(nome_arquivo, FILES_LIST):
    nm,ext = os.path.splitext(os.path.basename(nome_arquivo))
    nome = f"{nm}{ext}"
    contador = 1

    while nome in FILES_LIST:
        nome = f"{nm}({contador}){ext}"
        contador += 1
    
    return nome