# Prediksi Lama Rawat

ini adalah workspace memiliki minimal full-stack prototype untuk mewadahi pickled model (`random_forest_regressor_model.pkl`) dan Vite + React frontend yang memungkinkan pengguna memasukkan masukan (termasuk nama diagnosis yang mudah dipahami manusia) dan mendapatkan prediksi untuk "Lama Rawat" (lama tinggal dalam hari).

Important notes / assumptions
- Saya menggunakan model yang kompatibel dengan scikit-learn (atau serupa) yang diserialisasi dengan `joblib.dump` / `pickle` dan menerima Pandas DataFrame dengan nama kolom yang sesuai dengan kunci yang digunakan dalam muatan input.

How to run (Windows PowerShell)

1) Run Backend menggunakan
.\.venv\Scripts\Activate.ps1
python .\backend\app_flask.py

2) Run Frontend menggunakan
cd frontend
npm run dev
