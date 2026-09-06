# แผนปฏิบัติการ Secret Recon (ป้องกัน — สินทรัพย์ของตัวเองเท่านั้น)

สร้างจาก skill `redteam-secret-recon` สำหรับ GhostClaw / SIRINX

## สิ่งที่ระบบนี้ทำ

1. **L1 Scanner** — GitHub Secret Scanning + Gitleaks + `src/recon_engine.py`
2. **L2 Classifier** — แยก true positive / placeholder / docs แล้วจัด severity
3. **L3 Gate** — สร้าง Issue + รอคนอนุมัติก่อน rotate
4. **Dashboard / n8n / Terraform / Supabase** — เก็บ metadata (fingerprint) ไม่เก็บค่า key จริง

## สิ่งที่ระบบนี้ห้ามทำ

- ค้น GitHub สาธารณะหา `OPENAI_API_KEY.env` เพื่อเอา key ของคนอื่นไปใช้
- เก็บ raw secret ในแชท / wiki / R2 public
- auto-rotate production โดยไม่มี human approval
- สแกน repo ของลูกค้าหรือบุคคลที่สามโดยไม่มีหนังสืออนุญาต

## ลำดับงานที่ต้องทำด้วยมือ (ยังค้าง)

1. เปิด Secret scanning + Push protection บนทุก repo ของ `ton36475-lgtm` (Settings → Code security)
2. วาง `.github/workflows/secret-scan.yml` และ `.gitleaks.toml` ลง P0 repos
3. รัน `python3 src/recon_engine.py /path/to/local/monorepo` บน Mac mini
4. import n8n workflow แล้วตั้ง cron วันละครั้ง
5. ต่อโมดูล dashboard เข้า Pixel AI Office / sirinx.co (แสดงจำนวน findings ไม่แสดงค่า key)

## ผลสแกนล่าสุด (2026-09-06 22:01 +07)

- Live production keys ในโค้ดสาธารณะของตัวเอง: **0**
- GHAS ยังปิดทั้งกอง P0
- `.env.example` เป็น placeholder — ระดับ Low
