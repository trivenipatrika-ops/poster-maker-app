"""
Poster/Banner Maker App
Ek simple, offline poster/banner banane wala tool - Kivy + Pillow se.
Koi admin panel nahi hai - yah pura app user ke phone par hi chalta hai.
"""

import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp

from PIL import Image, ImageDraw, ImageFont
import datetime

# -------------------------------------------------
# THEMES: sirf rang (colors) - koi party logo/chinh nahi
# -------------------------------------------------
THEMES = {
    "Theme A (Saffron-White)": {"bg": (255, 153, 51), "accent": (255, 255, 255), "text": (20, 20, 20)},
    "Theme B (Red-Green)": {"bg": (198, 40, 40), "accent": (56, 142, 60), "text": (255, 255, 255)},
    "Theme C (Blue-White)": {"bg": (21, 101, 192), "accent": (255, 255, 255), "text": (255, 255, 255)},
    "Theme D (Green-White)": {"bg": (46, 125, 50), "accent": (255, 255, 255), "text": (255, 255, 255)},
    "Theme E (Tricolor)": {"bg": (255, 153, 51), "accent": (19, 136, 8), "text": (0, 0, 128)},
}

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350  # portrait poster - social media ke liye best


class PosterEngine:
    def __init__(self):
        self.theme_name = list(THEMES.keys())[0]
        self.user_photo_path = None
        self.user_logo_path = None
        self.title_text = ""
        self.subtitle_text = ""
        self.footer_text = ""

    def _load_font(self, size):
        try:
            return ImageFont.truetype(
                "/system/fonts/NotoSansDevanagari-Regular.ttf", size
            )
        except Exception:
            try:
                return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
            except Exception:
                return ImageFont.load_default()

    def generate(self, output_path):
        theme = THEMES[self.theme_name]
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), theme["bg"])
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, CANVAS_WIDTH, 40], fill=theme["accent"])
        draw.rectangle([0, CANVAS_HEIGHT - 40, CANVAS_WIDTH, CANVAS_HEIGHT], fill=theme["accent"])

        card_margin = 60
        card_top = 100
        card_bottom = CANVAS_HEIGHT - 100
        draw.rounded_rectangle(
            [card_margin, card_top, CANVAS_WIDTH - card_margin, card_bottom],
            radius=30,
            fill=(255, 255, 255),
        )

        photo_area_top = card_top + 30
        photo_h = 550
        if self.user_photo_path and os.path.exists(self.user_photo_path):
            try:
                user_img = Image.open(self.user_photo_path).convert("RGB")
                target_w = CANVAS_WIDTH - 2 * (card_margin + 30)
                user_img = self._crop_to_fit(user_img, target_w, photo_h)
                img.paste(user_img, (card_margin + 30, photo_area_top))
            except Exception:
                pass

        if self.user_logo_path and os.path.exists(self.user_logo_path):
            try:
                logo = Image.open(self.user_logo_path).convert("RGBA")
                logo.thumbnail((150, 150))
                img.paste(logo, (CANVAS_WIDTH - 190, 60), logo)
            except Exception:
                pass

        text_top = photo_area_top + photo_h + 40
        title_font = self._load_font(64)
        draw.text(
            (CANVAS_WIDTH / 2, text_top),
            self.title_text or "Aapka Sandesh Yahan",
            font=title_font,
            fill=theme["text"],
            anchor="ma",
        )

        sub_font = self._load_font(40)
        draw.text(
            (CANVAS_WIDTH / 2, text_top + 90),
            self.subtitle_text or "",
            font=sub_font,
            fill=theme["text"],
            anchor="ma",
        )

        footer_font = self._load_font(30)
        draw.text(
            (CANVAS_WIDTH / 2, card_bottom - 60),
            self.footer_text or "",
            font=footer_font,
            fill=(90, 90, 90),
            anchor="ma",
        )

        img.save(output_path, quality=95)
        return output_path

    @staticmethod
    def _crop_to_fit(img, target_w, target_h):
        src_ratio = img.width / img.height
        target_ratio = target_w / target_h
        if src_ratio > target_ratio:
            new_h = img.height
            new_w = int(new_h * target_ratio)
            left = (img.width - new_w) // 2
            img = img.crop((left, 0, left + new_w, new_h))
        else:
            new_w = img.width
            new_h = int(new_w / target_ratio)
            top = (img.height - new_h) // 2
            img = img.crop((0, top, new_w, top + new_h))
        return img.resize((target_w, target_h))


