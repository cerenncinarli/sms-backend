from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import random
import os
from twilio.rest import Client

app = FastAPI()

# Twilio bilgilerini Render panelinden al
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Kodları tutmak için sözlük
verification_codes = {}

@app.get("/")
def read_root():
    return {"message": "SMS Backend is running"}

class PhoneNumber(BaseModel):
    phone: str

@app.post("/send-code")
def send_code(data: PhoneNumber):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code

    try:
        message = client.messages.create(
            body=f"Doğrulama Kodunuz: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=data.phone
        )
        return {"message": "Kod gönderildi", "sid": message.sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS gönderilemedi: {str(e)}")

class CodeVerification(BaseModel):
    phone: str
    code: str

@app.post("/verify")
def verify_code(data: CodeVerification):
    stored_code = verification_codes.get(data.phone)
    if stored_code and stored_code == data.code:
        return {"message": "Doğrulama başarılı!"}
    raise HTTPException(status_code=400, detail="Kod yanlış")

@app.get("/favicon.ico")
async def favicon():
    return Response(content="", media_type="image/x-icon")
