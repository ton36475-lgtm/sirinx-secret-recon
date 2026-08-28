# SIRINX Secret Recon — Policy (Non-Negotiable)

ภาษาไทย / English

## ขอบเขตที่อนุญาต / Allowed scope
- สแกนเฉพาะทรัพยสินของตัวเอง: `ton36475-lgtm`, SIRINX, GhostClaw, OZ-CORP, Hermes
- Local working tree บนเครื่องที่ควบคุมเอง
- Cloudflare / Supabase / n8n ของ operator เท่านั้น

## สิ่งที่ห้ามเด็ดขาด / Forbidden
- ค้นหา public GitHub ด้วยคำว่า `OPENAI_API_KEY` / `OPENAI_API_KEY.env` เพื่อเอาคีย์ของคนอื่นไปใช้ฟรี
- เก็บหรือส่ง raw secret ในแชท, agent memory, R2 สาธารณะ, Obsidian
- หมุนคีย์ production โดยไม่มีมนุษย์อนุมัติ
- สแกนรีโปบุคคลที่สามหรือลูกค้าโดยไม่มีหนังสืออนุญาต

การใช้คีย์ที่รั่วของบุคคลที่สามละเมิด TOS ของผู้ให้บริการ และอาจเข้าข่ายการเข้าถึงระบบโดยไม่ได้รับอนุญาต

ระบบนี้เป็น **defensive hygiene** ไม่ใช่ key harvesting.
