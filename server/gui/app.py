import tkinter as tk
from tkinter import messagebox

def toggle_server():
    # Aqui, você pode conectar a lógica para ligar e desligar o servidor
    global server_running
    if server_running:
        server_running = False
        btn_server.config(text="Ligar Servidor")
        # Adicione a lógica para parar o servidor
        print("Servidor desligado")
    else:
        server_running = True
        btn_server.config(text="Desligar Servidor")
        # Adicione a lógica para iniciar o servidor
        print("Servidor ligado")

# Inicialização do Tkinter
root = tk.Tk()
root.title("Servidor TCP de Arquivos")

# Definindo o tamanho da janela
root.geometry("600x400")

# Cor de fundo escura para a tela
root.config(bg="#2e2e2e")

# Variável de controle do servidor (simulando se está ligado ou não)
server_running = False

# Título
title = tk.Label(root, text="Servidor TCP de Arquivos", fg="#007bff", bg="#2e2e2e", font=("Helvetica", 16))
title.pack(pady=10)

# Botão para ligar/desligar o servidor
btn_server = tk.Button(root, text="Ligar Servidor", command=toggle_server, bg="#007bff", fg="white", font=("Helvetica", 12))
btn_server.pack(pady=20)

# Caixa de listagem de arquivos
frame_files = tk.Frame(root, bg="#2e2e2e")
frame_files.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.Y)

files_label = tk.Label(frame_files, text="Arquivos Disponíveis", fg="#007bff", bg="#2e2e2e", font=("Helvetica", 12))
files_label.pack()

list_files = tk.Listbox(frame_files, bg="#333333", fg="white", width=30, height=10, font=("Helvetica", 10))
list_files.pack()

# Caixa de listagem de clientes
frame_clients = tk.Frame(root, bg="#2e2e2e")
frame_clients.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.Y)

clients_label = tk.Label(frame_clients, text="Clientes Conectados", fg="#007bff", bg="#2e2e2e", font=("Helvetica", 12))
clients_label.pack()

list_clients = tk.Listbox(frame_clients, bg="#333333", fg="white", width=30, height=10, font=("Helvetica", 10))
list_clients.pack()

# Iniciar o loop da interface gráfica
root.mainloop()
