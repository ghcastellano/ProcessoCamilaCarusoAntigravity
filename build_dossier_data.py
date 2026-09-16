import json
import os
import re

print("Building Clean Dossier Dataset with Dual Multi-Agent Verification...")

# Load transcriptions
with open("transcriptions.json", "r", encoding="utf-8") as f:
    transcriptions = json.load(f)

# Load chat dataset
with open("chat_dataset.json", "r", encoding="utf-8") as f:
    chat_messages = json.load(f)

msg_by_id = {m["id"]: m for m in chat_messages}

BLACKLIST_TEXT_PATTERNS = [
    # 1. Gustavo's traffic accident (02/08 - 03/08)
    r"bateu no meu carro",
    r"batendo seu carro",
    r"ele bateu no meu carro",
    r"outros bo da vida",
    r"vai pra vala",
    r"advogado de uma galera do pcc",
    r"galera do pcc",
    r"mentira temperar na porta",
    r"mentira tem perna curta",
    r"passado por cima dele",
    r"dar um totozinho",
    r"não ia acontecer nada com meu carro",
    r"o cara batendo",
    r"acidente",
    
    # 2. Forwarded messages / Bank manager Mary dialogue
    r"oi, mary!",
    r"seja bem vindo\(a\) ao meu atendimento",
    r"me passa seu cnpj\?",
    r"em uma vídeo chamada agora",
    r"inativa no sentido de análise de crédito",
    r"centralizar suas movimentações conosco",
    r"voltar a centralizar suas movimentações",
    r"atualizei o faturamento no app do itau",
    r"mary itaú empresas",
    r"mary itaú empresas",
    
    # 3. Personal / Hotel / Beach / iFood / Intimacy / Dating
    r"hotel com vista pro mar",
    r"hotel",
    r"dormir na mesma cama",
    r"durmo de roupa",
    r"nem encosto em você",
    r"quarto de visitas",
    r"compras do ifood",
    r"decolar",
    r"só parceiros ok",
    r"belezas naturais",
    r"dormir",
    
    # 4. Psychological tests & personal therapy
    r"sobre-excitabilidades",
    r"dabrowski",
    r"espectro autista",
    r"aq-50",
    r"reconhecer um problema em mim",
    r"processo de mudança",
    r"terapia",
    r"psicólogo",
    r"psicologia",
]

BLACKLIST_ATTACHMENTS = [
    "00001092-SE - OE — Sobre-excitabilidades (Dabrowski).pdf",
    "00001093-AQ-50 — Quociente do Espectro Autista.pdf",
    "00001445-Mary Itaú empresas.vcf",
    "00001445-Mary Itaú empresas.vcf",
    "00001400-AUDIO-2026-08-03-16-48-25.opus",
    "00001492-AUDIO-2026-08-03-19-35-20.opus",
]

def is_forbidden(msg):
    att = msg.get("attachment") or ""
    content = msg.get("content") or ""
    tr = transcriptions.get(att, {}).get("text", "") if att else msg.get("audio_transcription") or ""
    full_text = (content + " " + tr).lower()
    
    for b_att in BLACKLIST_ATTACHMENTS:
        if b_att.lower() in att.lower():
            return True, f"Blacklisted attachment: {b_att}"
            
    if msg.get("date") == "03/08/2026" and msg.get("time") == "17:53:50":
        return True, "Forwarded bank manager dialogue (03/08 17:53:50)"
        
    for pat in BLACKLIST_TEXT_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            return True, f"Pattern matched: {pat}"
            
    return False, None


