import re
import json
from pathlib import Path

DATA_PATH = Path(r"d:/Prediksi_Lama_Rawat/Data.txt")
OUT_PATH = Path(r"d:/Prediksi_Lama_Rawat/backend/schema.json")

def parse():
    text = DATA_PATH.read_text(encoding='utf-8')

    schema = {
        'categorical': {},
        'diagnosis_masuk': {},
        'diagnosis_primer': {}
    }

    # Parse categorical blocks like: --- Unique values for 'Jenis Kelamin': ---\nVALUE\n...
    cat_pattern = re.compile(r"--- Unique values for '([^']+)': ---\n(.*?)\n-{4,}", re.S)
    for m in cat_pattern.finditer(text):
        name = m.group(1).strip()
        vals_block = m.group(2).strip()
        vals = [line.strip() for line in vals_block.splitlines() if line.strip()]
        schema['categorical'][name] = vals

    # Parse mappings for diagnosis masuk and primer
    def parse_mapping(section_title):
        idx = text.find(section_title)
        if idx == -1:
            return {}
        sub = text[idx:]
        # stop at a line of ===== or at double newline followed by non-code
        stop_idx = len(sub)
        sep = "=================================================="
        si = sub.find(sep)
        if si != -1:
            stop_idx = si
        block = sub[:stop_idx]
        mapping = {}
        for line in block.splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            code, rest = line.split(':', 1)
            code = code.strip()
            desc = rest.strip()
            # remove repeated code in desc like 'A00: A00 Cholera' -> 'Cholera'
            parts = desc.split()
            if parts and parts[0] == code:
                desc = ' '.join(parts[1:]).strip()
            mapping[code] = desc
        return mapping

    schema['diagnosis_masuk'] = parse_mapping('Mapping for Kode Diagnosis Masuk')
    schema['diagnosis_primer'] = parse_mapping('Mapping for Kode Diagnosis Primer')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote schema to {OUT_PATH}")

if __name__ == '__main__':
    parse()
