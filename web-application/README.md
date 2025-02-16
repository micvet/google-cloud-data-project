# Web Application - Chatbot Assistente

Este diretório contém os arquivos da interface web utilizada para interagir com o chatbot Au-Stronauta, que fornece informações sobre asteroides próximos à Terra.

## Estrutura
1. index.html → Página principal da aplicação web, contendo a integração com o chatbot e um embed de um design do Canva.
2. df-messenger-custom.css → Arquivo de estilização do chatbot para personalização da interface.
3. README.md → Documentação sobre a configuração e uso da aplicação web.

## Como Funciona
A página index.html exibe:

1. Embed do Canva → Para personalizar a apresentação da interface.
2. Integração com o Dialogflow CX → O chatbot é carregado de forma assíncrona e permite que os usuários interajam com ele diretamente pela interface web.

## Configuração
1. Publicar um Design no Canva
O código inclui um embed do Canva para exibir uma página personalizada. Para utilizar corretamente:

* Acesse Canva.
* Crie um design no formato de página web.
* Clique em Compartilhar → Mais opções → Incorporar.
* Copie o código fornecido e substitua o valor do src no iframe e no link <a> dentro do index.html.

2. Configurar o Chatbot
O chatbot é carregado através de um embed do Dialogflow CX. Para configurá-lo corretamente:

* Acesse o Google Dialogflow CX.
* No menu lateral, vá até Integrações.
* Selecione Conversational Messenger.
* Copie o código de integração insira o valor do <script> no index.html.

3. Personalizar a Interface
O arquivo df-messenger-custom.css contém ajustes visuais para a exibição do chatbot. Caso queira modificar cores e fontes, edite esse arquivo conforme necessário.

## Implantação
A página pode ser hospedada no Cloud Storage para ser acessada publicamente.
* Crie um bucket e adicione o arquivo index.html e o arquivo de personalização df-messenger-custom.css;
* Utilize os seguintes comandos:
```
gsutil iam ch allUsers:objectViewer gs:/SEU-BUCKET
```
Depois:
```
gsutil setmeta -h "Content-Type:text/html" gs://SEU-BUCKET/index.html
```
A página estará disponível em:

* https://storage.googleapis.com/SEU-BUCKET/index.html


  
## Boas Práticas
* Manter o embed do Dialogflow seguro, evitando expor credenciais sensíveis.
* Monitorar as interações no Dialogflow, ajustando intents conforme necessário para melhorar a precisão do chatbot.