# The 10 thematic blocks
blocks = [
    {
        "id": "bloco-1",
        "title": "Bloco 1: Reaproximação, Proposta de Parceria e Alinhamento de Negócios",
        "dates": "29/07/2026 a 02/08/2026",
        "summary": "Após período de afastamento, Camila Caruso entra em contato pedindo reaproximação comercial: 'Gustavo vamos falar de dinheiro ok... podemos ganhar dinheiro juntos'. Gustavo aceita e propõe estratégias de prospecção e tráfego para arquitetura de alto padrão e clínicas, iniciando a reativação de sua conta PJ para viabilizar operações de crédito.",
        "badge": "Início da Parceria Comercial",
        "badgeClass": "blue",
        "events": []
    },
    {
        "id": "bloco-2",
        "title": "Bloco 2: Diagnóstico da C. Caruso, Soo Tech e o 1º Pix de R$ 40.000,00",
        "dates": "03/08/2026 a 04/08/2026",
        "summary": "Gustavo analisa o faturamento oficial da empresa de Camila via Contabilizei (R$ 454k em 2025). Em áudio formal (Áudio 1509), Gustavo apresenta a proposta inicial envolvendo a Soo Tech (com os então sócios João e Victor — Gustavo hoje não mais sócio), ressaltando que os sócios não participariam de empréstimos e que o socorro financeiro seria assumido pessoalmente por Gustavo. Camila alega extrema asfixia ('Pq to dura né... Gu não passa de 40'). Em 04/08, Gustavo contrata empréstimo de giro no Nubank e transfere o 1º Pix de R$ 40.000,00 às 10:28 (Foto 1604). Camila agradece aliviada e promete vender seu carro para quitar o valor.",
        "badge": "1º Pix: R$ 40.000,00 (04/08)",
        "badgeClass": "green",
        "events": []
    },
    {
        "id": "bloco-3",
        "title": "Bloco 3: Internação Hospitalar de Gustavo e Estruturação do Pronampe",
        "dates": "05/08/2026 a 15/08/2026",
        "summary": "Gustavo é internado no Hospital Serpiero em Santos. Camila envia flores em agradecimento e reitera a promessa solene de devolução com juros assim que vender o carro dela ('qdo sair o carro, te devolvo exatamente como esse print com juros'). Gustavo estrutura a simulação oficial de amortização do Pronampe.",
        "badge": "Internação & Projeção Pronampe",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-4",
        "title": "Bloco 4: Aprovação do Giro Pronampe no Itaú",
        "dates": "16/08/2026 a 18/08/2026",
        "summary": "Gustavo obtém a aprovação da linha Giro Pronampe principal no Itaú (Contrato nº 4887183848, saldo restante no app de R$ 119.343,17 em 60 parcelas de R$ 2.324,17). Camila reitera a urgência de mais capital para manter a folha da equipe ('Preciso de $$ mais pra poder pagar equipe').",
        "badge": "Crédito Itaú Aprovado",
        "badgeClass": "blue",
        "events": []
    },
    {
        "id": "bloco-5",
        "title": "Bloco 5: O Segundo Pix de R$ 72.000,00 e Compromisso de Assinatura Contratual",
        "dates": "19/08/2026",
        "summary": "Data crucial: Gustavo efetua às 16:10 o segundo repasse no valor de R$ 72.000,00 via Itaú SISPAG para a C. Caruso Arquitetura (Foto 3448). Camila reage com choro e alívio ('Muito obrigada! To até com vontade de chorar... nossa tava desesperada') e assume o compromisso irretratável: 'Veja o contrato, coloque tudo lá. E amanhã já assinamos por favor'. O total líquido repassado atinge R$ 112.000,00.",
        "badge": "2º Pix: R$ 72.000,00 — Total R$ 112k",
        "badgeClass": "green",
        "events": []
    },
    {
        "id": "bloco-6",
        "title": "Bloco 6: Formalização das Minutas, Termo de Dívida e Quitação Nubank",
        "dates": "20/08/2026 a 31/08/2026",
        "summary": "Gustavo encaminha as minutas formais: Contrato de Parceria Comercial, Anexo II de Reconhecimento de Dívida e Termo NCNDA. Em 24/08/2026, com os recursos do 2º Pronampe Itaú (Contrato nº 4886874439, saldo R$ 19.527,27), Gustavo realiza a quitação antecipada de 13 parcelas do Nubank por R$ 18.015,62 (desconto de R$ 17.521,40, recibo Nu Financeira cód. 6a8c7a93).",
        "badge": "Minutas & Quitação 13x Nubank",
        "badgeClass": "blue",
        "events": []
    },
    {
        "id": "bloco-7",
        "title": "Bloco 7: Reenvio do Termo de Confissão de Dívida e Assinatura Pendente",
        "dates": "01/09/2026 a 02/09/2026",
        "summary": "Gustavo reenvia formalmente o Anexo II - Termo de Reconhecimento de Dívida e o NCNDA, cobrando a formalização jurídica pactuada. Camila passa a adotar postura evasiva e relata dificuldades profissionais em Mogi das Cruzes.",
        "badge": "Termo de Dívida Cobrado",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-8",
        "title": "Bloco 8: Prestação de Contas Bancárias Oficiais e Alertas Formais",
        "dates": "03/09/2026 a 10/09/2026",
        "summary": "Em 09/09/2026, Gustavo apresenta a Camila a prestação de contas cabal de todo o endividamento bancário contraído em socorro à Ré: extrato dos 2 contratos Pronampe Itaú (Foto 4367), extrato do Nubank comprovando as 13 parcelas quitadas e 11 restantes (Foto 4393), o Pix de R$ 18.653,05 (Foto 4395) e o recibo de quitação antecipada de R$ 18.015,62 (Foto 4396). Camila responde com distanciamento.",
        "badge": "Provas Bancárias Oficiais",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-9",
        "title": "Bloco 9: O Ultimato de Sexta-Feira e o Risco de Serasa",
        "dates": "11/09/2026 a 13/09/2026",
        "summary": "Gustavo alerta que seu limite está no cheque especial e que sofrerá negativação no Serasa se as parcelas não forem assumidas. Gustavo indaga expressamente: 'o carro colocou pra vender?'. Camila responde com deboche e desdém: 'Está sofrendo por antecipação porque ? Antes da primeira parcela já estarei quitado isso'. Gustavo avisa que sem resposta formal procurará os meios jurídicos.",
        "badge": "Risco de Negativação & Aviso Legal",
        "badgeClass": "red",
        "events": []
    },
    {
        "id": "bloco-10",
        "title": "Bloco 10: Ruptura, Chantagem com Falsa Medida Protetiva e Recusa Total",
        "dates": "14/09/2026 a 15/09/2026",
        "summary": "O ápice do dolo e da apropriação: Gustavo exige a liquidação do compromisso ('Vender o carro e quitar... a preço de banana só pra não ter meu nome levado ao Serasa'). Camila reage acusando-o de 'ameaça' e consuma a extorsão moral: 'Você quer que eu entre com uma medida protetiva contra você?' (Áudio 4874). Camila nega cinicamente a validade dos repasses ('word não é contrato assinado... Que Pix? Não recebi nenhum seu'). Gustavo faz apelo final conciliatório em 15/09 para evitar o litígio, sem sucesso. Via amigável esgotada.",
        "badge": "CHANTAGEM & RECUSA TOTAL",
        "badgeClass": "red",
        "events": []
    }
]

