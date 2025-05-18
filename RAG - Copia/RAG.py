# --- 1. Imports Necessários ---
import os
import glob
import google.generativeai as genai # Importa a biblioteca do Google AI
import textwrap # Útil para formatar saída
import sys # Para verificar se o caminho de entrada existe

# --- 2. Configuração da API (Lida dentro de call_agent) ---
# A API Key será lida da variável de ambiente GOOGLE_API_KEY
# genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
# NOTA: A configuração será feita dentro da função call_agent para garantir que seja feita após a variável de ambiente estar disponível.

# --- 3. Classe Agent (Mantida como Data Structure) ---
class Agent:
    def __init__(self, name, model, instruction, description):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.description = description
        # Remover print de inicialização para não poluir o rastreamento do pipeline

# --- 4. Função call_agent (AGORA REAL) ---
# Esta função encapsula a chamada real para a API do modelo de IA.
def call_agent(agent: Agent, input_data: str) -> str:
    print(f"\n===== EXECUTANDO AGENTE: {agent.name} =====")
    print(f"--> Modelo utilizado: {agent.model}")
    print("--> Entrada do Agente (Primeiros 500 chars):")
    print(textwrap.shorten(input_data, width=500, placeholder="...")) # Formata a entrada para print

    # --- Lógica REAL para chamar o modelo AI ---
    actual_output = f"ERRO: Falha na execução do agente {agent.name} antes da chamada da API." # Default error message

    try:
        # Configura a API Key lendo da variável de ambiente
        api_key = 'AIzaSyB9mg4Rn6injM_OtG1eeHgkPffQhGq0Grk'
        if not api_key:
            raise ValueError("Variável de ambiente GOOGLE_API_KEY não configurada. Por favor, defina-a.")

        # Configura a biblioteca com a API Key
        genai.configure(api_key=api_key)

        # Obtém o modelo especificado pelo agente
        # Verifica se o modelo existe e é compatível com a tarefa de geração de texto
        try:
            model = genai.GenerativeModel(agent.model)
            # Opcional: verificar capabilities do modelo se necessário (ex: supports_text_generation)
        except Exception as e:
             raise ValueError(f"Erro ao carregar modelo '{agent.model}': {e}. Verifique o nome do modelo e sua disponibilidade.")


        # Combina a instrução do agente com os dados de entrada
        prompt_text = agent.instruction + "\n\n---\n\nDados de Entrada para Processar:\n" + input_data

        print("--> Chamando Google Gemini API...")
        # Chama a API
        # generate_content é adequado para a maioria das tarefas de texto
        # Adicionamos um timeout básico para evitar que a chamada fique travada indefinidamente
        generation_config = genai.GenerationConfig(temperature=0.5) # Ajuste a temperatura se quiser respostas mais ou menos criativas
        response = model.generate_content(prompt_text, generation_config=generation_config, request_options={'timeout': 120}) # Timeout de 120 segundos

        print("--> Resposta da API recebida.")

        # Processa a resposta da API
        if response.text:
            actual_output = response.text
        else:
            # Trata casos onde a resposta pode estar vazia ou bloqueada
            block_reason = None
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                 block_reason = response.prompt_feedback.block_reason
                 raise ValueError(f"Chamada da API bloqueada por motivo de segurança: {block_reason}")
            elif hasattr(response, 'candidates') and response.candidates:
                 # Tenta extrair texto dos candidatos mesmo que .text principal esteja vazio
                 text_parts = [part.text for candidate in response.candidates for part in candidate.content.parts if hasattr(part, 'text')]
                 actual_output = "".join(text_parts)
                 if not actual_output.strip(): # Verifica se o texto extraído não é apenas espaços
                      raise ValueError("Resposta da API não contém texto válido.")
            else:
                 raise ValueError("Resposta da API vazia ou em formato inesperado.")

    except ValueError as ve:
        print(f"ERRO na chamada do Agente {agent.name}: {ve}")
        actual_output = f"ERRO: Falha na execução do agente {agent.name} - {ve}"
    except Exception as e:
        print(f"ERRO inesperado na chamada do Agente {agent.name}: {e}")
        actual_output = f"ERRO: Falha inesperada na execução do agente {agent.name} - {e}"


    print("--> Saída do Agente (Primeiros 500 chars):")
    print(textwrap.shorten(actual_output, width=500, placeholder="...")) # Formata a saída para print
    print(f"===== FIM DA EXECUÇÃO: {agent.name} =====")
    return actual_output

