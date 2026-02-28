"""
Stell — WhatsApp Webhook (Meta Cloud API)
Komut işleme: stell_brain modülüne delege eder.
"""

import os
import sys
import logging
import httpx
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()

# stell_brain modülünü bul
sys.path.insert(0, "/root/stell")
from stell_brain import handle_command, action_log, save_note

WHATSAPP_TOKEN       = os.environ["WHATSAPP_TOKEN"]
PHONE_NUMBER_ID      = os.environ["PHONE_NUMBER_ID"]
WEBHOOK_VERIFY_TOKEN = os.environ["WEBHOOK_VERIFY_TOKEN"]
STELL_OWNER_PHONE    = os.environ["STELL_OWNER_PHONE"]
INGEST_DIR           = "/root/stell/genois/05_whatsapp_ingest"

GRAPH_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

os.makedirs(INGEST_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("stell-webhook")

app = FastAPI(title="Stell Webhook", docs_url=None, redoc_url=None)


# ── Internal Chat Endpoint (Backend API tarafından çağrılır, JWT yok) ────────
# Sadece 127.0.0.1 ve Docker gateway üzerinden erişilebilir

from pydantic import BaseModel

class InternalChatIn(BaseModel):
    message: str

class InternalChatOut(BaseModel):
    reply: str

@app.post("/stell/internal/chat", response_model=InternalChatOut)
async def internal_chat(body: InternalChatIn, request: Request):
    """Backend'in Stell'e erişimi için internal endpoint. Auth yok, dahili kullanım."""
    reply = handle_command(body.message.strip())
    return InternalChatOut(reply=reply)


@app.get("/stell/webhook")
async def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
        log.info("Webhook doğrulandı.")
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Doğrulama başarısız")


@app.post("/stell/webhook")
async def receive(request: Request):
    body = await request.json()
    try:
        change = body["entry"][0]["changes"][0]["value"]
        if "statuses" in change:
            return {"ok": True}

        message = change["messages"][0]
        sender  = message["from"]
        mtype   = message["type"]

        if sender != STELL_OWNER_PHONE:
            log.warning("Yetkisiz numara: %s", sender)
            return {"ok": True}

        if mtype == "text":
            text   = message["text"]["body"].strip()
            log.info("Mesaj [%s]: %s", sender, text)
            reply  = handle_command(text)
            await send_whatsapp(sender, reply)

        elif mtype == "document":
            fname = message.get("document", {}).get("filename", "belge")
            action_log("BELGE_ALINDI", fname)
            await send_whatsapp(sender, f"📎 Belge alındı: *{fname}*")

        else:
            log.info("Desteklenmeyen mesaj tipi: %s", mtype)

    except (KeyError, IndexError) as e:
        log.warning("Parse hatası: %s", e)

    return {"ok": True}


async def send_whatsapp(to: str, text: str):
    # WhatsApp max 4096 karakter
    if len(text) > 4000:
        text = text[:4000] + "\n...(kısaltıldı)"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(GRAPH_API_URL, json=payload, headers=headers, timeout=15)
    if resp.status_code != 200:
        log.error("Gönderilemedi: %s %s", resp.status_code, resp.text)
    else:
        log.info("Gönderildi → %s", to)
