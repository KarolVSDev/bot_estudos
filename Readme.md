# Analisador Estratégico de Editais (UFAM 2026)

Robô desenvolvido em Python para extração de dados e análise de relevância de tópicos em editais de concursos e guias de estudo.

O foco principal é automatizar a identificação dos assuntos mais cobrados, otimizando o tempo de planejamento do estudante.

## Problema

Editais de concursos públicos, como o da UFAM 2026, possuem centenas de tópicos. Identificar quais assuntos têm maior incidência de questões manualmente é um processo lento e sujeito a erros.

Este robô resolve a falta de dados estruturados em arquivos PDF.

## Funcionalidades

- Extração automatizada: lê arquivos PDF e identifica padrões de Assunto vs Quantidade de Questões.
- Filtro inteligente (Regex): ignora ruídos do PDF e captura apenas os tópicos numerados do conteúdo programático (ex: 1.1, 2.3.1).
- Exportação de dados: gera um arquivo Excel (.xlsx) com o ranking completo.
- Visualização de dados: gera gráficos (Top 15 e geral) em formato PNG para análise visual rápida.

## Tecnologias Utilizadas

- Python 3.x
- Pandas: manipulação e ordenação de dados.
- Matplotlib: geração de gráficos estatísticos.
- PyPDF: extração de texto de arquivos PDF.
- BotCity Maestro SDK: integração para orquestração de robôs (RPA).
- Pathlib: gerenciamento de caminhos de arquivos de forma multiplataforma.

## Arquitetura do Projeto

### Fluxo de Execução

![Diagrama de atividade](resources/diagrama%20de%20atividade.png)

## Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Prepare o arquivo:

Coloque o PDF do edital na pasta resources.

4. Execute o robô:

```bash
python bot.py
```

## Resultados Gerados

Após a execução, o robô entrega:

- Ranking_Estudo_UFAM.xlsx
- Grafico_Top_15_Assuntos.png
- Grafico_Todos_os_Topicos.png