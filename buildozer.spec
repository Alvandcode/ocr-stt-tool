[app]
title = OCR STT Tool
package.name = ocrstt
package.domain = org.alvandcode.ocrstt
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1.0
requirements = python3,kivy,pillow,pdfplumber,pytesseract,SpeechRecognition
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
p4a.branch = master
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deployment_target = 12.0

# NOTE: pytesseract needs a tesseract binary + traineddata, which
# python-for-android / kivy-ios do NOT provide out of the box.
# Image OCR will NOT work on mobile unless you add a tesseract recipe
# and bundle 'eng.traineddata' / 'fas.traineddata' yourself.
# PDF text-layer extraction and offline STT are more realistic on mobile.

[buildozer]
log_level = 2
warn_on_root = 1
