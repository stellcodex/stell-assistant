"""
Stell — WhatsApp Webhook (Meta Cloud API)
Kural tabanlı asistan: knowledge/ + playbooks/ dosyalarını beyin olarak kullanır.
Dış API çağrısı yoktur.
"""

import os
import json
import logging
import datetime
import subprocess
import httpx
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN     = os.environ["WHATSAPP_TOKEN"]
PHONE_NUMBER_ID    = os.environ["PHONE_NUMBER_ID"]
WEBHOOK_VERIFY_TOKEN = os.environ["WEBHOOK_VERIFY_TOKEN"]
STELL_OWNER_PHONE  = os.environ["STELL_OWNER_PHONE"]

GRAPH_API_URL  = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
STELL_ROOT     = "/root/stell"
LOG_DIR        = f"{STELL_ROOT}/genois/logs"
NOTES_PATH     = f"{STELL_ROOT}/genois/inbox/notes.md"
INBOX_PATH     = f"{STELL_ROOT}/genois/inbox/questions.md"
INGEST_DIR     = f"{STELL_ROOT}/genois/05_whatsapp_ingest"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("stell")

for d in [LOG_DIR, os.path.dirname(NOTES_PATH), INGEST_DIR]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(title="Stell Webhook", docs_url=None, redoc_url=None)


# ── Yardımcı fonksiyonlar ──────────────────────────────────────────────────

def ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def action_log(action: str, detail: str = ""):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(f"{LOG_DIR}/{date_str}.log", "a") as f:
        f.write(f"[{ts()}] [{action}] {detail}\n")


def save_note(text: str):
    with open(NOTES_PATH, "a") as f:
        f.write(f"\n- [{ts()}] {text}")
    action_log("NOT_KAYDET", text[:100])


def save_to_inbox(question: str):
    """Bilinmeyen soruları inbox'a kaydet, sahip kontrol etsin."""
    with open(INBOX_PATH, "a") as f:
        f.write(f"\n- [{ts()}] ❓ {question}")
    action_log("INBOX", question[:100])


def get_recent_notes(n: int = 5) -> str:
    try:
        lines = [l.strip() for l in open(NOTES_PATH) if l.strip().startswith("- [")]
        return "\n".join(lines[-n:]) or "Henüz not yok."
    except FileNotFoundError:
        return "Henüz not yok."


def read_knowledge_file(rel_path: str) -> str:
    """Bir knowledge/playbook dosyasını oku."""
    full = os.path.join(STELL_ROOT, rel_path)
    try:
        with open(full) as f:
            return f.read()
    except FileNotFoundError:
        return f"Dosya bulunamadı: {rel_path}"


def run_cmd(cmd: list, timeout: int = 15) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "Komut zaman aşımına uğradı."
    except Exception as e:
        return f"Hata: {e}"


# ── Platform durum sorgusu ─────────────────────────────────────────────────

def platform_status() -> str:
    lines = []

    # Docker
    out = run_cmd(["docker", "ps", "--filter", "name=stellcodex",
                   "--format", "{{.Names}}: {{.Status}}"])
    if out:
        lines.append("*Docker:*")
        for l in out.splitlines():
            icon = "✅" if "Up" in l else "❌"
            lines.append(f"  {icon} {l}")
    else:
        lines.append("Docker: servis yok")

    # PM2
    try:
        raw = run_cmd(["pm2", "jlist"])
        apps = json.loads(raw)
        stell = [a for a in apps if "stell" in a.get("name", "").lower()]
        if stell:
            lines.append("*PM2:*")
            for a in stell:
                st = a["pm2_env"]["status"]
                icon = "✅" if st == "online" else "❌"
                lines.append(f"  {icon} {a['name']} ({st})")
    except Exception:
        pass

    # Disk
    disk = run_cmd(["df", "-h", "/"])
    if disk:
        parts = disk.strip().splitlines()[-1].split()
        lines.append(f"*Disk:* {parts[4]} kullanılan ({parts[2]}/{parts[1]})")

    return "\n".join(lines) or "Durum alınamadı."


# ── Webhook doğrulama ──────────────────────────────────────────────────────

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


# ── Gelen mesajları al ─────────────────────────────────────────────────────

@app.post("/stell/webhook")
async def receive(request: Request):
    body = await request.json()
    log.info("Payload: %s", body)

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
            await handle_message(sender, message["text"]["body"].strip())
        elif mtype == "document":
            fname = message.get("document", {}).get("filename", "belge")
            action_log("BELGE", fname)
            await send_text(sender, f"📎 Belge alındı: {fname}")
        else:
            log.info("Desteklenmeyen tip: %s", mtype)

    except (KeyError, IndexError) as e:
        log.warning("Parse hatası: %s", e)

    return {"ok": True}


