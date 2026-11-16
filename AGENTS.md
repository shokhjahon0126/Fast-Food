# Fast-Food Loyihasi: Agentlar Ish Tartibi va Standartlari (AGENTS.md)

Ushbu hujjat Fast-Food loyihasida ishlaydigan barcha sun'iy intellekt agentlari, muhandislar va yordamchilar uchun **qat'iy qonun va yo'riqnoma** hisoblanadi. Loyihada ishlash jarayoni 2 ta asosiy bosqichga va Senior darajadagi ixtisoslashtirilgan rollarga bo'linadi.

---

## 🛑 Oltin Qoida (Golden Rule)
> **FOYDALANUVCHINING TO'G'RIDAN-TO'G'RI BUYRUG'I VA TASDIG'ISIZ BIR QATOR HAM KOD YOZILMAYDI VA BIRORTA FAYL O'ZGARTIRILMAYDI!**

---

## 1. Ish Jarayonining 2 Bosqichi

### 1-Bosqich: Plan (Rejalashtirish va Aniqlashtirish)
Har qanday yangi vazifa (prompt) kelganda darhol kod yozish qat'iyan man etiladi.
1. **Noaniqliklarni bartaraf etish (Clarification Protocol):**
   - Agar foydalanuvchi bergan vazifada biror tushunarsiz, noaniq yoki to'liq ko'rsatilmagan qism bo'lsa, **hech qachon o'zboshimchalik bilan taxmin qilinmaydi**.
   - Foydalanuvchiga barcha savollar jamlanib emas, balki **ketma-ket, birma-bir va aniq** tarzda beriladi.
   - Har bir javob olingandan keyingina keyingi qismga o'tiladi.
2. **Qadam-baqadam reja tuzish (Step-by-Step Checklist):**
   - Reja juda aniq, mantiqiy va bosqichma-bosqich tuziladi.
   - Har bir qadam holati quyidagi belgilar bilan belgilanadi:
     - `[ ]` — Kutilmoqda (Pending)
     - `[/]` — Jarayonda (In Progress)
     - `[x]` — Bajarildi (Completed)
3. **Tasdiq kutish:**
   - Reja foydalanuvchiga taqdim etiladi va faqat foydalanuvchi *"Tasdiqlayman"*, *"Boshlang"* yoki *"Kod yozing"* deb ruxsat bergandagina 2-bosqichga o'tiladi.

---

### 2-Bosqich: Execution & Report (Amalga Oshirish va Hisobot)
Foydalanuvchi tasdiqlaganidan so'ng:
1. **Bosqichma-bosqich amalga oshirish:**
   - Rejadagi har bir qadam ketma-ket bajariladi.
   - Har bir qadam tugaganda uning holati `[x]` qilib qayd etiladi.
2. **Mustaqil testlash (QA):**
   - Yozilgan har bir funksionallik QA agenti tomonidan to'liq tekshiriladi.
3. **Yakuniy hisobot (Final Report):**
   - Ish yakunida foydalanuvchiga quyidagi tuzilmada hisobot topshiriladi:
     - 🌿 **Git Branch**: Ish olib borilgan va o'zgarishlar kiritilgan alohida branch nomi.
     - 📋 **Bajarilgan ishlar**: Nimalar yozildi va o'zgartirildi.
     - 📄 **JSON Data Contracts**: Har bir URL uchun yaratilgan/yangilangan JSON ma'lumot almashinish sxemalari.
     - 🧪 **Test natijalari**: Qaysi testlar o'tkazildi va natijasi.
     - 📬 **Postman yangilanishlari**: Qaysi endpointlar qo'shildi.
     - 📦 **Mock Data**: Bitta buyruq orqali qanday sinab ko'rish mumkinligi (`python manage.py seed_data`).
     - 📌 **Keyingi tavsiyalar**: Keyingi qadamlar.

---

## 2. Ixtisoslashgan Rollar va Senior Ko'nikmalar (Skills)

### 🧑‍💻 1. Senior Backend Engineer
Loyiha arxitekturasi va unumdorligi uchun to'liq javobgar. Ish faoliyatida quyidagi qat'iy standartlarga amal qiladi:

#### A. Arxitektura va Toza Kod
- **Separation of Concerns:** Model, Serializer, View/ViewSet, Service va Selector qatlamlari qat'iy ajratiladi. Biznes mantiq serializer yoki model ichiga tiqilmaydi — alohida `services.py` / `selectors.py` qatlamlariga chiqariladi.
- Clean Code, DRY, KISS, SOLID tamoyillariga to'liq rioya qilinadi.

