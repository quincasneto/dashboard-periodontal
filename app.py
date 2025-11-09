import streamlit as st
from risk import calcular_risco
from pdf_utils import gerar_pdf_dentista, gerar_pdf_paciente
from ia_recommender import recommend

st.title("🦷 Dashboard de Avaliação Periodontal Inteligente")

# Dados do paciente
st.header("Dados do paciente")
nome = st.text_input("Nome do paciente")

# Entradas clínicas (PRA)
st.header("Parâmetros clínicos (PRA)")
bop = st.slider("BOP (% sangramento à sondagem)", 0, 100, 10)
bolsas = st.number_input("Nº de sítios com PPD ≥ 5mm", min_value=0, step=1)
perda_dentes = st.number_input("Nº de dentes perdidos por periodontite", min_value=0, step=1)
relacao_osso_idade = st.number_input("Relação perda óssea / idade", min_value=0.0, step=0.05)

tabagismo = st.selectbox("Tabagismo", ["Não fumante", "Fumante leve (<10/dia)", "Fumante pesado (≥10/dia)"])
diabetes = st.selectbox("Diabetes", ["Não", "Controlado", "Descontrolado"])

if st.button("Calcular e Gerar Recomendações"):
    # Calcula risco
    resultado, score, interpretacao = calcular_risco(
        bop, bolsas, perda_dentes, relacao_osso_idade,
        "Fumante pesado" if "pesado" in tabagismo else "Fumante leve" if "leve" in tabagismo else "Não fumante",
        diabetes if diabetes != "Não" else "Não"
    )

    st.subheader("📊 Resultado da avaliação")
    st.write(f"**Risco final:** {resultado} (score {score})")
    st.subheader("Detalhes clínicos")
    st.json(interpretacao)

    # Normaliza perfil para a IA
    profile = {
        "global_risk": "alto" if "Alto" in resultado else "moderado" if "moderado" in resultado.lower() else "baixo",
        "bop": bop,
        "pockets": bolsas,
        "tooth_loss": perda_dentes,
        "bone_age_ratio": relacao_osso_idade,
        "smoking": "heavy" if "pesado" in tabagismo else "light" if "leve" in tabagismo else "none",
        "diabetes": "uncontrolled" if diabetes=="Descontrolado" else "controlled" if diabetes=="Controlado" else "none"
    }

    recs = recommend(profile)

    st.subheader("🧭 Plano sugerido (dentista)")
    for i, step in enumerate(recs["dentist_plan"], 1):
        st.write(f"{i}. {step}")

    st.subheader("🙋 Dicas para você (paciente)")
    for tip in recs["patient_tips"]:
        st.write(f"• {tip}")

    st.subheader("🛒 Produtos sugeridos")
    for p in recs["products"]:
        st.write(f"- **{p['brand']} – {p['product']}** ({p['type']}) — *Ativos:* {p['actives']}")

    # PDFs
    dados = {"nome": nome}
    gerar_pdf_dentista(dados, (resultado, score), interpretacao, recs)
    gerar_pdf_paciente(dados, (resultado, score), interpretacao, recs)
    st.success("📑 PDFs gerados: relatorio_dentista.pdf e relatorio_paciente.pdf")