# ── Komut yönlendirme ──────────────────────────────────────────────────────

async def handle_message(sender: str, text: str):
    t = text.lower()

    # ── Selamlama ──
    if t in ("merhaba", "selam", "hi", "hello"):
        await send_text(sender, "👋 Merhaba! Ben Stell.\nKomutlar için *yardım* yaz.")
        return

    # ── Yardım ──
    if t in ("yardım", "yardim", "?", "help"):
        await send_text(sender, (
            "📋 *Stell Komutları*\n\n"
            "• `durum` — Platform durumu\n"
            "• `not: <metin>` — Not kaydet\n"
            "• `notlar` — Son notlar\n"
            "• `disk` — Disk kullanımı\n"
            "• `log: backend|worker|redis` — Log göster\n"
            "• `bilgi: <konu>` — Knowledge dosyasını göster\n"
            "  Konular: platform, urun, faq, ai, komutlar\n\n"
            "Bilinmeyen mesajlar → inbox'a kaydedilir."
        ))
        return

    # ── Platform durumu ──
    if t == "durum":
        await send_text(sender, "🔍 Kontrol ediyorum...")
        status = platform_status()
        await send_text(sender, f"📊 *Platform Durumu*\n\n{status}")
        action_log("DURUM", "OK")
        return

    # ── Disk ──
    if t == "disk":
        out = run_cmd(["df", "-h", "/"])
        await send_text(sender, f"💾 *Disk:*\n```\n{out}\n```")
        return

    # ── Not kaydet ──
    if t.startswith("not:"):
        note = text[4:].strip()
        if note:
            save_note(note)
            await send_text(sender, f"✅ Not kaydedildi:\n_{note}_")
        else:
            await send_text(sender, "Not metni boş. Örnek: `not: Müşteri ile Salı 14:00 görüşme`")
        return

    # ── Notları listele ──
    if t in ("notlar", "notlarım"):
        notes = get_recent_notes(5)
        await send_text(sender, f"📝 *Son Notlar:*\n\n{notes}")
        return

    # ── Log sorgula ──
    if t.startswith("log:"):
        svc = text[4:].strip().lower()
        svc_map = {
            "backend": "stellcodex-backend",
            "worker":  "stellcodex-worker",
            "redis":   "stellcodex-redis",
            "postgres":"stellcodex-postgres",
        }
        if svc in svc_map:
            out = run_cmd(["docker", "logs", svc_map[svc], "--tail", "20"])
            snippet = out[-1500:] if len(out) > 1500 else out
            await send_text(sender, f"📋 *{svc} log:*\n```\n{snippet}\n```")
        else:
            await send_text(sender, f"Bilinmeyen servis. Geçerliler: {', '.join(svc_map)}")
        return

    # ── Knowledge base sorgula ──
    if t.startswith("bilgi:"):
        konu = text[6:].strip().lower()
        konu_map = {
            "platform": "knowledge/operations/stellcodex-platform.md",
            "urun":     "knowledge/products/stellcodex-overview.md",
            "ürün":     "knowledge/products/stellcodex-overview.md",
            "faq":      "knowledge/faq/genel-sss.md",
            "ai":       "knowledge/automation/ai-models.md",
            "komutlar": "playbooks/whatsapp/komutlar.md",
            "guvenlik": "policies/security/access.md",
            "güvenlik": "policies/security/access.md",
        }
        if konu in konu_map:
            content = read_knowledge_file(konu_map[konu])
            # WhatsApp max 4096 karakter
            if len(content) > 3800:
                content = content[:3800] + "\n...(kısaltıldı)"
            await send_text(sender, content)
        else:
            valid = ", ".join(konu_map.keys())
            await send_text(sender, f"Bilinmeyen konu. Geçerliler: {valid}")
        return

    # ── Delegasyon prefix'leri (bilgi amaçlı not al) ──
    for prefix in ("claude:", "gemini:", "codex:", "abacus:"):
        if t.startswith(prefix):
            model = prefix.rstrip(":")
            task  = text[len(prefix):].strip()
            save_to_inbox(f"[{model.upper()} görevi] {task}")
            await send_text(
                sender,
                f"📥 _{model.capitalize()}_ görevi inbox'a kaydedildi.\n"
                f"Görevi: _{task[:200]}_\n\n"
                f"Kontrol et: /root/stell/genois/inbox/questions.md"
            )
            return

    # ── Bilinmeyen → inbox'a kaydet ──
    save_to_inbox(text)
    await send_text(
        sender,
        f"❓ Anlamadım, inbox'a kaydettim:\n_{text[:200]}_\n\n"
        "Konular için `yardım` yaz."
    )
    action_log("BILINMEYEN", text[:80])


# ── WhatsApp mesaj gönder ──────────────────────────────────────────────────

async def send_text(to: str, text: str):
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
