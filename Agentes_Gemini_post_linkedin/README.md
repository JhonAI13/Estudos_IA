# 🤖 Sistema Multi-Agente para Geração de Conteúdo de LinkedIn

Este projeto demonstra a criação de um sistema simples de múltiplos agentes, utilizando a API do Google Gemini, para automatizar a geração de rascunhos de posts para o LinkedIn e prompts para geração de imagens, com base em notas ou textos brutos fornecidos.

O sistema é otimizado para gerar conteúdo no estilo e com os focos (Data Science, IA, Python, etc.) do perfil de Jonathas Martins da Rocha, visando destacar suas habilidades e proatividade na busca por novas oportunidades.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JhonAI13/Estudos_IA/blob/main/Agentes_Gemini_post_linkedin)

## ✨ Funcionalidades

*   **Processamento de Texto:** Lê e estrutura notas ou conteúdos brutos, identificando o tópico principal e pontos chave.
*   **Geração de Post:** Cria um rascunho de post para LinkedIn, adaptado para o estilo e objetivos de carreira do usuário.
*   **Revisão e Refinamento:** Um agente revisor ajusta e melhora o rascunho, garantindo clareza, concisão e alinhamento com o estilo.
*   **Geração de Prompt Visual:** Cria um prompt otimizado para ferramentas de geração de imagem por IA, seguindo um estilo visual definido (minimalista, branco sobre preto) e sugerindo ícones/elementos relevantes ao post.
*   **Arquitetura Multi-Agente:** Divide o processo em etapas lógicas, cada uma executada por um agente especializado.

## 🛠️ Como Funciona

O pipeline de geração de conteúdo segue a seguinte sequência de agentes:

1.  **Processor:** Recebe o texto bruto, extrai o tópico, pontos chave, links e ideias visuais, gerando um "Plano de Post Detalhado".
2.  **Writer:** Utiliza o plano detalhado para escrever um rascunho inicial do post no estilo desejado, incluindo estrutura, emojis e hashtags.
3.  **Reviewer:** Revisa o rascunho, corrige erros, melhora a fluidez e garante que o post final esteja polido e alinhado com o plano original e o estilo.
4.  **Image:** Usa o plano detalhado (especialmente as ideias visuais) para gerar um prompt de imagem focado em um estilo visual minimalista e técnico.

## 🚀 Pré-requisitos

*   Uma conta Google para usar o Google Colab (opcional, mas recomendado).
*   Uma chave de API válida para o Google Gemini (Google AI Studio). Obtenha sua chave [aqui](https://aistudio.google.com/app/apikey).
*   Python 3.7+
*   Bibliotecas Python: `google-genai`, `google-adk`, `python-dotenv` (para carregar a API Key de um `.env`, embora o notebook use Colab Userdata).

## ⚙️ Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/JhonAI13/Estudos_IA.git
    cd Estudos_IA/Agentes_Gemini_post_linkedin # Ajuste o caminho se necessário
    ```
    *Nota:* Se estiver usando o Google Colab diretamente pelo badge "Open In Colab", você pode pular este passo, pois o notebook já estará carregado.

2.  **Obtenha sua Chave de API Gemini:**
    *   Vá para [Google AI Studio](https://aistudio.google.com/app/apikey) e crie uma chave de API.
    *   No Google Colab, é recomendado armazenar sua chave usando **Secrets/Userdata**:
        *   Clique no ícone de "Chave" (Secrets) na barra lateral esquerda.
        *   Clique em "+ New secret".
        *   Defina o **Name** como `GOOGLE_API_KEY`.
        *   Cole sua chave de API no campo **Value**.
        *   Certifique-se de que o switch "Notebook access" está ativado.

3.  **Instale as Dependências:**
    Execute as seguintes células no topo do notebook para instalar as bibliotecas necessárias:
    ```python
    %pip -q install google-genai
    !pip -q install google-adk
    !pip -q install python-dotenv # Opcional, se não usar Colab Secrets
    ```

## 📄 Uso

1.  **Prepare seu Conteúdo de Entrada:** Crie um arquivo de texto (`.txt`) contendo as notas, o resumo do projeto, aprendizado, etc., que você deseja transformar em um post de LinkedIn.
    *   Exemplo: `Dashboard_web.txt` (o caminho padrão no código).
    *   Se estiver no Colab, você pode fazer upload deste arquivo para o ambiente de sessão ou montá-lo a partir do Google Drive.

2.  **Atualize o Caminho do Arquivo:** No código, localize a variável `caminho_arquivo` e atualize o caminho para o seu arquivo de entrada:
    ```python
    caminho_arquivo = "/caminho/para/seu/arquivo.txt"
    ```
    *   No Colab, se você fizer upload para a raiz da sessão, o caminho será `/nome_do_arquivo.txt`.

3.  **Execute o Notebook:** Execute todas as células do notebook sequencialmente.

4.  **Visualize o Resultado:** O notebook exibirá a saída de cada agente e, no final, o "RESULTADO FINAL" com o texto do post de LinkedIn revisado e o prompt de imagem gerado.

## 🧩 Agentes Detalhados

*   **Processor:** Analisa o texto de entrada para extrair o essencial para o post.
*   **Writer:** Redige o primeiro rascunho do post, focado em seguir o estilo e estrutura definidos.
*   **Reviewer:** Atua como editor final, polindo o texto, corrigindo erros e garantindo a qualidade.
*   **Image:** Traduz as ideias visuais do plano em um prompt conciso para ferramentas de geração de imagem, mantendo um estilo específico.

## ✏️ Personalização

Você pode facilmente adaptar este sistema aos seus próprios objetivos:

*   **Instruções dos Agentes:** Modifique o `instruction` de cada agente na variável `agents` para ajustar seu comportamento, estilo de escrita, formato de saída, etc.
*   **Arquivo de Entrada:** Use diferentes arquivos `.txt` para gerar posts sobre diferentes tópicos.
*   **Modelo Gemini:** Altere a variável `MODELO_GLOBAL` para usar outro modelo Gemini (por exemplo, `gemini-1.5-pro`) se desejar.
*   **Estilo Visual da Imagem:** Ajuste o `instruction` do agente `image` para mudar o estilo das imagens sugeridas.

## 🚧 Melhorias Potenciais

*   Adicionar tratamento para outros formatos de arquivo (Markdown, .docx, etc.).
*   Implementar a integração com uma API de geração de imagem (como Midjourney, DALL-E) para gerar a imagem diretamente.
*   Criar uma interface web simples (usando Streamlit, Flask, etc.) para facilitar o upload do arquivo e visualização dos resultados.
*   Salvar automaticamente os resultados em arquivos separados (`.md` para o post, `.txt` para o prompt).
*   Permitir que o usuário forneça feedback para refinar as gerações.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar Pull Requests.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo `LICENSE` para mais detalhes (se você pretende adicionar um).

---

Desenvolvido com ❤️ por JhonAI13.