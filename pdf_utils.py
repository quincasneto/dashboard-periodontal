from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def _wrap_lines(c, text, x, y, max_chars=90, step=14):
    words = text.split()
    line = ""
    for w in words:
        if len(line + " " + w) <= max_chars:
            line = (line + " " + w).strip()
        else:
            c.drawString(x, y, line)
            y -= step
            line = w
    if line:
        c.drawString(x, y, line); y -= step
    return y

def gerar_pdf_dentista(dados, resultado, interpretacao, recs):
    c = canvas.Canvas("relatorio_dentista.pdf", pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Relatório Clínico – Dentista")

    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Paciente: {dados.get('nome','(sem nome)')}")
    c.drawString(50, 765, f"Risco final: {resultado[0]} (score {resultado[1]})")

    y = 740
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Achados e interpretação:"); y -= 18
    c.setFont("Helvetica", 11)
    for k, v in interpretacao.items():
        y = _wrap_lines(c, f"- {k}: {v}", 60, y)

    y -= 8
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Plano sugerido (apoio à decisão):"); y -= 18
    c.setFont("Helvetica", 11)
    for step in recs["dentist_plan"]:
        y = _wrap_lines(c, f"• {step}", 60, y)

    y -= 8
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Adjuntos e marcas (referências de mercado):"); y -= 18
    c.setFont("Helvetica", 11)
    for p in recs["products"]:
        y = _wrap_lines(
            c,
            f"• {p['brand']} – {p['product']} ({p['type']}). Ativos: {p['actives']}. Notas: {p['notes']}",
            60, y
        )

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Ferramenta educacional de apoio; ajustar à realidade clínica do paciente. Disponibilidade de produtos pode variar.")
    c.save()

def gerar_pdf_paciente(dados, resultado, interpretacao, recs):
    c = canvas.Canvas("relatorio_paciente.pdf", pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Seu Guia de Saúde da Gengiva")

    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Olá {dados.get('nome','Paciente')}, seu resultado foi: {resultado[0]}.")

    y = 755
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "O que fazer agora:"); y -= 18
    c.setFont("Helvetica", 11)
    for tip in recs["patient_tips"]:
        y = _wrap_lines(c, f"• {tip}", 60, y)

    y -= 8
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Produtos que podem te ajudar:"); y -= 18
    c.setFont("Helvetica", 11)
    count = 0
    for p in recs["products"]:
        y = _wrap_lines(c, f"• {p['brand']} – {p['product']} ({p['type']}).", 60, y)
        count += 1
        if count >= 5: break  # não sobrecarregar o paciente

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Este guia não substitui o dentista. Produtos são sugestões; verifique alergias e siga as orientações profissionais.")
    c.save()
