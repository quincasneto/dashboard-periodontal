import csv, json, math
from typing import Dict, List

def load_rules(path="ia_rules.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_products(path="products.csv"):
    items = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items

def pick_products(profile: Dict, catalog: List[Dict]) -> List[Dict]:
    """
    Seleciona produtos por necessidades:
    - BOP alto: antissépticos (CHX curto prazo), cremes com SnF/CPC
    - Bolsas altas: adjuvantes por curto prazo; foco em mecânica
    - Sensibilidade esperada: nitrato de potássio
    - Destreza limitada / alto risco: escova elétrica + interdental
    """
    recs = []

    bop = profile.get("bop", 0)
    pockets = profile.get("pockets", 0)
    smoker = profile.get("smoking", "none")        # none/light/heavy
    diabetes = profile.get("diabetes", "none")     # none/controlled/uncontrolled

    def add_if(predicate, types=None, actives_any=None):
        for p in catalog:
            ok_type = (types is None) or (p["type"] in types)
            ok_active = True
            if actives_any:
                ok_active = any(a.strip().lower() in p["actives"].lower() for a in actives_any)
            if predicate and ok_type and ok_active:
                recs.append(p)

    # BOP alto → CHX curto prazo, dentifrícios anti-gengivite (SnF/CPC)
    if bop >= 20:
        add_if(True, types=["mouthwash"], actives_any=["clorexidina"])
        add_if(True, types=["toothpaste"], actives_any=["estan", "cpc", "fluoreto de estanho", "cpc"])

    # BOP moderado → dentifrícios anti-gengivite
    elif 10 <= bop < 20:
        add_if(True, types=["toothpaste"], actives_any=["fluoreto de estanho", "cpc", "óleos essenciais"])

    # Bolsas significativas → foco em mecânica + adjuvantes curtos
    if pockets >= 4:
        add_if(True, types=["toothbrush"], actives_any=["macias", "oscilação", "rotatória"])
        add_if(True, types=["interdental"], actives_any=[""])

    # Fumante → controle químico auxiliar; elétricas podem ajudar
    if smoker in ["light", "heavy"]:
        add_if(True, types=["mouthwash"], actives_any=["óleos essenciais", "fluor"])
        add_if(True, types=["toothbrush"], actives_any=["oscilação", "rotatória"])

    # Itens genéricos úteis
    add_if(True, types=["toothbrush"], actives_any=["macias"])
    add_if(True, types=["interdental"], actives_any=[""])

    # Remover duplicatas mantendo ordem
    seen = set()
    unique = []
    for p in recs:
        key = (p["brand"], p["product"])
        if key not in seen:
            unique.append(p); seen.add(key)
    return unique[:6]  # limitar a 6 sugestões

def plan_for_dentist(profile: Dict, rules: Dict) -> List[str]:
    out = []
    risk = profile.get("global_risk", "moderate")
    follow_text = rules["followup"]["high" if risk=="alto" else "moderate" if risk=="moderado" else "low"]
    out.append(f"Periodicidade sugerida: {follow_text}")

    bop = profile.get("bop", 0)
    if bop >= 20:
        out += rules["bop"]["high"]
        out += rules["patient_tips"]["chlorhexidine"]
    elif 10 <= bop < 20:
        out += rules["bop"]["moderate"]

    pockets = profile.get("pockets", 0)
    if pockets >= 5:
        out += rules["pockets"]["high"]
    elif 2 <= pockets <= 4:
        out += rules["pockets"]["moderate"]

    ratio = profile.get("bone_age_ratio", 0)
    if ratio > 1.0:
        out += rules["bone_age_ratio"]["high"]
    elif 0.5 <= ratio <= 1.0:
        out += rules["bone_age_ratio"]["moderate"]

    smoking = profile.get("smoking", "none")
    if smoking == "light":
        out += rules["smoking"]["light"]
    elif smoking == "heavy":
        out += rules["smoking"]["heavy"]

    diabetes = profile.get("diabetes", "none")
    if diabetes == "controlled":
        out += rules["diabetes"]["controlled"]
    elif diabetes == "uncontrolled":
        out += rules["diabetes"]["uncontrolled"]

    return out

def tips_for_patient(profile: Dict, rules: Dict) -> List[str]:
    tips = list(rules["patient_tips"]["generic"])

    bop = profile.get("bop", 0)
    if bop >= 20:
        tips += rules["patient_tips"]["chlorhexidine"]
    tips += rules["patient_tips"]["electric_brush"]
    tips += rules["patient_tips"]["interdental"]

    smoking = profile.get("smoking", "none")
    if smoking in ["light", "heavy"]:
        tips.append("Parar de fumar ajuda MUITO a desinflamar a gengiva; busque apoio profissional.")

    diabetes = profile.get("diabetes", "none")
    if diabetes == "uncontrolled":
        tips.append("Controle melhor a glicemia com seu médico — isso reduz o risco periodontal.")

    return tips

def recommend(profile: Dict) -> Dict:
    """
    profile:
      - global_risk: 'baixo'|'moderado'|'alto'
      - bop: %
      - pockets: contagem de sítios >= 5mm
      - tooth_loss: int
      - bone_age_ratio: float
      - smoking: 'none'|'light'|'heavy'
      - diabetes: 'none'|'controlled'|'uncontrolled'
    """
    rules = load_rules()
    catalog = load_products()
    dentist_plan = plan_for_dentist(profile, rules)
    patient_tips = tips_for_patient(profile, rules)
    products = pick_products(profile, catalog)
    return {
        "dentist_plan": dentist_plan,
        "patient_tips": patient_tips,
        "products": products
    }
