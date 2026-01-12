# FastAPI server converting .doc to docx

MS Word Office has `Wordconv.exe` to natively convert .doc file to .docx file. By doing this, it's faster than any FOSS solutions. However, this api server needs to be on a Windows machine with MS Word Office. The api server calls Wordconv via Windows command line, then return .docx file instantly. This service is stateless, and only stores files temporarily during the process.

## Setup `Wordconv.exe`

- Install Windows 10
- Install MS Word Office 2024
- Find `Wordconv.exe` in program installation folder
- Add `Wordconv.exe` to `PATH`

(See Links section)

## Run with uv

All commands executed in wherever this repos is cloned to.

```bash
uv python pin 3.12
uv python install 3.12
uv tool install docx2pdf
```

Recommendation: use the latest patch of 3.12 for security fixes.

### With uv

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 9700
```

### With uv but a bit old school or legacy

Make a local .venv folder
```bash
uv venv --seed
```

Activate it, install dependencies, and just run,
```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9700
```

Note: can use other .venv creators, just need to activate it properly.

## Links

https://massgrave.dev/genuine-installation-media

https://stackoverflow.com/a/2405508

https://stackoverflow.com/questions/2405417/automation-how-to-automate-transforming-doc-to-docx/2405508#comment138534121_2405508

https://stackoverflow.com/a/9546345