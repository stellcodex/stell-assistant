"""
Stell Brain — Ortak Komut İşleme Modülü
Hem WhatsApp webhook hem de admin panel API tarafından kullanılır.
Dış API bağımlılığı yoktur; knowledge/ ve playbooks/ dosyalarını okur.
"""

import os
import json
import datetime
import subprocess

STELL_ROOT = os.environ.get("STELL_ROOT", "/root/stell")
LOG_DIR    = f"{STELL_ROOT}/genois/logs"
NOTES_PATH = f"{STELL_ROOT}/genois/inbox/notes.md"
INBOX_PATH = f"{STELL_ROOT}/genois/inbox/questions.md"

for d in [LOG_DIR, os.path.dirname(NOTES_PATH)]:
    os.makedirs(d, exist_ok=True)


# ── Yardımcılar ──────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def action_log(action: str, detail: str = ""):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(f"{LOG_DIR}/{date_str}.log", "a") as f:
        f.write(f"[{_ts()}] [{action}] {detail}\n")


def save_note(text: str):
    with open(NOTES_PATH, "a") as f:
        f.write(f"\n- [{_ts()}] {text}")
    action_log("NOT_KAYDET", text[:100])


def save_to_inbox(question: str):
    with open(INBOX_PATH, "a") as f:
        f.write(f"\n- [{_ts()}] ❓ {question}")
    action_log("INBOX", question[:100])


def get_recent_notes(n: int = 5) -> str:
    try:
        lines = [l.strip() for l in open(NOTES_PATH) if l.strip().startswith("- [")]
        return "\n".join(lines[-n:]) or "Henüz not yok."
    except FileNotFoundError:
        return "Henüz not yok."


def read_knowledge(rel_path: str) -> str:
    full = os.path.join(STELL_ROOT, rel_path)
    try:
        content = open(full).read()
        return content[:3800] + "\n...(kısaltıldı)" if len(content) > 3800 else content
    except FileNotFoundError:
        return f"Dosya bulunamadı: {rel_path}"


def run_cmd(cmd: list, timeout: int = 15) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "Zaman aşımı."
    except Exception as e:
        return f"Hata: {e}"


# ── Platform durum ────────────────────────────────────────────────────────────

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
        lines.append("Docker: servis bulunamadı")

    # PM2
    try:
        raw = run_cmd(["pm2", "jlist"])
        apps = json.loads(raw)
        stell_apps = [a for a in apps if "stell" in a.get("name", "").lower()]
        if stell_apps:
            lines.append("*PM2:*")
            for a in stell_apps:
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


# ── Knowledge topics ──────────────────────────────────────────────────────────

KNOWLEDGE_MAP = {
    "platform":  "knowledge/operations/stellcodex-platform.md",
    "urun":      "knowledge/products/stellcodex-overview.md",
    "ürün":      "knowledge/products/stellcodex-overview.md",
    "faq":       "knowledge/faq/genel-sss.md",
    "sss":       "knowledge/faq/genel-sss.md",
    "ai":        "knowledge/automation/ai-models.md",
    "modeller":  "knowledge/automation/ai-models.md",
    "komutlar":  "playbooks/whatsapp/komutlar.md",
    "admin":     "playbooks/admin/platform-ops.md",
    "guvenlik":  "policies/security/access.md",
    "güvenlik":  "policies/security/access.md",
    "onay":      "policies/approval/required-approvals.md",
    "whatsapp":  "policies/channels/whatsapp.md",
}

VALID_TOPICS = ", ".join(sorted(set(KNOWLEDGE_MAP.keys())))

# ── Ana komut router ──────────────────────────────────────────────────────────

def handle_command(text: str) -> str:
    """
    Gelen metni işle, yanıt döndür.
    Hem WhatsApp webhook hem admin API bu fonksiyonu çağırır.
    """
    t = text.strip()
    tl = t.lower()

    # Selamlama
    if tl in ("merhaba", "selam", "hi", "hello", "hey"):
        return "👋 Merhaba! Ben Stell, Stellcodex'in asistanıyım.\nKomutlar için `yardım` yaz."

    # Yardım
    if tl in ("yardım", "yardim", "?", "help", "komutlar"):
        return (
            "📋 *Stell Komutları*\n\n"
            "• `durum` — Platform servis durumu\n"
            "• `not: <metin>` — Not kaydet\n"
            "• `notlar` — Son 5 notu göster\n"
            "• `disk` — Disk kullanımı\n"
            "• `log: backend|worker|redis|postgres` — Servis logu\n"
            "• `bilgi: <konu>` — Knowledge dosyası göster\n"
            f"  Konular: {VALID_TOPICS}\n\n"
            "Bilinmeyen mesajlar inbox'a kaydedilir."
        )

    # Platform durumu
    if tl == "durum":
        action_log("DURUM", "sorgu")
        return f"📊 *Platform Durumu*\n\n{platform_status()}"

    # Disk
    if tl == "disk":
        out = run_cmd(["df", "-h", "/"])
        return f"💾 *Disk:*\n```\n{out}\n```"

    # Not kaydet
    if tl.startswith("not:"):
        note = t[4:].strip()
        if not note:
            return "Not metni boş. Örnek: `not: Müşteri ile Salı 14:00 görüşme`"
        save_note(note)
        return f"✅ Not kaydedildi:\n_{note}_"

    # Notları listele
    if tl in ("notlar", "notlarım"):
        return f"📝 *Son Notlar:*\n\n{get_recent_notes(5)}"

    # Log sorgula
    if tl.startswith("log:"):
        svc = t[4:].strip().lower()
        svc_map = {
            "backend":  "stellcodex-backend",
            "worker":   "stellcodex-worker",
            "redis":    "stellcodex-redis",
            "postgres": "stellcodex-postgres",
        }
        if svc in svc_map:
            out = run_cmd(["docker", "logs", svc_map[svc], "--tail", "20"])
            snippet = out[-1500:] if len(out) > 1500 else out
            return f"📋 *{svc} log:*\n```\n{snippet}\n```"
        return f"Bilinmeyen servis. Geçerliler: {', '.join(svc_map)}"

    # Knowledge sorgula
    if tl.startswith("bilgi:"):
        konu = t[6:].strip().lower()
        if konu in KNOWLEDGE_MAP:
            return read_knowledge(KNOWLEDGE_MAP[konu])
        return f"Bilinmeyen konu. Geçerliler: {VALID_TOPICS}"

    # Delegasyon prefix → inbox'a kaydet
    for prefix in ("claude:", "gemini:", "codex:", "abacus:"):
        if tl.startswith(prefix):
            model = prefix.rstrip(":")
            task  = t[len(prefix):].strip()
            save_to_inbox(f"[{model.upper()} görevi] {task}")
            return (
                f"📥 _{model.capitalize()}_ görevi inbox'a kaydedildi.\n"
                f"Görev: _{task[:200]}_\n\n"
                "İncelemek için: `/root/stell/genois/inbox/questions.md`"
            )

    # Bilinmeyen → inbox
    save_to_inbox(t)
    return (
        f"❓ Anlamadım, inbox'a kaydettim:\n_{t[:200]}_\n\n"
        "Yardım için `yardım` yaz."
    )
