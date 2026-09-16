import re
import json
import os
import glob

print("Generating consolidated chat and timeline dataset...")

# Load transcriptions if available
transcriptions = {}
if os.path.exists("transcriptions.json"):
    try:
        with open("transcriptions.json", "r", encoding="utf-8") as f:
            transcriptions = json.load(f)
        print(f"Loaded {len(transcriptions)} transcriptions.")
    except Exception as e:
        print("Error reading transcriptions:", e)

with open("_chat.txt", "r", encoding="utf-8", errors="ignore") as f:
    raw_text = f.read()

# Pattern for whatsapp line
pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}),\s(\d{2}:\d{2}:\d{2})\]\s([^:]+):\s([\s\S]*?)(?=\[\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}:\d{2}\]|$)')
matches = pattern.findall(raw_text)

print(f"Total raw messages parsed: {len(matches)}")

parsed_messages = []
for date_str, time_str, author, content in matches:
    author = author.strip('\u200e').strip()
    content = content.strip('\u200e').strip()
    
    # Check for attachment
    att_match = re.search(r'<anexado:\s*([^>]+)>', content)
    attachment = att_match.group(1).strip() if att_match else None
    
    # Clean content of attachment text
    display_content = re.sub(r'‎?<anexado:\s*[^>]+>', '', content).strip()
    
    audio_transcription = None
    if attachment and attachment in transcriptions:
        audio_transcription = transcriptions[attachment].get("text", "")
    
    # Tagging
    tags = []
    c_lower = (content + " " + (audio_transcription or "")).lower()
    
    if any(k in c_lower for k in ["pix", "ted", "40.000", "72.000", "112.000", "113.", "pronampe", "sispag", "banco", "comprovante", "transferência", "transferencia", "depósito", "deposito"]):
        tags.append("FINANCEIRO")
    if any(k in c_lower for k in ["contrato", "cláusula", "clausula", "minuta", "assinar", "termo", "reconhecimento de dívida", "advogado", "advogada"]):
        tags.append("CONTRATO")
    car_debt_kw = [
        "vender meu carro", "venda do meu carro", "vender o carro", "venda do carro",
        "carro da camila", "banco volkswagen", "volkswagen", "busca e apreens",
        "parcelas do carro", "parcela do carro", "dívida do carro", "divida do carro",
        "oficial de justi", "carro escondido", "processo do carro"
    ]
    if any(k in c_lower for k in car_debt_kw):
        tags.append("CARRO_DIVIDA")
    if any(k in c_lower for k in ["ameaça", "ameaca", "ameaçar", "polícia", "policia", "delegacia", "processo", "processar", "b.o", "crime", "justiça"]):
        tags.append("AMEACA_DISPUTA")
    if any(k in c_lower for k in ["hospital", "internação", "internacao", "médico", "medico", "serpiero", "exame", "remédio", "remedio"]):
        tags.append("HOSPITAL_SAUDE")
    if any(k in c_lower for k in ["site", "projeto", "prospecção", "prospeccao", "campanha", "anúncio", "anuncio", "arquiteta", "cliente"]):
        tags.append("COMERCIAL")
        
    parsed_messages.append({
        "id": len(parsed_messages) + 1,
        "date": date_str,
        "time": time_str,
        "author": author,
        "content": display_content,
        "attachment": attachment,
        "audio_transcription": audio_transcription,
        "tags": tags
    })

output_file = "chat_dataset.json"
with open(output_file, "w", encoding="utf-8") as out:
    json.dump(parsed_messages, out, ensure_ascii=False, indent=2)

print(f"Generated {output_file} with {len(parsed_messages)} messages.")
