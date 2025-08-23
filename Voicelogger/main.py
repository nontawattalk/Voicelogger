import argparse
import os
import sys
import json
from datetime import datetime

# --- Transcription (faster-whisper) ---
def transcribe(audio_path: str, model_size: str = "medium") -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("กรุณา: pip install faster-whisper", file=sys.stderr)
        sys.exit(1)

    model = WhisperModel(model_size)
    segments, info = model.transcribe(audio_path, language="th", vad_filter=True)
    lines = []
    for seg in segments:
        lines.append(seg.text.strip())
    return "\n".join(lines).strip()

# --- Very simple Thai summary (baseline) ---
def simple_summary(text: str, max_sentences: int = 5) -> str:
    if not text.strip():
        return ""
    # แยกคร่าว ่ ตามบรรท/.จุด (สำหรับ baseline; แนะนำปรับด้วย PyThaiNLP ในอนาคต)
    import re
    candidates = re.split(r"[\n\.!?]+", text)
    candidates = [c.strip() for c in candidates if c.strip()]
    return " ".join(candidates[:max_sentences])

# --- AES-GCM encryption helpers ---
def encrypt_file_aes_gcm(src_path: str, dst_path: str, passphrase: str):
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import os, secrets, base64

    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    key = kdf.derive(passphrase.encode("utf-8"))

    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)

    with open(src_path, "rb") as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    with open(dst_path, "wb") as f:
        f.write(ciphertext)

    meta = {
        "alg": "AES-256-GCM",
        "salt_b64": base64.b64encode(salt).decode(),
        "nonce_b64": base64.b64encode(nonce).decode(),
        "src_filename": os.path.basename(src_path),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "kdf": {"name": "PBKDF2HMAC", "hash": "SHA256", "iterations": 200000},
    }
    with open(dst_path + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def generate_report(transcript: str, summary: str, out_md: str, audio_name: str):
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Voicelogger Report\n\n")
        f.write(f"- Generated: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"- Audio file: {audio_name}\n\n")
        f.write("## Summary\n\n")
        f.write(summary.strip() + "\n\n")
        f.write("## Transcript (Thai)\n\n")
        f.write(transcript.strip() + "\n")

def main():
    ap = argparse.ArgumentParser(description="Voicelogger CLI")
    ap.add_argument("--input", required=True, help="ไฟล์เสียงเข้า (.wav/.mp3)")
    ap.add_argument("--outdir", default="output", help="โฟลเดอรผลลับ")
    ap.add_argument("--model", default="medium", help="ขนาดโมเดล faster-whisper (e.g., small, medium, large-v3)")
    ap.add_argument("--passphrase", help="รหัสผ่านสำหรับเข้ารหัสไฟล์เสียง (AES-GCM)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # 1) Transcribe
    print("Transcribing (Thai)...")
    transcript = transcribe(args.input, args.model)
    t_path = os.path.join(args.outdir, "transcript.txt")
    with open(t_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    # 2) Summarize (baseline)
    print("Summarizing...")
    summary = simple_summary(transcript, max_sentences=5)
    s_path = os.path.join(args.outdir, "summary.txt")
    with open(s_path, "w", encoding="utf-8") as f:
        f.write(summary)

    # 3) Report
    print("Generating report...")
    r_path = os.path.join(args.outdir, "report.md")
    generate_report(transcript, summary, r_path, os.path.basename(args.input))

    # 4) Encrypt audio (optional)
    if args.passphrase:
        print("Encrypting audio (AES-GCM)...")
        enc_path = os.path.join(args.outdir, "audio.enc")
        encrypt_file_aes_gcm(args.input, enc_path, args.passphrase)

    print("\nDone.")
    print(f"- {t_path}")
    print(f"- {s_path}")
    print(f"- {r_path}")
    if args.passphrase:
        print(f"- {os.path.join(args.outdir, 'audio.enc')} (+ .meta.json)")

if __name__ == "__main__":
    main()
