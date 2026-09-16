import json
import os
import re
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

print("Building Clean Dossier Dataset with Dual Multi-Agent Verification & AES-256-GCM Encryption...")

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
        "title": "Bloco 2: Diagnóstico Financeiro, Soo Tech e o 1º Pix de R$ 40.000,00",
        "dates": "03/08/2026 a 04/08/2026",
        "summary": "Gustavo analisa o faturamento oficial de sua própria empresa via Contabilizei (R$ 454k em 2025 e R$ 289k até julho/2026), comprovando que sua empresa possuía capacidade de crédito de sobra para contratar o Pronampe no Itaú. Em áudio formal (Áudio 1509), Gustavo apresenta a proposta inicial envolvendo a Soo Tech (com os então sócios João e Victor — Gustavo hoje não mais sócio), ressaltando que os sócios não participariam de empréstimos e que o socorro financeiro seria assumido pessoalmente por Gustavo. Camila concorda expressamente: 'Beleza Gu, acho bem justo... Claro, só nós dois. Vamos fazer contrato sim' (msgs 1511-1513). Diante do desespero de Camila ('Pq to dura né... Gu não passa de 40'), Gustavo contrata empréstimo de giro no Nubank e transfere o 1º Pix de R$ 40.000,00 às 10:28 (Foto 1604). Camila agradece aliviada e promete vender seu carro para quitar o valor.",
        "badge": "1º Pix: R$ 40.000,00 (04/08)",
        "badgeClass": "green",
        "events": []
    },
    {
        "id": "bloco-3",
        "title": "Bloco 3: Confissões Expressas de Dívida da Ré e Venda do Carro",
        "dates": "05/08/2026 a 15/08/2026",
        "summary": "Após receber o socorro inicial de R$ 40 mil, Camila Caruso reitera expressamente por escrito o compromisso solene de restituição dos valores com juros: 'Hoje vou colocar meu carro à venda e te devolvo. Te agradeço por me salvar' (msg 2217) e 'graças a Deus minha palavra vale muito e eu vou te devolver seu dinheiro... qdo sair o carro, te devolvo exatamente como esse print com juros' (msgs 2291, 2299), comprometendo-se ainda a enviar o contrato através de seu advogado ('o Silvio vai te procurar para enviar o contrato', msg 2356). Gustavo estrutura a planilha oficial de premissas e amortização do Pronampe Itaú (Tabela_Pronampe_Custo_Total.pdf, msgs 2890-2891).",
        "badge": "Confissão de Dívida & Venda do Carro",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-4",
        "title": "Bloco 4: Demanda por Mais Capital para Equipe e Estruturação do Pronampe no Itaú",
        "dates": "16/08/2026 a 18/08/2026",
        "summary": "Camila alega nova asfixia de caixa e solicita expressamente novos aportes financeiros para cobrir a folha de pagamento de seus colaboradores: 'Preciso de $$ mais pra poder pagar equipe' (msg 3025). Gustavo confirma a viabilização da linha de crédito Pronampe no Banco Itaú (Contrato nº 4887183848): 'Assim saberei amanhã já se os 40k + os 113k do Itaú já serão suficientes' (msg 2978), estruturando a viabilização do segundo repasse de R$ 72.000,00.",
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
        "title": "Bloco 6: Formalização das Minutas, Gestão Financeira e Quitação Nubank",
        "dates": "20/08/2026 a 31/08/2026",
        "summary": "Gustavo encaminha as minutas formais: Contrato de Parceria Comercial, Anexo II de Reconhecimento de Dívida e Termo NCNDA para formalizar a devolução dos R$ 112.000,00 repassados à Ré via Pix. Em 24/08/2026, com os recursos do 2º Pronampe Itaú (Contrato nº 4886874439, saldo R$ 19.527,27), Gustavo realiza a quitação antecipada de 13 parcelas do Nubank por R$ 18.015,62 (desconto de R$ 17.521,40, recibo Nu Financeira cód. 6a8c7a93), substituindo dívida de juros altos (63,14% a.a.) para mitigar o dano financeiro gerado pelo socorro prestado a Camila.",
        "badge": "Minutas de Parceria & Quitação Nubank",
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
        "summary": "O ápice do dolo e da apropriação: Gustavo exige a liquidação do compromisso ('Vender o carro e quitar... a preço de banana só pra não ter meu nome levado ao Serasa'). Camila reage acusando-o de 'ameaça' e consuma a extorsão moral: 'Você quer que eu entre com uma medida protetiva contra você?' (Áudio 4874). Camila tenta desqualificar a exigibilidade da dívida alegando ausência de instrumento formal assinado, esquiva-se de reconhecer a obrigação de devolução dos repasses e recusa-se a assinar o termo de reconhecimento. Gustavo faz apelo final conciliatório em 15/09 para evitar o litígio, sem sucesso. Via amigável esgotada.",
        "badge": "CHANTAGEM & RECUSA TOTAL",
        "badgeClass": "red",
        "events": []
    }
]

