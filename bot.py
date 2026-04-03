import pandas as pd
from pypdf import PdfReader
import re 
from botcity.maestro import *
from pathlib import Path
import matplotlib.pyplot as plt

# Desabilita erro se não estiver no Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def extrair_dados_pdf(caminho_pdf):
    reader = PdfReader(caminho_pdf)
    dados = []
    padrao_topico = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
    
    # Percorre todas as páginas do PDF
    for page in reader.pages:
        texto = page.extract_text()
        
        # Regex para pegar o nome do assunto e a quantidade de questões
        # Exemplo: "Licitações e Contratos ... 415 questões"
        padrao = r"([\w\s,()º./-]+?)\s+(\d+|uma)\s+questões?"
        matches = re.findall(padrao, texto)
        
        for assunto, qtd in matches:
            assunto_limpo = assunto.strip()

            # Mantém apenas assuntos que seguem a numeração do edital (1., 1.2., 3.5.1. etc.)
            if not padrao_topico.match(assunto_limpo):
                continue

            # Converte "uma" para 1 e limpa o texto
            valor = 1 if qtd == "uma" else int(qtd)
            dados.append({"Assunto": assunto_limpo, "Questões": valor})
            
    return dados


def gerar_grafico_assuntos_mais_cobrados(df_ranking, caminho_saida, top_n=None):
    if top_n is None:
        df_grafico = df_ranking.copy()
    else:
        df_grafico = df_ranking.head(top_n).copy()

    if df_grafico.empty:
        return

    # Inverte para exibir o maior valor no topo em gráfico horizontal
    df_grafico = df_grafico.iloc[::-1]

    altura = max(8, len(df_grafico) * 0.35)
    plt.figure(figsize=(14, altura))
    plt.barh(df_grafico["Assunto"], df_grafico["Questões"], color="#1f77b4")
    if top_n is None:
        plt.title("Todos os Assuntos por Quantidade de Questões")
    else:
        plt.title(f"Top {top_n} Assuntos Mais Cobrados")
    plt.xlabel("Quantidade de Questões")
    plt.ylabel("Assunto")
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()

def main():
    # 1. Caminho do arquivo PDF dentro da pasta resources
    base_dir = Path(__file__).resolve().parent
    arquivo_pdf = base_dir / "resources" / "Guia de Conhecimentos Específicos para Assistente em Administração - UFAM - 2026.pdf"
    if not arquivo_pdf.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_pdf}")
    
    print(f"Lendo arquivo: {arquivo_pdf.name}")
    lista_assuntos = extrair_dados_pdf(arquivo_pdf)
    
    # 2. Criar o DataFrame com Pandas
    df = pd.DataFrame(lista_assuntos)
    
    # 3. Ordenar todos os tópicos por volume de questões
    print("Organizando dados e montando ranking...")
    df_ranking = df.sort_values(by="Questões", ascending=False)
    
    # 4. Gerar Relatório de Relevância completo (sem imprimir tópicos no terminal)
    
    # 5. Salvar o ranking completo
    df_ranking.to_excel("Ranking_Estudo_UFAM.xlsx", index=False)
    print("\n Excel gerado com sucesso!")

    # 6. Gerar gráfico com todos os tópicos
    caminho_grafico_todos = "Grafico_Todos_os_Topicos.png"
    gerar_grafico_assuntos_mais_cobrados(df_ranking, caminho_grafico_todos, top_n=None)
    print(f"Gráfico gerado com sucesso: {caminho_grafico_todos}")

    # 7. Gerar gráfico com Top 15 assuntos mais cobrados
    caminho_grafico_top15 = "Grafico_Top_15_Assuntos.png"
    gerar_grafico_assuntos_mais_cobrados(df_ranking, caminho_grafico_top15, top_n=15)
    print(f"Gráfico gerado com sucesso: {caminho_grafico_top15}")

if __name__ == '__main__':
    main()