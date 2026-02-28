# Sık Sorulan Sorular — Genel

Son güncelleme: 2026-02-28

---

**S: Stell nedir?**
C: Stellcodex'in yapay zeka asistanıdır. WhatsApp üzerinden platform durumu sorgulama, not alma, AI model yönlendirme gibi işlemler yapar.

---

**S: Stell hangi AI modellerini kullanabilir?**
C: Claude (Anthropic), Gemini (Google), Codex (OpenAI), Abacus AI. Prefix ile yönlendirme yapılır: `claude:`, `gemini:`, `codex:`, `abacus:`.

---

**S: WhatsApp'tan nasıl komut gönderilir?**
C: Yetkili telefon numarasından WhatsApp mesajı gönderilir. Komut listesi için `yardım` yaz.

---

**S: Platform durumu nasıl sorgulanır?**
C: WhatsApp'tan `durum` yaz. Stell backend, frontend, worker, disk durumunu döner.

---

**S: Not nasıl kaydedilir?**
C: `not: <metin>` formatında yaz. Örnek: `not: Müşteri X ile Salı 14:00 görüşme`

---

**S: Hangi dosyalar Drive'da, hangileri GitHub'da saklanır?**
C: 
- GitHub: Metin dosyaları (md, json, py, prompts, policies, playbooks)
- Drive: PDF, DOCX, XLSX, görseller, ham müşteri dosyaları

---

**S: DXF dosyalarım açılmıyor, ne yapmalıyım?**
C: Bu bilinen bir açık issue'dur. Geliştirme devam ediyor. `claude: DXF viewer hata logu: [log]` ile debug yardımı alabilirsin.

---

**S: Admin şifresi nedir?**
C: Henüz belirlenmedi. `not: admin şifresi belirle` komutu ile kayıt et ve Claude Code ile backend üzerinden güncelle.
