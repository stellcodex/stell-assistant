# Stellcodex — Ürün Genel Bakış

Son güncelleme: 2026-02-28

---

## Nedir?

Stellcodex; mühendislik projelerinde kullanılan DXF, 2D ve 3D dosyaların güvenli şekilde yüklenmesini, saklanmasını ve görüntülenmesini sağlayan bir SaaS platformudur.

---

## Temel Özellikler

- DXF dosyası yükleme ve görüntüleme
- 2D ve 3D model viewer
- Kullanıcı yönetimi (kayıt, giriş, rol tabanlı erişim)
- Dosya/proje bazlı erişim kontrolü
- Admin paneli
- Güvenli depolama (MinIO)

---

## Kullanıcı Rolleri

| Rol | Yetkiler |
|-----|----------|
| `admin` | Tam erişim, kullanıcı yönetimi, sistem ayarları |
| `user` | Kendi projelerini görme/yükleme |
| `viewer` | Yalnızca görüntüleme |

---

## Teknik Stack

- **Backend:** FastAPI (Python), PostgreSQL, Redis, Celery
- **Frontend:** Next.js (React), TypeScript
- **Storage:** MinIO (S3-compat)
- **Auth:** Email + bcrypt şifre hash'i, JWT token
- **Proxy:** Nginx

---

## URL Yapısı

| Endpoint | Açıklama |
|----------|----------|
| `POST /api/v1/auth/register` | Yeni kullanıcı kaydı |
| `POST /api/v1/auth/login` | Giriş, JWT döner |
| `POST /api/v1/auth/invite` | Admin davet linki |
| `PUT /api/v1/change-password` | Şifre değiştirme |
| `GET /api/v1/files` | Dosya listesi |
| `POST /api/v1/files/upload` | Dosya yükleme |

---

## Planlar / Roadmap

- Email sistemi (Cloudflare + Resend)
- WhatsApp entegrasyonu (Meta Cloud API)
- Gelişmiş DXF renderer
- Çok dilli arayüz
