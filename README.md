# Voicelogger

โปรแกรมบันทึกเสียง → ถอดเสียงภาษาไทย → สรุปเนื้อหา → ออกรายงาน → เข้ารหัสเก็บไฟล์เสียงอย่างปลอดภัย

## คุณสมบัติ
- รับไฟ์เสียง (.wav/.mp3 ฌลล์) หรือเชื่อมส่วนบันทึกเสียงภายหลัง
- ถอดเสียง (ASR) ด้วย **faster-whisper** (รองรับภาษาไทย)
- สรุปเนื้อหาแบบย่อ (extractive แบบเบื้องต้น ปรับแต่งภายหลังได้)
- ออกรายงาน Markdown (transcript + summary)
- เข้ารหัสไฟล์เสียงด้วย AES-GCM (cryptography) พร้อมตัวอย่างการใช้ passphrase

## ติดตั้ง
```
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

## การใช้งาน
```
python Voicelogger/main.py \
  --input sample.wav \
  --outdir output \
  --model medium \
  --passphrase "ใส่รหัสผ่านของคุณ"
```

ผลลับในโฟลเดอร `output/`:
- `transcript.txt` : ข้อความถอดเสียงภาษาไทย
- `summary.txt` : สรุปย่อ
- `report.md` : รายงานรวม
- `audio.enc` : ไฟล์เสียงที่เข้ารหัส (AES-GCM)
- `audio.enc.meta.json` : เมตาดาตา (nonce/salt)

> หมายเทศ: ในงานจริงควรเก็บคีย์/พาสเฟรสใน Secret Manager/Key Vault แทนไฟล์

## แผนพัฒนาถถัดไป
- โหดบันทึกเสียงในแอป (PyAudio/SoundDevice)
- Thai segmentation/summary ที่ฉลาดขึ้น (PyThaiNLP + TextRank)
- RBAC + Audit log + การลบตามนโยบาย retention
