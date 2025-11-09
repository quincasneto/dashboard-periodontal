def calcular_risco(bop, bolsas, perda_dentes, relacao_osso_idade, tabagismo, diabetes):
    score = 0
    interpretacao = {}

    # BOP
    if bop < 10:
        interpretacao["BOP"] = "Baixo sangramento (<10%)"
    elif bop <= 20:
        score += 1
        interpretacao["BOP"] = "Moderado sangramento (10-20%)"
    else:
        score += 2
        interpretacao["BOP"] = "Alto sangramento (>20%)"

    # Bolsas
    if bolsas == 0:
        interpretacao["Bolsas"] = "Nenhuma bolsa profunda"
    elif bolsas <= 3:
        score += 1
        interpretacao["Bolsas"] = "Algumas bolsas (1-3)"
    else:
        score += 2
        interpretacao["Bolsas"] = "Muitas bolsas (≥4)"

    # Perda de dentes
    if perda_dentes == 0:
        interpretacao["Perda de dentes"] = "Nenhuma perda"
    elif perda_dentes <= 4:
        score += 1
        interpretacao["Perda de dentes"] = "Perda moderada (1-4)"
    else:
        score += 2
        interpretacao["Perda de dentes"] = "Perda grave (≥5)"

    # Relação perda óssea / idade
    if relacao_osso_idade < 0.25:
        interpretacao["Perda óssea/idade"] = "Compatível com idade (<0.25)"
    elif relacao_osso_idade <= 1.0:
        score += 1
        interpretacao["Perda óssea/idade"] = "Moderada (0.25–1.0)"
    else:
        score += 2
        interpretacao["Perda óssea/idade"] = "Grave (>1.0)"

    # Tabagismo
    if tabagismo == "Não fumante":
        interpretacao["Tabagismo"] = "Não fumante"
    elif tabagismo == "Fumante leve":
        score += 1
        interpretacao["Tabagismo"] = "Fumante leve (<10 cigarros/dia)"
    else:
        score += 2
        interpretacao["Tabagismo"] = "Fumante pesado (≥10 cigarros/dia)"

    # Diabetes
    if diabetes == "Não":
        interpretacao["Diabetes"] = "Sem diabetes"
    elif diabetes == "Controlado":
        score += 1
        interpretacao["Diabetes"] = "Diabetes controlado"
    else:
        score += 2
        interpretacao["Diabetes"] = "Diabetes descontrolado"

    # Classificação final
    if score <= 3:
        resultado = "Baixo risco"
    elif score <= 6:
        resultado = "Risco moderado"
    else:
        resultado = "Alto risco"

    return resultado, score, interpretacao

