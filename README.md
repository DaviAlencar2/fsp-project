# 📂 FSP - Sistema de Compartilhamento de Arquivos

## Autores
- [Davi Leite] - [davi.leite@academico.ifpb.edu.br]
- [Clara Alcantara] - [clara.alcantara@academico.ifpb.edu.br]

## Disciplinas
- Protocolos e Interconexão de Redes de Computadores
- Professor: [Leonidas]

## Descrição do Problema
O projeto FSP (File Sharing Protocol) implementa um sistema cliente-servidor para compartilhamento de arquivos. Ele permite aos usuários listar, enviar, baixar e excluir arquivos em um servidor remoto através de um protocolo personalizado baseado em JSON.

O sistema foi projetado para ser simples, eficiente e capaz de lidar com arquivos binários ou textuais, com recursos como:
- Tratamento de transferências concorrentes de múltiplos clientes
- Detecção e resolução de nomes de arquivos duplicados
- Registro de logs de todas as operações
- Interface de linha de comando intuitiva

## Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| **client/client.py** | Implementação do cliente FSEP com funções para listar, enviar, baixar e excluir arquivos |
| **client/downloads/** | Diretório onde são armazenados os arquivos baixados do servidor |
| **server/server.py** | Servidor FSEP multithreaded, responsável por escutar conexões e gerenciar requisições |
| **server/fsep.py** | Implementação do protocolo FSP, processa as mensagens recebidas dos clientes |
| **server/utils.py** | Funções utilitárias, como tratamento de arquivos duplicados |
| **server/data/files/** | Diretório onde os arquivos são armazenados no servidor |
| **docs/protocol.md** | Documentação do protocolo de comunicação FSP |

## Pré-requisitos para Execução

O projeto foi desenvolvido em Python 3.10+ e utiliza apenas bibliotecas padrão da linguagem:

- Python 3.10 ou superior
- Bibliotecas padrão: socket, json, os, datetime, threading, csv

Não é necessário instalar pacotes adicionais.

## Instruções para Execução

### 1. Iniciando o Servidor

```bash
# Na pasta raiz do projeto
python -m server.server
```

### 1. Iniciando o Servidor

```bash
# Na pasta raiz do projeto
python -m client.client
```
