from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def gerar_pdf_recomendacoes(dados_paciente, risco, recomendacoes):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    pdf.setTitle("Relatório Periodontal")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, altura - 50, "Relatório de Avaliação Periodontal")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, altura - 100, f"Nome: {dados_paciente.get('nome', 'Não informado')}")
    pdf.drawString(50, altura - 120, f"Idade: {dados_paciente.get('idade', 'Não informado')}")
    pdf.drawString(50, altura - 140, f"Data: {datetime.now().strftime('%d/%m/%Y')}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, altura - 180, "Classificação de Risco Periodontal:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(70, altura - 200, f"➡️ Risco: {risco}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, altura - 240, "Recomendações Personalizadas:")
    pdf.setFont("Helvetica", 11)

    y = altura - 260
    for linha in recomendacoes.split("\n"):
        pdf.drawString(70, y, linha)
        y -= 18

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer


