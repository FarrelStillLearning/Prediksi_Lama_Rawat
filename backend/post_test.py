import json
import urllib.request

payload = {
    "data": {
        "Umur": 55,
        "Jenis Kelamin": "LAKI-LAKI",
        "Segmentasi Peserta": "PPU",
        "Kepemilikan FKRTL": "Vertikal",
        "Jenis FKRTL": "Rumah sakit",
        "Tingkat Pelayanan FKRTL": "RITL",
        "Jenis Poli FKRTL": "JAN",
        "diagnosis_masuk": "N20 — Calculus of kidney and ureter",
        "diagnosis_primer": "N20 — Calculus of kidney and ureter"
    }
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/predict', data=data, headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        print('RAW_RESPONSE:')
        print(body)
        try:
            parsed = json.loads(body)
            print('\nPARSED_JSON:')
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except Exception as e:
            print('Failed to parse JSON:', e)
except Exception as e:
    print('Request failed:', e)