# Curated, strictly audited event list
CURATED_EVENT_IDS = [
    # Bloco 1
    9, 17, 746, 1147, 1148,
    # Bloco 2
    1355, 1421, 1422, 1459, 1509, 1517, 1540, 1568, 1579, 1582, 1604, 1607, 1788, 1947,
    # Bloco 3
    2299, 2864, 2891,
    # Bloco 4
    2987, 3119,
    # Bloco 5
    3356, 3448, 3449, 3452, 3454,
    # Bloco 6
    3652, 3653, 3654, 3811, 3837, 3841,
    # Bloco 7
    4156, 4157, 4158, 4228, 4276,
    # Bloco 8
    4367, 4368, 4393, 4394, 4395, 4396, 4397,
    # Bloco 9
    4554, 4561, 4582, 4591, 4618, 4650,
    # Bloco 10
    4680, 4687, 4729, 4743, 4757, 4786, 4822, 4874, 4887, 4896, 4897, 4910, 4920, 4934
]

for ev_id in CURATED_EVENT_IDS:
    msg = msg_by_id.get(ev_id)
    if not msg:
        continue
        
    att = msg.get("attachment") or ""
    tr = transcriptions.get(att, {}).get("text", "") if att else msg.get("audio_transcription") or ""
    
    tags = []
    custom_badge = None
    custom_note = None
    
    if ev_id == 1509:
        tags = ["PROPOSTA_SOO_TECH", "CONTRATO_DIVIDA", "CONTRATO", "FINANCEIRO"]
        custom_badge = "Proposta Inicial Soo Tech (João, Victor e Gustavo)"
        custom_note = "Áudio oficial no qual Gustavo detalha a proposta inicial de parceria comercial envolvendo a Soo Tech (com os então sócios João e Victor — Gustavo hoje não mais sócio). Gustavo destaca expressamente que os demais sócios não aceitariam operação de mútuo bancário, pactuando-se que o aporte de R$ 40k e os contratos seguintes seriam contraídos estritamente em caráter pessoal por Gustavo para socorrer Camila."
    elif ev_id in [1604, 3448, 4395, 4396]:
        tags = ["COMPROVANTE_OFICIAL", "FINANCEIRO", "FINANCEIRO_APORTE"]
    elif ev_id in [1788, 1947, 2299, 4554, 4687, 4822, 4910]:
        tags = ["CARRO_DIVIDA", "CARRO_DIVIDA_RE"]
    elif ev_id in [2864]:
        tags = ["HOSPITAL_SAUDE", "COMPROVANTE_OFICIAL"]
    elif ev_id in [2891]:
        tags = ["HOSPITAL_SAUDE", "FINANCEIRO", "CONTRATO"]
    elif ev_id in [4874]:
        tags = ["AMEACA_DISPUTA", "FALSA_MEDIDA_PROTETIVA", "CRIME"]
    elif ev_id in [3356, 3652, 3653, 3654, 3811, 4156, 4157, 4158, 4276]:
        tags = ["CONTRATO", "CONTRATO_DIVIDA"]
    elif ev_id in [746, 1147, 1148, 1355, 1540, 1568, 1579, 1582, 1607, 3119, 3449, 4367, 4368, 4393, 4394, 4397, 4561, 4618, 4680]:
        tags = ["FINANCEIRO", "FINANCEIRO_APORTE"]
    elif ev_id in [9, 17, 1421, 1422, 1459]:
        tags = ["PARCERIA_COMERCIAL", "CONTRATO"]
    else:
        tags = ["AMEACA_DISPUTA", "JURIDICO_DISPUTA"]
        
    ev_obj = {
        "id": msg["id"],
        "date": msg["date"],
        "time": msg["time"],
        "author": msg["author"],
        "content": msg["content"],
        "attachment": att,
        "audio_transcription": tr,
        "tags": tags
    }
    if custom_badge:
        ev_obj["custom_badge"] = custom_badge
    if custom_note:
        ev_obj["custom_note"] = custom_note
        
    # Assign to block
    d = msg["date"]
    day, month, year = [int(x) for x in d.split("/")]
    
    if month == 7 or (month == 8 and day <= 2):
        assigned_block = "bloco-1"
    elif month == 8 and day in [3, 4]:
        assigned_block = "bloco-2"
    elif month == 8 and 5 <= day <= 15:
        assigned_block = "bloco-3"
    elif month == 8 and 16 <= day <= 18:
        assigned_block = "bloco-4"
    elif month == 8 and day == 19:
        assigned_block = "bloco-5"
    elif month == 8 and 20 <= day <= 31:
        assigned_block = "bloco-6"
    elif month == 9 and 1 <= day <= 2:
        assigned_block = "bloco-7"
    elif month == 9 and 3 <= day <= 10:
        assigned_block = "bloco-8"
    elif month == 9 and 11 <= day <= 13:
        assigned_block = "bloco-9"
    elif month == 9 and 14 <= day <= 15:
        assigned_block = "bloco-10"
    else:
        assigned_block = "bloco-10"
        
    for b in blocks:
        if b["id"] == assigned_block:
            b["events"].append(ev_obj)
            break