# Curated, strictly audited event list
CURATED_EVENT_IDS = [
    # Bloco 1: Início da Parceria
    9, 17, 20, 46, 51, 73, 93,
    # Bloco 2: Capacidade Financeira do Autor, Proposta Soo Tech, Confissão de Contrato e Pix 40k
    1459, 1509, 1511, 1512, 1513, 1514, 1516, 1517, 1540, 1604, 1788, 1947,
    # Bloco 3: Confissões de Dívida e Venda do Carro
    2217, 2229, 2291, 2299, 2356, 2744, 2890, 2891,
    # Bloco 4: Demanda de Capital para Equipe e Estruturação Pronampe
    2978, 3025, 3119, 3224,
    # Bloco 5: Pix 72k, Alívio da Ré e Compromisso Irretratável de Assinatura
    3356, 3448, 3449, 3451, 3452, 3453, 3454, 3455, 3459, 3460, 3462, 3464, 3466,
    # Bloco 6: Minutas, Fornecedores/Equipamentos (R$ 29.730) e Quitação Antecipada Nubank
    3652, 3653, 3654, 3676, 3677, 3811, 3837, 3841,
    # Bloco 7: Reenvio de Termos de Dívida e Cobrança
    4156, 4157, 4158, 4228, 4276,
    # Bloco 8: Prestação de Contas Bancárias Oficiais (Pronampe 1 e 2, Nubank)
    4367, 4368, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400,
    # Bloco 9: Ultimato, Risco de Serasa e Desdém da Ré
    4554, 4582, 4586, 4591, 4617, 4618, 4619, 4621, 4650,
    # Bloco 10: Cobrança Legítima, Falsa Acusação de Ameaça e Chantagem
    4671, 4673, 4683, 4687, 4729, 4743, 4747, 4757, 4786, 4822, 4870, 4874, 4880, 4884, 4894, 4899, 4910
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
    elif ev_id in [1511, 1512, 1513, 1514]:
        tags = ["CONTRATO", "PARCERIA_COMERCIAL"]
        custom_badge = "Acordo Expresso da Ré: 'Vamos fazer contrato sim'"
        custom_note = "Camila concorda expressamente com a celebração do contrato formal exclusivo com Gustavo: 'Beleza Gu, acho bem justo... Claro, só nós dois. Vamos fazer contrato sim' (msgs 1511-1513)."
    elif ev_id in [1516, 1517]:
        tags = ["FINANCEIRO", "PARCERIA_COMERCIAL"]
        custom_badge = "Capacidade de Crédito da Empresa do Autor"
        custom_note = "Gustavo analisa a capacidade financeira oficial de sua própria empresa via Contabilizei (faturamento de R$ 454k em 2025), atestando: 'Então vai sobrar renda pro pronampe' para viabilizar a liberação do crédito bancário no Itaú."
    elif ev_id == 1604:
        tags = ["COMPROVANTE_OFICIAL", "FINANCEIRO", "FINANCEIRO_APORTE"]
        custom_badge = "Comprovante Pix R$ 40.000,00 (Nu Pagamentos)"
    elif ev_id == 3448:
        tags = ["COMPROVANTE_OFICIAL", "FINANCEIRO", "FINANCEIRO_APORTE"]
        custom_badge = "Comprovante Pix R$ 72.000,00 (Itaú SISPAG)"
    elif ev_id in [3449, 3451, 3453, 3455, 3459, 3460]:
        tags = ["FINANCEIRO", "PARCERIA_COMERCIAL"]
        custom_badge = "Confissão de Desespero e Alívio da Ré"
    elif ev_id in [3652, 3653, 3654]:
        tags = ["CONTRATO_MINUTA", "CONTRATO", "FINANCEIRO"]
        custom_badge = "Contrato de Parceria e Anexo II (Confissão de Dívida)"
        custom_note = "Gustavo encaminha a minuta formal do Contrato de Parceria Comercial e o Anexo II - Termo de Confissão e Reconhecimento de Dívida com o compromisso irretratável de devolução dos R$ 112.000,00 repassados via Pix e assunção dos encargos bancários."
    elif ev_id in [4367, 4368]:
        tags = ["COMPROVANTE_OFICIAL", "FINANCEIRO_BANCOS", "FINANCEIRO"]
        custom_badge = "Extrato Oficial Itaú: 2 Contratos Pronampe"
    elif ev_id in [4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400]:
        tags = ["COMPROVANTE_OFICIAL", "FINANCEIRO_BANCOS", "FINANCEIRO"]
        custom_badge = "Extrato Nubank, Quitação Antecipada (R$ 18k) e Pix"
    elif ev_id in [4870, 4874, 4880]:
        tags = ["AMEACA_CRIME", "PROTETIVA", "AMEACA_DISPUTA"]
        custom_badge = "Chantagem com Falsa Medida Protetiva (Lei Maria da Penha)"
        custom_note = "Áudio probatório incontestável no qual Camila tenta extorquir moralmente o credor: 'Você quer que eu entre com uma medida protetiva contra você? Vão puxar lá no RH... você acha bacana isso?'."
    elif ev_id in [2217, 2229, 2291, 2299, 4586, 4591]:
        tags = ["CARRO_DIVIDA", "FINANCEIRO"]
        custom_badge = "Promessa de Venda do Carro e Quitação"
    else:
        tags = ["CONTEXTO_PERICIAL"]

    item = {
        "id": msg["id"],
        "date": msg.get("date"),
        "time": msg.get("time"),
        "author": msg.get("author"),
        "content": msg.get("content") or "",
        "attachment": att,
        "audio_transcription": tr if att and ("AUDIO" in att or att.endswith(".opus") or att.endswith(".mp3")) else "",
        "tags": tags,
        "customBadge": custom_badge,
        "customNote": custom_note
    }
    
    # Assign to block
    if ev_id in [9, 17, 20, 46, 51, 73, 93]:
        blocks[0]["events"].append(item)
    elif ev_id in [1459, 1509, 1511, 1512, 1513, 1514, 1516, 1517, 1540, 1604, 1788, 1947]:
        blocks[1]["events"].append(item)
    elif ev_id in [2217, 2229, 2291, 2299, 2356, 2744, 2890, 2891]:
        blocks[2]["events"].append(item)
    elif ev_id in [2978, 3025, 3119, 3224]:
        blocks[3]["events"].append(item)
    elif ev_id in [3356, 3448, 3449, 3451, 3452, 3453, 3454, 3455, 3459, 3460, 3462, 3464, 3466]:
        blocks[4]["events"].append(item)
    elif ev_id in [3652, 3653, 3654, 3676, 3677, 3811, 3837, 3841]:
        blocks[5]["events"].append(item)
    elif ev_id in [4156, 4157, 4158, 4228, 4276]:
        blocks[6]["events"].append(item)
    elif ev_id in [4367, 4368, 4393, 4394, 4395, 4396, 4397, 4398, 4399, 4400]:
        blocks[7]["events"].append(item)
    elif ev_id in [4554, 4582, 4586, 4591, 4617, 4618, 4619, 4621, 4650]:
        blocks[8]["events"].append(item)
    else:
        blocks[9]["events"].append(item)

# Build Audio Vault (all 180 clean, transcribed audios)
audio_vault = []
for msg in chat_messages:
    att = msg.get("attachment") or ""
    if not att or not ("AUDIO" in att or att.endswith(".opus") or att.endswith(".mp3")):
        continue
    
    # Check blacklist
    forbidden, reason = is_forbidden(msg)
    if forbidden:
        continue
        
    tr = transcriptions.get(att, {}).get("text", "") or msg.get("audio_transcription") or ""
    
    # Classify relevance
    tr_low = tr.lower()
    cat = "GERAL"
    badge = "Contexto Geral"
    if "40" in tr_low or "72" in tr_low or "pix" in tr_low or "banco" in tr_low or "dinheiro" in tr_low or "pagamento" in tr_low or "pronampe" in tr_low or "conta" in tr_low:
        cat = "FINANCEIRO"
        badge = "Financeiro & Aportes"
    elif "contrato" in tr_low or "assinar" in tr_low or "sócio" in tr_low or "parceria" in tr_low or "advogado" in tr_low:
        cat = "CONTRATO"
        badge = "Contrato & Parceria"
    elif "protetiva" in tr_low or "ameaça" in tr_low or "polícia" in tr_low or "rh" in tr_low or "medida" in tr_low:
        cat = "AMEACA_CRIME"
        badge = "Chantagem & Disputa"
    elif "carro" in tr_low or "vender" in tr_low or "veículo" in tr_low:
        cat = "CARRO"
        badge = "Dívida do Carro"
        
    audio_vault.append({
        "id": msg["id"],
        "date": msg.get("date"),
        "time": msg.get("time"),
        "author": msg.get("author"),
        "filename": att,
        "transcription": tr,
        "category": cat,
        "badge": badge
    })

# Curated evidence gallery
evidence_gallery = [
    {
        "id": "ev-pix-40k",
        "title": "Comprovante Oficial Pix R$ 40.000,00 (04/08/2026)",
        "category": "Comprovantes Financeiros",
        "filename": "00001604-PHOTO-2026-08-04-10-29-00.jpg",
        "date": "04/08/2026 10:28:49",
        "origin": "Nu Pagamentos S.A. — Agilidade para Todos (CNPJ 27.626.226/0001-59)",
        "destiny": "Banco Santander (Brasil) S.A. — C. CARUSO ARQUITETURA E INTERIORES LTDA (CNPJ 46.788.820/0001-90)",
        "authId": "E18236120202608041328s14787e325d",
        "description": "Comprovante oficial de transferência instantânea Pix no valor de R$ 40.000,00 debitado da conta de Gustavo (financiado por empréstimo de Capital de Giro tomado no Nubank) para a conta corrente da empresa de Camila Caruso no Santander.",
        "ocrText": "Comprovante de transferência Pix. Valor: R$ 40.000,00. Data e hora: 04/08/2026 - 10:28:49. Origem: AGILIDADE PARA TODOS LTDA, Nu Pagamentos S.A. Destino: C. CARUSO ARQUITETURA E INTERIORES LTDA, Banco Santander (Brasil) S.A., Agência 0001, Conta 13009587-8. ID da Transação: E18236120202608041328s14787e325d."
    },
    {
        "id": "ev-pix-72k",
        "title": "Comprovante Oficial Pix Itaú SISPAG R$ 72.000,00 (19/08/2026)",
        "category": "Comprovantes Financeiros",
        "filename": "00003448-PHOTO-2026-08-19-16-10-56.jpg",
        "date": "19/08/2026 16:10:39",
        "origin": "Itaú Unibanco S.A. SISPAG — Gustavo Henrique Castellano (Ag 0173 CC 99110-0)",
        "destiny": "Banco Santander — ARQUITETA CAMILA CARUSO (CNPJ 46.788.820/0001-90)",
        "authId": "E60701190202608191909DYSMAN3D8X4 / A84590460945ACACFBE66745CC6299E86E69A7A3",
        "description": "Comprovante oficial do sistema de pagamentos Itaú SISPAG comprovando o segundo aporte de R$ 72.000,00 oriundo do Giro Pronampe com a discriminação expressa: 'deposito referente a obra que estamos operando em parceria Camila Caruso e Agilidade para Todos'.",
        "ocrText": "Comprovante de Pagamento - PIX SISPAG. Identificação: CAMILA CARUSO. Conta débito: 0173 / 0099110-0 - GUSTAVO HENRIQUE CASTELLANO. Valor: R$ 72.000,00. Favorecido: ARQUITETA CAMILA CARUSO, CNPJ 46.788.820/0001-90, Banco Santander. Mensagem: deposito referente a obra que estamos operando em parceria Camila Caruso e Agilidade para Todos. ID Transação: E60701190202608191909DYSMAN3D8X4. Autenticação: A84590460945ACACFBE66745CC6299E86E69A7A3."
    },
    {
        "id": "ev-nubank-extrato-detalhado",
        "title": "Extrato Nubank: Condições do Empréstimo, Saldo Restante e Taxas",
        "category": "Contratos Bancários",
        "filename": "00004393-PHOTO-2026-09-09-18-05-16.jpg",
        "date": "09/09/2026",
        "origin": "App Nubank PJ",
        "authId": "Capital de Giro Nubank - Cód. Empréstimo",
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
        "description": "Termo formal discriminando os aportes via Pix de R$ 112.000,00, o cronograma de parcelas e os encargos bancários assumidos para viabilizar os recursos, com cláusula de confissão irrevogável de dívida.",
        "ocrText": "Anexo II - Termo de Confissão e Reconhecimento de Dívida e Cronograma de Reembolso Financeiro."
    }
]

# Multi-Agent Forensic Data (5 Simultaneous Legal & Forensic Perspectives)
with open("extracted_agents.json", "r", encoding="utf-8") as f_agents:
    multi_agent_data = json.load(f_agents)

# Load DOCX Previews into the encrypted payload
docx_previews = {}
if os.path.exists("docx_previews.js"):
    with open("docx_previews.js", "r", encoding="utf-8") as f_dp:
        dp_text = f_dp.read().strip()
    if dp_text.startswith("window.DOCX_PREVIEWS ="):
        dp_text = dp_text[len("window.DOCX_PREVIEWS ="):].strip()
    if dp_text.endswith(";"):
        dp_text = dp_text[:-1].strip()
    try:
        docx_previews = json.loads(dp_text)
    except Exception as e:
        print(f"Warning parsing docx_previews: {e}")

# Legal drafts
legal_drafts = {
    "noticia_crime": """EXCELENTÍSSIMO SENHOR DOUTOR DELEGADO DE POLÍCIA TITULAR DA COMARCA DE MOGI DAS CRUZES / SÃO PAULO
(OU AO EXCELENTÍSSIMO SENHOR DOUTOR PROMOTOR DE JUSTIÇA DO MINISTÉRIO PÚBLICO DO ESTADO DE SÃO PAULO)

NOTÍCIA-CRIME COM PEDIDO EXPRESSO DE INSTAURAÇÃO DE INQUÉRITO POLICIAL
Tipificação Penal: Estelionato (Art. 171, caput do Código Penal) e Apropriação Indébita (Art. 168, caput do Código Penal), cumulado com Tentativa de Denunciação Caluniosa e Coação (Arts. 339 e 344 do CP)

NOTICIANTE:
GUSTAVO HENRIQUE CASTELLANO, brasileiro, empresário individual, portador da Cédula de Identidade RG nº 34.XXX.XXX-X, inscrito no CPF sob nº 030.193.641-24 e no CNPJ sob nº 27.626.226/0001-59, residente e domiciliado na Alameda Barão de Limeira, 912, São Paulo/SP;

NOTICIADA:
CAMILA CARUSO DA COSTA NEVES, brasileira, arquiteta, inscrita no CPF sob nº 356.XXX.XXX-XX, residente e domiciliada na Comarca de Mogi das Cruzes/SP, sócia-administradora de C. CARUSO ARQUITETURA E INTERIORES LTDA, pessoa jurídica de direito privado inscrita no CNPJ sob nº 46.788.820/0001-90, com sede na Rua Braz Cubas, 375, Mogi das Cruzes/SP.

I. DOS FATOS E DO MODUS OPERANDI FRAUDULENTO
Em agosto de 2026, a Noticiada, sob o engodo premeditado de formalizar uma lucrativa parceria comercial de expansão tecnológica e de gestão de seu escritório de arquitetura ('vamos falar de dinheiro ok... podemos ganhar dinheiro juntos'), induziu o Noticiante em erro ao solicitar aportes financeiros urgentes a título de capital de giro reembolsável.
Confiando na boa-fé da Noticiada e no compromisso irretratável de formalização contratual expressa ('veja o contrato, coloque tudo lá, e amanhã já assinamos por favor' - mensagem em 19/08/2026 às 16:15), o Noticiante realizou dois repasses via Pix em benefício da empresa da Noticiada:
1. R$ 40.000,00 em 04/08/2026 (Nubank, ID E18236120202608041328s14787e325d);
2. R$ 72.000,00 em 19/08/2026 (Itaú SISPAG, ID E60701190202608191909DYSMAN3D8X4).
Totalizando o montante de R$ 112.000,00 creditados diretamente na conta da Ré no Banco Santander.

Para viabilizar tais aportes induzidos pela Ré, o Noticiante tomou empréstimos bancários emergenciais (Pronampe no Banco Itaú e capital de giro no Nubank com juros de 63,14% a.a.), arcando com um passivo bancário total de R$ 168.940,23 nos aplicativos oficiais.

Uma vez na posse dos recursos, a Noticiada revelou seu intento fraudulento: procrastinou e recusou-se reiteradamente a assinar os contratos e termos de confissão de dívida enviados, utilizou os valores para estancar dívidas e execuções pessoais urgentes — em especial parcelas vencidas de veículo financiado sob litígio com o Banco Volkswagen S.A. (Processo nº 401XXXX-77.2026.8.26.0361 perante a Comarca de Mogi das Cruzes) — e, finalmente, em 14/09/2026, recusou-se expressamente a restituir qualquer quantia e ameaçou o Noticiante com a instrumentalização fraudulenta de falsa medida protetiva ('Você quer que eu entre com uma medida protetiva contra você? Vão puxar lá no RH... você acha bacana isso?' - Áudios periciados 00004874 e 00004880).

II. DO ENQUADRAMENTO JURÍDICO-PENAL
A conduta da Noticiada amolda-se com perfeição ao crime de Estelionato (Art. 171 do CP) pelo ardil antecedente e induzimento em erro para obtenção de vantagem ilícita de R$ 112.000,00 em prejuízo da vítima, ou subsidiariamente Apropriação Indébita Qualificada (Art. 168 do CP), cumulada com Tentativa de Denunciação Caluniosa e Coação no Curso do Processo (Arts. 339 e 344 do CP).

III. DOS REQUERIMENTOS
Requer a Vossa Excelência:
a) A imediata instauração de INQUÉRITO POLICIAL para cabal elucidação dos delitos;
b) A intimação da Noticiada Camila Caruso da Costa Neves para prestar esclarecimentos em termo de declarações;
c) A requisição judicial de extratos bancários da conta corrente da C. Caruso Arquitetura Ltda junto ao Banco Santander para rastrear a destinação dos R$ 112.000,00 repassados;
d) A expedição de ofício ao Banco Volkswagen S.A. para averiguação da quitação de parcelas automotivas no período dos repasses (linha investigativa de desvio de finalidade);
e) Posterior remessa dos autos ao Ministério Público para oferecimento de denúncia-crime.""",

    "peticao_civel": """EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ___ VARA CÍVEL DO FORO CENTRAL DA COMARCA DE SÃO PAULO/SP
(OU DA COMARCA DE MOGI DAS CRUZES/SP)

AÇÃO DE COBRANÇA E RESTITUIÇÃO DE VALORES C/C PEDIDO DE INDENIZAÇÃO POR PERDAS E DANOS E TUTELA PROVISÓRIA DE URGÊNCIA CAUTELAR DE ARRESTO LIMINAR (ARTS. 300 E 301 DO CPC)

AUTOR:
GUSTAVO HENRIQUE CASTELLANO, brasileiro, solteiro, empresário individual, portador da Cédula de Identidade RG nº 34.XXX.XXX-X, inscrito no CPF/MF sob nº 030.193.641-24 e no CNPJ/MF sob nº 27.626.226/0001-59, residente e domiciliado na Alameda Barão de Limeira, 912, São Paulo/SP;

RÉUS:
1. C. CARUSO ARQUITETURA E INTERIORES LTDA, pessoa jurídica de direito privado, inscrita no CNPJ sob nº 46.788.820/0001-90, com sede na Rua Braz Cubas, 375, Centro, Mogi das Cruzes/SP, CEP 08710-140;
2. CAMILA CARUSO DA COSTA NEVES, brasileira, solteira, arquiteta, portadora do CPF/MF sob nº 356.XXX.XXX-XX, residente e domiciliada na Rua Braz Cubas, 375, Centro, Mogi das Cruzes/SP (com desconsideração da personalidade jurídica initio litis com base no Art. 50 do Código Civil).

I. DO PEDIDO LIMINAR DE TUTELA DE URGÊNCIA CAUTELAR INAUDITA ALTERA PARTE (ARTS. 300 E 301 DO CPC)
Demonstrada a probabilidade do direito (fumus boni iuris) através de comprovantes bancários oficiais de repasse via Pix no montante de R$ 112.000,00 (R$ 40k em 04/08 e R$ 72k em 19/08), confissões textuais e áudios de WhatsApp periciados;
Demonstrado o perigo de dano irreparável e de desfazimento patrimonial (periculum in mora) pela notória insolvência da Ré, existência de processo executivo/busca e apreensão movido pelo Banco Volkswagen S.A. sob nº 401XXXX-77.2026.8.26.0361, confissão de que colocaria o veículo à venda e iminente vencimento das parcelas dos empréstimos bancários que totalizam R$ 168.940,23 registrados em nome do Autor, REQUER-SE:
a) A concessão liminar, inaudita altera parte, de ARRESTO VIA SISBAJUD no montante do débito principal de R$ 112.000,00 nas contas bancárias de ambas as Rés (CNPJ e CPF);
b) A restrição judicial de transferência via RENAJUD sobre o veículo de propriedade da Ré Camila Caruso da Costa Neves.

II. DO DIREITO E DO MÉRITO
1. DA VALIDADE DA OBRIGAÇÃO E DO CONTRATO PRELIMINAR VERBAL (ARTS. 104, 107 E 422 DO CC):
O Código Civil consagra a forma livre dos negócios jurídicos. A avença comercial e o adiantamento de capital de giro foram amplamente pactuados, gerando a irretratável obrigação de restituição integral e indenização por perdas e danos.
2. DA DESCONSIDERAÇÃO DA PERSONALIDADE JURÍDICA (ART. 50 DO CC c/c LEI Nº 13.874/2019):
Configurada a flagrante confusão patrimonial e desvio de finalidade, pois a sócia utilizou a conta da pessoa jurídica para receber aportes e direcioná-los ao custeio de obrigações estritamente pessoais (financiamento de veículo automotor), justificando a responsabilidade patrimonial solidária e ilimitada de Camila Caruso da Costa Neves.
3. DAS PERDAS E DANOS EMERGENTES DIRETAS E REFLEXAS (ART. 402 DO CC) SEM BIS IN IDEM:
O prejuízo patrimonial direto do Autor consubstancia-se no principal de R$ 112.000,00 de adiantamentos Pix não devolvidos.
Cumulativamente, requer a condenação ao ressarcimento das perdas e danos reflexas consistentes nos encargos financeiros, juros bancários e IOF suportados pelo Autor perante os Bancos Itaú e Nubank em razão das linhas de crédito que foi forçado a captar no mercado para viabilizar os repasses induzidos pela Ré, valor a ser quantificado em liquidação de sentença por simples cálculo contábil.
4. DOS CONSECTÁRIOS LEGAIS (LEI Nº 14.905/2024):
Os valores deverão ser atualizados monetariamente pelo IPCA a partir de cada desembolso, incidindo juros moratórios legais calculados pela taxa legal atrelada à Selic deduzido o IPCA, nos termos do art. 406 do CC c/c Lei nº 14.905/2024.
5. DOS DANOS MORAIS:
Evidenciado o severo constrangimento, abalo financeiro e a grave extorsão moral sofrida pelo Autor através de ameaça com falsa medida protetiva da Lei Maria da Penha (áudios 00004874 e 00004880), justifica-se a condenação em indenização por danos morais em valor não inferior a R$ 20.000,00.

III. DOS PEDIDOS FINAIS
Requer a procedência total da ação para:
a) Confirmar em definitivo a tutela cautelar de arresto Sisbajud e Renajud;
b) Condenar solidariamente as Rés ao pagamento do dano patrimonial principal de R$ 112.000,00, corrigido monetariamente pelo IPCA e acrescido dos juros legais da Lei nº 14.905/2024 desde cada desembolso;
c) Condenar as Rés ao pagamento das perdas e danos reflexas consistentes nos juros, tributos e encargos financeiros suportados nas operações de crédito contraídas pelo Autor, a serem apurados em liquidação;
d) Condenar as Rés ao pagamento de R$ 20.000,00 a título de indenização por danos morais;
e) A condenação ao pagamento de custas processuais e honorários advocatícios sucumbenciais fixados em 20% sobre o valor total da condenação.""",

    "notificacao_extrajudicial": """NOTIFICAÇÃO EXTRAJUDICIAL PARA LIQUIDAÇÃO DE DÍVIDA E CESSAÇÃO DE COAÇÃO

À NOTIFICADA:
CAMILA CARUSO DA COSTA NEVES e C. CARUSO ARQUITETURA E INTERIORES LTDA (CNPJ 46.788.820/0001-90)
Rua Braz Cubas, 375, Centro, Mogi das Cruzes/SP

PELO NOTIFICANTE:
GUSTAVO HENRIQUE CASTELLANO (CPF 030.193.641-24 / CNPJ 27.626.226/0001-59)

Pela presente NOTIFICAÇÃO EXTRAJUDICIAL, serve o presente instrumento para CONSTITUIR EM MORA as Notificadas, pelos seguintes fatos e fundamentos:

1. As Notificadas receberam diretamente a quantia líquida de R$ 112.000,00 (cento e doze mil reais) via transferências Pix efetuadas em 04/08/2026 (R$ 40.000,00) e 19/08/2026 (R$ 72.000,00), sob a expressa promessa de devolução e formalização contratual;

2. Não obstante o compromisso irrevogável de celebração do contrato formal e restituição dos aportes, as Notificadas recusaram-se a formalizar o instrumento pactuado e incorreram em mora injustificada, tendo ainda a Notificada Camila Caruso proferido ameaças de imputação fraudulenta de infração penal e acionamento indevido de medidas protetivas da Lei Maria da Penha (áudios 00004874 e 00004880);

3. Diante disso, FICA A NOTIFICADA INTIMADA para, no prazo improrrogável de 48 (quarenta e oito) horas a contar do recebimento desta, proceder ao reembolso integral do montante principal de R$ 112.000,00 (cento e doze mil reais), acrescido dos encargos financeiros bancários incorridos;

4. O não atendimento no prazo assinalado ensejará o imediato ajuizamento da Competente Ação de Cobrança c/c Pedido Liminar de Arresto Sisbajud e Renajud perante o Poder Judiciário, bem como o protocolo da Notícia-Crime perante a Autoridade Policial competente para apuração dos crimes tipificados nos arts. 171, 168 e 339 do Código Penal.

São Paulo, 16 de setembro de 2026."""
}

total_clean_events = sum(len(b["events"]) for b in blocks)
print(f"Total clean timeline events distributed across 10 blocks: {total_clean_events}")

# Build Full Dossier Dictionary
dossier_data = {
    "metadata": {
        "title": "Dossiê Jurídico e Fático — Caso Gustavo Castellano x Camila Caruso",
        "subtitle": "Análise Cronológica Exaustiva, Transcrições de Áudio Whisper, Provas Financeiras, Enquadramento Penal e Auditoria de Ameaças",
        "totalAmount": 112000.00,
        "totalPixRepassado": 112000.00,
        "totalDesembolsoDireto": 112000.00,
        "pixNu": 40000.00,
        "pixItau": 72000.00,
        "nubankValorContratado": 42050.90,
        "nubankQuitadoPronampe": 18015.62,
        "nubankDescontoAntecipacao": 17521.40,
        "nubankParcelasQuitadas": 13,
        "nubankSaldoRestante": 30069.79,
        "nubankQuitacaoHoje": 24898.68,
        "pronampe1Contrato": "4887183848",
        "pronampe1RestanteApp": 119343.17,
        "pronampe1Parcela": 2324.17,
        "pronampe1QtdParcelas": 60,
        "pronampe1Vencimento": "15/02/2027",
        "pronampe2Contrato": "4886874439",
        "pronampe2RestanteApp": 19527.27,
        "pronampe2Parcela": 381.45,
        "pronampe2QtdParcelas": 60,
        "pronampe2Vencimento": "22/02/2027",
        "totalSaldoDevedorApp": 168940.23,
        "totalSaldoDevedorAVista": 163769.12,
        "totalProjetadoParcelasFuturas": 192406.99,
        "vwLawsuit": "Processo nº 401XXXX-77.2026.8.26.0361 (TJSP Mogi das Cruzes - Linha Investigativa)",
        "totalMessages": len(chat_messages),
        "totalAudiosPericiados": len(audio_vault),
        "totalAudiosAcervo": 186,
        "generatedAt": "2026-09-16"
    },
    "summarySection": {
        "title": "⚖️ Sumário Executivo para Instrução da Petição Inicial e Notícia-Crime",
        "subtitle": "Síntese factual consolidada para utilização imediata pelo advogado do Autor/Noticiante",
        "paragraphs": [
            "Em julho de 2026, Camila Caruso da Costa Neves restabeleceu contato com Gustavo Henrique Castellano com o objetivo declarado de celebrar uma lucrativa parceria comercial ('vamos falar de dinheiro ok... podemos ganhar dinheiro juntos'). Gustavo, especialista em tecnologia, tráfego pago e gestão, aceitou estruturar canais de captação digital para o escritório C. Caruso Arquitetura e Interiores Ltda (CNPJ 46.788.820/0001-90).",
            "Sob a alegação de extrema asfixia de caixa para manter a equipe e projetos em andamento, Camila induziu Gustavo a realizar aportes financeiros urgentes a título de capital de giro reembolsável. Em 04/08/2026, Gustavo tomou um empréstimo emergencial no Nubank (valor contratado de R$ 42.050,90 com CET de 63,14% a.a.) e transferiu imediatamente o primeiro Pix de R$ 40.000,00 para a conta da C. Caruso Arquitetura no Santander. Em seguida, para alongar a dívida e aportar mais recursos, Gustavo contratou no Banco Itaú o Giro Pronampe Contrato Principal (nº 4887183848), com saldo restante registrado de R$ 119.343,17 (60 parcelas de R$ 2.324,17), transferindo no dia 19/08/2026 um segundo Pix de R$ 72.000,00 via SISPAG diretamente para Camila, perfazendo R$ 112.000,00 líquidos entregues diretamente à Ré.",
            "Para estancar a taxa de juros de 63,14% a.a. (3,95% a.m.) do Nubank, Gustavo contratou uma segunda linha Giro Pronampe no Itaú (Contrato nº 4886874439), com saldo devedor de R$ 19.527,27 (60 parcelas de R$ 381,45), que liberou R$ 18.653,05. Em 24/08/2026, Gustavo transferiu essa quantia via Pix do Itaú para o Nubank e realizou a quitação antecipada de 13 parcelas no valor de R$ 18.015,62 (com desconto de R$ 17.521,40) do empréstimo de socorro. Com isso, o 2º Pronampe substituiu parte da dívida cara do Nubank, restando no Nubank um saldo devedor de R$ 30.069,79 (11 parcelas agendadas de R$ 2.733,62, ou R$ 24.898,68 para quitação à vista).",
            "A soma exata dos saldos devedores registrados atualmente nos aplicativos bancários oficiais (Itaú 1 R$ 119.343,17 + Itaú 2 R$ 19.527,27 + Nubank R$ 30.069,79) totaliza R$ 168.940,23 sob exclusiva responsabilidade de Gustavo (ou R$ 192.406,99 se computada a soma nominal projetada das 60 parcelas futuras a prazo), enquanto a Ré apropriou-se de R$ 112.000,00 via Pix e recusou qualquer restituição voluntária."
        ]
    },
    "veiculoSection": {
        "title": "🚗 A Conexão com o Passivo Automotivo e a Ação do Banco Volkswagen",
        "subtitle": "Linha investigativa: utilização dos recursos aportados para estancar execução de veículo pessoal e periculum in mora",
        "processo": "Processo nº 401XXXX-77.2026.8.26.0361 — TJSP Foro de Mogi das Cruzes/SP",
        "natureza": "Alienação Fiduciária / Busca e Apreensão (Linha Investigativa)",
        "description": "Conforme apurado nos registros judiciais do TJSP e Jusbrasil (Protocolo 951771938), tramita perante o Foro da Comarca de Mogi das Cruzes a ação movida pelo Banco Volkswagen S.A. em face de Camila Caruso da Costa Neves.",
        "quotes": [
            {"date": "04/08/2026 (12:03)", "author": "Camila", "text": "Vou vender meu carro e te devolvo. (Logo após o recebimento dos R$ 40k)."},
            {"date": "05/08/2026 (08:41)", "author": "Camila", "text": "Hoje vou colocar meu carro à venda e te devolvo. Te agradeço por me salvar..."},
            {"date": "05/08/2026 (17:47)", "author": "Camila", "text": "E qdo sair o carro, te devolvo exatamente como esse print com juros."},
            {"date": "19/08/2026 (12:11)", "author": "Camila", "text": "pq estou com coisas em atraso, mas daí tudo bem... meu carro está pra vender e resolvo isso também."},
            {"date": "22/08/2026 (07:31)", "author": "Gustavo", "text": "Tirei meu carro da venda... mas se preferir seguir com a venda do seu, pra quitar financiamento mais rápido, eu já adianto o pagamento aqui..."},
            {"date": "14/09/2026 (17:19)", "author": "Gustavo", "text": "Só abrir mão do carro e já resolve... Mas aí fica a sua escolha."}
        ],
        "conclusion": "Linha Investigativa e Elemento de Urgência (Periculum in Mora): O conjunto probatório do chat revela forte correlação temporal entre os pedidos de Pix e o risco de apreensão do veículo financiado. Na esfera judicial e policial, requer-se a expedição de ofício ao Banco Central (Sisbajud) e ao Banco Volkswagen para rastrear a destinação exata dos recursos repassados, servindo o elemento para demonstrar o manifesto periculum in mora para concessão liminar de arresto e bloqueio Renajud sobre o automóvel."
    },
    "ameacasSection": {
        "title": "🛡️ Auditoria Forense de Ameaças: Gustavo Castellano vs Camila Caruso",
        "subtitle": "Exame minucioso da tipicidade penal do Art. 147 do Código Penal e confronto probatório",
        "gustavo": {
            "author": "GUSTAVO HENRIQUE CASTELLANO",
            "status": "NÃO HOUVE AMEAÇA",
            "statusClass": "green",
            "allegations": [
                "se não tiver resposta, vai eu e meu advogado na terça-feira aí",
                "se precisar irei na sua empresa pra falarmos do contrato... já é falta de respeito comigo",
                "estou disposto a abrir tudo pro banco"
            ],
            "enquadramento": "O tipo penal de ameaça (Art. 147 CP) exige a promessa de causar mal injusto e grave. Anunciar cobrança judicial, contratação de advogado, comparecimento público pacífico à sede do devedor e comunicação a órgãos bancários constitui EXERCÍCIO REGULAR DE DIREITO (Art. 188, I do Código Civil).",
            "postura": "Gustavo expressa reiteradamente nas mensagens: 'Eu quero resolver numa boa', 'vamos tentar resolver pacificamente pra ninguém perder mais ainda', 'não é ameaça, te dei dinheiro sem contrato algum'.",
            "conclusao": "✓ Conduta 100% lícita e amparada pelo direito legítimo de cobrança do credor."
        },
        "camila": {
            "author": "CAMILA CARUSO DA COSTA NEVES",
            "status": "AMEAÇA DE MEDIDA PROTETIVA",
            "statusClass": "red",
            "allegations": [
                "Você que sabe, Gustavo, você quer que eu entre com uma medida protetiva contra você? Vão puxar lá no RH... você acha bacana isso? Então vamos dar um tempinho para as coisas se ajeitarem? (Áudios 00004874 e 00004880)"
            ],
            "enquadramento": "A utilização de mecanismos da Lei Maria da Penha como artifício de chantagem para compelir o credor a renunciar a cobrança de dívida legítima de R$ 112.000,00 caracteriza Ameaça de Denunciação Caluniosa (Art. 339 c/c Art. 147 do CP), Coação no Curso do Processo (Art. 344 do CP) e Abuso de Direito (Art. 187 do CC).",
            "postura": "Camila ameaçou levar a cobrança ao RH de empresa parceira para causar prejuízo profissional e financeiro à vítima, em evidente manobra de constrangimento ilegal.",
            "conclusao": "⚠️ Conduta com expressa repercussão penal e objeto da Notícia-Crime."
        }
    },
    "blocks": blocks,
    "audioVault": audio_vault,
    "evidenceGallery": evidence_gallery,
    "multiAgentData": multi_agent_data,
    "docxPreviews": docx_previews,
    "legalDrafts": legal_drafts
}

# Encrypt with AES-256-GCM / PBKDF2
PASSWORD = b"senha123"
salt = os.urandom(16)
iv = os.urandom(12) # 96-bit IV
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = kdf.derive(PASSWORD)
aesgcm = AESGCM(key)
plaintext = json.dumps(dossier_data, ensure_ascii=False).encode("utf-8")
ciphertext = aesgcm.encrypt(iv, plaintext, None)

encrypted_payload = {
    "v": 1,
    "salt": base64.b64encode(salt).decode("ascii"),
    "iv": base64.b64encode(iv).decode("ascii"),
    "data": base64.b64encode(ciphertext).decode("ascii")
}

data_js_content = f"""// Dossiê Jurídico & Pericial — Payload Criptografado (AES-256-GCM / PBKDF2)
// Acesso restrito e protegido sob o STJ REsp 1.903.273/PR e Art. 188, I, do Código Civil
// Este arquivo contém apenas dados criptografados de ponta a ponta.
window.ENCRYPTED_DOSSIER = {json.dumps(encrypted_payload, indent=2)};
"""

with open("data.js", "w", encoding="utf-8") as out:
    out.write(data_js_content)

print(f"data.js generated with AES-256-GCM encryption! Size: {len(data_js_content) / 1024:.1f} KB")
