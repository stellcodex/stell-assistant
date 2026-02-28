# Stellcodex Platform — Operasyon Bilgisi

Son güncelleme: 2026-02-28

---

## Servisler ve Durum Kontrol Komutları

| Servis | Teknoloji | Port | Kontrol |
|--------|-----------|------|---------|
| Backend | FastAPI / Docker | 8000 | `docker ps \| grep stellcodex-backend` |
| Frontend | Next.js / PM2 | 3010 | `pm2 list \| grep stellcodex-next` |
| Worker | Celery / Docker | — | `docker ps \| grep stellcodex-worker` |
| DB | PostgreSQL 15 / Docker | 5432 | `docker ps \| grep stellcodex-postgres` |
| Cache | Redis 7 / Docker | 6379 | `docker ps \| grep stellcodex-redis` |
| Storage | MinIO / Docker | 9000/9001 | `docker ps \| grep stellcodex-minio` |
| Proxy | Nginx / systemd | 80/443 | `systemctl status nginx` |

**Proje dizini:** `/var/www/stellcodex/`
**Docker compose:** `/var/www/stellcodex/infrastructure/deploy/docker-compose.yml`

---

## Sık Kullanılan Komutlar

```bash
# Tüm docker servislerini listele
docker ps --filter name=stellcodex

# Backend log izle
docker logs -f stellcodex-backend --tail 50

# Worker log izle
docker logs -f stellcodex-worker --tail 50

# Frontend restart
pm2 restart stellcodex-next

# Frontend log
pm2 logs stellcodex-next --lines 50

# Nginx reload
systemctl reload nginx

# Disk kullanımı
df -h /

# Backend rebuild (değişiklik sonrası)
cd /var/www/stellcodex && docker-compose -f infrastructure/deploy/docker-compose.yml up -d --build stellcodex-backend
```

---

## Veritabanı

- **Host:** localhost (Docker internal)
- **User:** stellcodex
- **DB:** stellcodex
- **Port:** 5432

```bash
# DB bağlan
docker exec -it stellcodex-postgres psql -U stellcodex -d stellcodex

# Kullanıcı listesi
SELECT id, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 20;
```

---

## Admin Kullanıcısı

- **Email:** stell@stellcodex.com
- **Rol:** admin
- **Şifre:** Belirlenmedi — TODO

---

## Kritik Dosyalar

| Amaç | Yol |
|------|-----|
| Backend router | `/var/www/stellcodex/backend/app/api/v1/routes/` |
| Backend main | `/var/www/stellcodex/backend/app/main.py` |
| Frontend pages | `/var/www/stellcodex/frontend/src/app/` |
| Nginx config | `/etc/nginx/sites-enabled/stellcodex` |
| Docker compose | `/var/www/stellcodex/infrastructure/deploy/docker-compose.yml` |
| requirements.txt | `/var/www/stellcodex/backend/requirements.txt` |

---

## V7 Constitution (Bağlayıcı Kurallar)

- `storage_key` asla public response'a giremez
- State machine: S0 → S7, atlama yasak
- `decision_json` zorunlu, LLM kararı yasak
- Threshold'lar sadece `rule_configs` tablosundan okunur

---

## Yapılacaklar (Açık İşler)

- [ ] Frontend kayıt/giriş sayfası (email + şifre formu)
- [ ] DXF dosyaları açılmıyor — debug
- [ ] Admin panel tam çalışır hale getir
- [ ] Kullanıcı dashboard oluştur
- [ ] Email sistemi kur (Cloudflare Email Routing + Resend)
- [ ] Admin şifresi belirle