# --- 5. Definições dos Agentes (Instructions) ---
# Copie as funções completas daqui para baixo, mantendo as mesmas instructions que definimos antes.

################################################
# --- Agente 1: Processador de Informação --- #
################################################
def agente_processador_informacao(conteudo_md_bruto):
    processador_info = Agent(
        name="agente_processador_informacao",
        model="gemini-1.5-flash", # Modelo que lida bem com contextos longos
        instruction="""
            Você é um Processador de Informações e Planejador de Conteúdo para LinkedIn.
            Sua tarefa é ler atentamente o conteúdo bruto fornecido (que pode ser extenso, como notas de um projeto ou aprendizado em formato Markdown ou texto simples).
            Com base nesse conteúdo, você deve extrair o tópico principal e os pontos mais relevantes,
            e estruturá-los em um formato conciso para ser usado por agentes subsequentes (redator e gerador de prompt de imagem).

            O conteúdo bruto pode descrever:
            - Um projeto (objetivos, etapas, tecnologias usadas, desafios, soluções, resultados, links para código).
            - Um aprendizado (cursos, aulas, conceitos novos, como aplicar).
            - Uma reflexão sobre a área (mercado, tendências, soft skills).
            - Notas gerais sobre um tema técnico.

            Seu objetivo é criar um "Plano de Post Detalhado" e identificar o "Tópico Principal".
            Este plano deve incluir:
            - O Tópico Principal claro e conciso (uma ou duas frases).
            - Pontos Chave a Cobrir: Uma lista (em bullet points) dos detalhes mais importantes, tecnologias, resultados, aprendizados, desafios superados, ou quaisquer fatos relevantes do conteúdo bruto que devem aparecer no post do LinkedIn. Pense no que é mais interessante para destacar em um post técnico/de carreira.
            - Links a Incluir: Se houver links relevantes mencionados no texto (GitHub, artigo, etc.), liste-os aqui.
            - Conceitos Visuais Sugeridos: Ideias breves para imagens ou diagramas que representem o conteúdo (ex: "laptop com chat", "diagrama de fluxo de dados", "ícones de tecnologias"), mantendo o estilo visual de Jonathas (minimalista, técnico, branco no preto).

            Formato de Saída:
            A sua resposta deve seguir estritamente o seguinte formato:

            TÓPICO PRINCIPAL: [Seu Tópico Principal aqui]

            PLANO DE POST DETALHADO:
            Pontos Chave a Cobrir:
            - [Ponto 1]
            - [Ponto 2]
            - ...
            Links a Incluir (se aplicável):
            - [Link 1]
            - [Link 2]
            - ...
            Conceitos Visuais Sugeridos (se aplicável):
            - [Sugestão Visual 1]
            - [Sugestão Visual 2]
            - ...

            Se uma seção (Links, Conceitos Visuais) não for aplicável ou não houver informação no conteúdo bruto, omita essa seção ou coloque "N/A".

            Seja direto e focado na extração e organização. Não escreva o post final. Priorize informações que demonstrem habilidades técnicas e proatividade, alinhado com a busca por emprego de Jonathas.
            """,
        description="Agente que processa conteúdo bruto (como Markdown de notas/projetos) e extrai o tópico principal e um plano detalhado para posts e imagens de LinkedIn."
    )
    entrada_do_agente = conteudo_md_bruto
    plano_bruto_gerado = call_agent(processador_info, entrada_do_agente)
    return plano_bruto_gerado