class FilePickerPopup(Popup):
    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.title = "Photo/Logo Chunein"
        self.size_hint = (0.9, 0.9)
        layout = BoxLayout(orientation="vertical")
        chooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg"])
        layout.add_widget(chooser)

        btn_box = BoxLayout(size_hint_y=None, height=dp(50))
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(select_btn)
        btn_box.add_widget(cancel_btn)
        layout.add_widget(btn_box)
        self.content = layout

        def do_select(instance):
            if chooser.selection:
                on_select(chooser.selection[0])
            self.dismiss()

        select_btn.bind(on_release=do_select)
        cancel_btn.bind(on_release=lambda x: self.dismiss())


class EditorScreen(Screen):
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        title_lbl = Label(text="Poster / Banner Maker", size_hint_y=None, height=dp(40),
                           font_size="22sp", bold=True)
        root.add_widget(title_lbl)

        scroll = ScrollView()
        form = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(5))
        form.bind(minimum_height=form.setter("height"))

        form.add_widget(Label(text="Theme (Rang) Chunein:", size_hint_y=None, height=dp(30)))
        theme_box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(len(THEMES) * 45))
        for theme_name in THEMES:
            btn = Button(text=theme_name, size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda inst, t=theme_name: self.set_theme(t))
            theme_box.add_widget(btn)
        form.add_widget(theme_box)

        photo_btn = Button(text="Photo Upload Karein", size_hint_y=None, height=dp(45))
        photo_btn.bind(on_release=lambda x: self.open_picker(is_logo=False))
        form.add_widget(photo_btn)

        logo_btn = Button(text="Apna Logo/Chinh Upload Karein (Optional)", size_hint_y=None, height=dp(45))
        logo_btn.bind(on_release=lambda x: self.open_picker(is_logo=True))
        form.add_widget(logo_btn)

        form.add_widget(Label(text="Mukhya Sandesh (Title):", size_hint_y=None, height=dp(25)))
        self.title_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.title_input)

        form.add_widget(Label(text="Upshirshak (Subtitle):", size_hint_y=None, height=dp(25)))
        self.subtitle_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.subtitle_input)

        form.add_widget(Label(text="Neeche ka Text (Naam / Pad / Sampark):", size_hint_y=None, height=dp(25)))
        self.footer_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.footer_input)

        scroll.add_widget(form)
        root.add_widget(scroll)

        generate_btn = Button(text="Poster Banayein", size_hint_y=None, height=dp(55),
                               background_color=(0.1, 0.6, 0.2, 1))
        generate_btn.bind(on_release=self.generate_poster)
        root.add_widget(generate_btn)

        self.status_label = Label(text="", size_hint_y=None, height=dp(30))
        root.add_widget(self.status_label)

        self.add_widget(root)

    def set_theme(self, theme_name):
        self.engine.theme_name = theme_name
        self.status_label.text = f"Theme chuna gaya: {theme_name}"

    def open_picker(self, is_logo):
        def on_select(path):
            if is_logo:
                self.engine.user_logo_path = path
                self.status_label.text = "Logo/Chinh upload ho gaya"
            else:
                self.engine.user_photo_path = path
                self.status_label.text = "Photo upload ho gayi"

        FilePickerPopup(on_select=on_select).open()

    def generate_poster(self, instance):
        self.engine.title_text = self.title_input.text
        self.engine.subtitle_text = self.subtitle_input.text
        self.engine.footer_text = self.footer_input.text

        output_dir = os.path.join(App.get_running_app().user_data_dir, "posters")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"poster_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output_path = os.path.join(output_dir, filename)

        self.engine.generate(output_path)
        self.status_label.text = f"Poster ban gaya: {output_path}"

        preview_screen = self.manager.get_screen("preview")
        preview_screen.show_image(output_path)
        self.manager.current = "preview"


class PreviewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        self.img_widget = KivyImage()
        self.layout.add_widget(self.img_widget)

        back_btn = Button(text="Wapas Editor Par Jayein", size_hint_y=None, height=dp(50))
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def show_image(self, path):
        self.img_widget.source = path
        self.img_widget.reload()

    def go_back(self, instance):
        self.manager.current = "editor"


class PosterMakerApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        engine = PosterEngine()

        sm = ScreenManager()
        sm.add_widget(EditorScreen(engine=engine, name="editor"))
        sm.add_widget(PreviewScreen(name="preview"))
        return sm


if __name__ == "__main__":
    PosterMakerApp().run()
