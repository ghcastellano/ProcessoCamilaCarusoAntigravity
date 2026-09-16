import json
import os
import re

print("Building data.js for Dossier Web Platform...")

# Load transcriptions
with open("transcriptions.json", "r", encoding="utf-8") as f:
    transcriptions = json.load(f)

# Load chat dataset
with open("chat_dataset.json", "r", encoding="utf-8") as f:
    chat_messages = json.load(f)

# Filter key events for the Curated Chronological Timeline
# Organized into 10 thematic blocks
blocks = [
    {
        "id": "bloco-1",
        "title": "Bloco 1: Reaproximação, Proposta de Negócios e Ambiguidade Afetiva",
        "dates": "29/07/2026 a 02/08/2026",
        "summary": "Após período de afastamento, Camila Caruso entra em contato pedindo desbloqueio e propõe parceria comercial: 'Gustavo vamos falar de dinheiro ok... podemos ganhar dinheiro juntos'. Gustavo aceita e propõe estratégias de captação de clientes para arquitetura de alto padrão e clínicas. Concomitantemente, ocorrem rusgas e cobranças pessoais.",
        "badge": "Início da Relação Comercial",
        "badgeClass": "blue",
        "events": []
    },
    {
        "id": "bloco-2",
        "title": "Bloco 2: Diagnóstico da C. Caruso, Apuros Financeiros e o Primeiro Pix de R$ 40.000,00",
        "dates": "03/08/2026 a 04/08/2026",
        "summary": "Gustavo analisa as finanças da empresa de Camila via Contabilizei (faturamento 2025 de R$ 454k). Camila relata desespero financeiro com contas atrasadas e equipe a pagar: 'Gu não passa de 40... to dura né'. Em 04/08, para socorrer Camila com urgência antes da liberação do Pronampe, Gustavo contrata empréstimo emergencial de Capital de Giro no Nubank com juros elevados (R$ 40.000,00) e às 10:28 transfere o 1º Pix de R$ 40.000,00 diretamente para o CNPJ de Camila (Santander). Camila comemora aliviada: 'Nossa... nem sei como te agradecer... tudo o que eu for falar é pouco'. Logo em seguida surgem atritos e Camila promete: 'Vou vender meu carro e te devolvo com juros'.",
        "badge": "1º Pix: R$ 40.000,00 (04/08)",
        "badgeClass": "green",
        "events": []
    },
    {
        "id": "bloco-3",
        "title": "Bloco 3: Internação Hospitalar de Gustavo e Estruturação Financeira do Pronampe",
        "dates": "05/08/2026 a 15/08/2026",
        "summary": "Gustavo é internado no Hospital Serpiero em Santos. Camila envia flores em agradecimento pelo socorro financeiro. Durante o período, discutem a venda do carro dela para quitar o empréstimo ('qdo sair o carro, te devolvo exatamente com juros'). Gustavo elabora uma detalhada tabela de amortização do Pronampe para aliviar o fluxo de caixa de Camila com prazos longos.",
        "badge": "Internação & Projeção Pronampe",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-4",
        "title": "Bloco 4: Aprovação do Giro Pronampe no Itaú (R$ 113.653,00) e Planejamento",
        "dates": "16/08/2026 a 18/08/2026",
        "summary": "Gustavo obtém a liberação da linha Giro Pronampe no Itaú no valor de R$ 113.653,00 (60 parcelas de R$ 2.324,17). Camila pede mais capital: 'Preciso de $$ mais pra poder pagar equipe'. Alinham o lançamento do novo site institucional da arquiteta, planilhas de clínicas e hospitais em SP e aproximação com a gerente Mary do Itaú Empresas.",
        "badge": "Crédito Bancário Aprovado",
        "badgeClass": "blue",
        "events": []
    },
    {
        "id": "bloco-5",
        "title": "Bloco 5: O Segundo Pix de R$ 72.000,00 e o Compromisso Solene de Assinatura Contratual",
        "dates": "19/08/2026",
        "summary": "Data decisiva do negócio: Gustavo calcula a diferença (R$ 113k - R$ 41k = R$ 72k) e às 16:10 realiza o segundo Pix no valor de R$ 72.000,00 via Itaú SISPAG para a C. Caruso Arquitetura. Camila reage em lágrimas de alívio: 'Muito obrigada! To até com vontade de chorar... nossa tava desesperada'. Camila assume compromisso categórico: 'Veja o contrato, coloque tudo lá. E amanhã já assinamos por favor'. O total transferido atinge R$ 112.000,00.",
        "badge": "2º Pix: R$ 72.000,00 (19/08) — Total R$ 112k",
        "badgeClass": "green",
        "events": []
    },
    {
        "id": "bloco-6",
        "title": "Bloco 6: Formalização Jurídica, Quitação de 13 Parcelas Nubank e Início da Procrastinação",
        "dates": "20/08/2026 a 31/08/2026",
        "summary": "Gustavo envia a minuta completa do Contrato de Parceria Comercial e o Anexo II (Termo de Confissão de Dívida solidária física). Em 24/08/2026, com a aprovação de linha complementar no Itaú Pronampe, Gustavo realiza Pix de R$ 18.653,05 do Itaú para o Nubank (Foto 4395) e antecipa 13 parcelas (R$ 18.015,62) do empréstimo de socorro do Nubank (Foto 4396), reduzindo os juros e restando 11 parcelas agendadas de R$ 2.733,62 (R$ 30.069,79 de saldo remanescente, Foto 4393). No Itaú constam 2 contratos Pronampe ativos (Foto 4367). Paralelamente, Camila passa a postergar a assinatura alegando que seu advogado está analisando.",
        "badge": "Quitação Nubank 13x & Minutas",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-7",
        "title": "Bloco 7: Reenvio do Termo de Confissão de Dívida e Resistência Evasiva de Camila",
        "dates": "01/09/2026 a 02/09/2026",
        "summary": "Gustavo reenvia os contratos revisados por advogada especialista. Camila começa a questionar cláusulas e resiste: 'Gustavo projeto não é pastel... estamos conversando, não montando um processo'. Camila desdenha: 'Palavra qualquer um fala né?'. Gustavo explica que o piso mensal de R$ 2.325,00 reflete exatamente a parcela que ele tem que pagar ao banco.",
        "badge": "Evasão e Questionamento",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-8",
        "title": "Bloco 8: Prestação de Contas Bancárias (Nubank e Itaú) e Alertas Formais",
        "dates": "03/09/2026 a 10/09/2026",
        "summary": "Gustavo relata que está em situação crítica, sem faturamento e com crédito esgotado. Em 09/09/2026, Gustavo envia para Camila a comprovação documental cabal de todas as dívidas assumidas: foto dos 2 contratos Pronampe no Itaú (Foto 4367), extrato do Nubank comprovando as 13 parcelas quitadas e 11 restantes (Foto 4393), o Pix de R$ 18.653,05 Itaú-Nubank (Foto 4395) e a antecipação de R$ 18.015,62 (Foto 4396). Camila responde com evasivas e frieza. Gustavo convoca alinhamento formal de calendário para segunda-feira, 14/09.",
        "badge": "Provas Bancárias & Alerta",
        "badgeClass": "amber",
        "events": []
    },
    {
        "id": "bloco-9",
        "title": "Bloco 9: O Ultimato de Sexta-Feira e o Risco Iminente de Serasa",
        "dates": "11/09/2026 a 13/09/2026",
        "summary": "Gustavo informa que sua conta bancária está no limite do cheque especial e que terá o nome inscrito no Serasa se as parcelas não forem honradas. Camila alega que 'só em novembro' conseguiria fazer empréstimo. Gustavo avisa que se não houver resposta na segunda-feira, irá na terça com advogado. Camila ironiza: 'Nossa obrigada pela generosidade'.",
        "badge": "Risco de Negativação & Aviso Judicial",
        "badgeClass": "red",
        "events": []
    },
    {
        "id": "bloco-10",
        "title": "Bloco 10: A Ruptura Definitiva, Chantagem com Falsa Medida Protetiva e Recusa Total",
        "dates": "14/09/2026 a 15/09/2026",
        "summary": "O clímax do conflito: Gustavo exige prazo e restituição do dinheiro para não negativar suas contas. Camila dispara sequência de áudios agressivos, acusando Gustavo de 'ameaça' e ameaçando expressamente: 'Você quer que eu entre com uma medida protetiva contra você?'. Camila afirma que vai denunciá-lo no RH de parceiros e nega que o Pix tenha validade ('Que Pix? Não recebi nenhum seu... word não é contrato assinado'). Gustavo tenta conciliação pacífica no dia 15/09 para evitar processo, sem resposta. Esgotada a via amigável.",
        "badge": "GOLPE CONCLUÍDO & CHANTAGEM",
        "badgeClass": "red",
        "events": []
    }
]

