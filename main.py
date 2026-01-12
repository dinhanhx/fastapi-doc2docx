import os
import subprocess
from pathlib import Path
from typing import Literal
from uuid import uuid4

import aiofiles
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

load_dotenv()

TMP_DIR = Path(os.getenv("TMP_DIR", "tmp/"))
TMP_DIR.mkdir(exist_ok=True, parents=True)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10 MB

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "ok"}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


@app.get("/health_check")
async def health_check():
    return {"status": True}


def cleanup(*files: Path):
    for file in files:
        try:
            if file.exists():
                file.unlink()
        except Exception as e:
            print(f"Failed to delete {file}: {str(e)}")


def validate_file(
    file: UploadFile,
    file_ext_to_check: Literal[".doc", ".docx"],
) -> JSONResponse | None:
    if file.size is None or file.size > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": f"File size exceeds the maximum limit of {MAX_FILE_SIZE} bytes."},
        )
    if Path(str(file.filename)).suffix.lower() != file_ext_to_check:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid file type. Only {file_ext_to_check} files are allowed."},
        )
    return None


async def save_uploaded_file(file: UploadFile, file_input: Path) -> JSONResponse | None:
    try:
        await file.seek(0)
        async with aiofiles.open(file_input, "wb") as file_input_pointer:
            while content := await file.read(1024):
                await file_input_pointer.write(content)
        await file.close()
        return None
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to save the uploaded file: {str(e)}"},
        )


@app.post("/convert")
async def convert(file: UploadFile):
    # Validate the file
    any_response = validate_file(file, ".doc")
    if any_response is not None:
        return any_response

    original_file_stem = Path(str(file.filename)).stem
    original_file_extension = Path(str(file.filename)).suffix

    file_uuid = str(uuid4())
    file_input = TMP_DIR.joinpath(f"{file_uuid}{original_file_extension}")

    # Save the uploaded file
    any_response = await save_uploaded_file(file, file_input)
    if any_response is not None:
        return any_response

    file_output = TMP_DIR.joinpath(f"{file_uuid}.docx")

    # Convert the file using Microsoft Wordconv.exe
    try:
        subprocess.run(
            ["Wordconv", "-ocie", "-nme", str(file_input), str(file_output)],
            check=True,
            timeout=int(os.getenv("TIMEOUT", "300")),
        )
        return FileResponse(
            path=file_output,
            filename=f"{original_file_stem}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            background=BackgroundTask(cleanup, file_input, file_output),
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"File conversion failed: {str(e)}"},
        )


@app.post("/docx2pdf")
async def docx2pdf(file: UploadFile):
    # Validate the file
    any_response = validate_file(file, ".docx")
    if any_response is not None:
        return any_response

    original_file_stem = Path(str(file.filename)).stem
    original_file_extension = Path(str(file.filename)).suffix

    file_uuid = str(uuid4())
    file_input = TMP_DIR.joinpath(f"{file_uuid}{original_file_extension}")

    # Save the uploaded file
    any_response = await save_uploaded_file(file, file_input)
    if any_response is not None:
        return any_response

    file_output = TMP_DIR.joinpath(f"{file_uuid}.docx")

    # Convert the file using docx2pdf cli
    try:
        subprocess.run(
            ["uvx", "docx2pdf", "--keep-active", str(file_input), str(file_output)],
            check=True,
            timeout=int(os.getenv("TIMEOUT", "300")),
        )
        return FileResponse(
            path=file_output,
            filename=f"{original_file_stem}.pdf",
            media_type="application/pdf",
            background=BackgroundTask(cleanup, file_input, file_output),
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"File conversion failed: {str(e)}"},
        )
