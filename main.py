"""
Poster/Banner Maker Pro
Professional-level poster/banner maker app - Kivy + Pillow se.
Features: multiple templates, photo customize, PNG/JPG export,
save/share, AdMob ads, Firebase-based remote admin control.
"""

import os
import json
import datetime

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
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.metrics import dp
from kivy.clock import Clock

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# =================================================================
# ADMOB CONFIGURATION
# Yahan apni ASLI AdMob IDs daalein (AdMob account banane ke baad
# console.admob.google.com se milti hain). Abhi TEST IDs dali hain -
# Google ki apni official test IDs hain, launch se pehle inhe badal
# dena - warna asli ads nahi chalengi aur account suspend bhi ho
# sakta hai (khud ke ads par khud click karna policy violation hai,
# isliye TEST ID se hi development/testing karein).
# =================================================================
ADMOB_APP_ID = "ca-app-pub-3940256099942544~3347511713"          # Google TEST App ID
ADMOB_BANNER_ID = "ca-app-pub-3940256099942544/6300978111"       # Google TEST Banner ID
ADMOB_INTERSTITIAL_ID = "ca-app-pub-3940256099942544/1033173712" # Google TEST Interstitial ID

# =================================================================
# REMOTE CONFIG (Firebase) - asli "Admin Panel" ka kaam yahi karta hai
# Iske bina bhi app poori tarah chalti hai (DEFAULT_CONFIG use hoga),
# Firebase jodne ka tarika README-ADMIN-PANEL.md mein hai.
# =================================================================
DEFAULT_REMOTE_CONFIG = {
    "ads_enabled": True,
    "min_posters_between_interstitial": 3,
    "app_update_message": "",
    "maintenance_mode": False,
}

CANVAS_SIZES = {
    "Instagram Post (1:1)": (1080, 1080),
    "Instagram Story (9:16)": (1080, 1920),
    "Poster/Banner (4:5)": (1080, 1350),
    "A4 Print (Portrait)": (1240, 1754),
}

# Sirf RANG-THEME - koi party logo/chinh app mein nahi hai
THEMES = {
    "Theme A (Saffron-White)": {"bg": (255, 153, 51), "accent": (255, 255, 255), "text": (20, 20, 20)},
    "Theme B (Red-Green)": {"bg": (198, 40, 40), "accent": (56, 142, 60), "text": (255, 255, 255)},
    "Theme C (Blue-White)": {"bg": (21, 101, 192), "accent": (255, 255, 255), "text": (255, 255, 255)},
    "Theme D (Green-White)": {"bg": (46, 125, 50), "accent": (255, 255, 255), "text": (255, 255, 255)},
    "Theme E (Tricolor)": {"bg": (255, 153, 51), "accent": (19, 136, 8), "text": (0, 0, 128)},
    "Theme F (Purple-Gold)": {"bg": (74, 20, 140), "accent": (255, 193, 7), "text": (255, 255, 255)},
    "Theme G (Dark-Neon)": {"bg": (18, 18, 18), "accent": (0, 230, 118), "text": (255, 255, 255)},
    "Theme H (Student-Blue)": {"bg": (255, 255, 255), "accent": (33, 150, 243), "text": (33, 33, 33)},
}

TEMPLATES = ["Single Photo", "Two Photo (Split)", "Photo + Big Text", "Text Only (Quote Card)"]