# Distribute key messages across the 10 blocks
for msg in chat_messages:
    d = msg["date"]
    m_id = msg["id"]
    author = msg["author"]
    content = msg["content"]
    att = msg["attachment"]
    tr_text = msg["audio_transcription"]
    tags = msg["tags"]
    
    # Filter key messages
    is_key = False
    if att and (
        att.endswith(('.pdf', '.docx')) 
        or any(x in att for x in ['4367', '4368', '4393', '4395', '4396', '3941', '3944', '3945', '2295', '2296', '2297', '2298', '1604', '3448', '2864'])
    ):
        is_key = True
    elif any(t in tags for t in ["FINANCEIRO", "CONTRATO", "AMEACA_DISPUTA", "CARRO_DIVIDA"]):
        if any(w in (content + " " + (tr_text or "")).lower() for w in [
            "40k", "40.000", "72.000", "112.000", "113.000", "pronampe", "pix", "carro", "vender meu carro",
            "veja o contrato", "amanhã já assinamos", "medida protetiva", "ameaç", "advogado", "processo",
            "serasa", "cheque especial", "declaração", "banco volkswagen", "mogi", "word não é contrato",
            "nubank", "18.015", "18.653", "antecip", "capital de giro", "reorganizado", "13 parcelas",
            "meus contratos", "2.733", "2.324", "381,45"
        ]):
            is_key = True
            
    if not is_key:
        continue

    # Assign to block
    day, month, year = [int(x) for x in d.split("/")]
    assigned_block = None
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

    if assigned_block:
        for b in blocks:
            if b["id"] == assigned_block:
                b["events"].append({
                    "id": m_id,
                    "date": d,
                    "time": msg["time"],
                    "author": author,
                    "content": content,
                    "attachment": att,
                    "audio_transcription": tr_text,
                    "tags": tags
                })
                break

