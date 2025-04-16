from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

# Telefon numarasına karşılık geçici kodları tutmak için sözlük
verification_codes = {}

class PhoneNumber(BaseModel):
    phone: str

@app.post("/send-code")
def send_code(data: PhoneNumber):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    print(f"Telefon: {data.phone} - Kod: {code}")  # Şimdilik sadece terminalde
    return {"message": "Kod gönderildi"}

class CodeVerification(BaseModel):
    phone: str
    code: str

@app.post("/verify")
def verify_code(data: CodeVerification):
    stored_code = verification_codes.get(data.phone)
    if stored_code and stored_code == data.code:
        return {"message": "Doğrulama başarılı!"}
    raise HTTPException(status_code=400, detail="Kod yanlış")
