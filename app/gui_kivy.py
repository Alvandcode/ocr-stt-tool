from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView

from app.core import image_to_text, pdf_to_text, audio_to_text


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.file_chooser = FileChooserIconView()
        self.add_widget(self.file_chooser)

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

        self.output = Label(text="Output will appear here",
                            size_hint_y=None, height=100)
        self.add_widget(self.output)

    def _get_path(self):
        return self.file_chooser.selection[0] if self.file_chooser.selection else None

    def run_image(self, _):
        path = self._get_path()
        if path:
            self.output.text = image_to_text(path)

    def run_pdf(self, _):
        path = self._get_path()
        if path:
            self.output.text = pdf_to_text(path)

    def run_audio(self, _):
        path = self._get_path()
        if path:
            self.output.text = audio_to_text(path)


class OCRSTTApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    OCRSTTApp().run()
