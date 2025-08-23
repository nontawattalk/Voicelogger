# Voicelogger

โปรแกรมบันทึกเสียง → ถอดเสียงภาษาไทย → สรุปเนื้อหา → ส่งออกไฟล์หลากหลายรูปแบบ (TXT, SRT, VTT, JSON) → ออกรายงาน → เข้ารหัสไฟล์เสียงอย่างปลอดภัย

## คุณสมบัติ

- รองรับไฟล์เสียง (.wav/.mp3 ฯลฯ) หรือโฟลเดอร์ที่มีหลายไฟล์ (batch processing)
- ถอดเสียง (ASR) ด้วย **faster-whisper** (รองรับภาษาไทย) พร้อมเลือกขนาดโมเดล
- ส่งออกทรานสคริปต์ได้หลากหลาย: **TXT**, **SRT**, **VTT**, **JSON** (เลือกได้หลายอย่าง)
- สรุปเนื้อหาเบื้องต้น (extractive) พร้อมเลือกจำนวนประโยค
- สร้างรายงาน Markdown รวม transcript และสรุปผล
- เข้ารหัสไฟล์เสียงด้วย AES‑GCM ด้วย passphrase (เก็บเมตาดาตาแยกต่างหาก)
- ออกแบบให้ใช้ออฟไลน์ 100% (ไม่มีข้อมูลออกสู่อินเทอร์เน็ต)

## ติดตั้ง

```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

## การใช้งานผ่าน CLI

รันสคริปต์ `cli/voicelogger_cli.py` (หรือโมดูล `cli.voicelogger_cli`) เพื่อถอดเสียงและประมวลผลไฟล์เสียงต่าง ๆ:

```bash
python cli/voicelogger_cli.py \
  --input path/to/audio/or/folder \
  --outdir path/to/output \
  --model medium \
  --language th \
  --txt --srt --vtt --json \
  --summary --summary-length 5 \
  --passphrase "รหัสผ่านสำหรับเข้ารหัส"
```

พารามิเตอร์สำคัญ:

- `--input` : ไฟล์เสียงเดี่ยวหรือโฟลเดอร์ที่มีไฟล์เสียง
- `--outdir` : โฟลเดอร์สำหรับเก็บผลลัพธ์ (ค่าเริ่มต้น `output`)
- `--model` : ขนาดโมเดล faster-whisper (เช่น `small`, `medium`, `large-v2`)
- `--language` : รหัสภาษาสำหรับการถอดเสียง (ค่าเริ่มต้น `th`)
- `--txt / --srt / --vtt / --json` : เลือกรูปแบบผลลัพธ์ (ถ้าไม่ใส่จะสร้าง TXT)
- `--summary` : สร้างสรุปเนื้อหา; `--summary-length` ระบุจำนวนประโยค
- `--passphrase` : หากต้องการเข้ารหัสไฟล์เสียงด้วย AES‑GCM ให้กำหนดรหัสผ่านนี้

ผลลัพธ์จะถูกสร้างในโฟลเดอร์ `outdir` ประกอบด้วย:
- `*.txt` : ข้อความถอดเสียง
- `*.srt` : คำบรรยายรูปแบบ SRT
- `*.vtt` : คำบรรยายรูปแบบ VTT
- `*.json` : ข้อมูลคำบรรยายและ timecode ในรูปแบบ JSON
- `*.summary.txt` : สรุปย่อ (ถ้ามี)
- `*_report.md` : รายงานรวม (always)
- `*.enc` และ `*.enc.meta.json` : ไฟล์เสียงที่เข้ารหัสและข้อมูลเมตาดาตา (เมื่อใช้ `--passphrase`)

> หมายเหตุ: แนะนำให้เก็บ passphrase ในระบบจัดการกุญแจ (Key vault) และปฏิบัติตามแนวทางสำรองข้อมูล 3‑2‑1


## ไดอะแกรมการทำงาน

เพื่อให้ง่ายต่อการอ่าน ไดอะแกรมการทำงานของระบบนี้ถูกแสดงในรูปแบบ Mermaid diagram ด้านล่าง (GitHub รองรับการแสดง):

```mermaid
graph TD
  U[อัปโหลดไฟ์เสียงผ่าน Web GUI] --> Q{Job Queue}
  Q --> T[Transcribe Audio]
  Q --> S[Summarize / Translate]
  Q --> R[Report Generator]
  Q --> X[Exporters (TXT/SRT/VTT/JSON)]
  T --> C[Core Modules]
  S --> C
  R --> C
  X --> C
  C --> O[Output & Encryption]
  O --> D[ผลลัฉและไฟ์เข้ารหัสเก็บในเครื่อง]
```

## ภาพไดอะแกรรมระบบ

ภาพไดอะแกรรมนี้อธิบายขั้นตอนการทำงานโดยรวมของระบบ (ใส่ใน GitHub):

<img alt="Voicelogger system architecture diagram" src="data:image/png;base64,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"/>