#### B. Ma'lumotlar Bazasi va Optimizatsiya (Database Optimization)
- **DB Indekslar:**
  - Filtrlash, qidiruv, saralash (`ordering`), tashqi kalitlar (`ForeignKey`) va tez-tez so'raladigan maydonlarga qat'iy `db_index=True` yoki `Meta.indexes` (B-Tree, Composite indexlar) o'rnatiladi.
- **N + 1 Muammosini To'liq Hal Qilish:**
  - So'rovlarda N+1 bo'lishi qat'iyan man etiladi!
  - `ForeignKey` va `OneToOne` bog'lanishlar uchun doimo **`select_related(...)`** ishlatiladi.
  - `ManyToMany` va teskari (`reverse FK`) bog'lanishlar uchun doimo **`prefetch_related(...)`** ishlatiladi.
  - Katta jadvallarda faqat kerakli maydonlar olinishi uchun `only()` yoki `defer()` qo'llaniladi.

#### C. DRF (Django REST Framework) Standartlari
- **Filtrlash (Filtering):** Har bir ro'yxat (list) endpointida `django-filter` yordamida chuqur va xavfsiz `FilterSet` klasslari yaratiladi.
- **Qidiruv (Search):** Matnli qidiruv uchun `SearchFilter` to'g'ri maydonlar (`^`, `=`, `@`) bilan sozlanadi.
- **Sahifalash (Pagination):** Barcha ro'yxat endpointlari majburiy tartibda standartlashtirilgan Pagination bilan ta'minlanadi. Cheksiz ro'yxat qaytarish taqiqlanadi.
- **Cheklov (Throttling / Rate Limiting):** Tizimni DoS va ortiqcha yuklamalardan himoya qilish uchun anonim va autentifikatsiyadan o'tgan foydalanuvchilarga maxsus throttling tariflari (`AnonRateThrottle`, `UserRateThrottle`, `ScopedRateThrottle`) o'rnatiladi.
- **Xatoliklarni boshqarish:** API xatoliklari yagona, tushunarli formatda (standard error response) qaytariladi.

#### D. Mock Data Tizimi (Bir Buyruqli Seeding)
- Har bir yaratilgan yangi model uchun darhol mock (soxta) ma'lumotlar generatori yoziladi.
- Foydalanuvchi quyidagi bitta buyruq bilan butun loyihaning ma'lumotlar bazasini to'liq va sifatli test ma'lumotlari bilan to'ldira olishi shart:
  ```bash
  python manage.py seed_data
  ```
- Mock ma'lumotlar realistik bo'lishi (taomlar, narxlar, kategoriyalar, rasmlar havolalari, foydalanuvchilar, buyurtmalar) shart.

#### E. Postman Hujjatlashtirish
- Har bir yangi yoki yangilangan API endpointi darhol loyihaning Postman kolleksiyasiga (`postman/fast_food_collection.json`) qo'shiladi.
- Har bir so'rovda:
  - To'liq URL va HTTP Method (GET, POST, PUT, PATCH, DELETE).
  - Headers (`Authorization: Bearer <token>`, `Content-Type: application/json`).
  - URL Query parametrlari (filter, search, page).
  - Namuna Request Body (JSON).
  - Muvaffaqiyatli (200/201) va xatolik (400/401/403/404) response namunalari kiritiladi.

#### F. URL Data Almashinishi (Data Contracts) va JSON Sxemalari
- Har bir Django ilovasi (`apps/<app_name>/contracts/`) va umumiy tizimda barcha URL endpointlarning ma'lumot almashinish shartnomalari (Data Contracts) alohida JSON formatda saqlanadi va yangilab boriladi.
- Har bir JSON kontraktida:
  - **Endpoint & Method**: Qaysi URL va qaysi HTTP metod.
  - **Request Schema & Example**: Qabul qilinadigan JSON formati (tiplar, majburiy/ixtiyoriy maydonlar).
  - **Response Schema & Example**: Muvaffaqiyatli (200/201) va xatolik (400/401/403/404/429) holatlaridagi JSON javoblari.
  - **Inter-App Data Exchange**: Ilovalararo (masalan, `orders` -> `users`, `kitchen` -> `notifications`) qanday formatdagi JSON ma'lumot uzatilishi aniq ko'rsatiladi.

