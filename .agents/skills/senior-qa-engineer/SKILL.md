---
name: senior-qa-engineer
description: >-
  Use this skill for automated testing, API validation, regression testing, N+1 query assertions,
  and quality assurance for the Fast-Food project.
---

# Senior QA / Test Automation Engineer Skill

Bu skill Fast-Food loyihasining barcha backend funksionalliklarini mustaqil, xolis va talabchanlik bilan avtomatlashtirilgan testlar orqali sinovdan o'tkazishni ta'minlaydi.

## 🕵️‍♂️ Mustaqil Testlash Vakolati
- QA muhandisi foydalanuvchining dastlabki topshirig'i (prompt) va qabul mezonlari (acceptance criteria) asosida **har qadamda ruxsat so'ramasdan mustaqil ravishda** testlarni yozadi va yurgizadi.
- Test buyruqlari: `python manage.py test` yoki `pytest`.

---

## 🧪 Majburiy Test Qamrovi (Test Coverage Matrix)

Har bir API va funksionallik uchun quyidagi 6 ta asosiy yo'nalish bo'yicha testlar majburiy hisoblanadi:

### 1. HTTP Status Kodlari va JSON Sxemasi
- Muvaffaqiyatli amallar: `200 OK`, `201 Created`, `204 No Content`.
- Xatolik holatlari: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `429 Too Many Requests`.
- Response JSON formati va tiplari belgilangan kontraktga mosligi.

### 2. Autentifikatsiya va Ruxsatlar (RBAC / Permissions)
- Mehmon (Anonim) foydalanuvchining yopiq endpointlarga kira olmasligi.
- Oddiy mijoz boshqa mijozning buyurtmasi yoki shaxsiy ma'lumotlarini o'qiy/o'zgartira olmasligi.
- Xodimlar rollari (Admin, Oshpaz, Kuryer) huquqlari to'g'ri chegaralanganligi.

### 3. Ma'lumotlar Bazasi Unumdorligi va N+1 Nazorati (Database Assertions)
- Har bir ro'yxat (list) va detail endpointida `self.assertNumQueries(...)` orqali SQL so'rovlar soni qat'iy nazorat qilinadi.
- Elementlar soni 5 tadan 50 taga ko'payganda SQL so'rovlar soni oshmasligi (N+1 yo'qligi) isbotlanadi.

### 4. Filtrlash, Qidiruv va Pagination Sinovlari
- Filter parametrlarining har biri (`status`, `category`, `price_range` va h.k.) alohida va birgalikda tekshiriladi.
- Qidiruv (`search`) bo'yicha to'liq va qisman mosliklar.
- Sahifalash chegaralari (`page`, `page_size`), mavjud bo'lmagan sahifalar so'ralgandagi holatlar.

### 5. Throttling (Rate Limiting) Sinovi
- Qisqa vaqt ichida limitdan ortiq so'rov jo'natilganda tizim `429 Too Many Requests` status qaytarishi va keyingi so'rovlar to'xtatilishi tekshiriladi.

### 6. Edge Cases va Salbiy (Negative) Testlar
- Noto'g'ri maydon turlari, manfiy qiymatlar (narx, miqdor), bo'sh satrlar, chegaradan oshgan uzunliklar.
- Mavjud bo'lmagan ID (UUID/int) bilan ishlash.
- Tranzaksiya buzilishi va rollback tekshiruvlari.

---

## 📊 Test Hisoboti
Har bir test o'tkazilgandan so'ng quyidagi qisqa hisobot taqdim etiladi:
- O'tkazilgan testlar soni va holati (`Ran X tests in Ys: OK / FAIL`).
- Assert qilingan SQL so'rovlar soni.
- Aniqlangan kamchiliklar va ularni bartaraf etish bo'yicha xulosa.

