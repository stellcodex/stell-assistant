# Stell — Cloudflare Workers Kurulum

## Deploy Adımları

### 1. Wrangler kur
```bash
npm install -g wrangler
```

### 2. Cloudflare'e giriş yap
```bash
wrangler login
```

### 3. Secrets ekle (her biri için ayrı komut)
```bash
wrangler secret put WHATSAPP_TOKEN
wrangler secret put WEBHOOK_VERIFY_TOKEN
wrangler secret put STELL_OWNER_PHONE
wrangler secret put PHONE_NUMBER_ID
wrangler secret put GITHUB_TOKEN
wrangler secret put GITHUB_REPO
wrangler secret put BACKEND_URL
```

### 4. Deploy et
```bash
cd /root/stell/cloudflare
wrangler deploy
```

### 5. Webhook URL
Deploy sonrası URL gelir:
- Default: `https://stell-webhook.HESAP.workers.dev/stell/webhook`
- Custom (önerilen): `https://stell.stellcodex.com/stell/webhook`
  - Cloudflare Dashboard → Workers → Triggers → Add Custom Domain

### 6. Meta Developer Console
- URL'i kopyala
- Meta → WhatsApp → Configuration → Webhook URL olarak gir
- Verify Token: WEBHOOK_VERIFY_TOKEN değerin
- Subscribe: messages

## Nasıl Çalışır?
- Sunucu çökse de Stell WhatsApp'ta aktif kalır
- `not:` ve `bilgi:` → GitHub API (her zaman çalışır)
- `durum` ve `log:` → Sunucu API (sunucu varsa çalışır, yoksa bildirir)
- `merhaba`, `yardım` → Statik yanıt (her zaman çalışır)
