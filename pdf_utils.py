import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from io import BytesIO

LOGO_PATH = "assets/logo_unifor.png"

def gerar_valores_radar(interpretacao):
    radar_vals = []
    radar_vals.append(interpretacao["bop"].valor / 100)
    radar_vals.append(min(1, interpretacao["ppd5"].valor / 10))
    radar_vals.append(min(1, interpretacao["tooth_loss"].valor / 32))
    radar_vals.append(min(1, interpretacao["bone_age"].valor / 2))
    radar_vals.append(interpretacao["smoking"].valor)
    radar_vals.append(interpretacao["diabetes"].valor)
    return radar_vals

def criar_radar(interpretacao):
    labels = ["BOP%", "Bolsas ≥5mm", "Perda dentária", "Razão osso/idade", "Tabagismo", "Diabetes"]
    scores = gerar_valores_radar(interpretacao)
    
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    scores += scores[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, 'o-', linewidth=2, label="Risco")
    ax.fill(angles, scores, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0,1)
    ax.set_title("Radar do Risco Periodontal", fontsize=12)
    return fig

def gerar_pdf_base(dados, resultado, interpretacao, recs, publico="paciente"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    try:
        logo = ImageReader(LOGO_PATH)
        c.drawImage(logo, width-5*cm, height-3*cm, width=4*cm, height=2*cm, preserveAspectRatio=True)
    except:
        pass

    titulo = "Relatório Periodontal — " + ("Dentista" if publico=="dentista" else "Paciente")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, titulo)

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-2.7*cm, f"Nome: {dados.get('nome', '')}")
    c.drawString(2*cm, height-3.2*cm, f"Idade: {dados.get('idade', '')}")
    c.drawString(2*cm, height-3.7*cm, f"Risco global: {resultado}")

    fig = criar_radar(interpretacao)
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)
    img = ImageReader(img_buffer)
    c.drawImage(img, 2*cm, height-15*cm, width=12*cm, height=12*cm, preserveAspectRatio=True)

    y = height-16*cm
    c.setFont("Helvetica", 9)
    for k, d in interpretacao.items():
        c.drawString(2*cm, y, f"• {k}: {d.level} — {d.detail}")
        y -= 0.6*cm

    y -= 0.3*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Recomendações:")
    y -= 0.5*cm
    c.setFont("Helvetica", 9)
    plano = recs["dentist_plan"] if publico=="dentista" else recs["patient_tips"]
    for item in plano:
        c.drawString(2*cm, y, f"• {item}")
        y -= 0.5*cm

    disclaimer = "Ferramenta educacional; não substitui julgamento clínico."
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(2*cm, 1.5*cm, disclaimer)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def gerar_pdf_paciente(dados, resultado, interpretacao, recs):
    return gerar_pdf_base(dados, resultado, interpretacao, recs, publico="paciente")

def gerar_pdf_dentista(dados, resultado, interpretacao, recs):
    return gerar_pdf_base(dados, resultado, interpretacao, recs, publico="dentista")