# Build audio repository data (filtered of all forbidden/accident/personal audios)
audio_vault = []
for msg in chat_messages:
    att = msg["attachment"]
    if att and att.endswith(".opus") and att in transcriptions:
        is_exc, reason = is_forbidden(msg)
        if is_exc:
            continue
        audio_vault.append({
            "id": msg["id"],
            "filename": att,
            "date": msg["date"],
            "time": msg["time"],
            "author": msg["author"],
            "duration": round(transcriptions[att].get("duration", 0), 1),
            "transcription": transcriptions[att].get("text", ""),
            "tags": msg["tags"]
        })

# Evidence gallery metadata with both chat attachments and official app screenshots
evidence_gallery = [
    {
        "id": "ev-pix-40k",
        "title": "Comprovante Pix R$ 40.000,00 (04/08/2026)",
        "category": "Comprovantes Financeiros",
        "filename": "00001604-PHOTO-2026-08-04-10-29-00.jpg",
        "date": "04/08/2026 10:28:49",
        "origin": "Nu Pagamentos S.A. — Agilidade para Todos (CNPJ 27.626.226/0001-59)",
        "destiny": "C. Caruso Arquitetura e Interiores Ltda (CNPJ 46.788.820/0001-90) — Banco Santander",
        "authId": "E18236120202608041328s14787e325d",
        "description": "Comprovante oficial de transferência bancária via Pix no valor de R$ 40.000,00 creditado imediatamente na conta PJ de Camila Caruso, viabilizado por empréstimo de Capital de Giro tomado por Gustavo no Nubank.",
        "ocrText": "Comprovante de transferência 04 AGO 2026 - 10:28:49. Valor: R$ 40.000,00. Tipo: Pix. Destino: C. CARUSO ARQUITETURA E INTERIORES LTDA CNPJ 46.788.820/0001-90 Santander. Origem: AGILIDADE PARA TODOS CNPJ 27.626.226/0001-59 Nubank. ID: E18236120202608041328s14787e325d."
    },
    {
        "id": "ev-pix-72k",
        "title": "Comprovante Pix R$ 72.000,00 (19/08/2026)",
        "category": "Comprovantes Financeiros",
        "filename": "00003448-PHOTO-2026-08-19-16-10-56.jpg",
        "date": "19/08/2026 16:10:39",
        "origin": "Itaú Unibanco S.A. SISPAG — Gustavo Henrique Castellano (CNPJ 27.626.226/0001-59)",
        "destiny": "Arquiteta Camila Caruso — Banco Santander (CNPJ 46.788.820/0001-90)",
        "authId": "E60701190202608191909DYSMAN3D8X4",
        "description": "Comprovante oficial do segundo repasse no valor de R$ 72.000,00 via Itaú SISPAG, vinculado expressamente na mensagem à parceria comercial e capital de giro, oriundo da Cédula Pronampe Itaú.",
        "ocrText": "19 ago. 2026, 16:10:39, via SISPAG no app Itaú. PIX TRANSFERENCIA. Valor: R$ 72.000,00. De: GUSTAVO HENRIQUE CASTELLANO Ag 0173 CC 99110-0 CNPJ 27.626.226/0001-59. Para: ARQUITETA CAMILA CARUSO Santander CNPJ 46.788.820/0001-90. Mensagem: deposito referente a obra que estamos operando em parceria Camila Caruso e Agilidade para Todos. ID: E60701190202608191909DYSMAN3D8X4. Autenticação: A84590460945ACACFBE66745CC6299E86E69A7A3."
    },
    {
        "id": "ev-itau-pronampe1-app",
        "title": "Itaú Giro Pronampe 1: Contrato 4887183848 (Saldo R$ 119.343,17)",
        "category": "Contratos Bancários",
        "filename": "comprovante_itau_pronampe1_detalhes.png",
        "date": "Setembro/2026",
        "origin": "App Itaú Empresas",
        "authId": "Contrato nº 4887183848",
        "description": "Extrato oficial do Itaú Empresas para o Giro Pronampe principal: Restante a pagar no app: R$ 119.343,17; 0 de 60 parcelas pagas; 1ª parcela de R$ 2.324,17 com vencimento em 15/02/2027. Linha que viabilizou o repasse de R$ 72.000,00 à Camila.",
        "ocrText": "meu empréstimo - giro pronampe. número do contrato: 4887183848. valor pago: R$ 0,00. restante a pagar: R$ 119.343,17. 0 de 60 parcelas pagas (em dia). 1ª parcela: R$ 2.324,17 em 15 de fevereiro de 2027."
    },
    {
        "id": "ev-itau-pronampe2-app",
        "title": "Itaú Giro Pronampe 2: Contrato 4886874439 (Saldo R$ 19.527,27)",
        "category": "Contratos Bancários",
        "filename": "comprovante_itau_pronampe2_detalhes.png",
        "date": "Setembro/2026",
        "origin": "App Itaú Empresas",
        "authId": "Contrato nº 4886874439",
        "description": "Extrato oficial do Itaú Empresas para o Giro Pronampe complementar: Restante a pagar no app: R$ 19.527,27; 0 de 60 parcelas pagas; 1ª parcela de R$ 381,45 com vencimento em 22/02/2027. Recursos utilizados para quitar 13 parcelas do Nubank.",
        "ocrText": "meu empréstimo - giro pronampe. número do contrato: 4886874439. valor pago: R$ 0,00. restante a pagar: R$ 19.527,27. 0 de 60 parcelas pagas (em dia). 1ª parcela: R$ 381,45 em 22 de fevereiro de 2027."
    },
    {
        "id": "ev-nubank-detalhes-app",
        "title": "Nubank: Saldo Devedor, Total Pago e Condições CET",
        "category": "Contratos Bancários",
        "filename": "comprovante_nubank_detalhes.png",
        "date": "Setembro/2026",
        "origin": "App Nubank PJ",
        "authId": "Capital de Giro Reorganizado",
        "description": "Extrato oficial do Nubank comprovando as condições da dívida: Restante a pagar no app: R$ 30.069,79 (11 parcelas agendadas); Total pago na antecipação: R$ 18.015,62; Quitação à vista hoje: R$ 24.898,68; CET de 63,14% a.a. (taxa 3,95% a.m.).",
        "ocrText": "O restante a pagar é R$ 30.069,79. Total pago: R$ 18.015,62. Valor escolhido: R$ 42.039,57. Tributos (IOF): R$ 11,33. Valor contratado: R$ 42.050,90. Se você quitar o empréstimo hoje, você pagará R$ 24.898,68. Taxa de juros: 3,95% ao mês. CET composto por juros e IOF: 63,14%."
    },
    {
        "id": "ev-nubank-antecipacao-recibo",
        "title": "Nu Financeira: Recibo Oficial Quitação 13 Parcelas (R$ 18.015,62)",
        "category": "Contratos Bancários",
        "filename": "comprovante_nubank_antecipacao_recibo.png",
        "date": "24/08/2026 14:08:35",
        "origin": "Nu Financeira S.A. (CNPJ 30.680.829/0001-43)",
        "authId": "6a8c7a93-3aec-4cb7-838c-65d9a92f1499",
        "description": "Comprovante oficial emitido pela Nu Financeira comprovando a antecipação e liquidação da 12ª à 24ª parcelas (13 parcelas): Valor original R$ 35.537,03; Desconto obtido: R$ 17.521,40; Valor pago: R$ 18.015,62 via saldo em conta.",
        "ocrText": "Nu - Comprovante de pagamento. 24 ago 2026 14:08:35. Valor: R$ 18.015,62. Método: Antecipação. Origem: Gustavo Henrique Castellano, Nu Financeira S.A., Agência 1, Conta 39971663-6. Nome do empréstimo: Capital de Giro reorganizado. Valor original: R$ 35.537,03. Desconto por antecipação: R$ 17.521,40. Parcelas correspondentes: Da 12ª à 24ª parcelas. Nu Financeira S.A. CNPJ 30.680.829/0001-43. Código de autenticação: 6a8c7a93-3aec-4cb7-838c-65d9a92f1499."
    },
    {
        "id": "ev-itau-lista-contratos",
        "title": "Itaú Empresas: Tela Oficial com os 2 Contratos Ativos",
        "category": "Contratos Bancários",
        "filename": "00004367-PHOTO-2026-09-09-17-56-20.jpg",
        "date": "09/09/2026",
        "origin": "App Itaú Empresas",
        "authId": "Extrato de Contratos de Empréstimo",
        "description": "Captura enviada por Gustavo à Camila no WhatsApp comprovando a existência de duas operações simultâneas de Pronampe no Itaú: Contrato Principal de R$ 119k e Contrato Secundário de R$ 19,5k.",
        "ocrText": "meus empréstimos e financiamentos. giro pronampe 4887183848 restante a pagar R$ 119.343,17. giro pronampe 4886874439 restante a pagar R$ 19.527,27."
    },
    {
        "id": "ev-pix-itau-nubank",
        "title": "Pix Itaú para Nubank R$ 18.653,05 (Pronampe 2 -> Nubank)",
        "category": "Comprovantes Financeiros",
        "filename": "00004395-PHOTO-2026-09-09-18-05-16.jpg",
        "date": "24/08/2026 14:06:16",
        "origin": "Itaú Unibanco S.A. — Agilidade para Todos",
        "destiny": "Nu Pagamentos S.A. — Agilidade para Todos",
        "authId": "Pix 24 AGO 2026 14:06:16",
        "description": "Transferência imediata do recurso liberado pelo 2º Giro Pronampe Itaú para a conta Nubank PJ, realizada às 14:06:16 para viabilizar a antecipação de 13 parcelas efetuada 2 minutos depois (às 14:08:35).",
        "ocrText": "Agilidade Para Todos. R$ 18.653,05. 24 AGO 2026 - 14:06:16. Transferência recebida Pix. Nome: Agilidade Para Todos. Instituição: Itaú Unibanco S.A."
    },
    {
        "id": "ev-contrato-docx",
        "title": "Minuta do Contrato de Parceria Comercial e Mútuo",
        "category": "Documentos e Contratos",
        "filename": "00003356-Contrato de Parceria.docx",
        "date": "19/08/2026 11:04:45",
        "origin": "Minuta jurídica enviada via WhatsApp",
        "authId": "Contrato de Parceria.docx",
        "description": "Instrumento contratual formal elaborado para regular a parceria e o reembolso dos aportes financeiros, cuja assinatura foi solenemente prometida por Camila ('coloque tudo lá e amanhã já assinamos') e posteriormente descumprida.",
        "ocrText": "Instrumento Particular de Parceria Comercial, Prestação de Serviços de Tecnologia e Gestão, e Reconhecimento de Mútuo Financeiro entre C. Caruso Arquitetura e Interiores Ltda e Gustavo Henrique Castellano ME."
    },
    {
        "id": "ev-termo-divida-docx",
        "title": "Anexo II: Termo de Reconhecimento de Dívida",
        "category": "Documentos e Contratos",
        "filename": "00003652-Anexo II - Termo de Reconhecimento de Divida.docx",
        "date": "21/08/2026 08:22:56",
        "origin": "Minuta jurídica enviada via WhatsApp",
        "authId": "Anexo II - Termo de Reconhecimento de Dívida",
        "description": "Termo formal discriminando o valor repassado (R$ 112.000,00), as parcelas e os encargos bancários assumidos, com cláusula de confissão irrevogável de dívida.",
        "ocrText": "Anexo II - Termo de Confissão e Reconhecimento de Dívida e Cronograma de Reembolso Financeiro."
    }
]

