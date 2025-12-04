from flask import Flask, request, jsonify
from pathlib import Path
import json
import joblib
import pandas as pd
from flask_cors import CORS

BASE = Path(__file__).resolve().parent
SCHEMA_PATH = BASE / 'schema.json'

app = Flask(__name__)
# Allow CORS during development so the Vite frontend (different port) can call the API
CORS(app)

# load schema
if SCHEMA_PATH.exists():
    with SCHEMA_PATH.open('r', encoding='utf-8') as f:
        schema = json.load(f)
else:
    schema = {'categorical': {}, 'diagnosis_masuk': {}, 'diagnosis_primer': {}}

# find model .pkl
MODEL_PATH = None
for p in BASE.glob('*.pkl'):
    MODEL_PATH = p
    break

# Do not load the model at import/startup (it can be large and block the server).
# Instead we will load it lazily on the first predict call so /schema responds immediately.
model = None

def load_model_if_needed():
    global model
    if model is not None:
        return True
    if MODEL_PATH is None or not MODEL_PATH.exists():
        print('No .pkl model found in backend folder. Place your model there (e.g. random_forest_regressor_model.pkl)')
        return False
    try:
        print(f'Loading model from {MODEL_PATH.name} ...')
        model = joblib.load(MODEL_PATH)
        print(f'Model loaded from {MODEL_PATH.name}')
        return True
    except Exception as e:
        print('Failed to load model:', e)
        return False


@app.route('/schema', methods=['GET'])
def get_schema():
    return jsonify(schema)


@app.route('/', methods=['GET'])
def index():
    # Friendly root so users visiting / in a browser see available endpoints
    return jsonify({
        'message': 'Backend is running. Use /schema to fetch the form schema and /predict to POST inputs.',
        'endpoints': ['/schema', '/predict']
    })


@app.route('/predict', methods=['POST'])
def predict():
    # Ensure model is loaded (lazily). If loading fails, return 503 so frontend can still fetch /schema.
    if not load_model_if_needed():
        return jsonify({'detail': 'Model not loaded. Loading failed or model not present.'}), 503

    payload = request.get_json() or {}
    data = payload.get('data', payload)

    def map_diag(value, mapping):
        if value is None:
            return None
        v = str(value).strip()
        if v in mapping:
            return v
        if ' ' in v and v.split()[0] in mapping:
            return v.split()[0]
        for k, desc in mapping.items():
            if v.lower() == desc.lower() or v.lower() in desc.lower():
                return k
        return v

    if 'diagnosis_masuk' in schema and 'diagnosis_masuk' in data:
        data['diagnosis_masuk'] = map_diag(data.get('diagnosis_masuk'), schema.get('diagnosis_masuk', {}))
    if 'diagnosis_primer' in schema and 'diagnosis_primer' in data:
        data['diagnosis_primer'] = map_diag(data.get('diagnosis_primer'), schema.get('diagnosis_primer', {}))

    # Build a features vector that matches model.feature_names_in_ exactly (names and order).
    expected = None
    if hasattr(model, 'feature_names_in_'):
        try:
            expected = list(model.feature_names_in_)
        except Exception:
            expected = None

    # If we couldn't get expected feature names from the model, fall back to constructing from schema (best-effort)
    if expected is None:
        # fallback: create one-hot columns from schema (this was the previous behavior)
        features = {}
        if 'Umur' in data:
            features['Umur'] = data.get('Umur')
        for feat, opts in (schema.get('categorical') or {}).items():
            val = data.get(feat)
            for opt in opts:
                col = f"{feat}_{opt}"
                features[col] = 1 if (val == opt) else 0
        # diagnosis
        for code in (schema.get('diagnosis_masuk') or {}).keys():
            if not isinstance(code, str) or not code.isalnum():
                continue
            col = f"Kode Diagnosis Masuk_{code}"
            features[col] = 1 if (str(data.get('diagnosis_masuk') or '').startswith(code)) else 0
        for code in (schema.get('diagnosis_primer') or {}).keys():
            if not isinstance(code, str) or not code.isalnum():
                continue
            col = f"Kode Diagnosis Primer_{code}"
            features[col] = 1 if (str(data.get('diagnosis_primer') or '').startswith(code)) else 0

        df = pd.DataFrame([features])
    else:
        # initialize zeros for all expected features
        features = {c: 0 for c in expected}

        # set numeric Umur
        if 'Umur' in expected:
            try:
                if 'Umur' in data:
                    features['Umur'] = float(data.get('Umur'))
                elif 'umur' in data:
                    features['Umur'] = float(data.get('umur'))
            except Exception:
                # leave default 0 if conversion fails
                pass

        # populate categorical / one-hot columns by matching expected names
        for col in expected:
            # handle diagnosis masuk columns like 'Kode Diagnosis Masuk_A90'
            if col.startswith('Kode Diagnosis Masuk_'):
                code = col.split('_')[-1]
                if str(data.get('diagnosis_masuk') or '').startswith(code):
                    features[col] = 1
                continue
            if col.startswith('Kode Diagnosis Primer_'):
                code = col.split('_')[-1]
                if str(data.get('diagnosis_primer') or '').startswith(code):
                    features[col] = 1
                continue

            # generic one-hot pattern: base_opt (split on last underscore)
            if '_' in col:
                base, opt = col.rsplit('_', 1)
                # if base exists in schema categorical, check equality
                if base in (schema.get('categorical') or {}):
                    val = data.get(base)
                    if val == opt:
                        features[col] = 1

        # Build dataframe preserving the expected column order
        df = pd.DataFrame([features], columns=expected)

    # debug: print DataFrame columns so we can inspect what goes to the model
    print('DEBUG: df.columns ->', df.columns.tolist())
    print('DEBUG: df.head ->', df.head(1).to_dict(orient='records'))

    try:
        pred = model.predict(df)
        pred_val = pred.tolist()[0] if hasattr(pred, 'tolist') else float(pred)
        # Round the prediction to nearest integer for user-friendly "Lama Rawat (hari)"
        try:
            pred_rounded = int(round(float(pred_val)))
        except Exception:
            pred_rounded = pred_val
        print(f'DEBUG: raw prediction={pred_val}, rounded={pred_rounded}')
    except Exception as e:
        return jsonify({'detail': f'Failed to run prediction: {e}'}), 400

    return jsonify({'prediction': pred_rounded})


if __name__ == '__main__':
    # bind to 0.0.0.0 for deployment (allows external connections)
    # use PORT env var if provided (for platforms like Render/Railway)
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
