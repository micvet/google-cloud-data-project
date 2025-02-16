# Dialog Flow - Chatbot - Asteroid Assistant

Este diretório contém os arquivos relacionados ao chatbot baseado no Dialogflow, responsável por interagir com os usuários e fornecer informações sobre asteroides próximos à Terra.

## Estrutura
- exported_agent_asteroide-chatbot.blob → Arquivo exportado do agente Dialogflow.
- Asteroid-QueryAPI.yaml → Configuração da API utilizada na ferramenta Playbook do Dialogflow.
- README.md → Documentação sobre a configuração e uso do chatbot.

## Configuração

1. Importar o Agente Dialogflow
Acesse o Google Dialogflow CX.
Crie um novo agente ou selecione um já existente.
No menu lateral, vá até Configurações > Importar e Exportar.
Clique em Importar e carregue o arquivo exported_agent_asteroide-chatbot.blob.

3. Configurar a API do Playbook
A API Asteroid-QueryAPI.yaml define uma tool utilizada pelo Playbook do Dialogflow para acionar a Cloud Function responsável por consultar dados no BigQuery.

Para configurar a API:

No Dialogflow CX, vá até Playbooks > Manage All Tools > Create;
Verifique se a API Asteroid Query API já está configurada. Se não, crie uma nova TOOL, selecionando o Type OpenAPI e copie o conteúdo do arquivo Asteroid-QueryAPI.yaml. **Você deve alterar o end point que receberá as questions feitas pelo usuário**.
Certifique-se de que a API está configurada corretamente e integrada ao fluxo do Playbook.

4. Implantar a Função de Resposta do Chatbot
A função que processa as perguntas do usuário e gera respostas está no diretório cloud-functions/bot-response. Certifique-se de que ela está implantada,e caso contrário, siga os passos contidos no diretório específico do (Cloud Run Functions)[https://github.com/micvet/gcp-data-project/blob/main/cloud-run-functions/README.md]

5. Integrar o Chatbot com a Interface Web
O chatbot está incorporado na aplicação web e pode ser acessado via um container personalizado do Dialogflow Messenger. Selecione a opção Integrations > Conversational Messenger e ative o serviço. Um embed será fornecido e deve ser incorporado ao código de front-end. Certifique-se de que o frontend está configurado corretamente para exibir o assistente.

## Funcionamento
O fluxo de interação do chatbot é o seguinte:

1. O usuário faz uma pergunta sobre asteroides;
2. O Dialogflow identifica a intenção e aciona a API do Playbook;
3. A API faz uma requisição para a Cloud Function bot-response;
4. A função gera uma query para o BigQuery usando Vertex AI;
5. A query é executada, e os dados retornam para a função;
6. Outra etapa de Vertex AI formata a resposta de forma natural e envia na response para o Dialog Flow;
7. O chatbot recebe a response e exibe a resposta ao usuário.

  
## Boas Práticas

Gerenciamento de Versões: Sempre mantenha uma cópia exportada do agente Dialogflow antes de fazer alterações.
Treinamento Contínuo: Ajuste o chatbot conforme as interações dos usuários para melhorar a precisão.
