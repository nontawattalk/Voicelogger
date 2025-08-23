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