# Build audio repository data (all 186 opus audios)
audio_vault = []
for msg in chat_messages:
    att = msg["attachment"]
    if att and att.endswith(".opus") and att in transcriptions:
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

# Evidence gallery metadata
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
        "id": "ev-pronampe",
        "title": "Cédula de Crédito Bancário Giro Pronampe Itaú (R$ 113.653,00)",
        "category": "Contratos Bancários",
        "filename": "00003945-Documento.pdf",
        "date": "Agosto/2026",
        "origin": "Itaú Unibanco S.A. -> Gustavo Henrique Castellano",
        "authId": "Operação 4887183848",
        "description": "Contrato de financiamento federal Giro Pronampe contratado por Gustavo no valor líquido de R$ 113.653,00 (montante total com juros de R$ 139.450,20 em 60 parcelas de R$ 2.324,17), de onde saíram os R$ 72.000,00 repassados à ré.",
        "ocrText": "GUSTAVO HENRIQUE CASTELLANO. Giro Pronampe. Operação: 4887183848. Valor Liberado: R$ 113.653,00. Total Financiado: R$ 117.563,82. Total com Juros: R$ 139.450,20. 60 parcelas de R$ 2.324,17."
    },
    {
        "id": "ev-nubank-loan",
        "title": "Comprovante de Antecipação de 13 Parcelas Nubank (R$ 18.015,62)",
        "category": "Contratos Bancários",
        "filename": "00004396-PHOTO-2026-09-09-18-05-35.jpg",
        "date": "24/08/2026 às 14:08:35",
        "origin": "Nu Financeira S.A. — Gustavo Henrique Castellano (Conta 39971663-6)",
        "destiny": "Quitação Parcial de Capital de Giro tomado para socorrer Camila",
        "authId": "Antecipação Nubank 13 parcelas",
        "description": "Comprovante oficial de pagamento de R$ 18.015,62 antecipando 13 parcelas do empréstimo de Capital de Giro do Nubank contratado inicialmente para viabilizar o primeiro Pix de R$ 40k à Camila.",
        "ocrText": "Comprovante de pagamento 24 ago 2026 14:08:35. Valor: R$ 18.015,62. Método: Antecipação. Origem: Gustavo Henrique Castellano, Nu Financeira S.A. Empréstimo: Capital de Giro reorganizado. Valor original: R$ 35.537,03. Quitação de 13 parcelas antecipadas."
    },
    {
        "id": "ev-pix-itau-nubank",
        "title": "Pix Itaú para Nubank para Quitação das 13 Parcelas (R$ 18.653,05)",
        "category": "Comprovantes Financeiros",
        "filename": "00004395-PHOTO-2026-09-09-18-05-16.jpg",
        "date": "24/08/2026 às 14:06:16",
        "origin": "Itaú Unibanco S.A. (Giro Pronampe 2) -> Nu Pagamentos S.A.",
        "destiny": "Agilidade Para Todos (Gustavo Henrique Castellano)",
        "authId": "Pix 24 AGO 2026 14:06:16",
        "description": "Transferência recebida no Nubank oriunda da conta Itaú Pronampe para liquidar a antecipação de R$ 18.015,62 das parcelas do empréstimo de giro.",
        "ocrText": "Agilidade Para Todos. R$ 18.653,05. 24 AGO 2026 - 14:06:16. Transferência recebida Pix de Gustavo Henrique Castellano - Itaú Unibanco S.A."
    },
    {
        "id": "ev-nubank-app",
        "title": "Extrato Nubank: 13 Parcelas Pagas e 11 Parcelas Restantes",
        "category": "Contratos Bancários",
        "filename": "00004393-PHOTO-2026-09-09-18-03-38.jpg",
        "date": "09/09/2026",
        "origin": "App Nubank PJ",
        "authId": "Capital de Giro Reorganizado",
        "description": "Demonstrativo no app Nubank comprovando 13 parcelas pagas e saldo devedor remanescente de R$ 30.069,79 distribuído em 11 parcelas agendadas de R$ 2.733,62 sob exclusiva responsabilidade de Gustavo.",
        "ocrText": "Valor restante de Capital de Giro reorganizado: R$ 30.069,79. 13 parcelas pagas. 11 parcelas agendadas de R$ 2.733,62."
    },
    {
        "id": "ev-itau-contratos",
        "title": "Extrato Itaú Empresas: 2 Contratos de Giro Pronampe",
        "category": "Contratos Bancários",
        "filename": "00004367-PHOTO-2026-09-09-17-56-20.jpg",
        "date": "09/09/2026",
        "origin": "App Itaú Empresas",
        "authId": "Contratos Pronampe 1 e 2",
        "description": "Demonstrativo dos 2 contratos de Giro Pronampe tomados por Gustavo no Itaú: Contrato 1 com parcela de R$ 2.324,17 (60 parcelas = R$ 139.450,20) e Contrato 2 com parcela de R$ 381,45 (60 parcelas = R$ 22.887,00).",
        "ocrText": "Meus contratos. Giro Pronampe: Valor da parcela R$ 2.324,17 (0 de 60 pagas). Giro Pronampe: Valor da parcela R$ 381,45 (0 de 60 pagas)."
    },
    {
        "id": "ev-termo-divida",
        "title": "Termo de Reconhecimento de Dívida e Confissão Solidária (Anexo II)",
        "category": "Instrumentos Contratuais",
        "filename": "00004156-Anexo II - Termo de Reconhecimento de Divida.docx",
        "date": "Agosto/2026",
        "origin": "Elaborado por Castellano / Enviado à Camila Caruso",
        "authId": "Anexo II ao Contrato de Parceria Comercial",
        "description": "Instrumento contratual vinculando C. Caruso Arquitetura e Camila Caruso da Costa Neves como Devedora Solidária na pessoa física, reconhecendo os aportes reembolsáveis e o piso mensal das parcelas.",
        "ocrText": "TERMO DE RECONHECIMENTO DE DÍVIDA E COMPROMISSO DE REEMBOLSO. DEVEDORA: C. CARUSO ARQUITETURA E INTERIORES LTDA. DEVEDORA SOLIDÁRIA: Camila Caruso da Costa Neves, pessoa física. CREDOR: GUSTAVO HENRIQUE CASTELLANO. Cláusula 1.1: A DEVEDORA reconhece que recebeu do CREDOR, a título de adiantamento reembolsável de capital de giro..."
    },
    {
        "id": "ev-contrato-parceria",
        "title": "Minuta do Contrato de Parceria Comercial e Operacional",
        "category": "Instrumentos Contratuais",
        "filename": "00003944-6a87e441-f02c-4af4-a291-a27a1aab1c0b.pdf",
        "date": "24/08/2026",
        "origin": "Elaborado por Castellano / Enviado à Camila Caruso",
        "authId": "Doc 6a87e441-f02c",
        "description": "Instrumento formal com 9 páginas estipulando 20% sobre o faturamento bruto, piso mensal de reembolso bancário de R$ 2.325,00 a partir de fevereiro/2027 e prestação de contas quinzenal.",
        "ocrText": "INSTRUMENTO PARTICULAR DE PARCERIA COMERCIAL E OPERACIONAL. PARCEIRO 1: GUSTAVO HENRIQUE CASTELLANO. PARCEIRO 2: C. CARUSO ARQUITETURA E INTERIORES LTDA / CAMILA CARUSO DA COSTA NEVES. Cláusula 3.2: Piso mensal compensatório de R$ 2.325,00 todo dia 15..."
    },
    {
        "id": "ev-internacao",
        "title": "Declaração de Internação Hospitalar — Hospital Serpiero",
        "category": "Saúde e Fatos",
        "filename": "00002864-Declaração de INTERNAÇÃO HOSPITALAR.pdf",
        "date": "11/08/2026",
        "origin": "Hospital Serpiero — Santos/SP",
        "authId": "CNPJ 44.570.338/0001-54",
        "description": "Comprovação médica de que Gustavo Henrique Castellano encontrava-se internado sob cuidados médicos intensivos de 08/08/2026 em diante, momento em que Camila recebeu o primeiro aporte e planejavam o segundo.",
        "ocrText": "HOSPITAL SERPIERO CNPJ 44.570.338/0001-54. Santos/SP. DECLARAÇÃO DE INTERNAÇÃO HOSPITALAR: Declaramos que o paciente GUSTAVO HENRIQUE CASTELLANO portador do CPF 030.193.641-24 está internado nesta unidade desde 08/08/2026 até a presente data. Santos, 11 de Agosto de 2026."
    },
    {
        "id": "ev-vw-lawsuit",
        "title": "Ação Judicial Banco Volkswagen x Camila Caruso (TJSP Mogi das Cruzes)",
        "category": "Passivo Automotivo",
        "filename": "Processo nº 401XXXX-77.2026.8.26.0361",
        "date": "Ano 2026",
        "origin": "Tribunal de Justiça do Estado de São Paulo — Foro de Mogi das Cruzes",
        "authId": "Jusbrasil ID 951771938",
        "description": "Ação de cobrança / busca e apreensão movida pelo Banco Volkswagen S.A. contra Camila Caruso da Costa Neves por inadimplência do financiamento do seu veículo, cuja dívida coincide exatamente com o período dos pedidos desesperados de Pix a Gustavo.",
        "ocrText": "TJSP - Foro de Mogi das Cruzes/SP. Processo nº 401XXXX-77.2026.8.26.0361. Partes: Banco Volkswagen S.A. x Camila Caruso da Costa Neves. Assunto: Alienação Fiduciária / Busca e Apreensão / Inadimplemento de Financiamento Automotivo."
    }
]