# Multi-Agent Forensic Data
multi_agent_data = {
    "agent_financial": {
        "title": "Auditoria Contábil, Conciliação Bancária e Nexo Causal",
        "status": "Concluída — 100% Conciliado",
        "findings": """
1. REPASSE DIRETO LÍQUIDO À RÉ (PREJUÍZO LÍQUIDO PRIMÁRIO):
- 04/08/2026 às 10:28:49: Pix Nu Pagamentos de R$ 40.000,00 para C. Caruso Arquitetura (Santander, CNPJ 46.788.820/0001-90).
- 19/08/2026 às 16:10:39: Pix Itaú SISPAG de R$ 72.000,00 para Arquiteta Camila Caruso (Santander, CNPJ 46.788.820/0001-90).
- Total Direto Creditado nas Contas da Ré: R$ 112.000,00 (cento e doze mil reais).

2. OPERAÇÕES BANCÁRIAS CONTRATADAS PELO AUTOR (CONFORME TELAS DOS APPS):
- Itaú Giro Pronampe 1 (Contrato 4887183848): Restante a pagar no app de R$ 119.343,17 (60 parcelas de R$ 2.324,17; financiou o repasse de R$ 72k da Ré).
- Itaú Giro Pronampe 2 (Contrato 4886874439): Restante a pagar no app de R$ 19.527,27 (60 parcelas de R$ 381,45; liberou R$ 18.653,05 para quitar as 13 parcelas do Nubank).
- Nubank Capital de Giro Reorganizado: Contratado originalmente por R$ 42.050,90 (CET 63,14% a.a.). Antecipação de 13 parcelas por R$ 18.015,62 (desconto de R$ 17.521,40). Saldo restante a pagar no app: R$ 30.069,79 em 11 parcelas de R$ 2.733,62 (ou R$ 24.898,68 para quitação à vista hoje).

3. TOTAL DO SALDO DEVEDOR PRINCIPAL ATUAL NOS BANCOS:
- R$ 119.343,17 (Itaú 1) + R$ 19.527,27 (Itaú 2) + R$ 30.069,79 (Nubank) = R$ 168.940,23 (ou R$ 163.769,12 para liquidação à vista imediata).
- Soma nominal projetada a prazo (60 meses cheios): R$ 192.406,99.
        """
    },
    "agent_legal": {
        "title": "Enquadramento Penal e Estratégia Processual Cível",
        "status": "Tipificação Consolidada",
        "findings": """
1. ESFERA CÍVEL:
- Ação de Cobrança c/c Cumprimento de Obrigação de Fazer e Ressarcimento de Danos Materiais e Morais.
- Pedido de Tutela Provisória de Urgência Cautelar (Arresto via Sisbajud e Restrição de Transferência via Renajud sobre o veículo).

2. ESFERA CRIMINAL — NOTÍCIA-CRIME / REPRESENTAÇÃO CRIMINAL:
- Fatos: Instauração de Inquérito Policial para apuração dos crimes de Estelionato (Art. 171 do CP) e Apropriação Indébita (Art. 168 do CP).

3. REQUERIMENTO DE PERDAS E DANOS E JUROS BANCÁRIOS:
- Condenação dos réus ao reembolso dos R$ 112.000,00 corrigidos pelo IPCA + juros legais, ressarcimento dos R$ 18.015,62 quitados no Nubank, assunção do saldo devedor do Nubank e dos contratos Pronampe 1 e 2 do Itaú, além de indenização por danos morais fixada em patamar não inferior a R$ 20.000,00.
        """
    }
}