######################################
# --- Agente 3: Redator do Post --- #
######################################
def agente_redator_jonathas(topico_principal, plano_de_post_detalhado):
    redator_jonathas = Agent(
        name="agente_redator_jonathas",
        model="gemini-1.0-pro", # Modelos 'pro' são bons para tarefas de escrita
        instruction=f"""
            Você é um Redator de Conteúdo especializado em LinkedIn, com foco na área de Tecnologia, Análise de Dados e IA no Brasil.
            Você escreve rascunhos de posts para o perfil de Jonathas Martins da Rocha, mimetizando seu estilo autêntico e profissional.

            Sua missão é transformar o 'Tópico Principal' e o 'Plano de Post Detalhado' fornecidos em um RASCUNHO de post para LinkedIn.
            O rascunho deve ser engajador para profissionais da área, destacar as habilidades e conhecimentos de Jonathas (Python, Análise de Dados, IA, BI, etc.),
            e contribuir explicitamente ou implicitamente para seu objetivo de encontrar novas oportunidades de emprego, mostrando proatividade e aplicação prática.

            Diretrizes de Estilo e Estrutura (Baseado nos posts de Jonathas):
            1.  Tom: Profissional, direto, entusiasmado com tecnologia e aprendizado. Focar no "como" e "porquê".
            2.  Linguagem: Português do Brasil (PT-BR), claro e conciso.
            3.  Estrutura:
                -   Comece com um gancho inicial forte (frase curta, pergunta, referência a algo anterior).
                -   Desenvolva o conteúdo em parágrafos curtos. Use listas (bullet points ✨) para destacar pontos-chave, etapas ou características, se apropriado.
                -   Explique brevemente conceitos técnicos importantes (como fez com RAG).
                -   Se fizer sentido, conecte o post a projetos anteriores (referenciando-os, se possível com link) ou a planos futuros.
                -   Inclua links relevantes (GitHub, posts anteriores, etc.) se o 'Plano de Post Detalhado' contiver essa informação na seção "Links a Incluir".
            4.  Elementos Visuais (Texto): Use emojis relevantes com moderação (🚀, ✨, 🇧🇷, 👀, 🤖). Use espaçamento para facilitar a leitura.
            5.  Alinhamento com Objetivos: Enquadre o conteúdo para demonstrar as habilidades de Jonathas listadas em seu perfil. Mostre proatividade (iniciar projetos, buscar aprendizado), capacidade de aplicar conhecimento (projetos) e profissionalismo.
            6.  Hashtags: Gere um bloco de hashtags relevantes e estratégicas no final do post. Inclua termos técnicos (do post e do perfil do Jonathas), hashtags de tech brasileira (#DevBR, #TechBrasil, #Desenvolvimento), e hashtags sobre carreira, aprendizado e inovação (#Carreira, #AprendizadoContinuo, #ProjetosPessoais, #Inovação, #DataScience, #IA, #Python, #BI, etc.). Gere entre 5 e 15 hashtags, buscando relevância máxima.

            O resultado deve ser o rascunho COMPLETO do post, formatado para o LinkedIn.
            """,
        description="Agente redator de RASCUNHOS de posts profissionais para LinkedIn, no estilo de Jonathas Martins da Rocha, focado em Tech e Data."
    )
    entrada_do_agente_redator = f"Tópico Principal: {topico_principal}\nPlano de Post Detalhado:\n{plano_de_post_detalhado}"
    rascunho = call_agent(redator_jonathas, entrada_do_agente_redator)
    return rascunho

#########################################
# --- Agente 2: Revisor do Post --- #
#########################################
def agente_revisor_jonathas(topico_principal, plano_de_post_detalhado, rascunho_post):
    revisor = Agent(
        name="agente_revisor_jonathas",
        model="gemini-1.0-pro", # Modelo bom para tarefas de revisão e edição
        instruction="""
            Você é um Revisor de Conteúdo e Editor especializado em posts de LinkedIn para profissionais de Tecnologia/Dados,
            atuando como um editor final para os posts de Jonathas Martins da Rocha.

            Sua tarefa é analisar o 'Rascunho do Post' gerado pelo agente redator, comparando-o com o 'Tópico Principal' e o 'Plano de Post Detalhado' originais.
            Verifique se o post:
            1.  Representa fielmente o conteúdo e os pontos chave do plano.
            2.  Adere ao estilo e tom de Jonathas (profissional, direto, entusiasmado, PT-BR), conforme as diretrizes: Tom direto e focado no "como/porquê", Linguagem clara, Estrutura com gancho/parágrafos curtos/listas/explicações, uso moderado de emojis (🚀, ✨, 🇧🇷, 👀, 🤖), espaçamento.
            3.  Efetivamente demonstra suas habilidades técnicas e proatividade, alinhado com seu objetivo de busca de emprego.
            4.  Está bem estruturado, claro e SEM erros gramaticais/ortográficos ou de pontuação.
            5.  Possui um bloco de hashtags relevantes e no formato esperado no final.

            Revise o rascunho de ponta a ponta. Corrija quaisquer erros encontrados. Ajuste a clareza, a fluidez e o tom se necessário para torná-lo mais impactante e alinhado com o estilo de Jonathas. Garanta que o post finalize de forma profissional, incentivando a leitura e demonstração de expertise.

            O objetivo é entregar a versão FINAL e polida do texto do post de LinkedIn. Sua resposta deve ser APENAS o texto FINAL do post.
            """,
        description="Agente que revisa e edita rascunhos de posts de LinkedIn para garantir clareza, estilo, gramática e alinhamento com objetivos de carreira."
    )
    entrada_para_revisor = f"Tópico Principal: {topico_principal}\nPlano de Post Detalhado:\n{plano_de_post_detalhado}\n\nRascunho do Post a Revisar:\n{rascunho_post}"
    post_final = call_agent(revisor, entrada_para_revisor)
    return post_final

