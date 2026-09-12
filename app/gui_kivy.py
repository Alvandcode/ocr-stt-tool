"""Kivy GUI for OCR / PDF / speech-to-text.

Heavy work runs in a background thread so the UI never freezes.
Errors are shown inside the app instead of crashing it.
"""

from __future__ import annotations

import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from app.core.models import ExtractResult

# NOTE: backend imports (kivy-adjacent heavy deps like pdfplumber /
# SpeechRecognition) are lazy inside the callbacks so the GUI can still
# start when only one backend is broken or missing.

STT_LANGS = ("fa-IR", "en-US", "ar-SA", "de-DE", "fr-FR")
OCR_LANGS = ("fas+eng", "fas", "eng")
STT_ENGINES = ("google", "whisper")


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.file_chooser = FileChooserListView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff",
                     "*.bmp", "*.webp", "*.pdf", "*.wav", "*.aiff",
                     "*.aif", "*.flac"]
        )
        self.add_widget(self.file_chooser)

        options = BoxLayout(size_hint_y=None, height=48)
        self.stt_spinner = Spinner(
            text=STT_LANGS[0], values=STT_LANGS, size_hint_x=0.25
        )
        self.ocr_spinner = Spinner(
            text=OCR_LANGS[0], values=OCR_LANGS, size_hint_x=0.25
        )
        self.engine_spinner = Spinner(
            text=STT_ENGINES[0], values=STT_ENGINES, size_hint_x=0.25
        )
        self.norm_check = CheckBox(size_hint_x=0.1, active=False)
        self.status = Label(text="Select a file, then choose an action.")
        options.add_widget(Label(text="STT:", size_hint_x=0.08))
        options.add_widget(self.stt_spinner)
        options.add_widget(Label(text="OCR:", size_hint_x=0.08))
        options.add_widget(self.ocr_spinner)
        self.add_widget(options)

        options2 = BoxLayout(size_hint_y=None, height=40)
        options2.add_widget(Label(text="Engine:", size_hint_x=0.15))
        options2.add_widget(self.engine_spinner)
        options2.add_widget(Label(text="Normalize FA:", size_hint_x=0.25))
        options2.add_widget(self.norm_check)
        options2.add_widget(self.status)
        self.add_widget(options2)

        btn_layout = BoxLayout(size_hint_y=None, height=50)
        self.btn_image = Button(text="Image → Text")
        self.btn_pdf = Button(text="PDF → Text")
        self.btn_audio = Button(text="Audio → Text")
        self.btn_save = Button(text="Save output")
        self.btn_image.bind(on_press=self.run_image)
        self.btn_pdf.bind(on_press=self.run_pdf)
        self.btn_audio.bind(on_press=self.run_audio)
        self.btn_save.bind(on_press=self.save_output)
        btn_layout.add_widget(self.btn_image)
        btn_layout.add_widget(self.btn_pdf)
        btn_layout.add_widget(self.btn_audio)
        btn_layout.add_widget(self.btn_save)
        self.add_widget(btn_layout)

        # NOTE: TextInput scrolls internally; wrapping it in a ScrollView
        # causes nested-scroll conflicts on touch devices, so it fills
        # the remaining space directly.
        self.output = TextInput(
            text="Output will appear here",
            readonly=True,
            multiline=True,
        )
        self.add_widget(self.output)

        self._worker: threading.Thread | None = None
        self._last_text = ""

    # -- helpers ------------------------------------------------------
    def _get_path(self) -> str | None:
        sel = self.file_chooser.selection
        return sel[0] if sel else None

    def _set_busy(self, busy: bool, msg: str = "") -> None:
        for btn in (self.btn_image, self.btn_pdf, self.btn_audio, self.btn_save):
            btn.disabled = busy
        if msg:
            self.status.text = msg

    def _finish_ok(self, result: ExtractResult, msg: str) -> None:
        def _update(_dt):
            self._last_text = result.text if result.text.strip() else "(no text found)"
            self.output.text = self._last_text
            notes = list(result.warnings)
            if self.norm_check.active:
                notes.append("Persian normalization applied.")
            suffix = f" | {'; '.join(notes)}" if notes else ""
            self.status.text = f"{msg} ({result.engine}, {result.elapsed_sec:.1f}s){suffix}"
            self._set_busy(False)

        Clock.schedule_once(_update)

    def _finish_err(self, message: str) -> None:
        def _update(_dt):
            self.output.text = f"Error: {message}"
            self.status.text = "Failed. See output."
            self._set_busy(False)

        Clock.schedule_once(_update)

    def _maybe_normalize(self, result: ExtractResult) -> ExtractResult:
        if self.norm_check.active and result.text:
            from app.core.fa_normalize import normalize_persian

            result.text = normalize_persian(result.text)
        return result

    def _run_in_thread(self, func, *args, start_msg: str):
        if self._worker is not None and self._worker.is_alive():
            self.status.text = "Please wait, another task is running…"
            return
        path = self._get_path()
        if not path:
            self.status.text = "No file selected."
            self.output.text = "Please select a file first."
            return
        if not os.path.isfile(path):
            self.status.text = "Invalid selection."
            self.output.text = f"Error: file not found: {path}"
            return
        self._set_busy(True, start_msg)

        def _target():
            try:
                result = self._maybe_normalize(func(path, *args))
                if not isinstance(result, ExtractResult):
                    result = ExtractResult(
                        text=str(result), engine="unknown",
                        source=path, lang="n/a",
                    )
                self._finish_ok(result, "Done.")
            except Exception as exc:  # noqa: BLE001 - intentional: never crash UI thread
                self._finish_err(str(exc))

        self._worker = threading.Thread(target=_target, daemon=True)
        self._worker.start()

    # -- button callbacks ---------------------------------------------
    def save_output(self, _):
        if not self._last_text or self._last_text == "Output will appear here":
            self.status.text = "Nothing to save yet."
            return
        try:
            with open("ocrstt_output.txt", "w", encoding="utf-8") as fh:
                fh.write(self._last_text + "\n")
        except OSError as exc:
            self.status.text = "Save failed."
            self.output.text = f"Error: cannot write ocrstt_output.txt: {exc}"
            return
        self.status.text = "Saved to ocrstt_output.txt"

    def run_image(self, _):
        def _image(p, lang):
            from app.core.image_ocr import image_to_text

            return image_to_text(p, lang=lang)

        self._run_in_thread(
            _image, self.ocr_spinner.text,
            start_msg="Running OCR…",
        )

    def run_pdf(self, _):
        def _pdf(p, ocr_lang):
            from app.core.pdf_ocr import pdf_to_text

            return pdf_to_text(p, ocr_lang=ocr_lang)

        self._run_in_thread(
            _pdf, self.ocr_spinner.text,
            start_msg="Extracting PDF text…",
        )

    def run_audio(self, _):
        engine = self.engine_spinner.text
        lang = self.stt_spinner.text

        def _audio(p, _engine=engine, _lang=lang):
            if _engine == "whisper":
                from app.core.whisper_stt import whisper_to_result

                return whisper_to_result(p, lang=_lang)
            from app.core.speech_to_text import audio_to_text

            return audio_to_text(p, lang=_lang)

        self._run_in_thread(
            _audio,
            start_msg="Transcribing offline…"
            if engine == "whisper"
            else "Transcribing audio (needs internet)…",
        )


class OCRSTTApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    OCRSTTApp().run()
