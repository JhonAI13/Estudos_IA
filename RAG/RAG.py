import os, re, sys, time
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status
from rich.syntax import Syntax

# LangChain RAG
from langchain.docstore.document import Document as Doc
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Constantes
API_URL = "http://127.0.0.1:1234/v1/chat/completions"
THINK_PATTERN = r'(<think>)(.*?)(</think>)'

def load_md_sections(path: str) -> List[Doc]:
    """
    Lê um arquivo Markdown e divide o conteúdo em seções usando títulos (# a ######).
    Cada seção vira um documento separado para facilitar o split.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Divide no início de cada título Markdown
    sections = re.split(r"(?=^#{1,6} )", content, flags=re.MULTILINE)
    return [Doc(page_content=sec.strip()) for sec in sections if sec.strip()]

class RAGMonitor:
    def __init__(self, console: Console):
        self.console = console
        self.spinner = "dots"
    def _show_step(self, message: str, emoji: str = "🔄"):
        return self.console.status(
            f"{emoji} [bold yellow]{message}[/bold yellow]",
            spinner=self.spinner,
            spinner_style="cyan"
        )
    def loading_document(self, path: str):
        with self._show_step(f"Carregando documento: {Path(path).name}"):
            time.sleep(0.5)
    def splitting_chunks(self, total_chunks: int):
        self.console.print(
            Panel(f"[green]✓ Documento dividido em [bold]{total_chunks}[/bold] chunks[/green]",
                  title="Processamento RAG")
        )
    def building_index(self):
        with self._show_step("Construindo índice FAISS", "🔍"):
            time.sleep(0.5)
    def searching_context(self, query: str):
        self.console.print(
            Panel.fit(f"[bold white]{query}[/bold white]",
                      title="🔎 Buscando Contexto", border_style="magenta")
        )
    def show_context(self, context: str, top_k: int):
        panel = Panel(
            Syntax(context, "markdown", line_numbers=True, word_wrap=True),
            title=f"📚 Contexto Relevante (Top {top_k})",
            border_style="dim"
        )
        self.console.print(panel)

class RAGSystem:
    def __init__(self):
        load_dotenv()
        self.console = Console()
        self.monitor = RAGMonitor(self.console)
        self.config = self._load_config()
        self.vector_db = self._initialize_rag()
        self.chat_history = self._create_initial_history()

    def _load_config(self) -> dict:
        return {
            "model": os.getenv("MODEL", "bode-7b-alpaca-pt-br"),
            "temperature": float(os.getenv("TEMPERATURE", 0.7)),
            "document": os.getenv("DOCUMENT_PATH", "texto.txt"),
            "chunk_size": int(os.getenv("CHUNK_SIZE", 512)),
            "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", 64)),
            "top_k": int(os.getenv("TOP_K", 3)),
            "embeddings": HuggingFaceEmbeddings(
                model_name=os.getenv("EMBEDDINGS_MODEL",
                                     "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"),
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': False}
            )
        }

    def _initialize_rag(self) -> FAISS:
        try:
            self.monitor.loading_document(self.config["document"])
            # carregador customizado para Markdown grande
            documents = load_md_sections(self.config["document"])
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config["chunk_size"],
                chunk_overlap=self.config["chunk_overlap"]
            )
            chunks = splitter.split_documents(documents)
            self.monitor.splitting_chunks(len(chunks))
            self.monitor.building_index()
            return FAISS.from_documents(chunks, self.config["embeddings"])
        except Exception as e:
            self.console.print(Panel(f"[red]ERRO RAG: {e}[/red]", title="Falha no Sistema"))
            sys.exit(1)

    def _create_initial_history(self) -> List[dict]:
        return [{
            'role': 'system',
            'content': "Você é um assistente especialista que responde em português. Contexto:\n{context}"
                        "Escreva sempre usando os recursos do markdonw"
        }]

    def _get_api_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("API_KEY")}'
        }

    def _extract_think(self, text: str) -> tuple:
        match = re.search(THINK_PATTERN, text, re.DOTALL)
        return (match.group(2).strip(), text.replace(match.group(0), '').strip()) \
            if match else ('[sem análise]', text.strip())

    def _retrieve_context(self, query: str) -> str:
        self.monitor.searching_context(query)
        docs = self.vector_db.similarity_search(query, k=self.config["top_k"])
        ctx = "\n".join([f"📄 Chunk {i+1}:\n{d.page_content}\n"
                         for i, d in enumerate(docs)])
        self.monitor.show_context(ctx, self.config["top_k"])
        return ctx

    def _format_response(self, resp: str):
        think, final = self._extract_think(resp)
        self.console.print(Panel(Markdown(think), title="🧠 Análise Interna", border_style="yellow"))
        time.sleep(0.5)
        self.console.print(Panel(Markdown(final), title="💡 Resposta Final", border_style="blue"))

    def run(self):
        self.console.print(Panel.fit(
            "[bold green]Sistema RAG Inteligente[/]\n"
            f"[cyan]Documento:[/] [bold white]{Path(self.config['document']).name}[/]\n"
            f"[cyan]Modelo LLM:[/] [bold white]{self.config['model']}[/]",
            title="🤖 Assistente de Conhecimento", border_style="magenta"
        ))
        while True:
            try:
                user_input = self.console.input("\n[bold cyan]>> Você:[/bold cyan] ").strip()
                if user_input.lower() in ('sair', 'exit'):
                    self.console.print(Panel("[green]Até logo! 👋[/green]", title="Encerramento"))
                    break
                context = self._retrieve_context(user_input)
                self.chat_history[0]['content'] = self.chat_history[0]['content'].format(context=context)
                self.chat_history.append({'role': 'user', 'content': user_input})
                response = requests.post(
                    API_URL,
                    headers=self._get_api_headers(),
                    json={
                        'model': self.config["model"],
                        'messages': self.chat_history,
                        'temperature': self.config["temperature"]
                    }
                ).json()
                assistant_msg = response['choices'][0]['message']['content']
                self.chat_history.append({'role': 'assistant', 'content': assistant_msg})
                # self._format_response(assistant_msg)
            except Exception as e:
                self.console.print(Panel(f"[red]ERRO: {e}[/red]", title="Falha na Operação"))

if __name__ == "__main__":
    chat_system = RAGSystem()
    chat_system.run()
