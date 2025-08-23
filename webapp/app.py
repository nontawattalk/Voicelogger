from __future__ import annotations
import os, shutil, tempfile
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from webapp.jobs import queue, Job

# ---- import core functions ----
from core.transcribe import transcribe_to_segments, segments_to_text
from core.summary import simple_summary
from core.crypto import encrypt_file_aes_gcm
from core.report import generate_markdown_report
from core.exporters import export_txt, export_srt, export_vtt, export_json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "web_data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Voicelogger Web")
app.mount("/static", StaticFiles(directory=BASE_DIR/"webapp"/"static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR/"webapp"/"templates"))

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    jobs = sorted(queue.jobs.values(), key=lambda j: j.created_at, reverse=True)
    return templates.TemplateResponse("index.html", {"request": request, "jobs": jobs})

@app.post("/upload", response_class=RedirectResponse)
async def upload(
    request: Request,
    file: UploadFile,
    model: str = Form("medium"),
    language: str = Form("th"),
    do_txt: bool = Form(True),
    do_srt: bool = Form(True),
    do_vtt: bool = Form(True),
    do_json: bool = Form(True),
    do_summary: bool = Form(True),
    passphrase: Optional[str] = Form(None),
):
    tmpdir = Path(tempfile.mkdtemp(prefix="voicelogger_"))
    in_path = tmpdir / file.filename
    with open(in_path, "wb") as f:
        f.write(await file.read())

    def worker() -> str:
        # outdir
        outdir = DATA_DIR / in_path.stem
        outdir.mkdir(exist_ok=True)

        # 1) transcribe
        segs = transcribe_to_segments(str(in_path), model_size=model, language=language)
        text = segments_to_text(segs)
        (outdir/"transcript.txt").write_text(text, encoding="utf-8")

        # 2) summary
        if do_summary:
            summ = simple_summary(text, max_sentences=5)
            (outdir/"summary.txt").write_text(summ, encoding="utf-8")
        else:
            summ = ""

        # 3) exporters
        if do_txt:
            export_txt(segs, outdir / "transcript.txt")  # overwrite with clean text
        if do_srt:
            export_srt(segs, outdir / "subtitle.srt")
        if do_vtt:
            export_vtt(segs, outdir / "subtitle.vtt")
        if do_json:
            export_json(segs, outdir / "segments.json")

        # 4) report
        report_md = generate_markdown_report(text, summ, in_path.name)
        (outdir/"report.md").write_text(report_md, encoding="utf-8")

        # 5) encryption (optional)
        if passphrase:
            enc_path = outdir/"audio.enc"
            encrypt_file_aes_gcm(str(in_path), str(enc_path), passphrase)

        # preserve original
        shutil.copy2(in_path, outdir / file.filename)
        return str(outdir)

    job = queue.submit(
        worker,
        filename=file.filename,
    )
    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)

@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail(request: Request, job_id: str):
    job = queue.get(job_id)
    if not job:
        return HTMLResponse("Job not found", status_code=404)
    files: List[str] = []
    if job.result_dir and Path(job.result_dir).exists():
        files = [p.name for p in Path(job.result_dir).iterdir() if p.is_file()]
    return templates.TemplateResponse("job_detail.html", {"request": request, "job": job, "files": files})

@app.get("/download/{job_id}/{name}")
def download(job_id: str, name: str):
    job = queue.get(job_id)
    if not job or not job.result_dir:
        return HTMLResponse("Not ready", status_code=404)
    path = Path(job.result_dir) / name
    if not path.exists():
        return HTMLResponse("File not found", status_code=404)
    return FileResponse(path)
