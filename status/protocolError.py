'''
Erros que começam com 1 vão ser erros de comandos e os que começam em 2 erros de processamento da mensagem,
os que começam em 3 erros no servidor e os que começam em 5 erros de cliente.
'''

error_dict = {
    11: "Erro ao enviar arquivo",
    12: "Erro ao baixar o arquivo",
    13: "Erro ao deletar o arquivo",
    14: "Arquivo não encontrado no servidor",
    21: "Comando Inválido",
    22: "Formato de Mensagem Inválido",
    30: "Erro no servidor",
    31: "Erro ao processar mensagem",
    # Erros de cliente (50-59)
    50: "Operação cancelada pelo usuário",
    51: "Não foi possível conectar ao servidor",
    52: "Sem permissão para acessar o arquivo",
    53: "Arquivo não encontrado localmente",
    54: "Erro de I/O ao manipular o arquivo",
    55: "Timeout na conexão",
    56: "Resposta inválida do servidor",
    57: "Marcador de fim de arquivo não encontrado"
}