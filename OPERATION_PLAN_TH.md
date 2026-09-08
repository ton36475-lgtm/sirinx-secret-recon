# แผนปฏิบัติการ Secret Recon (ป้องกัน — สินทรัพย์ของตัวเองเท่านั้น)

สร้างจาก skill `redteam-secret-recon` สำหรับ GhostClaw / SIRINX  
รอบนี้: 2026-09-09 05:20 +07

## สิ่งที่ระบบนี้ทำ

1. **L1 Scanner** — GitHub Secret Scanning + Gitleaks + `src/recon_engine.py`
2. **L2 Classifier** — แยก true positive / placeholder / docs แล้วจัด severity
3. **L3 Gate** — สร้าง Issue + รอคนอนุมัติก่อน rotate
4. **Dashboard / n8n / Terraform / Supabase** — เก็บ metadata (ไม่เก็บค่า key จริง)

## สิ่งที่ระบบนี้ห้ามทำ

- ค้น GitHub สาธารณหา `OPENAI_API_KEY.env` เพื่อเอา key ของคนอื่นไปใช้
- เก็บ raw secret ในแชท / wiki / R2 public
- auto-rotate production โดยไม่มี human approval
- สแกน repo ของลูกค้าหรือบุคคลที่สามโดยไม่มีหนังสืออนุญาต

## ผลสแกนสด 2026-09-09

- Live production keys ในโค้ดสาธารณะของตัวเอง: **0**
- GHAS ยังปิดทั้งกอง P0 ที่ตรวจ
- `.env.example` เป็น placeholder — ระดับ Low
