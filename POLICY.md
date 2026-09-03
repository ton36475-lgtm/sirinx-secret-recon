# POLICY — Own Assets Only

ระบบนี้เป็น **defensive secret recon** สำหรับสินทรัพย์ของ operator เท่านั้น

## อนุญาต
- สแกน repo / working tree / export ของ `ton36475-lgtm`
- ใช้ GitHub Secret Scanning, Gitleaks, TruffleHog (verify แบบไม่ทำลาย)
- เก็บ fingerprint + path + severity — ไม่เก็บค่า secret จริง
- เปิด Issue / PR / GhostClaw task หลังจัดระดับความรุนแรง
- หมุนคีย์ production ได้เฉพาะหลัง human approval

## ห้ามเด็ดขาด
- ค้น `OPENAI_API_KEY` / `.env` บน GitHub สาธารณะเพื่อเอาคีย์คนอื่นมาใช้
- ใช้คีย์ที่รั่วของบุคคลที่สาม (ผิด TOS และอาจเข้าข่าย unauthorized access)
- เก็บหรือส่งค่า secret ดิบในแชท, agent memory, R2 public, Obsidian
- auto-rotate production โดยไม่มีคนอนุมัติ
- สแกน repo ของลูกค้า / บุคคลที่สามโดยไม่มีหนังสืออนุญาต

ข้อความในแชทที่ชวน “search GitHub แล้วได้ key ฟรี” เป็น anti-pattern ของสกิลนี้ และถูกปฏิเสธโดยระบบ
