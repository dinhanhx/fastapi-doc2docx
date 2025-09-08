# API server converting .doc to docx

## With uv

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 9700
```

## With uv but a bit old school or legacy

```bash
uv python pin 3.12
uv venv --seed
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9700
```