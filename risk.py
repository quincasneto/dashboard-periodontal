from dataclasses import dataclass
from typing import Dict

@dataclass
class DomainScore:
    level: str  # 'baixo', 'moderado', 'alto'
    detail: str
    valor: float  # valor numérico para radar

def calcular_risco(bop_pct, ppd5, tooth_loss, bone_age_ratio, smoking_input, diabetes_input):
    # --- BOP ---
    if bop_pct < 10:
        bop_level = "baixo"
    elif bop_pct <= 25:
        bop_level = "moderado"
    else:
        bop_level = "alto"

    # --- Bolsas ≥5mm ---
    if ppd5 == 0:
        ppd5_level = "baixo"
    elif ppd5 <= 4:
        ppd5_level = "moderado"
    else:
        ppd5_level = "alto"

    # --- Perda dentária ---
    if tooth_loss <= 4:
        tl_level = "baixo"
    elif tooth_loss <= 8:
        tl_level = "moderado"
    else:
        tl_level = "alto"

    # --- Razão perda óssea/idade ---
    if bone_age_ratio < 0.5:
        bar_level = "baixo"
    elif bone_age_ratio <= 1.0:
        bar_level = "moderado"
    else:
        bar_level = "alto"

    # --- Tabagismo ---
    if smoking_input.lower() == "não fumante":
        smoking_level = "baixo"
        smoking_val = 0
    elif "leve" in smoking_input.lower():
        smoking_level = "moderado"
        smoking_val = 0.5
    else:
        smoking_level = "alto"
        smoking_val = 1

    # --- Diabetes ---
    if diabetes_input.lower() == "não":
        diabetes_level = "baixo"
        diabetes_val = 0
    elif diabetes_input.lower() == "controlado":
        diabetes_level = "moderado"
        diabetes_val = 0.5
    else:
        diabetes_level = "alto"
        diabetes_val = 1

    # --- Monta dicionário de domínios ---
    interpretacao = {
        "bop": DomainScore(bop_level, f"BOP {bop_pct:.1f}%", bop_pct),
        "ppd5": DomainScore(ppd5_level, f"Sítios ≥5 mm: {ppd5}", ppd5),
        "tooth_loss": DomainScore(tl_level, f"Perda dentária: {tooth_loss}", tooth_loss),
        "bone_age": DomainScore(bar_level, f"Razão perda óssea/idade: {bone_age_ratio:.2f}", bone_age_ratio),
        "smoking": DomainScore(smoking_level, f"Tabagismo: {smoking_input}", smoking_val),
        "diabetes": DomainScore(diabetes_level, f"Diabetes: {diabetes_input}", diabetes_val)
    }

    # --- Score global heurístico ---
    highs = sum(1 for d in interpretacao.values() if d.level == "alto")
    moderates = sum(1 for d in interpretacao.values() if d.level == "moderado")

    if highs >= 2 or (highs == 1 and moderates >= 2):
        resultado = "Alto"
    elif moderates >= 2 and highs == 0:
        resultado = "Moderado"
    else:
        resultado = "Baixo"

    score = highs * 2 + moderates  # score simples
    return resultado, score, interpretacao



