# 🔗 DataBridge

### CSV Data Integration & Quality Platform

DataBridge is a Python-based data integration and quality platform built with Streamlit. It allows users to upload datasets, inspect data quality, perform data cleaning and transformations, convert file formats, and load datasets into PostgreSQL.

**Live Application:** https://databridge-etl.streamlit.app/  
**GitHub Repository:** https://github.com/tan118/DataBridge

---

## 📌 Features

### 1. Dashboard
- Overview of the DataBridge application.
- Navigation between different data management modules.

### 2. Dataset Upload
- Upload CSV datasets.
- Preview uploaded records.
- View basic dataset information.

### 3. Data Profiling
- Dataset dimensions and data types.
- Missing-value analysis.
- Duplicate record detection.
- Unique-value analysis.
- Numerical statistics.

### 4. Data Transformation
- Duplicate record removal.
- Missing-value handling.
- Text standardization.
- Negative and zero-value handling.
- Date standardization.
- Column-name standardization.
- Before-and-after comparison and cleaning report.

### 5. File Conversion
- Convert Excel files (`.xlsx` and `.xls`) to CSV.
- Convert JSON files to CSV.
- Preview converted datasets.
- Download converted CSV files.

### 6. PostgreSQL Database Loading
- Load datasets into PostgreSQL.
- Replace existing tables or append records.
- Display submitted and loaded record counts.
- Supports local PostgreSQL and hosted PostgreSQL through Neon.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend / Application | Streamlit |
| Data Processing | Pandas, NumPy |
| Database | PostgreSQL |
| Database Integration | SQLAlchemy, pg8000 |
| File Handling | OpenPyXL, xlrd |
| Configuration | python-dotenv, Streamlit Secrets |
| Deployment | Streamlit Community Cloud |
| Hosted Database | Neon |

---

## 📁 Project Structure

```text
DataBridge/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── extract.py
│   ├── profile.py
│   ├── transform.py
│   ├── database.py
│   ├── load.py
│   └── convert_to_csv.py
│
├── screenshots/
│
├── logs/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env.example
```

---

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/tan118/DataBridge.git
cd DataBridge
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and configure the connection details in a `.env` file in the project root.

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
```

Do not commit your actual `.env` file or database credentials.

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

---

## ☁️ Cloud Deployment

DataBridge is deployed using Streamlit Community Cloud.

- Application hosting: Streamlit Community Cloud
- Database hosting: Neon PostgreSQL
- Database credentials: Streamlit Secrets

For cloud deployment, configure the following secrets in the Streamlit application settings:

```toml
DB_HOST = "your_neon_host"
DB_PORT = "5432"
DB_NAME = "neondb"
DB_USER = "your_neon_role"
DB_PASSWORD = "your_neon_password"
```

Never publish actual database credentials.

---

## 📸 Application Screenshots

Screenshots of the application's modules are available in the `screenshots/` directory.

The screenshots demonstrate the dashboard, dataset upload, profiling, transformation, file conversion, and PostgreSQL loading functionality.

---

## 📊 Sample Dataset

DataBridge was tested using the Online Retail dataset from the UCI Machine Learning Repository.

Dataset source:

https://archive.ics.uci.edu/dataset/352/online+retail

---

## 🔮 Future Enhancements

- Support for additional input file formats.
- Advanced data-quality visualizations.
- Automated data validation.
- Additional database integrations.
- More transformation options.

---

## 👩‍💻 Author

**Tanishka Mhetre**

GitHub: https://github.com/tan118

---

*DataBridge — Simplifying Data Integration and Transformation.*
