
📘 OCR‑STT Tool

ابزار چندسکویی برای استخراج متن از تصویر، PDF و تبدیل گفتار به نوشتار

یک ابزار پایتونی چندسکویی (Cross‑Platform) که قابلیت‌های زیر را در یک پروژه واحد ارائه می‌دهد:

- استخراج متن از تصویر (OCR)  
- استخراج متن از PDF  
- تبدیل گفتار به نوشتار (Speech‑to‑Text)  
- رابط CLI برای استفادهٔ سریع  
- رابط GUI با Kivy برای اجرا روی Windows / macOS / Linux / Android / iOS

این پروژه کاملاً اوپن‌سورس است و برای توسعه‌دهندگان، پژوهشگران، دانشجویان و کاربران عمومی طراحی شده است.

---

⭐ لطفاً از پروژه حمایت کنید
اگر این ابزار برای شما مفید بود، لطفاً با زدن دکمهٔ Star ⭐ از پروژه حمایت کنید.  
این کار باعث می‌شود پروژه دیده شود و توسعهٔ آن ادامه پیدا کند.

---

📢 کانال رسمی تلگرام
برای دریافت آخرین آپدیت‌ها، نسخه‌های جدید، آموزش‌ها و ابزارهای مرتبط:  
کانال رسمی: @a_c_official

---

✨ ویژگی‌ها
- پشتیبانی از تصویر، PDF، فایل صوتی  
- پشتیبانی از زبان‌های مختلف (fa‑IR، en‑US و …)  
- اجرای مستقیم روی:
  - Windows  
  - macOS  
  - Linux  
  - Android (با Buildozer)  
  - iOS (با Xcode + Kivy-iOS)  
- طراحی ماژولار و قابل توسعه  
- مناسب برای انتشار در GitHub بدون نیاز به Git لوکال

---

📁 ساختار پروژه
`text
ocr-stt-tool/
├─ app/
│  ├─ core/
│  │  ├─ init.py
│  │  ├─ image_ocr.py
│  │  ├─ pdf_ocr.py
│  │  ├─ speechtotext.py
│  ├─ init.py
│  ├─ cli.py
│  ├─ gui_kivy.py
├─ examples/
│  ├─ sample.png
│  ├─ sample.pdf
│  ├─ sample.wav
├─ requirements.txt
├─ README.md
├─ LICENSE
`

---

🔧 نصب و راه‌اندازی

1) نصب وابستگی‌ها
`bash
pip install -r requirements.txt
`

2) نصب Tesseract OCR
- Windows:  
  دانلود از سایت رسمی: https://github.com/tesseract-ocr/tesseract (github.com in Bing)  
- macOS:  
  `bash
  brew install tesseract
  `
- Linux:  
  `bash
  sudo apt install tesseract-ocr
  `

---

▶️ اجرای ابزار

اجرای CLI
`bash
python -m app.cli image examples/sample.png
python -m app.cli pdf examples/sample.pdf
python -m app.cli audio examples/sample.wav --lang fa-IR
`

اجرای GUI
`bash
python -m app.gui_kivy
`

---

📱 راهنمای بیلد برای موبایل (Android / iOS)

🟩 Android (Buildozer)

1. نصب Buildozer  
   `bash
   pip install buildozer
   sudo apt install buildozer
   `
2. ساخت فایل پیکربندی  
   `bash
   buildozer init
   `
3. بیلد APK  
   `bash
   buildozer -v android debug
   `

خروجی در مسیر زیر قرار می‌گیرد:  
`
bin/*.apk
`

---

🟦 iOS (Kivy-iOS + Xcode)

1. نصب Kivy-iOS  
   `bash
   pip install kivy-ios
   `
2. ساخت پروژه iOS  
   `bash
   toolchain create ocrstt ios
   `
3. بیلد  
   `bash
   toolchain build python3 kivy
   `
4. باز کردن پروژه در Xcode  
   `
   ios/ocrstt.xcodeproj
   `

5. بیلد و اجرا روی دستگاه یا شبیه‌ساز

---

🖥️ راهنمای بیلد برای دسکتاپ

Windows / macOS / Linux
`bash
pip install pyinstaller
pyinstaller app/cli.py --onefile
`

خروجی در پوشهٔ dist/ قرار می‌گیرد.

---

⚠️ نکات مهم
- برای STT نیاز به اینترنت دارید (Google Speech API).  
- برای OCR فارسی باید پکیج زبان فارسی Tesseract نصب شود.  
- روی موبایل، عملکرد OCR وابسته به قدرت CPU دستگاه است.  
- اگر قصد توسعه دارید، ساختار ماژولار پروژه امکان افزودن قابلیت‌های جدید را فراهم می‌کند.

---

📄 لایسنس
این پروژه تحت لایسنس MIT منتشر شده است.  
برای مشاهدهٔ متن کامل، فایل LICENSE را ببینید.
