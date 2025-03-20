# Protocolo FSP (File Sharing Protocol)

## Visão Geral

O FSP é um protocolo de aplicação para compartilhamento de arquivos baseado em TCP/IP. O protocolo permite operações básicas de gerenciamento de arquivos, incluindo listagem, upload, download e exclusão de arquivos em um servidor remoto.

## Arquitetura

O FSP utiliza o modelo cliente-servidor, onde:
- O **servidor** gerencia os arquivos armazenados e processa as solicitações dos clientes
- Os **clientes** se conectam ao servidor para realizar operações sobre os arquivos

## Formato das Mensagens

As mensagens do protocolo FSP são codificadas em formato JSON, o que permite uma comunicação legível por humanos e facilita o debug.

### Estrutura das Mensagens de Requisição:

```json
{
    "comando": "COMANDO",
    "arquivo": "nome_do_arquivo"  // Opcional, dependendo do comando
}
```

### Estrutura das Mensagens de Resposta:

```json
{
    "stt": "tipo código",  // Ex: "ok 45" ou "err 14"
    "msg": "Descrição do status",
    "files": [...]         // Opcional, presente apenas em respostas de listagem
}
```

## Comandos do Protocolo

### 1. LISTAR

Solicita a lista de todos os arquivos disponíveis no servidor.

**Requisição:**
```json
{
    "comando": "LISTAR"
}
```

**Resposta de Sucesso:**
```json
{
    "stt": "ok 45",
    "msg": "Arquivos listados com sucesso.",
    "files": ["arquivo1.txt", "imagem.jpg", "documento.pdf"]
}
```

### 2. ENVIAR

Upload de um arquivo para o servidor.

**Requisição:**
```json
{
    "comando": "ENVIAR",
    "arquivo": "nome_do_arquivo.ext"
}
```

**Resposta Inicial (antes de iniciar a transferência):**
```json
{
    "stt": "ok 40",
    "msg": "Iniciando transferência"
}
```

Após esta resposta, o cliente começa a enviar o conteúdo do arquivo em blocos de até 4096 bytes. Quando o arquivo é completamente transferido, o cliente envia a sequência de bytes `<EOF>` e o servidor responde:

**Resposta Final (após concluir a transferência):**
```json
{
    "stt": "ok 41", 
    "msg": "Arquivo enviado com sucesso."
}
```

### 3. BAIXAR

Download de um arquivo do servidor.

**Requisição:**
```json
{
    "comando": "BAIXAR",
    "arquivo": "nome_do_arquivo.ext"
}
```

**Resposta Inicial (antes de iniciar a transferência):**
```json
{
    "stt": "ok 44",
    "msg": "Iniciando download."
}
```

Após esta resposta, o servidor começa a enviar o conteúdo do arquivo em blocos de até 4096 bytes. Quando o arquivo é completamente transferido, o servidor envia a sequência de bytes `<EOF>` seguida de:

**Resposta Final (após concluir a transferência):**
```json
{
    "stt": "ok 46", 
    "msg": "Arquivo baixado com sucesso."
}
```

### 4. DELETAR

Exclui um arquivo do servidor.

**Requisição:**
```json
{
    "comando": "DELETAR",
    "arquivo": "nome_do_arquivo.ext"
}
```

**Resposta de Sucesso:**
```json
{
    "stt": "ok 43",
    "msg": "Arquivo deletado com sucesso."
}
```

## Códigos de Status

### Códigos de Sucesso (40-49)

| Código | Mensagem | Descrição |
|--------|----------|-----------|
| 40 | Iniciando transferência | Sinaliza o início de uma operação de transferência |
| 41 | Arquivo enviado com sucesso | Confirma que o servidor recebeu o arquivo completamente |
| 42 | Arquivo recebido com sucesso | Confirma que o arquivo foi processado e armazenado pelo servidor |
| 43 | Arquivo deletado com sucesso | Confirma que o arquivo foi removido do servidor |
| 44 | Iniciando download | Sinaliza que o servidor está pronto para enviar o arquivo |
| 45 | Arquivos listados com sucesso | A listagem foi realizada com sucesso |
| 46 | Arquivo baixado com sucesso | O arquivo foi transferido do servidor para o cliente com sucesso |

### Códigos de Erro (10-39)

| Código | Mensagem | Descrição |
|--------|----------|-----------|
| 11 | Erro ao enviar arquivo | Ocorreu um problema durante o upload do arquivo |
| 12 | Erro ao baixar o arquivo | Ocorreu um problema durante o download do arquivo |
| 13 | Erro ao deletar o arquivo | Não foi possível remover o arquivo do servidor |
| 14 | Arquivo não encontrado no servidor | O arquivo solicitado não existe no servidor |
| 21 | Comando Inválido | O comando enviado não é reconhecido pelo protocolo |
| 22 | Formato de Mensagem Inválido | A mensagem JSON está malformada ou tem campos inválidos |
| 30 | Erro no servidor | Problema interno no servidor |
| 31 | Erro ao processar mensagem | O servidor não conseguiu processar a requisição |

## Tratamento de Arquivos Duplicados

Quando um cliente tenta enviar um arquivo com um nome que já existe no servidor, o protocolo implementa um mecanismo para evitar sobrescrição:

1. O servidor identifica a duplicação de nomes
2. Um contador numérico é adicionado ao nome do arquivo (ex: "arquivo(1).txt")
3. O processo é repetido incrementando o contador até encontrar um nome único

## Transferência de Arquivos

A transferência de arquivos é realizada em blocos de até 4096 bytes para otimizar o uso de memória.

O final da transferência é marcado pelo envio da sequência `<EOF>` pelo lado que está transmitindo o arquivo (cliente no caso de upload, servidor no caso de download).

## Concorrência e Segurança

O protocolo implementa mecanismos de lock para garantir a integridade dos arquivos durante operações concorrentes de múltiplos clientes. Isso evita condições de corrida que poderiam corromper os arquivos durante transferências simultâneas.