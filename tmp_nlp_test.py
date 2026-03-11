import json
from app.services.nlp_service import nlp_service

print("--- Testing HF AI Engine Extraction ---")

mock_messages = [
    "Hi team, this is Rohan Sharma from Apex Logistics. We are urgently looking to upgrade our CRM system for 50 agents before next quarter. I want to schedule a demo ASAP. You can reach my direct line at 98765-43210 or email me at r.sharma@apexlogistics.in. Is Thursday 2PM IST open?",
    "Hey, reaching out regarding a potential tech partnership. I'm Sarah Jenkins, VP of Engineering at CloudScale. We don't have an immediate timeline, just exploring options for now. email: sarah.j@cloudscale.io"
]

results = []
for idx, text in enumerate(mock_messages):
    print(f"\nProcessing Message {idx+1}...")
    extracted = nlp_service.extract_contact_info(text, source="WhatsApp API")
    
    parsed = None
    try:
        start = extracted.find('{')
        end = extracted.rfind('}') + 1
        if start != -1 and end != -1:
            parsed = json.loads(extracted[start:end])
    except Exception:
        pass

    results.append({
        "raw_text": text,
        "raw_api_output": extracted,
        "parsed_json": parsed
    })
    
with open('nlp_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4)
print("Done! Check nlp_test_results.json")