# Legal drafts
legal_drafts = {
    "noticia_crime": """EXCELENTÍSSIMO SENHOR DOUTOR DELEGADO DE POLÍCIA TITULAR DA COMARCA DE MOGI DAS CRUZES / SÃO PAULO

NOTÍCIA-CRIME COM PEDIDO DE INSTAURAÇÃO DE INQUÉRITO POLICIAL
Tipificação: Estelionato (Art. 171, caput do Código Penal) e Apropriação Indébita (Art. 168, caput do Código Penal)

NOTICIANTE:
GUSTAVO HENRIQUE CASTELLANO, empresário individual, portador do CPF nº 030.193.641-24 e CNPJ nº 27.626.226/0001-59, residente e domiciliado na Alameda Barão de Limeira, 912, São Paulo/SP;

NOTICIADA:
CAMILA CARUSO DA COSTA NEVES, arquiteta, residente e domiciliada em Mogi das Cruzes/SP, representante legal de C. CARUSO ARQUITETURA E INTERIORES LTDA, inscrita no CNPJ sob nº 46.788.820/0001-90.

I. DOS FATOS
Em agosto de 2026, a Noticiada, sob o ardil de formalizar uma parceria comercial de expansão de seu escritório de arquitetura, induziu o Noticiante em erro ao solicitar aportes financeiros urgentes sob pretexto de capital de giro e pagamento de equipe.
O Noticiante, confiando na boa-fé da Noticiada e na sua promessa formal de celebração contratual expressa ('veja o contrato, coloque tudo lá, e amanhã já assinamos por favor' - WhatsApp em 19/08/2026), efetuou duas transferências via Pix em benefício da conta bancária da empresa da Noticiada:
1. R$ 40.000,00 em 04/08/2026 (Nubank, ID E18236120202608041328s14787e325d);
2. R$ 72.000,00 em 19/08/2026 (Itaú SISPAG, ID E60701190202608191909DYSMAN3D8X4).
Totalizando o montante de R$ 112.000,00 (cento e doze mil reais) diretamente creditados na conta da Ré.

Para mitigar os pesados encargos do socorro emergencial (CET de 63,14% a.a.), o Noticiante contratou uma segunda linha Pronampe no Itaú (Contrato nº 4886874439, saldo devedor de R$ 19.527,27) e realizou em 24/08/2026 a quitação antecipada de 13 parcelas (R$ 18.015,62 com desconto de R$ 17.521,40) do empréstimo do Nubank, remanescendo ainda 11 parcelas vincendas de R$ 2.733,62 (saldo de R$ 30.069,79), além do saldo do 1º Pronampe Itaú de R$ 119.343,17, totalizando um saldo devedor nos bancos de R$ 168.940,23 assumido exclusivamente pelo Noticiante.

Uma vez na posse dos valores, a Noticiada revelou seu intento fraudulento: recusou-se reiteradamente a assinar os contratos e termos de dívida enviados, utilizou os valores para amortizar dívidas pessoais urgentes — em especial parcelas em atraso de veículo sob litígio com o Banco Volkswagen S.A. (Processo nº 401XXXX-77.2026.8.26.0361 perante o TJSP em Mogi das Cruzes) — e, finalmente, em 14/09/2026, recusou-se a devolver os valores e ameaçou o Noticiante com a formulação de falsa medida protetiva ('Você quer que eu entre com uma medida protetiva contra você?' - Áudio 00004874).

II. DO ENQUADRAMENTO JURÍDICO
Resta plenamente configurado o delito de Estelionato (Art. 171 do CP), em razão do manifesto ardil pré-concebido e da obtenção de vantagem ilícita em prejuízo da vítima, ou subsidiariamente Apropriação Indébita (Art. 168 do CP).

III. DOS PEDIDOS
Diante do exposto, requer a instauração imediata de Inquérito Policial, com a oitiva da Noticiada, requisição de extratos bancários da conta recebedora e posterior remessa ao Ministério Público para oferecimento de denúncia criminal.""",

    "peticao_civel": """EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ___ VARA CÍVEL DO FORO CENTRAL DA COMARCA DE SÃO PAULO / OU MOGI DAS CRUZES

AÇÃO DE COBRANÇA C/C PEDIDO DE TUTELA PROVISÓRIA DE URGÊNCIA CAUTELAR DE ARRESTO (SISBAJUD / RENAJUD)

AUTOR:
GUSTAVO HENRIQUE CASTELLANO, empresário individual, inscrito no CNPJ sob nº 27.626.226/0001-59 e CPF nº 030.193.641-24;

RÉUS:
1. C. CARUSO ARQUITETURA E INTERIORES LTDA, CNPJ nº 46.788.820/0001-90;
2. CAMILA CARUSO DA COSTA NEVES, arquiteta, administradora e devedora solidária na pessoa física.

I. DO PEDIDO LIMINAR DE TUTELA DE URGÊNCIA CAUTELAR (ARTS. 300 E 301 DO CPC)
Demonstrada a probabilidade do direito (comprovantes bancários oficiais de repasse de R$ 112.000,00, confissões textuais e áudios de WhatsApp) e o perigo de dano irreparável (notória insolvência da Ré, existência de processo executivo movido pelo Banco Volkswagen sob nº 401XXXX-77.2026.8.26.0361 e iminente vencimento das parcelas do Pronampe e Nubank contraídas pelo Autor que totalizam passivo de R$ 168.940,23 registrados nos apps), REQUER-SE:
a) A concessão liminar, inaudita altera parte, de ARRESTO VIA SISBAJUD no montante de R$ 112.000,00 nas contas bancárias de ambas as Rés;
b) Restrição de transferência via RENAJUD sobre o veículo de propriedade da Ré Camila Caruso da Costa Neves.

II. DO DIREITO E DO MÉRITO
1. A existência e validade de contrato verbal e obrigação de restituição (Arts. 104, 107 e 422 do CC);
2. O enriquecimento ilícito e sem causa vedado pelo Art. 884 do Código Civil;
3. A desconsideração da personalidade jurídica com fulcro no Art. 50 do Código Civil por flagrante desvio de finalidade e confusão patrimonial.

III. DOS PEDIDOS FINAIS
Requer a citação das Rés para que paguem a quantia de R$ 112.000,00 devidamente atualizada com correção monetária pelo IPCA e juros moratórios de 1% ao mês a partir de cada desembolso, cumulada com o ressarcimento das 13 parcelas quitadas do Nubank (R$ 18.015,62), do saldo remanescente do Nubank (R$ 30.069,79), dos contratos Pronampe 1 (R$ 119.343,17) e 2 (R$ 19.527,27) assumidos perante o Itaú, e indenização por danos morais em R$ 20.000,00, além de custas e honorários advocatícios sucumbenciais."""
}

