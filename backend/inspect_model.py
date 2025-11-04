import joblib
import json
import sys

MODEL_PATH = r"D:\Prediksi_Lama_Rawat\backend\random_forest_regressor_model.pkl"

def safe_print(obj, label=None):
    if label:
        print(f"--- {label} ---")
    try:
        print(obj)
    except Exception as e:
        print(f"<unable to print {label}: {e}>")

def main():
    try:
        m = joblib.load(MODEL_PATH)
    except Exception as e:
        print('ERROR: failed to load model:', e)
        sys.exit(2)

    safe_print(type(m), 'model type')

    # If it's a pipeline, show steps
    if hasattr(m, 'named_steps'):
        try:
            safe_print(list(m.named_steps.keys()), 'pipeline steps')
        except Exception as e:
            safe_print(str(e), 'pipeline steps error')

    # Common attributes that may hold feature names
    attrs = ['feature_names_in_', 'n_features_in_', 'get_feature_names_out',
             'feature_names', 'columns_', 'feature_names_out']

    for a in attrs:
        if hasattr(m, a):
            try:
                val = getattr(m, a)
                # If callable, call without args and print sample
                if callable(val):
                    try:
                        out = val()
                        safe_print(type(out), f"{a}() type")
                        safe_print(list(out)[:200], f"{a}() sample")
                    except Exception as e:
                        safe_print(str(e), f"calling {a}() failed")
                else:
                    # print a sample if it's a list/ndarray
                    try:
                        safe_print(list(val)[:200], a)
                    except Exception:
                        safe_print(val, a)
            except Exception as e:
                safe_print(str(e), f"error accessing {a}")

    # Try to inspect estimators for fitted vectorizers or encoders
    try:
        if hasattr(m, 'named_steps'):
            for name, step in m.named_steps.items():
                print(f"--- step: {name} ({type(step)}) ---")
                # try to list attributes of the step that look like feature names
                for k in dir(step):
                    kl = k.lower()
                    if 'feature' in kl or 'columns' in kl or 'get_feature' in kl:
                        print('  ', k)
    except Exception as e:
        print('error enumerating pipeline steps:', e)

    # As a last resort, try to access attribute `feature_names_` on subestimators
    print('--- done ---')

if __name__ == '__main__':
    main()
