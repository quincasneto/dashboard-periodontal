import streamlit as st
from risk import calcular_risco
from ia_recommender import recommend
from pdf_utils import gerar_pdf_recomendacoes

st.set_page_config(page_title="Dashboard Periodontal Inteligente", layout="wide")

# --- Cabeçalho ---
st.title("🦷 Dashboard Clínico Inteligente — Avaliação Periodontal (PRA)")
st.caption("Protótipo educacional desenvolvido para o INOVA-S | Universidade de Fortaleza (UNIFOR)")

# --- Dados do paciente ---
st.header("🧍 Dados do paciente")
nome = st.text_input("Nome do paciente")
idade = st.number_input("Idade", min_value=1, max_value=120, value=35)

# --- Entradas clínicas (PRA) ---
st.header("📋 Parâmetros clínicos (PRA)")
bop = st.slider("BOP (% de sítios com sangramento à sondagem)", 0, 100, 10)
bolsas = st.number_input("Nº de sítios com PPD ≥ 5 mm", min_value=0, step=1)
perda_dentes = st.number_input("Nº de dentes perdidos por periodontite", min_value=0, step=1)
relacao_osso_idade = st.number_input("Relação perda óssea / idade", min_value=0.0, step=0.05)
tabagismo = st.selectbox("Tabagismo", ["Não fumante", "Fumante leve (<10/dia)", "Fumante pesado (≥10/dia)"])
diabetes = st.selectbox("Diabetes", ["Não", "Controlado", "Descontrolado"])

# --- Botão principal ---
if st.button("Calcular Risco e Gerar Recomendações"):
    # Calcula o risco clínico
    resultado, score, interpretacao = calcular_risco(
        bop, bolsas, perda_dentes, relacao_osso_idade,
        "Fumante pesado" if "pesado" in tabagismo else "Fumante leve" if "leve" in tabagismo else "Não fumante",
        diabetes if diabetes != "Não" else "Não"
    )

    st.subheader("📊 Resultado da Avaliação")
    st.write(f"**Risco final:** {resultado} (score {score})")

    st.subheader("Detalhamento Clínico (interpretação dos domínios)")
    st.json(interpretacao)

    # Perfil para IA
    profile = {
        "global_risk": "alto" if "alto" in resultado.lower() else "moderado" if "moderado" in resultado.lower() else "baixo",
        "bop": bop,
        "pockets": bolsas,
        "tooth_loss": perda_dentes,
        "bone_age_ratio": relacao_osso_idade,
        "smoking": "heavy" if "pesado" in tabagismo else "light" if "leve" in tabagismo else "none",
        "diabetes": "uncontrolled" if diabetes == "Descontrolado" else "controlled" if diabetes == "Controlado" else "none"
    }

    # Gera recomendações via IA
    recs = recommend(profile)

    # --- Recomendações ---
    st.subheader("🧭 Plano sugerido para o dentista")
    for i, step in enumerate(recs["dentist_plan"], 1):
        st.write(f"{i}. {step}")

    st.subheader("🙋 Dicas de autocuidado para o paciente")
    for tip in recs["patient_tips"]:
        st.write(f"• {tip}")

    st.subheader("🛒 Produtos sugeridos")
    for p in recs["products"]:
        st.write(f"- **{p['brand']} –**