#########################################
# --- Agente 4: Gerador de Prompt de Imagem --- #
#########################################
def agente_gerador_prompt_imagem_jonathas(topico_principal, plano_de_post_detalhado):
    gerador_prompt_imagem = Agent(
        name="agente_gerador_prompt_imagem_jonathas",
        model="gemini-1.0-pro", # 'Pro' pode ser melhor para gerar texto descritivo
        instruction=f"""
            Você é um especialista em traduzir conceitos técnicos e de marketing para prompts visuais,
            especialmente no estilo minimalista e com foco em tecnologia, dados e IA.
            Sua tarefa é criar um prompt detalhado para uma ferramenta de geração de imagens AI,
            baseado no 'Tópico Principal' e no 'Plano de Post Detalhado' (incluindo "Conceitos Visuais Sugeridos") fornecidos.

            O prompt gerado deve instruir a ferramenta a criar uma imagem no estilo visual dos posts de Jonathas Martins da Rocha:
            1.  **Estilo Visual:** Minimalista, Flat Design, Line Art (contornos/linhas finas), Limpo, Conceitual, Diagramático (se apropriado). Use termos como "vector art", "line art", "minimal", "clean".
            2.  **Paleta de Cores:** **Elementos BRANCOS ou cinza CLARO em um fundo PRETO PURO (#000000)**. Monocromático branco/claro no preto. Use termos como "white on black background", "monochromatic".
            3.  **Conteúdo:** Deve representar visualmente o 'Tópico Principal' e os conceitos-chave ou as "Conceitos Visuais Sugeridos" listados no plano detalhado. Use ícones simples, diagramas conceituais, representações esquemáticas de sistemas (laptop, servidor, banco de dados, cérebro/IA, chat bubbles, setas de fluxo, escudos de segurança). Traduza os conceitos em elementos visuais concretos.
            4.  **Composição:** A imagem deve ser clara e focar nos elementos conceituais. Deve ter uma composição que permita sobreposição de texto (para título ou subtítulos do post), talvez com espaços vazios na parte superior ou inferior. Use termos como "conceptual illustration", "diagrammatic", "ample negative space for text".
            5.  **Formato:** O output deve ser APENAS o texto do prompt para a ferramenta de geração de imagem AI. Comece diretamente com a descrição visual. Inclua parâmetros comuns de ferramentas se apropriado (ex: `--ar 1:1` para aspect ratio quadrado).

            Traduza os conceitos do plano de post (especialmente a seção "Conceitos Visuais Sugeridos") em elementos visuais concretos para o prompt. Seja descritivo sobre o estilo e os elementos.

            Exclua do prompt da imagem:
            -   Textos longos ou frases completas que você quer que apareçam NA IMAGEM (ferramentas de imagem não geram texto confiável).
            -   Qualquer coisa que não seja a descrição visual detalhada para a ferramenta AI.
            """,
        description="Agente que gera prompts para ferramentas de AI de imagem, focando no estilo visual minimalista, branco no preto, para posts técnicos de LinkedIn."
    )
    entrada_para_gerar_prompt = f"Tópico Principal do Post: {topico_principal}\nDetalhes e Conceitos Visuais do Post:\n{plano_de_post_detalhado}"
    prompt_imagem = call_agent(gerador_prompt_imagem, entrada_para_gerar_prompt)
    return prompt_imagem


