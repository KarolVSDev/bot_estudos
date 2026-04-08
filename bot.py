from playwright.sync_api import sync_playwright
import pandas as pd
import re
import smtplib
import logging
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# ================================
# CONFIG — carregado do arquivo .env
# ================================
EMAIL = os.getenv("EMAIL")
SENHA = os.getenv("SENHA")

URL_LOGIN = os.getenv("URL_LOGIN", "https://www.tecconcursos.com.br/login")
CONCURSO_BUSCA = os.getenv("CONCURSO_BUSCA", "UFAM")

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_EMAIL = os.getenv("SENHA_EMAIL")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")


# ================================
# ENVIO DE E-MAIL
# ================================
def enviar_email(arquivos: list[str]):
    msg = EmailMessage()
    msg["Subject"] = f"Ranking UFAM — {len(arquivos)} disciplina(s)"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg.set_content("Segue(m) em anexo o(s) arquivo(s) gerado(s) pela automação.")

    for caminho in arquivos:
        p = Path(caminho)
        if p.exists():
            msg.add_attachment(
                p.read_bytes(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=p.name,
            )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
        smtp.send_message(msg)

    logging.info(f"E-mail enviado para {EMAIL_DESTINATARIO} com {len(arquivos)} anexo(s)!")


# ================================
# FLUXO PRINCIPAL
# ================================
def rodar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.evaluate("window.moveTo(0,0); window.resizeTo(screen.width, screen.height);")

        # --- 1. LOGIN ---
        logging.info("Acessando página de login...")
        page.goto(URL_LOGIN)
        page.fill("input[type='email'], input[name='email']", EMAIL)
        page.fill("input[type='password'], input[name='password']", SENHA)
        page.click("button[type='submit']")
        logging.info("Aguardando resolução do captcha e carregamento...")
        page.wait_for_load_state("networkidle")
        logging.info("Login realizado!")

        # --- 2. CLICAR EM CONCURSOS ---
        logging.info("Clicando em 'Concursos'...")
        page.wait_for_selector("text=Concursos", timeout=15000)
        page.click("text=Concursos")

        page.wait_for_load_state("networkidle")
        logging.info("Página de Concursos carregada!")

        # --- 3. PESQUISAR CONCURSO ---
        logging.info(f"Pesquisando por '{CONCURSO_BUSCA}'...")
        page.wait_for_selector("#valor-busca", timeout=15000)
        page.click("#valor-busca")
        page.fill("#valor-busca", CONCURSO_BUSCA)
        page.keyboard.press("Enter")

        page.wait_for_load_state("networkidle")
        logging.info(f"Pesquisa por '{CONCURSO_BUSCA}' realizada!")

        # --- 4. CLICAR NO CARGO ---
        logging.info("Clicando no cargo desejado...")
        SELETOR_CARGO = "#resultado-busca > div > div.resultado-conteudo.ng-scope > div:nth-child(1) > div.edital-concursos > div:nth-child(2) > div.edital-concurso-informacoes > div.concurso-link > a"
        page.wait_for_selector(SELETOR_CARGO, timeout=15000)
        page.click(SELETOR_CARGO)

        page.wait_for_load_state("networkidle")
        logging.info("Cargo selecionado!")

        # --- 5. CLICAR NO MENU DE DETALHES ---
        logging.info("Clicando no menu de detalhes...")
        SELETOR_MENU = "#pesquisa-concursos > div > div > div.detalhes > div.detalhes-complementos.ng-scope > nav > span.detalhes-complementos-menu-item.menu-item-link"
        page.wait_for_selector(SELETOR_MENU, timeout=15000)
        page.click(SELETOR_MENU)

        page.wait_for_load_state("networkidle")
        logging.info("Menu de detalhes clicado!")

        # --- 6. COLETAR TODAS AS DISCIPLINAS ---
        logging.info("Coletando disciplinas disponíveis...")
        page.wait_for_selector("#concurso-guias-de-estudo", timeout=15000)

        # Lê href e nome de cada disciplina de uma vez (evita referencias obsoletas)
        disciplinas = page.evaluate("""
            () => {
                const items = document.querySelectorAll('#concurso-guias-de-estudo .cadernos-item-disciplina');
                return Array.from(items).map(item => {
                    const link = item.querySelector('span:nth-child(2) a');
                    const nomeEl = item.querySelector('div:first-child');
                    return {
                        nome: nomeEl ? nomeEl.innerText.trim() : (link ? link.innerText.trim() : 'Disciplina'),
                        href: link ? link.href : null
                    };
                }).filter(d => d.href);
            }
        """)

        logging.info(f"{len(disciplinas)} disciplina(s) encontrada(s).")

        # --- 7. EXTRAIR E SALVAR CADA DISCIPLINA ---
        arquivos_gerados = []
        for i, disc in enumerate(disciplinas, 1):
            nome = disc["nome"] or f"Disciplina_{i}"
            href = disc["href"]

            # Sanitiza nome para usar como nome de arquivo
            nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", nome)[:60].strip()

            logging.info(f"[{i}/{len(disciplinas)}] Acessando: {nome_arquivo}")
            page.goto(href)
            page.wait_for_load_state("networkidle")

            texto = page.inner_text("body")
            dados = []
            linhas = texto.splitlines()
            for idx, linha in enumerate(linhas):
                linha = linha.strip()
                if not linha:
                    continue
                match_qtd = re.match(r'^(\d+|uma)\s+questões?$', linha, re.IGNORECASE)
                if match_qtd:
                    qtd_raw = match_qtd.group(1)
                    qtd = 1 if qtd_raw.lower() == "uma" else int(qtd_raw)
                    assunto = ""
                    for j in range(idx - 1, -1, -1):
                        candidato = linhas[j].strip()
                        if candidato:
                            assunto = candidato
                            break
                    if assunto:
                        dados.append({"Assunto": assunto, "Qtd de Questões": qtd})

            if not dados:
                logging.warning(f"Nenhum dado encontrado para {nome_arquivo}.")
            else:
                df = pd.DataFrame(dados).drop_duplicates(subset="Assunto")
                df = df.sort_values("Qtd de Questões", ascending=False).reset_index(drop=True)
                pasta_saida = Path("resultados")
                pasta_saida.mkdir(exist_ok=True)
                arquivo = pasta_saida / f"Ranking_{nome_arquivo}.xlsx"
                with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                    ws = writer.sheets["Sheet1"]
                    ws.column_dimensions["A"].width = max(df["Assunto"].str.len().max() + 2, 30)
                arquivos_gerados.append(str(arquivo))
                logging.info(f"Salvo: {arquivo} ({len(df)} tópicos)")

        logging.info("Todas as disciplinas extraídas!")

        logging.info("Fechando o navegador...")
        browser.close()

        if arquivos_gerados:
            logging.info("Enviando por e-mail...")
            enviar_email(arquivos_gerados)


# ================================
# EXECUÇÃO
# ================================
if __name__ == "__main__":
    rodar()