from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import random

app = FastAPI()

# Telefon numarasına karşılık geçici doğrulama kodlarını tutmak için sözlük
verification_codes = {}

# Telefon numarası modeli
class PhoneNumber(BaseModel):
    phone: str

# Kod gönderme endpoint'i
@app.post("/send-code")
def send_code(data: PhoneNumber):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    print(f"Telefon: {data.phone} - Kod: {code}")  # Geçici olarak terminale yazdır
    return {"message": "Kod gönderildi"}

# Kod doğrulama modeli
class CodeVerification(BaseModel):
    phone: str
    code: str

# Kod doğrulama endpoint'i
@app.post("/verify")
def verify_code(data: CodeVerification):
    stored_code = verification_codes.get(data.phone)
    if stored_code and stored_code == data.code:
        return {"message": "Doğrulama başarılı!"}
    raise HTTPException(status_code=400, detail="Kod yanlış")

# Tarayıcının otomatik istediği favicon.ico isteğine boş yanıt döner
@app.get("/favicon.ico")
async def favicon():
    return Response(content="", media_type="image/x-icon")
