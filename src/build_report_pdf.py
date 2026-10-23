"""Build the capstone report from verified, saved project outputs."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from xml.sax.saxutils import escape

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "capstone-mpl-cache"))
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, KeepTogether, HRFlowable,
)

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "reports/Relatorio_Capstone.pdf"
RESULTS = json.loads((ROOT / "outputs/analysis_results.json").read_text(encoding="utf-8"))
API_ROWS = sum(1 for _ in open(ROOT / "data/processed/api_launches_normalized.csv", encoding="utf-8")) - 1
SCRAPE_ROWS = sum(1 for _ in open(ROOT / "data/raw/wikipedia_launch_history.csv", encoding="utf-8")) - 1
NAVY = colors.HexColor("#12304A")
BLUE = colors.HexColor("#225EA8")
TEAL = colors.HexColor("#41B6C4")
INK = colors.HexColor("#243746")
PALE = colors.HexColor("#EDF4F8")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=17, textColor=BLUE, alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=5, spaceAfter=7))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=BLUE, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12.2, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=INK, spaceAfter=2))
styles.add(ParagraphStyle(name="SmallWh", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.2, leading=9, textColor=colors.white, spaceAfter=2))
styles.add(ParagraphStyle(name="Captionx", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=7.5, leading=9, textColor=colors.HexColor("#526878"), alignment=TA_CENTER, spaceAfter=5))
styles.add(ParagraphStyle(name="Calloutx", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.8, leading=12, textColor=NAVY, backColor=PALE, borderColor=TEAL, borderWidth=1, borderPadding=6, spaceBefore=3, spaceAfter=7))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def pct(value):
    return f"{value * 100:.1f}%".replace(".", ",")


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18 * mm, height - 12 * mm, "IBM Applied Data Science Capstone | SpaceX Falcon 9")
        canvas.setStrokeColor(TEAL)
        canvas.line(18 * mm, height - 14 * mm, width - 18 * mm, height - 14 * mm)
    canvas.setFillColor(colors.HexColor("#526878"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18 * mm, 10 * mm, "Relatório do Projeto Capstone em Ciência de Dados")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


def figure(cell, caption, max_height=61 * mm):
    path = ROOT / f"outputs/figures/eda_cell_{cell:02d}.png"
    if not path.exists():
        return P(f"Figura da célula {cell} não encontrada.", "Smallx")
    iw, ih = ImageReader(str(path)).getSize()
    width = 170 * mm
    height = min(max_height, width * ih / iw)
    return KeepTogether([Image(str(path), width=width, height=height), P(caption, "Captionx")])


def make_confusion_png():
    values = RESULTS["models"]["best_confusion_matrix"]
    fig, ax = plt.subplots(figsize=(5.3, 3.8))
    ax.imshow(values, cmap="Blues")
    ax.set_xticks([0, 1], labels=["Previsto 0", "Previsto 1"])
    ax.set_yticks([0, 1], labels=["Real 0", "Real 1"])
    ax.set_title(f"Matriz de confusão - {RESULTS['models']['best_by_cv_accuracy']}")
    for i in range(2):
        for j in range(2):
            color = "white" if values[i][j] > max(max(row) for row in values) * 0.55 else "#102a43"
            ax.text(j, i, str(values[i][j]), ha="center", va="center", color=color, fontsize=14)
    fig.tight_layout()
    target = ROOT / "outputs/figures/best_model_confusion_matrix.png"
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return target


def main():
    PDF.parent.mkdir(parents=True, exist_ok=True)
    confusion_png = make_confusion_png()
    res = RESULTS
    models = res["models"]
    story = [
        Spacer(1, 15 * mm),
        P("Relatório do Projeto Capstone<br/>em Ciência de Dados", "CoverTitle"),
        P("Previsão de pouso do primeiro estágio do Falcon 9", "SubTitle"),
        HRFlowable(width="45%", thickness=2, color=TEAL, hAlign="CENTER"),
        Spacer(1, 7 * mm),
        P("Resumo executivo", "H1x"),
        P("Este projeto reúne a coleta e análise de registros de lançamentos da SpaceX e constrói classificadores para estimar o sucesso do pouso do primeiro estágio do Falcon 9. A matriz de atributos fornecida contém 90 lançamentos e 80 colunas; sua correspondência foi validada por número do voo e categorias contra a tabela rotulada oficial da IBM. A variável `Class` tem 60 sucessos e 30 falhas."),
        P(f"Foram comparados Regressão Logística, SVM, KNN e Árvore de Decisão com busca de hiperparâmetros em validação cruzada estratificada de cinco partes. O modelo escolhido por acurácia média de validação cruzada foi {escape(models['best_by_cv_accuracy'])}; os resultados de teste e a matriz de confusão aparecem na seção de modelagem. O teste contém apenas 18 lançamentos, então os resultados são didáticos e exploratórios."),
        P("A coleta da API, o scraping histórico, o mapa Folium e o dashboard Dash foram executados e seus arquivos estão incluídos no projeto. O extrato da API, o scrape da Wikipedia e a tabela modelada têm escopos diferentes e foram mantidos separados.", "Calloutx"),
        P("Visão das etapas", "H2x"),
    ]
    status = [
        [P("Etapa", "SmallWh"), P("Artefato e evidência", "SmallWh")],
        [P("API SpaceX", "Smallx"), P(f"{API_ROWS} registros no JSON arquivado; tabela normalizada em `data/processed/api_launches_normalized.csv`.", "Smallx")],
        [P("Web scraping", "Smallx"), P(f"{SCRAPE_ROWS} linhas de lançamento da revisão da Wikipedia datada de 2020-11-06.", "Smallx")],
        [P("Preparação", "Smallx"), P("90 linhas e 80 atributos validados contra a tabela rotulada IBM.", "Smallx")],
        [P("EDA e SQL", "Smallx"), P("Gráficos do notebook original, consultas SQL e CSVs incluídos.", "Smallx")],
        [P("Folium e Dash", "Smallx"), P("Mapa HTML gerado; layout, endpoint e callback Dash testados.", "Smallx")],
        [P("Modelagem", "Smallx"), P("Quatro modelos ajustados com GridSearchCV; métricas e matriz no relatório.", "Smallx")],
    ]
    t = Table(status, [37 * mm, 133 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4E0E8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [t, PageBreak()]

    story += [
        P("1. Problema e objetivo", "H1x"),
        P("O objetivo é classificar o resultado do pouso do primeiro estágio do Falcon 9 a partir de atributos de voo, carga, órbita, local e hardware. `Class=1` indica pouso bem-sucedido; `Class=0` indica falha. As relações descritas são observacionais e não demonstram causalidade."),
        P("2. Coleta pela API SpaceX", "H1x"),
        P(f"O arquivo JSON arquivado do IBM Skills Network foi coletado e preservado em `data/raw/API_call_spacex_api.json`. Ele contém {API_ROWS} registros. Os campos de voo, data, foguete, plataforma, carga, núcleo, tentativas de pouso e falhas foram normalizados em `data/processed/api_launches_normalized.csv` ({API_ROWS} linhas e 18 campos). O conjunto arquivado tem cobertura maior que a amostra didática rotulada, por isso não foi misturado com ela."),
        P("3. Web scraping", "H1x"),
        P(f"Para manter o período histórico, foi usada a revisão 987426997 da página da Wikipedia, de 6 de novembro de 2020. `pandas.read_html` extraiu as tabelas de lançamentos; datas e números de voo foram limpos, registros sem data e duplicados removidos, e o recorte terminou em 5 de novembro de 2020. O CSV final contém {SCRAPE_ROWS} linhas numeradas. O esquema e a numeração da página diferem da tabela didática IBM de 90 registros; as fontes permanecem separadas."),
        P("4. Limpeza e preparação", "H1x"),
        P("A matriz `dataset_part_3.csv` (90 × 80) foi conferida contra `data/raw/dataset_part_2.csv` (90 × 18). O código valida número do voo, valores das categorias decodificadas e alinhamento antes de usar a coluna oficial `Class`. A distribuição é 60 sucessos e 30 falhas. O conjunto `course_model_dataset.csv` preserva os atributos categóricos e o alvo para SQL, mapa e dashboard."),
        P("5. Análise exploratória", "H1x"),
        P("As figuras abaixo foram extraídas das saídas do notebook de EDA fornecido. Elas comparam resultado por local de lançamento, massa da carga e órbita, além de mostrar a evolução por número do voo e por ano. As diferenças são descrições da amostra e podem refletir mudanças simultâneas de veículo, local, missão e período."),
        figure(23, "Figura 1. Número do voo por local de lançamento e resultado."),
        PageBreak(),
        P("5. Análise exploratória (continuação)", "H1x"),
        figure(28, "Figura 2. Massa da carga por local de lançamento e resultado."),
        figure(33, "Figura 3. Taxa observada de sucesso por órbita."),
        figure(38, "Figura 4. Número do voo por órbita e resultado."),
        PageBreak(),
        P("5. Análise exploratória (continuação)", "H1x"),
        figure(42, "Figura 5. Massa da carga por órbita e resultado."),
        figure(48, "Figura 6. Taxa observada de sucesso por ano."),
        P("6. Análise exploratória com SQL", "H1x"),
        P("As consultas foram executadas em SQLite sobre o conjunto rotulado de 90 lançamentos. O arquivo SQL e os resultados CSV estão em `outputs/sql/`."),
    ]

    site_rows = [[P("Local", "SmallWh"), P("Lançamentos", "SmallWh"), P("Taxa de sucesso", "SmallWh")]]
    for row in res["sql"]["site_success"]:
        site_rows.append([P(escape(row["LaunchSite"]), "Smallx"), P(str(row["launches"]), "Smallx"), P(pct(row["success_rate"]), "Smallx")])
    site_table = Table(site_rows, [75 * mm, 42 * mm, 53 * mm], repeatRows=1)
    site_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4E0E8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ]))
    payload_rows = res["sql"]["payload_by_success"]
    fail_mean = next(r["mean_payload_kg"] for r in payload_rows if int(r["Class"]) == 0)
    success_mean = next(r["mean_payload_kg"] for r in payload_rows if int(r["Class"]) == 1)
    story += [site_table,
        P(f"A massa média da carga foi {fail_mean:,.1f} kg nas falhas e {success_mean:,.1f} kg nos sucessos. A diferença não ajusta por órbita, local ou ano e não deve ser interpretada causalmente.".replace(",", "X").replace(".", ",").replace("X", ".")),
        P("7. Mapa de locais de lançamento", "H1x"),
        P("`src/build_folium_map.py` gerou `outputs/launch_sites_folium.html` com Folium. O mapa mostra os três locais da amostra, marcadores proporcionais à contagem de lançamentos e popups com contagem e taxa observada de sucesso. O HTML é interativo e está incluído na pasta do projeto."),
        P("8. Dashboard Plotly Dash", "H1x"),
        P("`src/dash_app.py` oferece filtros por local e órbita, taxa de sucesso por local e distribuição da massa da carga por resultado. A rota principal, o layout Dash, as dependências do callback e os dois gráficos filtrados foram verificados pelo cliente de teste do Flask. Para abrir localmente: `python src/dash_app.py`, depois `http://127.0.0.1:8050`.")]

    story += [PageBreak(), P("9. Modelagem preditiva", "H1x"),
        P("A matriz de 80 atributos foi dividida em treino e teste com estratificação (72/18, semente 2). Regressão Logística, SVM e KNN usam padronização dentro de um pipeline; a Árvore de Decisão usa os atributos sem escala. Os hiperparâmetros foram escolhidos por acurácia média em validação cruzada estratificada de cinco partes, executada apenas nos dados de treino. As métricas finais abaixo vêm do holdout."),]
    model_rows = [[P("Modelo", "SmallWh"), P("CV", "SmallWh"), P("Teste", "SmallWh"), P("Precisão", "SmallWh"), P("Recall", "SmallWh"), P("F1", "SmallWh")]]
    for name, m in models["metrics"].items():
        cv = models["cross_validation"][name]["cv_accuracy"]
        model_rows.append([P(escape(name), "Smallx"), P(pct(cv), "Smallx"), P(pct(m["accuracy"]), "Smallx"), P(pct(m["precision"]), "Smallx"), P(pct(m["recall"]), "Smallx"), P(pct(m["f1"]), "Smallx")])
    model_table = Table(model_rows, [42 * mm, 25 * mm, 25 * mm, 27 * mm, 25 * mm, 26 * mm], repeatRows=1)
    model_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D4E0E8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story += [model_table, Spacer(1, 3 * mm), P(f"Modelo selecionado por acurácia média de validação cruzada: <b>{escape(models['best_by_cv_accuracy'])}</b>. Parâmetros selecionados: <font name='Courier'>{escape(json.dumps(models['cross_validation'][models['best_by_cv_accuracy']]['best_params'], ensure_ascii=False))}</font>. A matriz de confusão usa linhas para classe real e colunas para classe prevista."), Image(str(confusion_png), width=112 * mm, height=80 * mm),
        P("O holdout tem apenas seis falhas; cada erro muda bastante as métricas dessa classe. A comparação serve como exercício de modelagem, não como garantia de desempenho em lançamentos futuros."),
        P("10. Conclusão", "H1x"),
        P("A amostra do curso permite comparar o comportamento de quatro classificadores após ajuste de hiperparâmetros. O modelo selecionado por validação cruzada obteve o maior desempenho médio nos folds de treino; o holdout fornece a checagem final independente usada no relatório. As análises por local, órbita e carga são descritivas, e o tamanho limitado da amostra impede conclusões operacionais."),
        P("Arquivos para o envio", "H2x"),
        P("O PDF é o arquivo de relatório. Os notebooks, dados, scripts e saídas de mapa/dashboard estão organizados na pasta `SpaceX_Falcon9_Capstone`. O Mark também solicita um link GitHub no critério do projeto; esta pasta ainda não foi publicada em uma conta GitHub, portanto falta inserir esse URL caso o campo de avaliação o exija."),
        P("Fontes", "H2x")]

    refs = [
        ("IBM Skills Network - API arquivada", "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json"),
        ("IBM Skills Network - tabela rotulada dataset_part_2.csv", "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv"),
        ("IBM Skills Network - dataset_part_3.csv", "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv"),
        ("Wikipedia - revisão 987426997 (6 nov. 2020)", "https://en.wikipedia.org/w/index.php?oldid=987426997"),
        ("Wikipedia - página atual de lançamentos Falcon", "https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches"),
    ]
    for label, url in refs:
        story.append(P(f'<link href="{escape(url)}" color="#225EA8">{escape(label)}</link>', "Smallx"))

    doc = SimpleDocTemplate(str(PDF), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=19 * mm, bottomMargin=17 * mm,
                            title="Relatório do Projeto Capstone em Ciência de Dados")
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(PDF)


if __name__ == "__main__":
    main()
