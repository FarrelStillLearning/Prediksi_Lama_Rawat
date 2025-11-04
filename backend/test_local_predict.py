import importlib
import app_flask
import pandas as pd

def run_test():
    ok = app_flask.load_model_if_needed()
    if not ok:
        print('Model failed to load')
        return

    model = app_flask.model
    schema = app_flask.schema

    sample = {
        'Umur': 30,
        'Jenis Kelamin': 'LAKI-LAKI',
        'Segmentasi Peserta': 'PPU',
        'Kepemilikan FKRTL': 'Swasta',
        'Jenis FKRTL': 'Rumah sakit',
        'Tingkat Pelayanan FKRTL': 'RJTL',
        'Jenis Poli FKRTL': 'INT',
        'diagnosis_masuk': 'A90 - Dengue fever [classical dengue]',
        'diagnosis_primer': 'A91 - Dengue haemorrhagic fever'
    }

    expected = None
    if hasattr(model, 'feature_names_in_'):
        expected = list(model.feature_names_in_)

    if expected is None:
        print('Model has no feature_names_in_. Cannot run deterministic test.')
        return

    features = {c: 0 for c in expected}
    if 'Umur' in expected:
        features['Umur'] = float(sample['Umur'])

    for col in expected:
        if col.startswith('Kode Diagnosis Masuk_'):
            code = col.split('_')[-1]
            if str(sample.get('diagnosis_masuk') or '').startswith(code):
                features[col] = 1
            continue
        if col.startswith('Kode Diagnosis Primer_'):
            code = col.split('_')[-1]
            if str(sample.get('diagnosis_primer') or '').startswith(code):
                features[col] = 1
            continue
        if '_' in col:
            base, opt = col.rsplit('_', 1)
            if base in (schema.get('categorical') or {}):
                val = sample.get(base)
                if val == opt:
                    features[col] = 1

    df = pd.DataFrame([features], columns=expected)
    print('DF columns sample:', df.columns[:10].tolist())
    pred = model.predict(df)
    print('Prediction:', pred.tolist())

if __name__ == '__main__':
    run_test()
