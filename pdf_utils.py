import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from io import BytesIO

# Caminho do logo UNIFOR
LOGO_PATH = "assets/logo_unifor.png"

# --- Função para gerar valores normalizados para radar ---
def gerar_valores_radar(interpretacao):
    radar_vals = []
    
    # BOP% → 0-100%
    bop = interpretacao["bop"].get("valor", 50) / 100
    radar_vals.append(min(1, max(0, bop)))
    
    # Bolsas ≥5mm → contagem / 10
    ppd5 = interpretacao["ppd5"].get("valor", 2) / 10
    radar_vals.append(min(1, max(0, ppd5)))
    
    # Perda dentária → 0-32 dentes
    tooth_loss = interpretacao["tooth_loss"].get("valor", 4) / 32
    radar_vals.append(min(1, max(0, tooth_loss)))
    
    # Razão perda óssea/idade → 0-2
    bar = interpretacao["bone_age"].get("valor", 1) / 2
    radar_vals.append(min(1, max(0, bar)))
    
    # Tabagismo → 0 = baixo, 0.5 = moderado, 1 = alto
    smoking_map = {"baixo": 0, "moderado": 0.5, "alto": 1}
    radar_vals.append(smoking_map.get(interpretacao["smoking"]["level"], 0.5))
    
    # Diabetes → 0 = baixo, 0.5 = moderado, 1 = alto
    diabetes_map = {"baixo": 0, "moderado": 0.5, "alto": 1}
    radar_vals.append(diabetes_map.get(interpretacao["diabetes"]["level"], 0.5))
    
    return radar_vals

# --- Função para gerar gráfico radar ---
def criar_radar(interpretacao):
    labels = ["BOP%", "Bolsas ≥5mm", "Perda dentária", "Razão osso/idade", "Tabagismo", "Diabetes"]
    scores = gerar_valores_radar(interpretacao)
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores += scores[:1]  # fechar o círculo
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, 'o-', linewidth=2, label="Risco")
    ax.fill(angles, scores, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0,1)
    ax.set_title("Radar do Risco Periodontal", fontsize=12)
    return fig

# --- Função para criar PDF ---
def gerar_pdf_base(dados, resultado, interpretacao, recs, publico="paciente"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo UNIFOR
    try:
        logo = ImageReader(LOGO_PATH)
        c.drawImage(logo, width-5*cm, height-3*cm, width=4*cm, height=2*cm, preserveAspectRatio=True)
    except:
        pass

    # Título
    titulo = "Relatório Periodontal — " + ("Dentista" if publico=="dentista" else "Paciente")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, titulo)

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-2.7*cm, f"Nome: {dados.get('nome', '')}")
    c.drawString(2*cm, height-3.2*cm, f"Idade: {dados.get('idade', '')}")
    c.drawString(2*cm, height-3.7*cm, f"Risco global: {resultado}")

    # Gráfico radar
    fig = criar_radar(interpretacao)
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", bbox_inches='tight')
    plt.close(fig)
    img_buffer.seek(0)
    img = ImageReader(img_buffer)
    c.drawImage(img, 2*cm, height-15*cm, width=12*cm, height=12*cm, preserveAspectRatio=True)

    # Detalhes clínicos
    y = height-16*cm
    c.setFont("Helvetica", 9)
    for k, d in interpretacao.items():
        detalhe = d.get("detail", "")
        c.drawString(2*cm, y, f"• {k}: {d.get('level','')} — {detalhe}")
        y -= 0.6*cm

    # Recomendações (paciente ou dentista)
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

# --- Funções específicas ---
def gerar_pdf_paciente(dados, resultado, interpretacao, recs):
    return gerar_pdf_base(dados, resultado, interpretacao, recs, publico="paciente")

def gerar_pdf_dentista(dados, resultado, interpretacao, recs):
    return gerar_pdf_base(dados, resultado, interpretacao, recs, publico="dentista")






