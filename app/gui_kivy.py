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
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from app.core import audio_to_text, image_to_text, pdf_to_text

STT_LANGS = ("fa-IR", "en-US")
OCR_LANGS = ("fas+eng", "fas", "eng")


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
            text=STT_LANGS[0], values=STT_LANGS, size_hint_x=0.35
        )
        self.ocr_spinner = Spinner(
            text=OCR_LANGS[0], values=OCR_LANGS, size_hint_x=0.35
        )
        self.status = Label(text="Select a file, then choose an action.",
                            size_hint_x=0.3)
        options.add_widget(Label(text="STT:", size_hint_x=0.1))
        options.add_widget(self.stt_spinner)
        options.add_widget(Label(text="OCR:", size_hint_x=0.1))
        options.add_widget(self.ocr_spinner)
        self.add_widget(options)

        btn_layout = BoxLayout(size_hint_y=None, height=50)
        self.btn_image = Button(text="Image → Text")
        self.btn_pdf = Button(text="PDF → Text")
        self.btn_audio = Button(text="Audio → Text")
        self.btn_image.bind(on_press=self.run_image)
        self.btn_pdf.bind(on_press=self.run_pdf)
        self.btn_audio.bind(on_press=self.run_audio)
        btn_layout.add_widget(self.btn_image)
        btn_layout.add_widget(self.btn_pdf)
        btn_layout.add_widget(self.btn_audio)
        self.add_widget(btn_layout)

        self.add_widget(BoxLayout(size_hint_y=None, height=30))
        self.output = TextInput(
            text="Output will appear here",
            readonly=True,
            multiline=True,
        )
        scroll = ScrollView()
        scroll.add_widget(self.output)
        self.add_widget(scroll)
        self.add_widget(self.status)

        self._worker: threading.Thread | None = None

    # -- helpers ------------------------------------------------------
    def _get_path(self) -> str | None:
        sel = self.file_chooser.selection
        return sel[0] if sel else None

    def _set_busy(self, busy: bool, msg: str = "") -> None:
        for btn in (self.btn_image, self.btn_pdf, self.btn_audio):
            btn.disabled = busy
        if msg:
            self.status.text = msg

    def _finish_ok(self, text: str, msg: str) -> None:
        def _update(_dt):
            self.output.text = text if text.strip() else "(no text found)"
            self.status.text = msg
            self._set_busy(False)

        Clock.schedule_once(_update)

    def _finish_err(self, message: str) -> None:
        def _update(_dt):
            self.output.text = f"Error: {message}"
            self.status.text = "Failed. See output."
            self._set_busy(False)

        Clock.schedule_once(_update)

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
                result = func(path, *args)
                if isinstance(result, str) and not result.strip():
                    Clock.schedule_once(
                        lambda _dt: setattr(self.output, "text", "(no text found)")
                    )
                self._finish_ok(result, "Done.")
            except Exception as exc:  # noqa: BLE001 - intentional: never crash UI thread
                self._finish_err(str(exc))

        self._worker = threading.Thread(target=_target, daemon=True)
        self._worker.start()

    # -- button callbacks ---------------------------------------------
    def run_image(self, _):
        self._run_in_thread(
            lambda p: image_to_text(p, lang=self.ocr_spinner.text),
            start_msg="Running OCR…",
        )

    def run_pdf(self, _):
        self._run_in_thread(
            lambda p: pdf_to_text(p, ocr_lang=self.ocr_spinner.text),
            start_msg="Extracting PDF text…",
        )

    def run_audio(self, _):
        self._run_in_thread(
            lambda p: audio_to_text(p, lang=self.stt_spinner.text),
            start_msg="Transcribing audio (needs internet)…",
        )


class OCRSTTApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    OCRSTTApp().run()