# Multi-Agent Data: In-depth technical breakdown from 5 angles
multi_agent_data = {
    "agent_penal": {
        "title": "Agente 1: Direito Penal e Investigação Criminal",
        "lead": "Tipificação em Estelionato (Art. 171, CP) e Apropriação Indébita (Art. 168, CP)",
        "articles": ["Art. 171, caput, CP", "Art. 168, caput, CP", "Art. 339, CP (Denunciação Caluniosa)", "Art. 147, CP (Inexistência por parte da Vítima)"],
        "content": """
1. SUBSUNÇÃO AO CRIME DE ESTELIONATO (ART. 171 DO CÓDIGO PENAL):
A conduta de Camila Caruso amolda-se com precisão cirúrgica ao tipo penal de Estelionato:
- 'Obtenção de vantagem ilícita': Camila recebeu R$ 112.000,00 líquidos (R$ 40k em 04/08 e R$ 72k em 19/08) na conta bancária Santander de sua empresa C. Caruso Arquitetura.
- 'Em prejuízo alheio': Gustavo Castellano teve seu patrimônio espoliado e foi induzido a contrair um endividamento bancário consolidado de R$ 192.406,99 (empréstimo de socorro no Nubank + 2 Cédulas de Crédito Pronampe no Itaú), comprometendo gravemente sua subsistência pessoal e capacidade de crédito.
- 'Induzimento em erro mediante ardil/meio fraudulento': Camila utilizou como engodo a promessa de celebração de parceria empresarial e a garantia solene de formalização e assinatura do contrato no dia seguinte ao repasse ('veja o contrato, coloque tudo lá, e amanhã já assinamos por favor' - 19/08 às 16:15). Ocultou deliberadamente que utilizaria os recursos para estancar dívidas pessoais urgentes e manter a posse de veículo financiado perante o Banco Volkswagen (Processo nº 401XXXX-77.2026.8.26.0361 TJSP).
- 'Dolo antecedente (animus lucri faciendi)': Uma vez creditados os recursos, Camila passou a procrastinar sistematicamente a assinatura formal, inventando desculpas relativas a advogados e, no momento da cobrança legítima das parcelas bancárias, declarou com desdém que 'word não é contrato assinado' e chegou a questionar 'que Pix? Não recebi nenhum seu' (14/09).

2. SUBSIDIARIAMENTE — APROPRIAÇÃO INDÉBITA (ART. 168 DO CÓDIGO PENAL):
Caso se cogite de ausência de dolo originário, configura-se apropriação indébita qualificada, pois a investigada recebeu a posse de recursos financeiros com destinação vinculada e específica (capital de giro e despesas operacionais da parceria) e inverteu arbitrariamente o título da posse, recusando-se a restituir os valores e convertendo-os em proveito próprio e quitação de passivos pessoais.

3. TENTATIVA DE DENUNCIAÇÃO CALUNIOSA E CHANTAGEM COM LEI MARIA DA PENHA (ART. 339 DO CP):
No áudio 00004874, Camila indaga com tom intimidador: 'Você quer que eu entre com uma medida protetiva contra você?'. Essa conduta evidencia a tentativa deliberada de forjar crime inexistente e instrumentalizar os mecanismos de proteção da mulher para constranger o credor a renunciar à cobrança de dívida legítima.
        """
    },
    "agent_civil": {
        "title": "Agente 2: Direito Civil e Teoria Geral dos Contratos",
        "lead": "Contrato Verbal Válido, Violação da Boa-Fé Objetiva (Art. 422, CC) e Enriquecimento Sem Causa (Art. 884, CC)",
        "articles": ["Art. 104, CC", "Art. 107, CC (Forma Livre)", "Art. 422, CC (Boa-Fé Objetiva)", "Art. 884 a 886, CC (Enriquecimento sem Causa)", "Arts. 389 e 395, CC (Inadimplemento)"],
        "content": """
1. PLENA VALIDADE DO NEGÓCIO JURÍDICO VERBAL:
O Código Civil consagra o Princípio do Consensualismo e da Forma Livre (Art. 107). A celebração de avença comercial e mútuo feneratício não exige solenidade ad solemnitatem. As milhares de mensagens trocadas, os comprovantes de Pix de R$ 112.000,00 com expressa identificação de finalidade e os áudios confessionais comprovam inquestionavelmente a existência de vínculo obrigacional perfeito.

2. QUEBRA DA BOA-FÉ OBJETIVA E VEDAÇÃO AO VENIRE CONTRA FACTUM PROPRIUM (ART. 422 DO CC):
Camila violou de forma frontal a cláusula geral de boa-fé objetiva:
- Praticou comportamento contraditório inadmissível: solicitou o dinheiro sob a promessa solene de formalizar o contrato; após receber a quantia, tentou alegar a inexistência de instrumento assinado para se esquivar da obrigação de restituir.
- Descumprimento dos deveres anexos de conduta (lealdade, probidade, informação e cooperação).

3. ENRIQUECIMENTO SEM CAUSA (ART. 884 DO CC):
Ainda que se pretendesse desconsiderar o vínculo contratual, o ordenamento jurídico repudia o enriquecimento sem causa: 'Aquele que, sem justa causa, se enriquecer à custa de outrem, será obrigado a restituir o indevidamente auferido, feita a atualização dos valores monetários'. Não há qualquer título jurídico idôneo que justifique a apropriação dos R$ 112.000,00 pela ré.

4. PERDAS E DANOS E RESSARCIMENTO INTEGRAL DO PASSIVO BANCÁRIO:
Nos termos dos Arts. 389, 395 e 402 do CC, o inadimplemento culposo e doloso de Camila gera a obrigação de indenizar Gustavo pela integralidade dos custos financeiros decorrentes:
- Devolução dos R$ 112.000,00 corrigidos monetariamente;
- Ressarcimento das 13 parcelas quitadas antecipadamente no Nubank (R$ 18.015,62);
- Assunção ou ressarcimento do saldo devedor de 11 parcelas restantes no Nubank (R$ 30.069,79);
- Ressarcimento integral das 60 parcelas de R$ 2.324,17 do Pronampe 1 (R$ 139.450,20) e das 60 parcelas de R$ 381,45 do Pronampe 2 (R$ 22.887,00).
        """
    },
    "agent_banking": {
        "title": "Agente 3: Direito Bancário e Operações de Crédito",
        "lead": "Cédula de Crédito Giro Pronampe, Desvio de Recursos e Ação do Banco Volkswagen",
        "articles": ["Lei 13.999/2020 (Pronampe)", "Decreto-Lei 911/1969 (Alienação Fiduciária)", "Art. 50, CC (Desconsideração da Personalidade Jurídica)"],
        "content": """
1. O EMPRÉSTIMO EMERGENCIAL NUBANK (R$ 40.000,00) E A ANTECIPAÇÃO DE 13 PARCELAS:
Para viabilizar o primeiro repasse imediato em 04/08/2026, Gustavo tomou empréstimo de Capital de Giro no Nubank com taxas elevadas. Em 24/08/2026, para diminuir a asfixia provocada pelos juros do Nubank, Gustavo contratou um 2º empréstimo Pronampe no Itaú no valor de R$ 18.653,05 (parcela de R$ 381,45) e transferiu via Pix para sua conta Nubank (Foto 4395), realizando a antecipação e quitação de 13 parcelas no total de R$ 18.015,62 (Foto 4396). Restou no Nubank um saldo devedor de R$ 30.069,79 distribuído em 11 parcelas vincendas de R$ 2.733,62 (Foto 4393).

2. AS CÉDULAS DE CRÉDITO BANCÁRIO GIRO PRONAMPE (ITAÚ EMPRESAS):
Gustavo contratou duas operações Pronampe no Itaú (Foto 4367):
- Contrato Principal (Operação 4887183848): R$ 113.653,00 liberados, amortizados em 60 parcelas mensais de R$ 2.324,17 (total a prazo: R$ 139.450,20). Desses fundos saíram os R$ 72.000,00 repassados à Camila em 19/08. O valor de R$ 2.325,00 da Cláusula 3.2 do contrato refletia exatamente essa parcela.
- Contrato Complementar: 60 parcelas mensais de R$ 381,45 (total a prazo: R$ 22.887,00), cujos recursos de R$ 18.653,05 foram direcionados integralmente para quitar as 13 parcelas do socorro Nubank.

3. CONSOLIDAÇÃO DO PASSIVO BANCÁRIO ASSUMIDO (R$ 192.406,99):
O passivo futuro total assumido por Gustavo perante as instituições financeiras soma R$ 192.406,99 (R$ 139.450,20 do Pronampe 1 + R$ 22.887,00 do Pronampe 2 + R$ 30.069,79 do Nubank remanescente). Camila apropriou-se de R$ 112.000,00 líquidos e deixou toda a carga da dívida bancária sob responsabilidade exclusiva de Gustavo.

4. A CORRELAÇÃO COM O PROCESSO DO BANCO VOLKSWAGEN (TJSP MOGI DAS CRUZES):
Ação nº 401XXXX-77.2026.8.26.0361 movida pelo Banco Volkswagen S.A. contra Camila Caruso da Costa Neves. Confirma que os pedidos de socorro visavam evitar a apreensão de seu veículo pessoal, tendo prometido vendê-lo para ressarcir Gustavo ('vou vender meu carro e te devolvo com juros'). Os valores repassados por Gustavo foram desviados de sua finalidade comercial para estancar a execução da dívida automotiva pessoal.

5. DESCONSIDERAÇÃO DA PERSONALIDADE JURÍDICA (ART. 50 DO CC):
Houve flagrante confusão patrimonial entre a pessoa jurídica C. Caruso Arquitetura e a pessoa física de Camila Caruso, legitimando o pedido liminar de arresto patrimonial sobre as contas da empresa, sobre as contas de Camila (CPF) e sobre o veículo envolvido.
        """
    },
    "agent_defense": {
        "title": "Agente 4: Perspectiva Crítica da Defesa da Ré (Contrapontos)",
        "lead": "Antecipação de Teses Oponentes e Demonstração de sua Inconsistência Fática",
        "articles": ["Art. 541, CC (Forma da Doação)", "Art. 476, CC (Exceção do Contrato Não Cumprido)", "Art. 188, I, CC"],
        "content": """
1. TESE DEFENSIVA 1: ALEGAÇÃO DE DOAÇÃO / MERA LIBERALIDADE AFETIVA
- O que a ré alegará: Camila tentará destacar a frase dita por Gustavo em 05/08 ('não iria precisar devolver o pix') durante uma discussão passional para sustentar que o valor foi doado.
- Refutação irrefutável: A doação verbal só é válida para bens móveis de pequeno valor (Art. 541, parágrafo único do CC); a transferência de R$ 112.000,00 extrapola em ordens de grandeza o pequeno valor e exige instrumento público ou particular. Além disso, os atos subsequentes de ambas as partes revogaram qualquer declaração de liberalidade: em 19/08 Camila solicitou o segundo Pix de R$ 72.000,00 comprometendo-se expressamente a assinar o contrato formal ('coloque tudo lá no contrato e amanhã já assinamos'), calculou tabelas do Pronampe e, em 14/09 (áudio 00004854), confirmou que repassaria os valores que recebesse de propostas para ajudar Gustavo.

2. TESE DEFENSIVA 2: INEXISTÊNCIA DE INSTRUMENTO FORMAL ASSINADO
- O que a ré alegará: Não houve assinatura digital ou física do contrato.
- Refutação irrefutável: A recusa dolosa em assinar documento previamente prometido constitui quebra flagrante da boa-fé pré-contratual e venire contra factum proprium. Ademais, o recebimento comprovado da quantia impõe o dever irrecusável de restituição por enriquecimento sem causa (Art. 884 do CC).

3. TESE DEFENSIVA 3: ALEGAÇÃO DE ASSÉDIO / COAÇÃO
- O que a ré alegará: Camila tentará isolar as mensagens de cobrança incisiva de Gustavo em 14/09 para afirmar que foi perseguida ou coagida.
- Refutação irrefutável: Cobrança veemente de quantia expressiva, vencida e não paga, necessária à subsistência do credor e ao pagamento de financiamento bancário, não configura coação nem ameaça ilícita, mas legítimo exercício de direito (Art. 188, I do CC). Não houve promessa de mal injusto e grave.
        """
    },
    "agent_strategy": {
        "title": "Agente 5: Estrategista Processual de Gustavo (Roteiro do Advogado)",
        "lead": "Plano de Ação Jurídica Imediata: Ação de Cobrança com Arresto Cautelar e Notícia-Crime",
        "articles": ["Art. 300, CPC (Tutela de Urgência)", "Art. 301, CPC (Arresto Cautelar Sisbajud)", "Art. 50, CC", "Art. 5º, II, CPP (Inquérito Policial)"],
        "content": """
ROTEIRO PRÁTICO PARA O ADVOGADO AJUIZAR AMANHÃ CEDO:

1. ESFERA CÍVEL — AÇÃO DE COBRANÇA C/C PEDIDO LIMINAR DE TUTELA DE URGÊNCIA DE ARRESTO SISBAJUD:
- Foro: Foro Central da Comarca da Capital/SP ou Foro da Comarca de Mogi das Cruzes/SP.
- Polo Passivo: C. CARUSO ARQUITETURA E INTERIORES LTDA e CAMILA CARUSO DA COSTA NEVES (desconsideração da personalidade jurídica initio litis com base no Art. 50 do CC por confusão patrimonial e desvio de finalidade).
- Pedido Liminar Inaudita Altera Parte: Bloqueio via SISBAJUD do montante de R$ 112.000,00 (atualizado para R$ 115.000,00 com encargos) em contas bancárias da empresa e da sócia física, bem como bloqueio RENAJUD de transferência do veículo de Camila (para evitar desfazimento fraudulento de patrimônio).
- Fumus Boni Iuris: Comprovantes oficiais de Pix (Nu Pagamentos e Itaú SISPAG), confissões em áudios e mensagens de WhatsApp.
- Periculum in Mora: Risco manifesto de dilapidação, confissão de endividamento da ré, existência de ação judicial movida pelo Banco Volkswagen e declaração expressa de que pretendia vender o veículo.

2. ESFERA CRIMINAL — NOTÍCIA-CRIME / REPRESENTAÇÃO CRIMINAL:
- Endereçamento: Delegacia de Polícia de Mogi das Cruzes ou Delegacia de Polícia Especializada / Ministério Público do Estado de São Paulo.
- Fatos: Instauração de Inquérito Policial para apuração dos crimes de Estelionato (Art. 171 do CP) e Apropriação Indébita (Art. 168 do CP), requerendo a oitiva dos envolvidos, quebra de sigilo bancário da conta Santander recebedora e expedição de ofício ao Banco Volkswagen.

3. REQUERIMENTO DE PERDAS E DANOS E JUROS BANCÁRIOS:
- Condenação dos réus ao reembolso dos R$ 112.000,00 corrigidos pelo IPCA + juros de 1% ao mês, ressarcimento dos R$ 18.015,62 amortizados no Nubank, assunção do saldo devedor do Nubank de R$ 30.069,79 e das 60 parcelas do Pronampe 1 e 2, além de indenização por danos morais fixada em patamar não inferior a R$ 20.000,00.
        """
    }
}

