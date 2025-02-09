## FSEP Protocol

O protocolo FSEP é utilizado para comunicação entre um cliente e um servidor para manipulação de arquivos. A comunicação é feita através de mensagens JSON.

A mensagem enviada pelo cliente deve estar no formato JSON com a seguinte estrutura:

```json
{
    "comando": "COMANDO",
    "arquivo": "NOME_ARQUIVO",
    "conteudo": "CONTEUDO"
}