# --- 6. Lógica de Conexão dos Agentes (Pipeline) ---
# A lógica do pipeline permanece a mesma, orquestrando a chamada aos agentes.
def pipeline_gerar_post_e_imagem(conteudo_bruto: str) -> tuple[str | None, str | None]:
    """
    Orquestra o pipeline de agentes para gerar um post de LinkedIn e um prompt de imagem
    a partir de conteúdo bruto.

    Args:
        conteudo_bruto: O conteúdo do arquivo .md ou .txt a ser processado.

    Returns:
        Uma tupla contendo o texto final do post e o prompt da imagem,
        ou (None, None) se ocorrer um erro no parseamento inicial.
    """
    print("\n===== INICIANDO PIPELINE =====")
    print("--> Conteúdo Bruto de Entrada (Primeiros 500 chars):")
    print(textwrap.shorten(conteudo_bruto, width=500, placeholder="..."))

    # 1. Processa o conteúdo bruto para gerar o plano
    plano_bruto_gerado = agente_processador_informacao(conteudo_bruto)
    print("\n--- Transição: Saída do Processador -> Parseamento ---")

    # 2. Parseia o plano bruto gerado nas variáveis necessárias
    print("===== Executando Parseamento (Código Python) =====")
    topico_principal = ""
    plano_de_post_detalhado = ""
    # Verifica se a saída do processador contém o marcador PLANO DE POST DETALHADO
    if "PLANO DE POST DETALHADO:" in plano_bruto_gerado:
        partes = plano_bruto_gerado.split("PLANO DE POST DETALHADO:", 1)
        # Tenta extrair o tópico principal
        if "TÓPICO PRINCIPAL:" in partes[0]:
            topico_linha = partes[0].split("TÓPICO PRINCIPAL:", 1)[1].strip()
            topico_principal = topico_linha
        else:
             # Se o marcador de tópico não for encontrado, usa um padrão ou as primeiras linhas
             topico_principal = partes[0].strip().splitlines()[0] if partes[0].strip() else "Conteúdo Processado"
             print(f"Aviso: Marcador 'TÓPICO PRINCIPAL:' não encontrado. Usando '{topico_principal}' como tópico provisório.")

        plano_de_post_detalhado = partes[1].strip()
        print(f"--> Variável 'topico_principal' gerada: '{topico_principal}'")
        print(f"--> Variável 'plano_de_post_detalhado' gerada (Primeiras 200 chars):\n{textwrap.shorten(plano_de_post_detalhado, width=200, placeholder='...')}")
    else:
        print("ERRO ao parsear a saída do Agente Processador: Marcador 'PLANO DE POST DETALHADO:' não encontrado.")
        print("===== FIM DO PIPELINE (COM ERRO NO PARSEAMENTO) =====")
        return None, None
    print("===== FIM DO PARSEAMENTO =====")
    print("\n--- Transição: Variáveis Parseadas -> Redator e Gerador de Imagem ---")


    # 3. Redige o rascunho do post usando o plano
    rascunho_post = agente_redator_jonathas(topico_principal, plano_de_post_detalhado)
    print("\n--- Transição: Saída do Redator -> Revisor ---")


    # 4. Revisa e finaliza o post usando o rascunho e o plano (para contexto de estilo/conteúdo)
    post_final = agente_revisor_jonathas(topico_principal, plano_de_post_detalhado, rascunho_post)
    print("\n--- Transição: Saída do Revisor -> Resultado Final ---")

    # 5. Gera o prompt para a imagem usando o tópico e o plano (para extrair conceitos visuais)
    # Nota: Esta execução pode ocorrer em paralelo com o Redator/Revisor na vida real,
    # mas aqui no código sequencial, acontece depois do Revisor.
    prompt_imagem = agente_gerador_prompt_imagem_jonathas(topico_principal, plano_de_post_detalhado)
    print("\n--- Transição: Saída do Gerador de Imagem -> Resultado Final ---")


    # 6. Retorna os resultados finais
    print("\n===== PIPELINE CONCLUÍDO COM SUCESSO =====")
    return post_final, prompt_imagem


