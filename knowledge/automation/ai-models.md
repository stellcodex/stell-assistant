# AI Model Delegasyon Rehberi

Son güncelleme: 2026-02-28

---

## Mevcut AI Araçlar

| Araç | Config | Komut | Güçlü Olduğu Alan |
|------|--------|-------|-------------------|
| Claude Code | `~/.claude/` | `claude` | Kod yazma, mimari, debug, refactor |
| OpenAI Codex | `~/.codex/` | `codex` (gpt-5.3-codex) | Hızlı kod üretimi |
| Abacus AI | `~/.abacusai/` | — | ML/veri analizi |
| AITK/Gemini | `~/.aitk/` | `aitk` | Doküman analizi, dosya okuma |
| CodeLLM | `~/.codellm/` | — | Yerel model |
| Codeium | `~/.codeium/` | — | IDE entegrasyonu |
| Copilot | `~/.copilot/` | — | IDE önerileri |

---

## Yönlendirme Kuralları

### Prefix Tabanlı

```
claude: [görev]    → Claude Code API (claude-sonnet-4-6)
gemini: [görev]    → AITK / Gemini
codex: [görev]     → OpenAI Codex
abacus: [görev]    → Abacus AI
```

### Otomatik Yönlendirme (prefix yoksa)

| Mesaj İçeriği | Yönlendirme |
|---------------|-------------|
| Kod yazma, bug fix, refactor | Claude |
| Doküman okuma, PDF analizi | Gemini |
| ML model, veri seti | Abacus |
| Hızlı snippet | Codex |
| Genel soru, not, durum | Stell kendisi |

---

## Handoff Mekanizması

Her AI aracı son durumunu şuraya yazar:
```
/root/workspace/handoff/<ajan>-status.md
```

Örnek:
- `/root/workspace/handoff/claude-status.md`
- `/root/workspace/handoff/gemini-status.md`

---

## Ortak Workspace

```
/root/workspace/
├── CLAUDE.md       — Claude context
├── AGENTS.md       — Gemini/diğer ajan context
├── PROJECT.md      — Stellcodex proje detayları
├── notes/          — Ortak notlar
└── handoff/        — Ajan durum dosyaları
```

---

## Örnek Delegasyon Akışı

1. Kullanıcı WhatsApp'tan yazar: `claude: /var/www/stellcodex/backend/app/api/v1/routes/users.py dosyasını incele ve login endpoint'ini düzelt`
2. Stell mesajı parse eder → `claude:` prefix → Claude API'ye gönderir
3. Claude yanıt döner → Stell özetler → WhatsApp'tan kullanıcıya iletir
4. Stell handoff dosyasını günceller
