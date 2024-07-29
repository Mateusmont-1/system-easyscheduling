# Sistema de Barbearia

## Descrição

Este é um projeto de um sistema de barbearia desenvolvido em Python, utilizando Flet como interface web e Firestore da Google como banco de dados. O sistema visa otimizar a gestão de agendamentos, colaboradores, serviços, produtos e controle financeiro.

## Funcionalidades

- **Usuários:**
  - Criação de usuário com cadastro de email e senha no autenticador do Google.
  - Cadastro de nome e telefone no Firestore.
  - Salvamento dos dados de usuário no Firestore.
  - 
- **Agendamentos:**
  - Criar novos agendamentos.
  - Editar agendamentos existentes.
  - Cancelar agendamentos.
  - Barbeiro/administrador pode finalizar atendimentos.
  - Enviar mensagem via WhatsApp informando sobre a criação do agendamento, edição e cancelamento.
  
- **Colaboradores:**
  - Criar novos colaboradores.
  - Editar informações dos colaboradores.
  - Adicionar folgas para colaboradores.
  - Verificar folgas dos colaboradores.
  - Cancelar folgas dos colaboradores.

- **Serviços:**
  - Adicionar novos serviços para agendamento.
  - Editar serviços existentes.

- **Produtos:**
  - Adicionar novos produtos.
  - Editar informações dos produtos.

- **Controle de Caixa:**
  - Verificar o saldo diário, semanal e mensal dos barbeiros.
  - Verificar o saldo mensal do estabelecimento.
  - Verificar o saldo mensal de despesas.
  - Adicionar e editar categorias de despesas.
  - Adicionar e editar despesas.

## Instalação

Para instalar e executar este projeto, siga os passos abaixo:

1. Clone o repositório:
    ```bash
    git clone https://github.com/Mateusmont-1/sistema-de-barbearia.git
    ```

2. Navegue até o diretório do projeto:
    ```bash
    cd sistema-de-barbearia
    ```

3. Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```

4. Ative o ambiente virtual:

    - No Windows:
      ```bash
      venv\Scripts\activate
      ```
    - No Linux/Mac:
      ```bash
      source venv/bin/activate
      ```

5. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

6. Configure suas credenciais do Firestore e configuracações do sistema:
    - Crie um arquivo `.env` na raiz do projeto e adicione suas credenciais do Firestore. O arquivo `.env` deve conter:
      ```
      API_KEY=seu_id_api_whatsapp
      FIREBASE_WEB_API_KEY=sua_chave_web
      FIREBASE_TYPE=service_account
      FIRESTORE_PROJECT_ID=seu_projeto_id
      FIRESTORE_PRIVATE_KEY_ID=sua_chave_privada_id
      FIRESTORE_PRIVATE_KEY=sua_chave_privada
      FIRESTORE_CLIENT_EMAIL=seu_email_cliente
      FIRESTORE_CLIENT_ID=seu_cliente_id
      FIRESTORE_AUTH_URI=seu_auth_uri
      FIRESTORE_TOKEN_URI=seu_token_uri
      FIRESTORE_AUTH_PROVIDER_x509_CERT_URL=seu_auth_provider_cert_url
      FIRESTORE_CLIENT_x509_CERT_URL=seu_cliente_cert_url
      FIREBASE_UNIVERSE_DOMAIN=googleapis.com

      TELEFONE_CONTACT=seu_telefone_contato
      CONTACT_NAME=seu_nome_contato

      URL_MAPS=seu_url_google_maps

      FLET_PATH=/sistema_exemplo
      
      COLOR_BACKGROUND_PAGE=#303030
      COLOR_BACKGROUND_CONTAINER=#0F0F0F
      COLOR_BACKGROUND_BUTTON=#16181b
      COLOR_BACKGROUND_TEXT_FIELD=#0F0F0F
      COLOR_TEXT_BUTTON=#ccaf7e
      COLOR_TEXT=#C0C0C0
      COLOR_TEXT_IN_BUTTON=#ccaf7e
      COLOR_TEXT_IN_DROPDOWN=#ccaf7e
      COLOR_TEXT_IN_FIELD=#ccaf7e
      COLOR_BORDER_COLOR=#ccaf7e
      COLOR_BORDER_COLOR_ERROR=#FF0000
      ```

