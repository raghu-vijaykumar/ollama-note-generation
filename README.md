# Notes Generator

## Setup

```powershell
python -m venv .env
.\.env\Scripts\Activate.ps1
python.exe -m pip install --upgrade pip
pip install -r .\requirements.txt
```

## Running

```powershell
# Run the model
ollama run phi3:14b

# Run the notes generation pipeline
python app.py raw_to_notes 2 phi3:14b "G:\My Drive\workspace\study-new"
```
