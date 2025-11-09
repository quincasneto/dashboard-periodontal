from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np

def criar_grafico_radar(domains, scores):
    """
    domains: lista de nomes dos domínios ['BOP','Bolsas',...]
    scores: lista de valores normalizados 0-1
    """
    N = len(domains)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    scores += scores[:1]  # fechar o círculo
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, 'o-', linewidth=2)
    ax.fill(angles, scores, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), domains)
    ax.set_ylim(0,1)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='PNG', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def gerar_pdf_paciente(dados_paciente, risco, interpretacao, recs):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    logo_unifor = os.path.join("assets", "unifor_logo.png")
    if os.path.exists(logo_unifor):
        pdf.drawImage(ImageReader(logo_unifor), 2*cm, altura - 3*cm, width=3*cm, height=2*cm, preserveAspectRatio=True)
    pdf.setFont("Helvetica-Bold",16)
    pdf.drawCentredString(largura/2, altura-2.7*cm, "Avaliação Periodontal - Paciente")
    pdf.setLineWidth(1)
    pdf.line(2*cm, altura-3.2*cm, largura-2*cm, altura-3.2*cm)

    # Gráfico radar
    domains = ['BOP','Bolsas','Perda Dentária','Perda Óssea/Idade','Tabagismo','Diabetes']
    # Normalizando valores para 0-1
    score_vals = [min(1, max(0, interpretacao[d]['valor']/100 if 'valor' in interpretacao[d] else 0.5)) for d in interpretacao]
    radar_img = criar_grafico_radar(domains, score_vals)
    pdf.drawImage(ImageReader(radar_img), largura/2 - 6*cm, altura-15*cm, width=12*cm, height=12*cm, preserveAspectRatio=True)

    # Dados do paciente
    y = altura-17*cm
    pdf.setFont("Helvetica",12)
    pdf.drawString(2*cm, y, f"Nome: {dados_paciente.get('nome','Não informado')}")
    pdf.drawString(2*cm, y-20, f"Idade: {dados_paciente.get('idade','Não informado')}")
    pdf.drawString(2*cm, y-40, f"Risco global: {risco.upper()}")
    y -= 70

    # Recomendações paciente
    pdf.setFont("Helvetica-Bold",13)
    pdf.drawString(2*cm, y, "Dicas para o paciente:")
    pdf.setFont("Helvetica",11)
    y -= 20
    for tip in recs['patient_tips']:
        pdf.drawString(2.5*cm, y, f"• {tip}")
        y -= 14

    # Produtos sugeridos
    pdf.drawString(2*cm, y-10, "Produtos sugeridos:")
    y -= 30
    for p in recs['products']:
        pdf.drawString(2.5*cm, y, f"- {p['brand']} – {p['product']} ({p['type']})")
        y -= 14

    # Rodapé
    pdf.setFont("Helvetica-Oblique",9)
    pdf.setFillColorRGB(0.3,0.3,0.3)
    pdf.drawCentredString(largura/2,1.5*cm, "Protótipo educacional INOVA-S | UNIFOR")
    pdf.drawCentredString(largura/2,1*cm, "Ferramenta de apoio. Não substitui julgamento clínico")

    pdf.save()
    buffer.seek(0)
    return buffer

def gerar_pdf_dentista(dados_paciente, risco, interpretacao, recs):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    logo_unifor = os.path.join("assets", "unifor_logo.png")
    if os.path.exists(logo_unifor):
        pdf.drawImage(ImageReader(logo_unifor), 2*cm, altura - 3*cm, width=3*cm, height=2*cm, preserveAspectRatio=True)
    pdf.setFont("Helvetica-Bold",16)
    pdf.drawCentredString(largura/2, altura-2.7*cm, "Avaliação Periodontal - Dentista")
    pdf.setLineWidth(1)
    pdf.line(2*cm, altura-3.2*cm, largura-2*cm, altura-3.2*cm)

    # Gráfico radar
    domains = ['BOP','Bolsas','Perda Dentária','Perda Óssea/Idade','Tabagismo','Diabetes']
    score_vals = [min(1, max(0, interpretacao[d]['valor']/100 if 'valor' in interpretacao[d] else 0.5)) for d in interpretacao]
    radar_img = criar_grafico_radar(domains, score_vals)
    pdf.drawImage(ImageReader(radar_img), largura/2 - 6*cm, altura-15*cm, width=12*cm, height=12*cm, preserveAspectRatio=True)

    # Dados do paciente
    y = altura-17*cm
    pdf.setFont("Helvetica",12)
    pdf.drawString(2*cm, y, f"Nome: {dados_paciente.get('nome','Não informado')}")
    pdf.drawString(2*cm, y-20, f"Idade: {dados_paciente.get('idade','Não informado')}")
    pdf.drawString(2*cm, y-40, f"Risco global: {risco.upper()}")
    y -= 70

    # Recomendações dentista
    pdf.setFont("Helvetica-Bold",13)
    pdf.drawString(2*cm, y, "Plano sugerido para o dentista:")
    pdf.setFont("Helvetica",11)
    y -= 20
    for step in recs['dentist_plan']:
        pdf.drawString(2.5*cm, y, f"• {step}")
        y -= 14

    # Rodapé
    pdf.setFont("Helvetica-Oblique",9)
    pdf.setFillColorRGB(0.3,0.3,0.3)
    pdf.drawCentredString(largura/2,1.5*cm, "Protótipo educacional INOVA-S | UNIFOR")
    pdf.drawCentredString(largura/2,1*cm, "Ferramenta de apoio. Não substitui julgamento clínico")

    pdf.save()
    buffer.seek(0)
    return buffer




