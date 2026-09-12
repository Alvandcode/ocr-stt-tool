# OCR-STT Tool

[![Stars](https://img.shields.io/github/stars/Alvandcode/ocr-stt-tool?style=flat-square)](https://github.com/Alvandcode/ocr-stt-tool/stargazers) [![License](https://img.shields.io/github/license/Alvandcode/ocr-stt-tool?style=flat-square)](./LICENSE) [![Last commit](https://img.shields.io/github/last-commit/Alvandcode/ocr-stt-tool?style=flat-square)](https://github.com/Alvandcode/ocr-stt-tool/commits)

> Cross-platform OCR, PDF text extractor and speech-to-text tool in Python (CLI + Kivy GUI, Persian supported).

<p align="center">
  <a href="https://alvandcode.github.io/ocr-stt-tool/tutorial.html"><b>📖 آموزش قدم‌به‌قدم استفاده (موبایل + ویندوز + لینوکس + مک)</b></a>
</p>

> اگر دکمه آموزش باز نشد: فایل `docs/tutorial.html` را دانلود و مستقیم در مرورگر باز کنید، یا در تنظیمات ریپو GitHub Pages را روی Branch ‏`main` و پوشه `docs` فعال کنید تا همان دکمه آنلاین شود.

<div dir="rtl">

## ابزار استخراج متن و تبدیل گفتار

ابزار چندسکویی پایتون برای استخراج متن از عکس و PDF و تبدیل گفتار به نوشتار؛ با رابط خط فرمان و رابط گرافیکی Kivy و پشتیبانی از زبان فارسی.

</div>

---

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
  - Android (با Buildozer، با محدودیت OCR — بخش موبایل را ببینید)
  - iOS (با Xcode + Kivy-iOS، با محدودیت OCR)
- طراحی ماژولار و قابل توسعه
- مدیریت خطای مناسب (پیام واضح به‌جای Traceback خام)

---

📖 آموزش قدم‌به‌قدم

اگر تازه شروع کرده‌ای، صفحه آموزش تعاملی را باز کن — بخش موبایل (اندروید/آیفون) و دسکتاپ (ویندوز/لینوکس/مک) کاملاً تفکیک شده‌اند:

<p align="center">
  <a href="https://alvandcode.github.io/ocr-stt-tool/tutorial.html"><b>📖 ورود به صفحه آموزش</b></a>
  · <a href="docs/tutorial.html">مشاهده فایل آموزش در ریپو</a>
</p>

---

📁 ساختار پروژه

```text
ocr-stt-tool/
├─ app/
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ models.py
│  │  ├─ image_ocr.py
│  │  ├─ pdf_ocr.py
│  │  ├─ speech_to_text.py
│  │  ├─ whisper_stt.py
│  │  └─ fa_normalize.py
│  ├─ __init__.py
│  ├─ __main__.py
│  ├─ cli.py
│  └─ gui_kivy.py
├─ examples/
│  ├─ sample.png
│  ├─ sample.pdf
│  └─ sample.wav
├─ tests/
│  ├─ test_smoke.py
│  └─ test_golden.py
├─ docs/
│  └─ tutorial.html
├─ requirements.txt
├─ requirements-gui.txt
├─ requirements-optional.txt
├─ pyproject.toml
├─ buildozer.spec
├─ Dockerfile
├─ CHANGELOG.md
├─ README.md
└─ LICENSE
```

---

🔧 نصب و راه‌اندازی

1) نصب وابستگی‌ها (CLI و هسته — بدون GUI)

```bash
pip install -r requirements.txt
```

GUI دسکتاپ (Kivy):

```bash
pip install -r requirements-gui.txt
```

موارد اختیاری (میکروفون، تبدیل MP3، OCR اسکن-PDF، STT آفلاین، نرمالایز فارسی):

```bash
pip install -r requirements-optional.txt
# یا انتخابی: pip install "ocr-stt-tool[offline,fa]"
```

2) نصب Tesseract OCR

- Windows:
  باینری UB-Mannheim را نصب کنید:
  https://github.com/UB-Mannheim/tesseract/wiki
  و گزینهٔ زبان فارسی (`fas`) را موقع نصب فعال کنید. سپس `tesseract` باید در PATH باشد.
- macOS:

```bash
brew install tesseract tesseract-lang
```

- Linux:

```bash
sudo apt install tesseract-ocr tesseract-ocr-fas tesseract-ocr-eng poppler-utils
```

بررسی:

```bash
tesseract --version
tesseract --list-langs
```

---

▶️ اجرای ابزار

اجرای CLI

```bash
python -m app.cli image examples/sample.png --ocr-lang eng
python -m app.cli pdf examples/sample.pdf
python -m app.cli pdf scan.pdf --ocr-fallback --ocr-lang fas+eng
python -m app.cli audio examples/sample.wav --lang fa-IR
python -m app.cli audio speech.wav --lang en-US -o out.txt
```

آفلاین (بدون اینترنت، نیازمند `pip install faster-whisper`):

```bash
python -m app.cli audio speech.wav --engine whisper --whisper-model small --lang fa-IR
```

فرمت خروجی و نرمالایز فارسی:

```bash
python -m app.cli pdf examples/sample.pdf --format json -o res.json
python -m app.cli audio speech.wav --engine whisper --format srt -o subs.srt
python -m app.cli audio speech.wav --normalize-fa -o clean.txt
```