# --- 7. Lógica de Execução Principal (Movemos tudo para cá) ---
# Este bloco só executa quando o script é rodado diretamente.
if __name__ == "__main__":
    # --- Configurações ---
    # Defina o caminho para o seu diretório ou arquivo de entrada.
    # <-- SUBSTITUA ESTE CAMINHO PELO REAL CAMINHO DO SEU DIRETÓRIO OU ARQUIVO -->
    caminho_entrada = r"C:\Users\jonat\Documents\GitHub\Readnator\relatorios\Dashboard_web.txt" # Pode ser um diretório ou um arquivo específico (.md ou .txt)

    # Crie o diretório de saída, se não existir
    diretorio_saida = "./posts_gerados"
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
        print(f"Diretório de saída criado: {diretorio_saida}")

    # --- Lógica de Encontrar Arquivos ---
    caminhos_arquivos_a_processar = []

    if not os.path.exists(caminho_entrada):
        print(f"ERRO: O caminho de entrada '{caminho_entrada}' não foi encontrado.")
        sys.exit(1) # Sai do script com erro

    if os.path.isfile(caminho_entrada):
        # Se for um arquivo único, verifica a extensão e adiciona se for .md ou .txt
        if caminho_entrada.lower().endswith(('.md', '.txt')):
            caminhos_arquivos_a_processar.append(caminho_entrada)
            print(f"Caminho de entrada é um arquivo único: {caminho_entrada}")
        else:
            print(f"ERRO: O arquivo único '{caminho_entrada}' não é .md nem .txt. Nenhum arquivo para processar.")

    elif os.path.isdir(caminho_entrada):
        # Se for um diretório, encontra todos os arquivos .md e .txt dentro dele
        print(f"Caminho de entrada é um diretório: {caminho_entrada}")
        caminhos_arquivos_a_processar = glob.glob(os.path.join(caminho_entrada, "*.md"))
        caminhos_arquivos_a_processar.extend(glob.glob(os.path.join(caminho_entrada, "*.txt"))) # Adiciona arquivos .txt

        if not caminhos_arquivos_a_processar:
            print(f"Nenhum arquivo .md ou .txt encontrado no diretório: {caminho_entrada}")

    else:
         print(f"ERRO: O caminho de entrada '{caminho_entrada}' não é um arquivo nem um diretório válido.")
         sys.exit(1) # Sai do script com erro


    # --- Lógica de Iteração e Processamento ---
    if not caminhos_arquivos_a_processar:
        print("Nenhum arquivo para processar. Encerrando.")
    else:
        print(f"\n===== INICIANDO PROCESSAMENTO DE {len(caminhos_arquivos_a_processar)} ARQUIVO(S) =====")

        # Itera sobre cada arquivo a processar
        for caminho_arquivo in caminhos_arquivos_a_processar:
            nome_arquivo = os.path.basename(caminho_arquivo) # Pega só o nome do arquivo (ex: meu_projeto.md)
            nome_base, _ = os.path.splitext(nome_arquivo) # Pega o nome sem a extensão (ex: meu_projeto)

            print(f"\n--- Processando arquivo: {nome_arquivo} ---")

            try:
                # Leia o conteúdo do arquivo
                # Usamos 'r' para leitura e 'utf-8' para compatibilidade com vários caracteres
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo_do_arquivo = f.read()

                if not conteudo_do_arquivo.strip():
                    print(f"Arquivo {nome_arquivo} está vazio. Pulando.")
                    continue # Pula para o próximo arquivo se estiver vazio

                # Chama o pipeline com o conteúdo lido
                post_final, prompt_imagem_gerado = pipeline_gerar_post_e_imagem(conteudo_do_arquivo)

                # Salva ou imprime os resultados
                if post_final is not None and prompt_imagem_gerado is not None:
                    # Salva o post em um arquivo .txt
                    caminho_post_saida = os.path.join(diretorio_saida, f"{nome_base}_post.txt")
                    with open(caminho_post_saida, 'w', encoding='utf-8') as f:
                        f.write("Testo do post:\n\n")
                        f.write(post_final)
                    print(f"Post gerado salvo em: {caminho_post_saida}")

                    # Salva o prompt da imagem em um arquivo .txt
                    caminho_prompt_saida = os.path.join(diretorio_saida, f"{nome_base}_prompt_imagem.txt")
                    with open(caminho_prompt_saida, 'w', encoding='utf-8') as f:
                        f.write("Prompt para gera img:\n\n")
                        f.write(prompt_imagem_gerado)
                    print(f"Prompt de imagem gerado salvo em: {caminho_prompt_saida}")

                else:
                    print(f"Falha ao gerar post e prompt para o arquivo: {nome_arquivo} (Pipeline retornou None)")

            except FileNotFoundError:
                 print(f"ERRO: Arquivo não encontrado: {caminho_arquivo}")
            except Exception as e:
                print(f"Ocorreu um erro inesperado ao processar o arquivo {nome_arquivo}: {e}")
                # Opcional: logar o erro completo trace

        print(f"\n===== PROCESSAMENTO DE DIRETÓRIO CONCLUÍDO =====")
        print(f"Verifique o diretório '{diretorio_saida}' para os arquivos gerados.")