## Visão Geral

O protocolo FSP é um protocolo simples baseado em JSON para transferência de arquivos entre cliente e servidor. Ele define comandos para listar, enviar, baixar e excluir arquivos, com suporte para transferência de dados binários.

## Características do Protocolo

- Baseado em TCP para garantir entrega confiável dos dados
- Mensagens de controle codificadas em JSON
- Suporte para transferência de arquivos binários
- Marcador de fim de arquivo (`<EOF>`) para delimitar transferências binárias

## Formato das Mensagens