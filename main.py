from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import random
import sqlite3

app = FastAPI()

# CORS ayarları (Flutter'dan erişim için gerekli)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Geçici kodları burada tutacağız
verification_codes = {}

# SQLite veritabanı bağlantısı
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Kullanıcılar tablosunu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE,
    name TEXT,
    profile_image TEXT,
    public_key TEXT
)
""")
conn.commit()

@app.get("/")
def read_root():
    return {"message": "SMS Backend is running"}

# --- Telefon numarasına kod gönderme ---
class PhoneNumber(BaseModel):
    phone: str

@app.post("/send-code")
def send_code(data: PhoneNumber):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    print(f"Telefon: {data.phone} - Kod: {code}")
    return {"message": "Kod gönderildi"}

# --- Kod doğrulama ---
class CodeVerification(BaseModel):
    phone: str
    code: str

@app.post("/verify")
def verify_code(data: CodeVerification):
    stored_code = verification_codes.get(data.phone)
    if stored_code and stored_code == data.code:
        return {"message": "Doğrulama başarılı!"}
    raise HTTPException(status_code=400, detail="Kod yanlış")

# --- Kayıt işlemi ---
class RegisterRequest(BaseModel):
    phone: str
    name: str
    profile_image: str
    public_key: str

@app.post("/register")
def register_user(data: RegisterRequest):
    try:
        cursor.execute("INSERT INTO users (phone, name, profile_image, public_key) VALUES (?, ?, ?, ?)",
                       (data.phone, data.name, data.profile_image, data.public_key))
        conn.commit()
        return {"message": "Kayıt başarılı!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Bu numara zaten kayıtlı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası: " + str(e))

@app.get("/favicon.ico")
async def favicon():
    return Response(content="", media_type="image/x-icon")