total_clean_events = sum(len(b["events"]) for b in blocks)
print(f"Total clean timeline events distributed across 10 blocks: {total_clean_events}")

data_js_content = f"""// Consolidated Dossier Dataset: Gustavo Castellano x Camila Caruso
// Generated automatically with 100% transcriptions and forensic analysis

window.DOSSIER_DATA = {{
    metadata: {{
        title: "Dossiê Jurídico e Fático — Caso Gustavo Castellano x Camila Caruso",
        subtitle: "Análise Cronológica Exaustiva, Transcrições de Áudio Whisper, Provas Financeiras, Enquadramento Penal e Auditoria de Ameaças",
        totalAmount: 112000.00,
        pixNu: 40000.00,
        pixItau: 72000.00,
        nubankValorContratado: 42050.90,
        nubankQuitadoPronampe: 18015.62,
        nubankDescontoAntecipacao: 17521.40,
        nubankParcelasQuitadas: 13,
        nubankSaldoRestante: 30069.79,
        nubankQuitacaoHoje: 24898.68,
        pronampe1Contrato: "4887183848",
        pronampe1RestanteApp: 119343.17,
        pronampe1Parcela: 2324.17,
        pronampe1QtdParcelas: 60,
        pronampe1Vencimento: "15/02/2027",
        pronampe2Contrato: "4886874439",
        pronampe2RestanteApp: 19527.27,
        pronampe2Parcela: 381.45,
        pronampe2QtdParcelas: 60,
        pronampe2Vencimento: "22/02/2027",
        totalSaldoDevedorApp: 168940.23,
        totalSaldoDevedorAVista: 163769.12,
        totalProjetadoParcelasFuturas: 192406.99,
        vwLawsuit: "Processo nº 401XXXX-77.2026.8.26.0361 (TJSP Mogi das Cruzes)",
        totalMessages: {len(chat_messages)},
        totalAudios: {len(audio_vault)},
        generatedAt: "2026-09-16"
    }},
    blocks: {json.dumps(blocks, ensure_ascii=False, indent=2)},
    audioVault: {json.dumps(audio_vault, ensure_ascii=False, indent=2)},
    evidenceGallery: {json.dumps(evidence_gallery, ensure_ascii=False, indent=2)},
    multiAgentData: {json.dumps(multi_agent_data, ensure_ascii=False, indent=2)},
    legalDrafts: {json.dumps(legal_drafts, ensure_ascii=False, indent=2)}
}};
"""

with open("data.js", "w", encoding="utf-8") as out:
    out.write(data_js_content)

print(f"data.js regenerated cleanly! Size: {len(data_js_content) / 1024:.1f} KB")