# Legal drafts for the attorney
legal_drafts = {
    "noticia_crime": """EXCELENTÍSSIMO SENHOR DOUTOR DELEGADO DE POLÍCIA TITULAR DA COMARCA DE MOGI DAS CRUZES / SÃO PAULO

NOTÍCIA-CRIME COM PEDIDO DE INSTAURAÇÃO DE INQUÉRITO POLICIAL
Tipificação: Estelionato (Art. 171, caput do Código Penal) e Apropriação Indébita (Art. 168, caput do Código Penal)

NOTICIANTE:
GUSTAVO HENRIQUE CASTELLANO, empresário individual, portador do CPF nº 030.193.641-24 e CNPJ nº 27.626.226/0001-59, residente e domiciliado na Alameda Barão de Limeira, 912, São Paulo/SP;

NOTICIADA:
CAMILA CARUSO DA COSTA NEVES, arquiteta, residente e domiciliada em Mogi das Cruzes/SP, representante legal de C. CARUSO ARQUITETURA E INTERIORES LTDA, inscrita no CNPJ sob nº 46.788.820/0001-90, com sede na Av. Vereador Narciso Yague Guimarães, 1.145, Conj. 1214, Mogi das Cruzes/SP.

I. DOS FATOS
Em agosto de 2026, a Noticiada, sob o ardil de formalizar uma parceria comercial de expansão de seu escritório de arquitetura, induziu o Noticiante em erro ao solicitar aportes financeiros urgentes sob pretexto de capital de giro e pagamento de equipe.
O Noticiante, confiando na boa-fé da Noticiada e na sua promessa formal de celebração contratual expressa ('veja o contrato, coloque tudo lá, e amanhã já assinamos por favor' - WhatsApp em 19/08/2026), efetuou duas transferências via Pix em benefício da conta bancária da empresa da Noticiada (Banco Santander, chave CNPJ 46.788.820/0001-90):
1. R$ 40.000,00 em 04/08/2026 às 10:28:49 (Nu Pagamentos, ID E18236120202608041328s14787e325d), viabilizado por empréstimo emergencial de giro no Nubank;
2. R$ 72.000,00 em 19/08/2026 às 16:10:39 (Itaú SISPAG, ID E60701190202608191909DYSMAN3D8X4), viabilizado por Cédula de Crédito Bancário Giro Pronampe junto ao Banco Itaú (Operação nº 4887183848).
Totalizando o montante de R$ 112.000,00 (cento e doze mil reais) diretamente creditados na conta da Ré.

Para viabilizar essas operações e mitigar os pesados encargos do socorro emergencial, o Noticiante contratou uma segunda linha Pronampe no Itaú e realizou em 24/08/2026 a quitação antecipada de 13 parcelas (R$ 18.015,62) do empréstimo do Nubank, remanescendo ainda 11 parcelas vincendas de R$ 2.733,62 (R$ 30.069,79), além das 60 parcelas mensais de R$ 2.324,17 e R$ 381,45 do Itaú Pronampe, totalizando um passivo bancário consolidado de R$ 192.406,99 assumido exclusivamente pelo Noticiante.

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
1. C. CARUSO ARQUITETURA E INTERIORES LTDA, CNPJ nº 46.788.820/0001-90, sediada na Av. Vereador Narciso Yague Guimarães, 1.145, Conj. 1214, Mogi das Cruzes/SP;
2. CAMILA CARUSO DA COSTA NEVES, arquiteta, administradora e devedora solidária na pessoa física.

I. DO PEDIDO LIMINAR DE TUTELA DE URGÊNCIA CAUTELAR (ARTS. 300 E 301 DO CPC)
Demonstrada a probabilidade do direito (comprovantes bancários oficiais de repasse de R$ 112.000,00, confissões textuais e áudios de WhatsApp) e o perigo de dano irreparável (notória insolvência da Ré, existência de processo executivo movido pelo Banco Volkswagen sob nº 401XXXX-77.2026.8.26.0361 e iminente vencimento das parcelas do Pronampe e Nubank contraídas pelo Autor que totalizam passivo de R$ 192.406,99), REQUER-SE:
a) A concessão liminar, inaudita altera parte, de ARRESTO VIA SISBAJUD no montante de R$ 112.000,00 nas contas bancárias de ambas as Rés;
b) Restrição de transferência via RENAJUD sobre o veículo de propriedade da Ré Camila Caruso da Costa Neves.

II. DO DIREITO E DO MÉRITO
1. A existência e validade de contrato verbal e obrigação de restituição (Arts. 104, 107 e 422 do CC);
2. O enriquecimento ilícito e sem causa vedado pelo Art. 884 do Código Civil;
3. A desconsideração da personalidade jurídica com fulcro no Art. 50 do Código Civil por flagrante desvio de finalidade e confusão patrimonial.

III. DOS PEDIDOS FINAIS
Requer a citação das Rés para que paguem a quantia de R$ 112.000,00 devidamente atualizada com correção monetária pelo IPCA e juros moratórios de 1% ao mês a partir de cada desembolso, cumulada com o ressarcimento das 13 parcelas quitadas do Nubank (R$ 18.015,62), do saldo remanescente do Nubank (R$ 30.069,79), dos juros e parcelas dos Pronampos 1 e 2 assumidos perante o Itaú, e indenização por danos morais em R$ 20.000,00, além de custas e honorários advocatícios sucumbenciais."""
}

# Export data.js
data_js_content = f"""// Consolidated Dossier Dataset: Gustavo Castellano x Camila Caruso
// Generated automatically with 100% transcriptions and forensic analysis

window.DOSSIER_DATA = {{
    metadata: {{
        title: "Dossiê Jurídico e Fático — Caso Gustavo Castellano x Camila Caruso",
        subtitle: "Análise Cronológica Exaustiva, Transcrições de Áudio Whisper, Provas Financeiras, Enquadramento Penal e Auditoria de Ameaças",
        totalAmount: 112000.00,
        pixNu: 40000.00,
        pixItau: 72000.00,
        nubankLoanInitial: 40000.00,
        nubankQuitadoPronampe: 18015.62,
        nubankParcelasQuitadas: 13,
        nubankSaldoRestante: 30069.79,
        pronampe1Total: 139450.20,
        pronampe1Parcela: 2324.17,
        pronampe1QtdParcelas: 60,
        pronampe2Total: 22887.00,
        pronampe2Parcela: 381.45,
        pronampe2QtdParcelas: 60,
        totalEndividamentoConsolidado: 192406.99,
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

print(f"data.js written successfully! Size: {len(data_js_content) / 1024:.1f} KB")
