---
name: senior-backend-engineer
description: >-
  Use this skill for all backend development, architecture design, database optimization,
  Django REST Framework implementation, mock data seeding, and API documentation for the Fast-Food project.
---

# Senior Backend Engineer Skill

Bu skill Fast-Food loyihasida Senior darajasidagi Backend arxitekturasi va kod yozish standartlarini belgilaydi va amalga oshiradi.

## 🛑 Asosiy Qoidalar
1. **Tasdiqsiz kod yozilmaydi**: Foydalanuvchining to'g'ridan-to'g'ri buyrug'i va tasdig'isiz bir qator ham kod yozilmaydi.
2. **Har bir o'zgarish alohida Git branchda**: `feature/<nomi>`, `fix/<nomi>`, `perf/<nomi>` formatidagi alohida branch ochiladi. `main` branchda to'g'ridan-to'g'ri ishlash taqiqlanadi.

---

## 🏛️ Arxitektura va Kod Standartlari (Separation of Concerns)
Loyihada biznes mantiqni ViewSet yoki Modellar ichiga yozish qat'iyan man etiladi. Quyidagi qatlamlar ajratiladi:
- **Models**: Faqat maydonlar, table-level cheklovlar (`CheckConstraint`, `UniqueConstraint`), indekslar va `__str__`.
- **Selectors (`selectors.py`)**: Faqat ma'lumotlar bazasidan o'qish (`query`) amallari (barcha `select_related`, `prefetch_related`, filtrlar shu yerda bo'ladi).
- **Services (`services.py`)**: Barcha biznes mantiq va yozish (`create`, `update`, `delete`, hisob-kitoblar, tashqi integratsiyalar).
- **Serializers**: Faqat validation va ma'lumotlarni serialization/deserialization qilish.
- **Views/ViewSets**: Faqat HTTP so'rovni qabul qilish, tegishli Service/Selector'ni chaqirish va HTTP Response qaytarish.

---

## ⚡ Ma'lumotlar Bazasi va N+1 Optimizatsiyasi
1. **Indekslar (`db_index=True`, `Meta.indexes`)**:
   - Har bir `ForeignKey` va `OneToOneField`.
   - Barcha filtrlash, qidiruv va tartiblashda (`ordering`) ishlatiladigan maydonlar (`status`, `created_at`, `category_id`, `slug` va h.k.).
   - Birgalikda filtrlanadigan maydonlar uchun Composite indexlar (`models.Index(fields=['status', 'created_at'])`).
2. **N+1 Muammosini Hal Qilish**:
   - `ForeignKey` va `OneToOne` bog'lanishlar uchun majburiy **`select_related(...)`**.
   - `ManyToManyField` va teskari bog'lanishlar (`related_name`) uchun majburiy **`prefetch_related(...)`**.
   - Katta hajmdagi jadvallardan kerakli ustunlarni olishda `only()` yoki og'ir matnli ustunlarni qoldirishda `defer()` qo'llaniladi.

---

## 🛡️ DRF (Django REST Framework) Standartlari
- **Filtrlash**: `django-filter` yordamida maxsus `FilterSet` klasslari yaratiladi.
- **Qidiruv**: `rest_framework.filters.SearchFilter` orqali to'g'ri indekslangan maydonlar bo'yicha qidiruv sozlanadi.
- **Sahifalash (Pagination)**: Barcha ro'yxat qaytaruvchi endpointlarda majburiy standart Pagination bo'lishi shart.
- **Throttling**: Anonim va autentifikatsiyadan o'tgan foydalanuvchilar uchun tegishli cheklovlar (`AnonRateThrottle`, `UserRateThrottle`).
- **Data Contracts**: Har bir app uchun `apps/<app_name>/contracts/*.json` faylida URL ma'lumot almashinish sxemasi yuritiladi.

---

## 📦 Mock Data Tizimi (Bir Buyruqli Seeding)
- Har bir yangi yoki o'zgargan model uchun `management/commands/seed_data.py` generatori yoziladi/yangilanadi.
- Foydalanuvchi quyidagi bitta buyruq orqali bazani realistik ma'lumotlar bilan to'ldira olishi ta'minlanadi:
  ```bash
  python manage.py seed_data
  ```

---

## 📬 Postman Hujjatlashtirish
- Har bir endpoint darhol `postman/fast_food_collection.json` fayliga kiritiladi.
- URL, HTTP method, query parametrlar, sarlavhalar (headers), request body va barcha response namunalari (200/201/400/401/403/404) to'liq yoritiladi.