`--format srt` فقط برای صوت است؛ خروجی `json` شامل موتور، زبان، تعداد صفحات، هشدارها و زمان اجراست.
`--normalize-fa` از hazm (اگر نصب باشد) وگرنه جایگزین داخلی استفاده می‌کند.

اجرای GUI

```bash
python -m app.gui_kivy
```

در GUI زبان STT و OCR و موتور (google/whisper) از منوی کشویی انتخاب می‌شود،
گزینهٔ Normalize FA نرمال‌سازی فارسی را فعال می‌کند، کار سنگین در Thread پس‌زمینه
اجرا می‌شود (UI فریز نمی‌شود) و خطاها داخل خود برنامه نمایش داده می‌شوند.

---

🐳 اجرا با Docker (بدون نصب Tesseract و poppler روی سیستم)

```bash
docker build -t ocrstt:1.2.0 .
docker run --rm -v "$PWD/examples:/data" ocrstt:1.2.0 pdf /data/sample.pdf
docker run --rm -v "$PWD:/work" ocrstt:1.2.0 audio /work/speech.wav --lang fa-IR --format json
```

ایمیج شامل `tesseract-ocr-fas`، `poppler-utils` و `ffmpeg` است (پایتون 3.12-slim).

---

📱 وضعیت موبایل (Android / iOS) — آزمایشی

هدف اصلی پروژه **دسکتاپ و سرور** است. بیلد موبایل نگه داشته شده ولی آزمایشی محسوب می‌شود:

> محدودیت مهم: `pytesseract` فقط Wrapper است و به باینری `tesseract` نیاز دارد.
> `python-for-android` و `kivy-ios` به‌صورت پیش‌فرض `tesseract` ندارند، پس OCR عکس
> روی موبایل بدون Recipe اختصاصی و باندل `fas.traineddata` کار نمی‌کند.
> استخراج متن PDF (text-layer) واقع‌بینانه‌ترین قابلیت روی موبایل است.

🟩 Android (Buildozer، روی لینوکس)

```bash
pip install buildozer
sudo apt install openjdk-17-jdk unzip autoconf libtool pkg-config zlib1g-dev \
  libncurses-dev cmake libffi-dev libssl-dev
buildozer -v android debug
```

فایل `buildozer.spec` در ریپو موجود است. خروجی: `bin/*.apk`.
دسترسی اینترنت/حافظه در spec فعال شده (`INTERNET`, `READ_EXTERNAL_STORAGE`).

🟦 iOS (Kivy-iOS + Xcode، روی macOS)

```bash
pip install kivy-ios
toolchain build python3 kivy pillow
toolchain create ocrstt .
open ocrstt-ios/ocrstt.xcodeproj
```

سپس در Xcode بیلد و اجرا روی دستگاه یا شبیه‌ساز.

---

🖥️ راهنمای بیلد برای دسکتاپ

Windows / macOS / Linux

```bash
pip install pyinstaller
pyinstaller --name ocrstt --paths . --onefile -m app.cli
```

خروجی در پوشهٔ `dist/` قرار می‌گیرد.
توجه: باینری `tesseract` جداگانه روی سیستم مقصد لازم است (داخل exe باندل نمی‌شود).

---

⚠️ نکات مهم
- برای STT آنلاین نیاز به اینترنت دارید (Google Speech API). صوت شما به سرور گوگل ارسال می‌شود — برای فایل حساس رضایت بگیرید. جایگزین آفلاین: `requirements-optional.txt` (Vosk / faster-whisper).
- برای OCR فارسی باید دیتای زبان فارسی Tesseract نصب شود (`fas`) و `--ocr-lang fas` یا `fas+eng` بدهید.
- PDF اسکن‌شده لایهٔ متنی ندارد؛ خروجی خالی یعنی اسکن است — با `--ocr-fallback` (نیازمند poppler + tesseract) دوباره تلاش کنید.
- فرمت صوتی پشتیبانی‌شده: WAV/AIFF/FLAC. برای MP3/OGG/M4A اول با `ffmpeg` به WAV تبدیل کنید.
- توجه پایتون 3.15: کتابخانه `SpeechRecognition` هنوز با 3.15 ناسازگار است (`aifc` حذف شده). برای STT از پایتون 3.10 تا 3.13 استفاده کنید یا جایگزین آفلاین (Vosk / faster-whisper).
- روی موبایل، عملکرد OCR وابسته به قدرت CPU دستگاه است.
- محدودیت حجم پیش‌فرض برای جلوگیری از OOM: عکس ۳۰MB، PDF و صوت ۱۰۰MB.

---

📄 لایسنس
این پروژه تحت لایسنس MIT منتشر شده است.
برای مشاهدهٔ متن کامل، فایل LICENSE را ببینید.

---

## Contributing / مشارکت

- EN: Issues and Pull Requests are welcome. Please see `CONTRIBUTING.md`.
- FA: برای گزارش مشکل یا پیشنهاد قابلیت جدید، لطفا ایشو یا پول‌ریکوئست ثبت کنید.

## License / لایسنس

MIT — see [LICENSE](./LICENSE).

## Contact / ارتباط

- Telegram: https://t.me/a_c_official
- Website: https://alvandcode.github.io