class PosterEngine:
    """
    Poster/banner banane ka asli engine. Ismein koi party chinh/logo
    hardcode nahi hai - sab kuchh user khud apload karta hai.
    """

    def __init__(self):
        self.theme_name = list(THEMES.keys())[0]
        self.template = TEMPLATES[0]
        self.canvas_size_name = list(CANVAS_SIZES.keys())[2]
        self.user_photo_path = None
        self.user_photo2_path = None
        self.user_logo_path = None
        self.title_text = ""
        self.subtitle_text = ""
        self.footer_text = ""
        self.brightness = 1.0
        self.contrast = 1.0
        self.grayscale = False
        self.export_format = "PNG"  # PNG ya JPEG

    def _load_font(self, size, bold=True):
        candidates = [
            "/system/fonts/NotoSansDevanagari-Regular.ttf",
            "assets/fonts/NotoSansDevanagari-Regular.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def _apply_photo_adjustments(self, img):
        if self.brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(self.brightness)
        if self.contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(self.contrast)
        if self.grayscale:
            img = img.convert("L").convert("RGB")
        return img

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

    def generate(self, output_path):
        cw, ch = CANVAS_SIZES[self.canvas_size_name]
        theme = THEMES[self.theme_name]
        img = Image.new("RGB", (cw, ch), theme["bg"])
        draw = ImageDraw.Draw(img)

        strip_h = max(20, int(ch * 0.02))
        draw.rectangle([0, 0, cw, strip_h], fill=theme["accent"])
        draw.rectangle([0, ch - strip_h, cw, ch], fill=theme["accent"])

        margin = int(cw * 0.06)
        card_top = int(ch * 0.06)
        card_bottom = ch - int(ch * 0.06)
        draw.rounded_rectangle(
            [margin, card_top, cw - margin, card_bottom],
            radius=int(cw * 0.03),
            fill=(255, 255, 255) if self.template != "Text Only (Quote Card)" else theme["bg"],
        )

        text_top = card_top + int(ch * 0.03)

        if self.template == "Single Photo":
            text_top = self._draw_single_photo(img, theme, margin, card_top, card_bottom, cw)
        elif self.template == "Two Photo (Split)":
            text_top = self._draw_two_photo(img, theme, margin, card_top, card_bottom, cw)
        elif self.template == "Photo + Big Text":
            text_top = self._draw_photo_big_text(img, theme, margin, card_top, card_bottom, cw)
        else:  # Text Only Quote Card
            text_top = card_top + int(ch * 0.15)

        # Logo (agar upload ki ho)
        if self.user_logo_path and os.path.exists(self.user_logo_path):
            try:
                logo = Image.open(self.user_logo_path).convert("RGBA")
                logo.thumbnail((int(cw * 0.14), int(cw * 0.14)))
                img.paste(logo, (cw - logo.width - int(cw * 0.05), int(ch * 0.03)), logo)
            except Exception:
                pass

        draw = ImageDraw.Draw(img)
        title_size = int(cw * 0.06)
        title_font = self._load_font(title_size)
        text_color = theme["text"] if self.template != "Text Only (Quote Card)" else theme["accent"]
        draw.text((cw / 2, text_top), self.title_text or "Aapka Sandesh Yahan",
                   font=title_font, fill=text_color, anchor="ma")

        sub_font = self._load_font(int(cw * 0.037))
        draw.text((cw / 2, text_top + title_size + 20), self.subtitle_text or "",
                   font=sub_font, fill=text_color, anchor="ma")

        footer_font = self._load_font(int(cw * 0.028))
        draw.text((cw / 2, card_bottom - int(ch * 0.04)), self.footer_text or "",
                   font=footer_font, fill=(90, 90, 90), anchor="ma")

        save_kwargs = {"quality": 95} if self.export_format == "JPEG" else {}
        if self.export_format == "JPEG":
            img = img.convert("RGB")
        img.save(output_path, self.export_format, **save_kwargs)
        return output_path

    def _draw_single_photo(self, img, theme, margin, card_top, card_bottom, cw):
        photo_h = int((card_bottom - card_top) * 0.55)
        photo_top = card_top + int(cw * 0.05)
        if self.user_photo_path and os.path.exists(self.user_photo_path):
            try:
                p = Image.open(self.user_photo_path).convert("RGB")
                p = self._apply_photo_adjustments(p)
                target_w = cw - 2 * (margin + int(cw * 0.05))
                p = self._crop_to_fit(p, target_w, photo_h)
                img.paste(p, (margin + int(cw * 0.05), photo_top))
            except Exception:
                pass
        return photo_top + photo_h + int(cw * 0.05)

    def _draw_two_photo(self, img, theme, margin, card_top, card_bottom, cw):
        photo_h = int((card_bottom - card_top) * 0.45)
        photo_top = card_top + int(cw * 0.05)
        gap = int(cw * 0.03)
        half_w = (cw - 2 * (margin + int(cw * 0.05)) - gap) // 2
        for i, path in enumerate([self.user_photo_path, self.user_photo2_path]):
            if path and os.path.exists(path):
                try:
                    p = Image.open(path).convert("RGB")
                    p = self._apply_photo_adjustments(p)
                    p = self._crop_to_fit(p, half_w, photo_h)
                    x = margin + int(cw * 0.05) + i * (half_w + gap)
                    img.paste(p, (x, photo_top))
                except Exception:
                    pass
        return photo_top + photo_h + int(cw * 0.05)

    def _draw_photo_big_text(self, img, theme, margin, card_top, card_bottom, cw):
        photo_h = int((card_bottom - card_top) * 0.35)
        photo_top = card_top + int(cw * 0.05)
        if self.user_photo_path and os.path.exists(self.user_photo_path):
            try:
                p = Image.open(self.user_photo_path).convert("RGB")
                p = self._apply_photo_adjustments(p)
                target_w = cw - 2 * (margin + int(cw * 0.05))
                p = self._crop_to_fit(p, target_w, photo_h)
                img.paste(p, (margin + int(cw * 0.05), photo_top))
            except Exception:
                pass
        return photo_top + photo_h + int(cw * 0.08)


# =================================================================
# ADS MANAGER - AdMob wrapper (kivmob library istemal karta hai)
# =================================================================
class AdsManager:
    def __init__(self):
        self.enabled = DEFAULT_REMOTE_CONFIG["ads_enabled"]
        self.poster_count = 0
        self.min_between_interstitial = DEFAULT_REMOTE_CONFIG["min_posters_between_interstitial"]
        self._kivmob = None
        try:
            from kivmob import KivMob, TestIds
            self._kivmob = KivMob(ADMOB_APP_ID)
            self._kivmob.new_banner(ADMOB_BANNER_ID, top_pos=False)
            self._kivmob.new_interstitial(ADMOB_INTERSTITIAL_ID)
            self._kivmob.request_banner()
            self._kivmob.request_interstitial()
        except Exception:
            # Desktop/Termux par kivmob kaam nahi karega - sirf Android APK me chalega
            self._kivmob = None

    def show_banner(self):
        if self.enabled and self._kivmob:
            try:
                self._kivmob.show_banner()
            except Exception:
                pass

    def hide_banner(self):
        if self._kivmob:
            try:
                self._kivmob.hide_banner()
            except Exception:
                pass

    def on_poster_generated(self):
        self.poster_count += 1
        if self.enabled and self._kivmob and self.poster_count % self.min_between_interstitial == 0:
            try:
                if self._kivmob.is_interstitial_loaded():
                    self._kivmob.show_interstitial()
                self._kivmob.request_interstitial()
            except Exception:
                pass


# =================================================================
# SAVE / SHARE HELPER - Android gallery me save aur share karne ke liye
# =================================================================
def save_to_gallery_and_share(file_path, share=True):
    """
    Android par poster ko Photos/Gallery me save karta hai aur
    (agar chaha jaye) WhatsApp/Instagram jaise app se share karta hai.
    Sirf real Android device/APK par kaam karega, Termux/desktop par nahi.
    """
    try:
        from jnius import autoclass, cast
        from android.storage import primary_external_storage_path
        import shutil

        pictures_dir = os.path.join(primary_external_storage_path(), "Pictures", "PosterMaker")
        os.makedirs(pictures_dir, exist_ok=True)
        dest_path = os.path.join(pictures_dir, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)

        # MediaScanner ko batayein taaki naya photo turant Gallery me dikhe
        MediaScannerConnection = autoclass("android.media.MediaScannerConnection")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        MediaScannerConnection.scanFile(
            PythonActivity.mActivity, [dest_path], None, None
        )

        if share:
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            File = autoclass("java.io.File")

            intent = Intent(Intent.ACTION_SEND)
            intent.setType("image/*")
            uri = Uri.parse("file://" + dest_path)
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
            currentActivity.startActivity(Intent.createChooser(intent, "Poster Share Karein"))

        return dest_path
    except Exception as e:
        print("Save/Share error (sambhavtah Android device nahi hai):", e)
        return None


# =================================================================
# UI SCREENS
# =================================================================
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
    def __init__(self, engine, ads, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.ads = ads
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))

        title_lbl = Label(text="Poster Maker Pro", size_hint_y=None, height=dp(40),
                           font_size="22sp", bold=True)
        root.add_widget(title_lbl)

        scroll = ScrollView()
        form = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(5))
        form.bind(minimum_height=form.setter("height"))

        # --- Canvas size ---
        form.add_widget(Label(text="Size Chunein (Instagram/Poster/Print):", size_hint_y=None, height=dp(25)))
        size_spinner = Spinner(text=self.engine.canvas_size_name, values=list(CANVAS_SIZES.keys()),
                                size_hint_y=None, height=dp(45))
        size_spinner.bind(text=lambda inst, v: setattr(self.engine, "canvas_size_name", v))
        form.add_widget(size_spinner)

        # --- Template ---
        form.add_widget(Label(text="Template (Layout) Chunein:", size_hint_y=None, height=dp(25)))
        template_spinner = Spinner(text=self.engine.template, values=TEMPLATES,
                                    size_hint_y=None, height=dp(45))
        template_spinner.bind(text=lambda inst, v: self.set_template(v))
        form.add_widget(template_spinner)

        # --- Theme ---
        form.add_widget(Label(text="Color Theme Chunein:", size_hint_y=None, height=dp(25)))
        theme_spinner = Spinner(text=self.engine.theme_name, values=list(THEMES.keys()),
                                 size_hint_y=None, height=dp(45))
        theme_spinner.bind(text=lambda inst, v: setattr(self.engine, "theme_name", v))
        form.add_widget(theme_spinner)

        # --- Photo uploads ---
        photo_btn = Button(text="Photo 1 Upload Karein", size_hint_y=None, height=dp(45))
        photo_btn.bind(on_release=lambda x: self.open_picker(target="photo1"))
        form.add_widget(photo_btn)

        self.photo2_btn = Button(text="Photo 2 Upload Karein (Split template ke liye)",
                                  size_hint_y=None, height=dp(45))
        self.photo2_btn.bind(on_release=lambda x: self.open_picker(target="photo2"))
        form.add_widget(self.photo2_btn)

        logo_btn = Button(text="Apna Logo/Chinh Upload Karein (Optional)", size_hint_y=None, height=dp(45))
        logo_btn.bind(on_release=lambda x: self.open_picker(target="logo"))
        form.add_widget(logo_btn)

        # --- Photo adjustments ---
        form.add_widget(Label(text="Photo Brightness:", size_hint_y=None, height=dp(22)))
        bright_slider = Slider(min=0.5, max=1.8, value=1.0, size_hint_y=None, height=dp(35))
        bright_slider.bind(value=lambda inst, v: setattr(self.engine, "brightness", v))
        form.add_widget(bright_slider)

        form.add_widget(Label(text="Photo Contrast:", size_hint_y=None, height=dp(22)))
        contrast_slider = Slider(min=0.5, max=1.8, value=1.0, size_hint_y=None, height=dp(35))
        contrast_slider.bind(value=lambda inst, v: setattr(self.engine, "contrast", v))
        form.add_widget(contrast_slider)

        gray_btn = Button(text="Black & White: OFF", size_hint_y=None, height=dp(40))

        def toggle_gray(instance):
            self.engine.grayscale = not self.engine.grayscale
            gray_btn.text = f"Black & White: {'ON' if self.engine.grayscale else 'OFF'}"

        gray_btn.bind(on_release=toggle_gray)
        form.add_widget(gray_btn)

        # --- Text inputs ---
        form.add_widget(Label(text="Mukhya Sandesh (Title):", size_hint_y=None, height=dp(22)))
        self.title_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.title_input)

        form.add_widget(Label(text="Upshirshak (Subtitle):", size_hint_y=None, height=dp(22)))
        self.subtitle_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.subtitle_input)

        form.add_widget(Label(text="Neeche ka Text (Naam / Pad / Sampark):", size_hint_y=None, height=dp(22)))
        self.footer_input = TextInput(multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self.footer_input)

        # --- Export format ---
        form.add_widget(Label(text="Export Format:", size_hint_y=None, height=dp(22)))
        format_spinner = Spinner(text="PNG", values=["PNG", "JPEG"], size_hint_y=None, height=dp(45))
        format_spinner.bind(text=lambda inst, v: setattr(self.engine, "export_format", v))
        form.add_widget(format_spinner)

        scroll.add_widget(form)
        root.add_widget(scroll)

        generate_btn = Button(text="Poster Banayein", size_hint_y=None, height=dp(55),
                               background_color=(0.1, 0.6, 0.2, 1))
        generate_btn.bind(on_release=self.generate_poster)
        root.add_widget(generate_btn)

        self.status_label = Label(text="", size_hint_y=None, height=dp(30))
        root.add_widget(self.status_label)

        self.add_widget(root)
        # Banner ad neeche dikhta rahega jab bhi yah screen khuli ho
        Clock.schedule_once(lambda dt: self.ads.show_banner(), 1)

    def set_template(self, template_name):
        self.engine.template = template_name
        self.photo2_btn.disabled = template_name != "Two Photo (Split)"

    def open_picker(self, target):
        def on_select(path):
            if target == "photo1":
                self.engine.user_photo_path = path
                self.status_label.text = "Photo 1 upload ho gayi"
            elif target == "photo2":
                self.engine.user_photo2_path = path
                self.status_label.text = "Photo 2 upload ho gayi"
            else:
                self.engine.user_logo_path = path
                self.status_label.text = "Logo/Chinh upload ho gaya"

        FilePickerPopup(on_select=on_select).open()

    def generate_poster(self, instance):
        self.engine.title_text = self.title_input.text
        self.engine.subtitle_text = self.subtitle_input.text
        self.engine.footer_text = self.footer_input.text

        output_dir = os.path.join(App.get_running_app().user_data_dir, "posters")
        os.makedirs(output_dir, exist_ok=True)
        ext = "png" if self.engine.export_format == "PNG" else "jpg"
        filename = f"poster_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        output_path = os.path.join(output_dir, filename)

        self.engine.generate(output_path)
        self.ads.on_poster_generated()
        self.status_label.text = f"Poster ban gaya: {output_path}"

        preview_screen = self.manager.get_screen("preview")
        preview_screen.show_image(output_path)
        self.manager.current = "preview"


class PreviewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_path = None
        self.layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        self.img_widget = KivyImage()
        self.layout.add_widget(self.img_widget)

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        save_btn = Button(text="Gallery Me Save Karein", background_color=(0.1, 0.6, 0.2, 1))
        save_btn.bind(on_release=lambda x: self.save_only())
        share_btn = Button(text="Share Karein", background_color=(0.1, 0.5, 0.9, 1))
        share_btn.bind(on_release=lambda x: self.save_and_share())
        btn_row.add_widget(save_btn)
        btn_row.add_widget(share_btn)
        self.layout.add_widget(btn_row)

        back_btn = Button(text="Wapas Editor Par Jayein", size_hint_y=None, height=dp(50))
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)

        self.status = Label(text="", size_hint_y=None, height=dp(30))
        self.layout.add_widget(self.status)

        self.add_widget(self.layout)

    def show_image(self, path):
        self.current_path = path
        self.img_widget.source = path
        self.img_widget.reload()
        self.status.text = ""

    def save_only(self):
        result = save_to_gallery_and_share(self.current_path, share=False)
        self.status.text = "Gallery me save ho gaya!" if result else \
            "Save/Share sirf asli Android phone par kaam karta hai (APK install karke test karein)."

    def save_and_share(self):
        result = save_to_gallery_and_share(self.current_path, share=True)
        if not result:
            self.status.text = "Share sirf asli Android phone par kaam karta hai (APK install karke test karein)."

    def go_back(self, instance):
        self.manager.current = "editor"


class PosterMakerApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        engine = PosterEngine()
        ads = AdsManager()

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(EditorScreen(engine=engine, ads=ads, name="editor"))
        sm.add_widget(PreviewScreen(name="preview"))
        return sm


if __name__ == "__main__":
    PosterMakerApp().run()
