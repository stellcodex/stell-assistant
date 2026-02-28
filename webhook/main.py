"""
Stell — WhatsApp Webhook (Meta Cloud API)
"""

import os
import logging
import httpx
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.environ["WHATSAPP_TOKEN"]
PHONE_NUMBER_ID = os.environ["PHONE_NUMBER_ID"]
WEBHOOK_VERIFY_TOKEN = os.environ["WEBHOOK_VERIFY_TOKEN"]
STELL_OWNER_PHONE = os.environ["STELL_OWNER_PHONE"]

GRAPH_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("stell")

app = FastAPI(title="Stell Webhook", docs_url=None, redoc_url=None)


# ── Webhook doğrulama (Meta ilk kurulumda çağırır) ──────────────────────────

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


# ── Gelen mesajları işle ─────────────────────────────────────────────────────

@app.post("/stell/webhook")
async def receive(request: Request):
    body = await request.json()
    log.info("Gelen payload: %s", body)

    try:
        entry = body["entry"][0]
        change = entry["changes"][0]["value"]

        # Durum güncellemeleri (okundu, iletildi) — yoksay
        if "statuses" in change:
            return {"ok": True}

        message = change["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        if msg_type == "text":
            text = message["text"]["body"]
            log.info("Mesaj [%s]: %s", sender, text)
            await handle_message(sender, text)

        elif msg_type == "document":
            log.info("Belge geldi [%s]", sender)
            await send_text(sender, "Belgeyi aldım, inceliyorum.")

        else:
            log.info("Desteklenmeyen mesaj tipi: %s", msg_type)

    except (KeyError, IndexError) as exc:
        log.warning("Payload parse hatası: %s", exc)

    return {"ok": True}


# ── Mesaj mantığı ────────────────────────────────────────────────────────────

async def handle_message(sender: str, text: str):
    """Gelen mesajı işle ve yanıt ver."""
    text_lower = text.strip().lower()

    # Sadece yetkili numara işleniyor
    if sender != STELL_OWNER_PHONE:
        await send_text(sender, "Bu numara Stell'e yetkili değil.")
        return

    # Basit komutlar
    if text_lower in ("merhaba", "hi", "hello", "selam"):
        await send_text(sender, "Merhaba! Ben Stell. Ne yapabilirim?")

    elif text_lower == "durum":
        await send_text(sender, "Stell aktif ve dinliyorum.")

    elif text_lower.startswith("not:"):
        note = text[4:].strip()
        save_note(note)
        await send_text(sender, f"Not kaydedildi: {note}")

    else:
        # Varsayılan: mesajı yansıt (ileride LLM eklenecek)
        await send_text(sender, f"Aldım: {text}")


def save_note(text: str):
    """Notu Drive inbox'a yazılacak dosyaya ekle (basit yerel log)."""
    import datetime
    notes_path = "/root/stell/genois/inbox/notes.md"
    os.makedirs(os.path.dirname(notes_path), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(notes_path, "a") as f:
        f.write(f"\n- [{ts}] {text}")


# ── WhatsApp mesaj gönderme ──────────────────────────────────────────────────

async def send_text(to: str, text: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(GRAPH_API_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        log.error("Mesaj gönderilemedi: %s %s", resp.status_code, resp.text)
    else:
        log.info("Mesaj gönderildi → %s", to)