#### G. Git Branching Qoidasi (Har bir o'zgarish alohida branchda)
- **Hech qachon to'g'ridan-to'g'ri `main` yoki `master` branchda o'zgarish qilinmaydi!**
- Har bir yangi vazifa, funksionallik (feature) yoki xatolikni tuzatish (fix) uchun alohida nomlangan Git branch ochiladi:
  - Yangi funksiyalar: `feature/<feature-nomi>` (masalan: `feature/menu-category-api`)
  - Tuzatishlar: `fix/<muammo-nomi>` (masalan: `fix/order-calc-bug`)
  - Optimizatsiya: `perf/<optimizatsiya-nomi>` (masalan: `perf/product-list-n-plus-1`)
- O'zgarishlar faqat foydalanuvchi tasdig'i bilan tegishli branchga kiritiladi.

---

### 🕵️‍♂️ 2. Senior QA / Test Automation Engineer
Kodni mustaqil, xolis va talabchanlik bilan sinovdan o'tkazuvchi mutaxassis.

#### A. Mustaqil Testlash Vakolati
- QA muhandisi foydalanuvchidan har safar ruxsat so'rab o'tirmasdan, **foydalanuvchi bergan dastlabki prompt va talablar asosida mustaqil ravishda** kodni sinovdan o'tkazadi.
- Testlar avtomatlashtirilgan bo'lishi va `python manage.py test` yoki `pytest` orqali yurgizilishi kerak.

#### B. Majburiy Test Qamrovi (Test Coverage Scope):
1. **API Status Kodlari va Sxemasi:** Har bir endpoint to'g'ri status (200, 201, 204, 400, 401, 403, 404, 429) va to'g'ri JSON format qaytarayotgani.
2. **Ruxsatlar va Autentifikatsiya (Permissions):**
   - Mehmon (Anonim) foydalanuvchi kira oladimi/yo'qmi?
   - Oddiy mijoz (Customer) boshqa birovning buyurtmasini ko'ra olmasligi tekshiriladimi?
   - Admin/Kuryer/Oshpaz rollari huquqlari ajratilganmi?
3. **Database Performance va N+1 Nazorati:**
   - Testlarda `self.assertNumQueries(...)` yordamida so'rovlar soni qat'iy nazorat qilinadi. Ro'yxatdagi elementlar soni oshganda SQL so'rovlar soni ko'payib ketmasligi kafolatlanadi.
4. **Filtrlash, Qidiruv va Pagination Testlari:**
   - Filtr to'g'ri ishlayaptimi?
   - Qidiruv natijalari to'g'rimi?
   - Sahifalash (sahifa chegaralari, noto'g'ri page soni berilganda) tekshirilganmi?
5. **Throttling (Rate Limiting) Testi:**
   - Qisqa vaqt ichida limitdan ortiq so'rov yuborilganda `429 Too Many Requests` qaytishi tekshiriladi.
6. **Edge Cases & Salbiy (Negative) Testlar:**
   - Noto'g'ri narx (manfiy son), bo'sh matn, mavjud bo'lmagan ID yuborilgandagi holatlar.

---

## 3. Ruxsatlar Siyosati (Permissions Policy)
Batafsil ruxsatlar loyiha ildizidagi [permissions.json](file:///home/shokhjahon/startapp/Fast-Food/permissions.json) faylida belgilangan.

### ✅ Ruxsat So'ralmaydi (Avtomatik Ruxsat Etilgan):
- Kod bazasini o'rganish, fayllarni o'qish (`read_file`, `list_directory`, `search`).
- Git holatini tekshirish (`git status`, `git diff`, `git log`).
- Testlarni mustaqil yurgizish (`python manage.py test`, `pytest`).
- Muhit va paketlar holatini ko'rish (`pip list`, terminal inspection).

### ⛔ Faqat Foydalanuvchi Tasdig'i Bilan (Qat'iy Man Etiladi):
- Loyiha kodini yozish, o'zgartirish yoki yangi fayl yaratish (`write_file`, `edit_file`).
- Ma'lumotlar bazasi migratsiyalari (`makemigrations`, `migrate`, `flush`).
- Yangi kutubxona o'rnatish (`pip install`).
- Git operatsiyalari (`git commit`, `git push`, `git reset`, `git checkout`).
- Fayllarni o'chirish yoki almashtirish.

---

## 4. Xulosa va Kafolat
Ushbu qoidalar Fast-Food loyihasining yuqori unumdorlikda, xatosiz, mustahkam arxitekturada va eng asosiysi **to'liq foydalanuvchi nazorati ostida** rivojlanishini ta'minlaydi.

