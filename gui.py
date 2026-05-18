# coding: utf-8
"""
Stabil GUI - Hextech Akademi
Bu dosya önceki karmaşık sidebar patchlerini kaldırıp tek ve stabil bir arayüz kullanır.
Amaç: iz bırakmayan sidebar animasyonu, koyu tema, ortalı giriş ekranı ve temel proje özellikleri.
"""

import calendar
from datetime import date, datetime
import webbrowser
from pathlib import Path
import os
import sys
try:
    import ctypes
except Exception:
    ctypes = None

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

import veritabani as db

# Uygulama logosu: assets/hextech_logo.png
BASE_DIR = Path(__file__).resolve().parent
LOGO_PNG = BASE_DIR / "assets" / "hextech_logo.png"
LOGO_ICO = BASE_DIR / "assets" / "hextech_logo.ico"

def setup_app_icon(window):
    """Pencere logosunu ve Windows görev çubuğu ikonunu güvenli şekilde ayarlar."""
    try:
        if sys.platform.startswith("win"):
            try:
                if ctypes is not None:
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("HextechAkademi.App")
            except Exception:
                pass
            try:
                if LOGO_ICO.exists():
                    window.iconbitmap(default=str(LOGO_ICO))
            except Exception:
                pass

        if LOGO_PNG.exists():
            window._hextech_window_icon = tk.PhotoImage(file=str(LOGO_PNG))
            window.iconphoto(True, window._hextech_window_icon)
    except Exception as e:
        print("Logo yüklenemedi:", e)



def open_material_link(link):
    """Materyal butonunun her zaman kendi linkini açmasını sağlar.
    - Link boşsa uyarır.
    - http/https linklerini direkt açar.
    - Yerel dosya adlarını proje klasörüne göre açar.
    """
    link = str(link or "").strip()
    if not link:
        messagebox.showwarning("Materyal", "Bu materyalin bağlantısı boş.")
        return
    try:
        lower = link.lower()
        if lower.startswith(("http://", "https://", "mailto:", "file://")):
            webbrowser.open(link, new=2)
            return

        p = Path(link)
        if not p.is_absolute():
            p = BASE_DIR / link
        if p.exists():
            webbrowser.open(p.resolve().as_uri(), new=2)
        else:
            # Dosya yoksa yine de yazılan bağlantıyı açmayı dene.
            webbrowser.open(link, new=2)
    except Exception as e:
        messagebox.showerror("Materyal Açılamadı", f"Materyal açılamadı:\n{e}")





# Tkinter/CustomTkinter bazen kapanmış Entry/Textbox/Toplevel nesnelerine
# birkaç milisaniye sonra focus vermeye çalışabiliyor. Bu durum özellikle
# destek/forum gibi sayfalar yenilenirken veya pencere hızlı kapanırken
# konsola "bad window path name" hatası basar. Aşağıdaki koruma çalışan
# özellikleri değiştirmez; sadece artık var olmayan widgetlara odaklanma
# denemelerini güvenli şekilde yok sayar.
import traceback

_ORIGINAL_FOCUS_SET = tk.Misc.focus_set
_ORIGINAL_FOCUS_FORCE = tk.Misc.focus_force
_ORIGINAL_TK_REPORT = getattr(tk.Tk, "report_callback_exception", None)

def _is_dead_widget_error(err):
    return isinstance(err, tk.TclError) and "bad window path name" in str(err)

def _safe_focus_set(self, *args, **kwargs):
    try:
        if hasattr(self, "winfo_exists") and not self.winfo_exists():
            return None
        return _ORIGINAL_FOCUS_SET(self, *args, **kwargs)
    except tk.TclError as e:
        if "bad window path name" in str(e) or "can't invoke" in str(e):
            return None
        return None
    except Exception:
        return None

def _safe_focus_force(self, *args, **kwargs):
    try:
        if hasattr(self, "winfo_exists") and not self.winfo_exists():
            return None
        return _ORIGINAL_FOCUS_FORCE(self, *args, **kwargs)
    except tk.TclError as e:
        if "bad window path name" in str(e) or "can't invoke" in str(e):
            return None
        return None
    except Exception:
        return None

def _safe_report_callback_exception(self, exc, val, tb):
    # Kapanmış widget focus hatalarını tamamen susturur. Diğer gerçek hatalar
    # normal şekilde konsola yazılmaya devam eder.
    if exc is tk.TclError and "bad window path name" in str(val):
        return
    traceback.print_exception(exc, val, tb)

# Sınıf düzeyinde uygula: sonradan oluşturulan tüm Entry/Text/Textbox widgetları etkilenir.
tk.Misc.focus_set = _safe_focus_set
tk.Misc.focus_force = _safe_focus_force
for _cls_name in ("Widget", "Entry", "Text", "Toplevel", "Tk", "Frame", "Canvas"):
    _cls = getattr(tk, _cls_name, None)
    if _cls is not None:
        try:
            _cls.focus_set = _safe_focus_set
            _cls.focus_force = _safe_focus_force
        except Exception:
            pass

try:
    tk.Tk.report_callback_exception = _safe_report_callback_exception
    tk.Toplevel.report_callback_exception = _safe_report_callback_exception
    ctk.CTk.report_callback_exception = _safe_report_callback_exception
    ctk.CTkToplevel.report_callback_exception = _safe_report_callback_exception
except Exception:
    pass

try:
    import mail_servisi
except Exception:
    mail_servisi = None

# ─────────────────────────────────────────────────────────────────────────────
# TEMA
# ─────────────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

FONT = "Segoe UI"
BG = "#07111F"
BG_2 = "#0B172A"
BG_3 = "#10213A"
CARD = "#10203A"
CARD_2 = "#132844"
BORDER = "#25486F"
TEXT = "#F4F8FF"
MUTED = "#AFC1D6"
GREEN = "#22C59B"
GREEN_2 = "#17A982"
BLUE = "#15A9E6"
BLUE_2 = "#0C80B5"
PURPLE = "#7C4DFF"
RED = "#EF4444"
YELLOW = "#F7B731"
ORANGE = "#F97316"
RAIL_W = 76
SIDEBAR_OPEN_W = 264
ANIM_FRAMES = 14
ANIM_MS = 12

THEME_LIGHT = False

def apply_theme(light=False):
    """Uygulamanın ana renklerini koyu/açık tema arasında değiştirir.
    Yeni renkler aktif sayfa yeniden çizildiğinde uygulanır.
    """
    global THEME_LIGHT, BG, BG_2, BG_3, CARD, CARD_2, BORDER, TEXT, MUTED
    THEME_LIGHT = bool(light)
    if THEME_LIGHT:
        # Beyaz tema artık tamamen bembeyaz değil; göz yormayan gri-mavi tonlarda.
        ctk.set_appearance_mode("Light")
        BG = "#EEF3FA"
        BG_2 = "#DDE8F6"
        BG_3 = "#F7FAFE"
        CARD = "#F8FAFE"
        CARD_2 = "#E7EEF9"
        BORDER = "#9EBCE0"
        TEXT = "#0A1628"
        MUTED = "#3E526B"
    else:
        ctk.set_appearance_mode("Dark")
        BG = "#07111F"
        BG_2 = "#0B172A"
        BG_3 = "#10213A"
        CARD = "#10203A"
        CARD_2 = "#132844"
        BORDER = "#25486F"
        TEXT = "#F4F8FF"
        MUTED = "#AFC1D6"


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI UI
# ─────────────────────────────────────────────────────────────────────────────
def clear(widget):
    try:
        for w in widget.winfo_children():
            w.destroy()
    except Exception:
        pass


def lbl(parent, text, size=12, weight="normal", color=None, **kw):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=(FONT, size, weight),
        text_color=color or TEXT,
        **kw,
    )


def btn(parent, text, command=None, color=GREEN, hover=None, width=120, height=36, **kw):
    tc = kw.pop("text_color", None)
    if tc is None:
        # Açık temada BG_3/CARD gibi açık renkli butonların yazısı görünmez olmasın.
        neutral_colors = {BG_3, CARD, CARD_2, "transparent"}
        tc = TEXT if color in neutral_colors else "white"
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=color,
        hover_color=hover or color,
        width=width,
        height=height,
        corner_radius=12,
        font=(FONT, 12, "bold"),
        text_color=tc,
        **kw,
    )


def card(parent, **pack_kw):
    c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
    c.pack(**pack_kw)
    return c


def toast(master, text, color=GREEN):
    try:
        t = ctk.CTkToplevel(master)
        t.overrideredirect(True)
        t.attributes("-topmost", True)
        x = master.winfo_x() + master.winfo_width() - 360
        y = master.winfo_y() + master.winfo_height() - 96
        t.geometry(f"330x54+{x}+{y}")
        t.configure(fg_color=color)
        lbl(t, text, 12, "bold", "white", wraplength=290).pack(expand=True, padx=14)
        t.after(2400, lambda: t.destroy() if t.winfo_exists() else None)
    except Exception:
        pass


def egitmen_adi(eid):
    try:
        v = db.veri_yukle()
        for e in v.get("egitmenler", []):
            if e.get("egitmen_id") == eid or e.get("id") == eid:
                return e.get("ad", eid)
    except Exception:
        pass
    return eid or "Bilinmiyor"


def ogrenci_adi(oid):
    try:
        v = db.veri_yukle()
        for o in v.get("ogrenciler", []):
            if o.get("ogrenci_id") == oid or o.get("id") == oid:
                return o.get("ad", oid)
    except Exception:
        pass
    return oid or "Bilinmiyor"


def get_courses():
    try:
        d = db.tum_kurslar_getir()
        return list(d.values()) if isinstance(d, dict) else list(d)
    except Exception:
        return []


def user_id(user):
    return user.get("id") or user.get("ogrenci_id") or user.get("egitmen_id") or user.get("kullanici_adi")




def remember_login_account(user, role):
    """Beni hatırla seçilince hesabı rol bazlı listeye ekler."""
    try:
        veri = db.veri_yukle()
        ayar = veri.setdefault("sistem_ayarlari", {})
        hesaplar = ayar.setdefault("hatirlanan_hesaplar", [])
        uid = user_id(user)
        ad = user.get("ad", uid)
        # Aynı hesap tekrar eklenmesin; en sona taşı.
        hesaplar = [h for h in hesaplar if not (h.get("id") == uid and h.get("rol") == role)]
        hesaplar.append({"id": uid, "rol": role, "ad": ad, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
        ayar["hatirlanan_hesaplar"] = hesaplar[-12:]
        ayar["beni_hatirla"] = {"id": uid, "rol": role, "ad": ad}
        db.veri_kaydet(veri)
    except Exception:
        pass


def remembered_accounts(role=None):
    try:
        hesaplar = db.veri_yukle().get("sistem_ayarlari", {}).get("hatirlanan_hesaplar", []) or []
        if role:
            hesaplar = [h for h in hesaplar if h.get("rol") == role]
        return hesaplar
    except Exception:
        return []


def load_remembered_user(uid, role):
    """Şifre sormadan hatırlanan kullanıcıyı güvenli şekilde yükler."""
    try:
        veri = db.veri_yukle()
        if role == "ogrenci":
            for u in veri.get("ogrenciler", []):
                if uid in [u.get("id"), u.get("ogrenci_id"), u.get("kullanici_adi")]:
                    if u.get("durum", "aktif") != "pasif":
                        return u
        elif role == "egitmen":
            for u in veri.get("egitmenler", []):
                if uid in [u.get("id"), u.get("egitmen_id"), u.get("kullanici_adi")]:
                    if u.get("durum", "aktif") != "pasif" and u.get("onayli", True):
                        return u
        elif role == "admin":
            for u in veri.get("adminler", []):
                if uid in [u.get("id"), u.get("admin_id"), u.get("kullanici_adi")]:
                    if u.get("durum", "aktif") != "pasif":
                        return u
            a = veri.get("admin", {})
            if uid in [a.get("id"), a.get("admin_id"), a.get("kullanici_adi")]:
                return a
    except Exception:
        pass
    return None

def course_badge(kurs):
    """Kurs kartının üst kısmında fotoğraf yerine temiz ve okunaklı sembol üretir."""
    name = (kurs.get("kurs_adi") or "").lower()
    code = (kurs.get("ders_kodu") or kurs.get("kurs_id") or "DERS").replace("KURS_", "")
    if "veri tabanı" in name or "database" in name:
        return "DB", "Veri Tabanı", "#123A5A"
    if "web" in name or "internet" in name:
        return "WEB", "Web", "#103A55"
    if "programlama" in name or "algoritma" in name or "nesne" in name or "mobil" in name or "görsel" in name:
        return "</>", "Kodlama", "#123F35"
    if "fizik" in name or "matematik" in name:
        return "Fx", "Temel Bilim", "#3B2F13"
    if "yabancı" in name or "ingilizce" in name or "almanca" in name or "fransızca" in name or "türkçe" in name:
        return "Dil", "Dil", "#2E2458"
    if "bitirme" in name or "proje" in name:
        return "PRJ", "Proje", "#3A1235"
    if "işyeri" in name or "kariyer" in name:
        return "CV", "Kariyer", "#283A12"
    if "işletim" in name or "açık kaynak" in name:
        return "OS", "Sistem", "#12323A"
    short = code[:4].upper() if code else "DERS"
    return short, "Kurs", "#132844"


def sorted_courses_for_display(courses):
    def key(k):
        is_platform = 0 if str(k.get("kurs_id", "")).startswith("KURS_") else 1
        return (is_platform, str(k.get("seviye", "")), str(k.get("ders_kodu", k.get("kurs_adi", ""))))
    return sorted(courses, key=key)


class HoverGlow:
    """Boyut değiştirmeyen, sadece parlama veren güvenli hover efekti."""
    def __init__(self, widget, normal, glow, border_normal=None, border_glow=None):
        self.widget = widget
        self.normal = normal
        self.glow = glow
        self.border_normal = border_normal
        self.border_glow = border_glow
        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)

    def on_enter(self, _=None):
        try:
            self.widget.configure(fg_color=self.glow)
            if self.border_glow:
                self.widget.configure(border_color=self.border_glow, border_width=2)
        except Exception:
            pass

    def on_leave(self, _=None):
        try:
            self.widget.configure(fg_color=self.normal)
            if self.border_normal:
                self.widget.configure(border_color=self.border_normal, border_width=1)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# GİRİŞ EKRANI
# ─────────────────────────────────────────────────────────────────────────────
class LoginScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG)
        self.master = master
        self.build()

    def build(self):
        clear(self)
        try:
            self.login_logo_img = tk.PhotoImage(file=str(LOGO_PNG)).subsample(8, 8)
            tk.Label(self, image=self.login_logo_img, bg=BG, bd=0, highlightthickness=0).place(relx=0.5, y=28, anchor="center")
        except Exception as e:
            print("Giriş logosu yüklenemedi:", e)
        lbl(self, "Hextech Akademi", 24, "bold").place(relx=0.5, y=62, anchor="center")
        lbl(self, "Geleceğini Şekillendir", 14, "normal", MUTED).place(relx=0.5, y=92, anchor="center")
        lbl(self, "Yapımcı: E.Hira YAĞMUR", 12, "bold", GREEN).place(relx=0.5, rely=0.94, anchor="center")

        panel = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=26, width=500, height=390)
        panel.place(relx=0.5, rely=0.52, anchor="center")
        panel.pack_propagate(False)

        lbl(panel, "Sisteme Giriş Yapın", 20, "bold", "#0B172A").pack(pady=(40, 24))
        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack()

        roles = [
            ("Öğrenci\nGirişi", "ogrenci", BLUE, "#16B7F5", "O"),
            ("Öğretmen\nGirişi", "egitmen", "#8658F5", "#9B72FF", "E"),
            ("Admin\nGirişi", "admin", "#653BD7", "#7E52F0", "A"),
        ]
        for title, role, color, glow, icon in roles:
            k = ctk.CTkFrame(row, fg_color=color, corner_radius=16, width=126, height=134, border_width=1, border_color="#FFFFFF")
            k.pack(side="left", padx=9)
            k.pack_propagate(False)
            lbl(k, icon, 30, "bold", "white").pack(pady=(22, 8))
            lbl(k, title, 12, "bold", "white", justify="center").pack()
            HoverGlow(k, color, glow, "#FFFFFF", "#BDEBFF")
            k.bind("<Button-1>", lambda e, r=role: LoginDialog(self.master, r, self.master.show_panel))
            for child in k.winfo_children():
                child.bind("<Button-1>", lambda e, r=role: LoginDialog(self.master, r, self.master.show_panel))

        lbl(panel, "Henüz üye değil misiniz?", 11, "normal", "#667085").pack(pady=(30, 8))
        btn(panel, "Öğrenci Olarak Kaydol", lambda: StudentRegisterDialog(self.master), GREEN, GREEN_2, 280, 44).pack()
        link = lbl(panel, "Öğretmen/Admin Hesap Başvurusu", 11, "normal", GREEN)
        link.pack(pady=(14, 0))
        link.bind("<Button-1>", lambda e: ApplicationDialog(self.master))

        try:
            remember = db.veri_yukle().get("sistem_ayarlari", {}).get("beni_hatirla")
            if remember:
                rid = remember.get("id", "")
                rr = remember.get("rol", "")
                last = ctk.CTkFrame(panel, fg_color="#DCFCE7", corner_radius=12, height=42)
                last.pack(fill="x", padx=62, pady=(18, 0))
                last.pack_propagate(False)
                lbl(last, f"Son giriş: {rid} ({rr})", 10, "bold", "#047857").pack(side="left", padx=12)
        except Exception:
            pass


class LoginDialog(ctk.CTkToplevel):
    def __init__(self, master, role, callback):
        super().__init__(master)
        self.role = role
        self.callback = callback
        self.title("Giriş Yap")
        self.geometry("390x540")
        self.configure(fg_color=BG)
        self.grab_set()
        self.resizable(False, False)
        role_names = {"ogrenci":"Öğrenci", "egitmen":"Öğretmen", "admin":"Admin"}
        lbl(self, f"{role_names.get(role, role)} Girişi", 24, "bold").pack(pady=(34, 8))
        lbl(self, "Kullanıcı ID ve şifrenizi girin", 12, "normal", MUTED).pack(pady=(0, 22))
        self.e_user = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=280, height=44, corner_radius=12, fg_color=BG_3, border_color=BORDER)
        self.e_user.pack(pady=7)
        self.e_pass = ctk.CTkEntry(self, placeholder_text="Şifre", show="●", width=280, height=44, corner_radius=12, fg_color=BG_3, border_color=BORDER)
        self.e_pass.pack(pady=7)
        self.remember = ctk.CTkCheckBox(self, text="Beni hatırla", fg_color=GREEN, hover_color=GREEN_2)
        self.remember.pack(pady=(8, 4))
        self.e_pass.bind("<Return>", lambda e: self.try_login())
        btn(self, "Giriş Yap", self.try_login, GREEN, GREEN_2, 280, 44).pack(pady=(18, 8))
        self.render_remembered_accounts()

    def render_remembered_accounts(self):
        accounts = remembered_accounts(self.role)
        if not accounts:
            return
        box = ctk.CTkFrame(self, fg_color=BG_2, corner_radius=14, border_width=1, border_color=BORDER)
        box.pack(fill="x", padx=54, pady=(6, 0))
        lbl(box, "Hatırlanan hesaplar", 11, "bold", GREEN).pack(anchor="w", padx=12, pady=(8, 2))
        for acc in accounts[-4:][::-1]:
            text = f"{acc.get('ad', acc.get('id'))}  •  {acc.get('id')}"
            b = ctk.CTkButton(
                box, text=text, fg_color="transparent", hover_color=BG_3,
                text_color=TEXT, anchor="w", height=28, corner_radius=8,
                command=lambda uid=acc.get("id"), role=acc.get("rol"): self.direct_login(uid, role)
            )
            b.pack(fill="x", padx=8, pady=2)
        lbl(box, "Tıklayınca şifre sormadan giriş yapar.", 9, "normal", MUTED).pack(anchor="w", padx=12, pady=(2, 8))

    def direct_login(self, uid, role):
        user = load_remembered_user(uid, role)
        if not user:
            messagebox.showwarning("Hesap bulunamadı", "Hatırlanan hesap artık geçerli değil.")
            return
        try:
            self.destroy()
        except Exception:
            pass
        self.callback(user)

    def try_login(self):
        uid = self.e_user.get().strip()
        pw = self.e_pass.get().strip()
        ok, user = db.kullanici_dogrula(uid, pw, self.role)
        if not ok:
            messagebox.showerror("Giriş başarısız", "Kullanıcı ID, şifre veya onay durumu hatalı.")
            return
        try:
            if self.remember.get():
                remember_login_account(user, self.role)
        except Exception:
            pass
        self.destroy()
        self.callback(user)


class StudentRegisterDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Öğrenci Kaydı")
        self.geometry("420x470")
        self.configure(fg_color=BG)
        self.grab_set()
        lbl(self, "Yeni Öğrenci Kaydı", 22, "bold").pack(pady=(30, 14))
        self.entries = []
        for ph in ["Öğrenci ID", "Ad Soyad", "E-posta", "Şifre"]:
            e = ctk.CTkEntry(self, placeholder_text=ph, width=300, height=42, fg_color=BG_3, border_color=BORDER)
            if ph == "Şifre":
                e.configure(show="●")
            e.pack(pady=6)
            self.entries.append(e)
        btn(self, "Kaydı Tamamla", self.save, GREEN, GREEN_2, 300, 44).pack(pady=22)

    def save(self):
        vals = [e.get().strip() for e in self.entries]
        if not all(vals):
            messagebox.showwarning("Eksik bilgi", "Tüm alanları doldurun.")
            return
        ok, msg = db.ogrenci_ekle(vals[0], vals[1], vals[2], vals[3])
        messagebox.showinfo("Bilgi", msg)
        if ok:
            self.destroy()


class ApplicationDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Öğretmen/Admin Başvurusu")
        self.geometry("460x560")
        self.configure(fg_color=BG)
        self.grab_set()
        lbl(self, "Hesap Başvurusu", 22, "bold").pack(pady=(28, 10))
        self.role = ctk.StringVar(value="Öğretmen")
        ctk.CTkSegmentedButton(self, values=["Öğretmen", "Admin"], variable=self.role, fg_color=BG_3, selected_color=GREEN, selected_hover_color=GREEN_2).pack(pady=10)
        self.id_entry = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=310, height=42, fg_color=BG_3, border_color=BORDER)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Ad Soyad", width=310, height=42, fg_color=BG_3, border_color=BORDER)
        self.email_entry = ctk.CTkEntry(self, placeholder_text="E-posta", width=310, height=42, fg_color=BG_3, border_color=BORDER)
        self.spec_entry = ctk.CTkEntry(self, placeholder_text="Uzmanlık / Açıklama", width=310, height=42, fg_color=BG_3, border_color=BORDER)
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Şifre", show="●", width=310, height=42, fg_color=BG_3, border_color=BORDER)
        for e in [self.id_entry, self.name_entry, self.email_entry, self.spec_entry, self.pass_entry]:
            e.pack(pady=6)
        btn(self, "Başvuru Gönder", self.send, GREEN, GREEN_2, 310, 44).pack(pady=22)
        lbl(self, "Başvuru maili ayarlar doğruysa ana e-postana gider.", 10, "normal", MUTED, wraplength=310).pack()

    def send(self):
        rid = self.id_entry.get().strip(); name = self.name_entry.get().strip()
        email = self.email_entry.get().strip(); spec = self.spec_entry.get().strip(); pw = self.pass_entry.get().strip()
        if not all([rid, name, email, pw]):
            messagebox.showwarning("Eksik bilgi", "ID, ad, e-posta ve şifre zorunludur.")
            return
        if self.role.get() == "Öğretmen":
            ok, msg = db.egitmen_ekle(rid, name, spec or "Belirtilmedi", email, pw)
        else:
            ok, msg = db.admin_basvuru_ekle(rid, name, email, pw, spec or "Admin yetkisi başvurusu")
        messagebox.showinfo("Bilgi", msg)
        if ok:
            self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# PANEL TABANI - TEK SIDEBAR, TEMİZ ANİMASYON
# ─────────────────────────────────────────────────────────────────────────────
class BasePanel(ctk.CTkFrame):
    def __init__(self, master, user, accent=GREEN):
        super().__init__(master, fg_color=BG)
        self.master = master
        self.user = user
        self.accent = accent
        self.sidebar_open = True
        self.sidebar_width = SIDEBAR_OPEN_W
        self.animating = False
        self.after_id = None
        self.menu_items = []
        self.pages = []
        self.active_idx = 0
        self.category_open = {"Genel": True, "Dersler": True, "Akademik": True, "İletişim": True, "Kişisel": True, "Yönetim": True}
        self.profile_dropdown = None
        self.theme_colors = [GREEN, BLUE, PURPLE, ORANGE]
        self.theme_index = 0

        # Sidebar artık animasyonlu değil: tıklanınca anında açılır/kapanır.
        # CustomTkinter'da place(width=...) ve canlı genişlik animasyonu ghosting/hata yapabildiği için
        # en stabil çözüm olarak pack + configure(width=...) kullanıyoruz.
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_2, width=self.sidebar_width, corner_radius=0, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main = ctk.CTkFrame(self, fg_color=BG)
        self.main.pack(side="left", fill="both", expand=True, padx=(18, 0))
        self.render_sidebar()
        btn(self, "Asistan", lambda: AssistantDialog(self.master, self.user), GREEN, GREEN_2, 118, 36).place(relx=0.985, rely=0.965, anchor="se")

    def sidebar_category_for(self, title):
        if title in ["Panel", "Yapılacaklar", "Takvim"]:
            return "Genel"
        if title in ["Derslerim", "Ders Kaydı", "Materyaller", "Not/Belge"]:
            return "Dersler"
        if title in ["Ödevler", "Sınavlar", "Yorumlar", "Yoklama", "Not Girişi", "Risk Analizi"]:
            return "Akademik"
        if title in ["Forum", "Mesajlar", "Destek", "Duyuru"]:
            return "İletişim"
        if title in ["Favoriler", "Hedef/Rozet", "Proje Plus", "Yardım"]:
            return "Kişisel"
        return "Yönetim"

    def add_menus(self, menus):
        for title, icon, func in menus:
            idx = len(self.pages)
            page = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
            self.pages.append((page, func))
            self.menu_items.append({"idx": idx, "title": title, "icon": icon, "func": func, "cat": self.sidebar_category_for(title)})
        self.render_sidebar()
        self.select_page(0)

    def safe_cancel_anim(self):
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def toggle_sidebar(self):
        # Animasyon yok: iz/ghosting olmasın diye sidebar anında yeniden çizilir.
        self.safe_cancel_anim()
        self.animating = False
        self.sidebar_open = not self.sidebar_open
        self.sidebar_width = SIDEBAR_OPEN_W if self.sidebar_open else RAIL_W
        clear(self.sidebar)
        self.sidebar.configure(width=self.sidebar_width, fg_color=BG_2)
        self.render_sidebar()
        try:
            self.update_idletasks()
        except Exception:
            pass

    def ease(self, t):
        return t

    def animate_sidebar(self, start, target, opening, frame):
        # Eski animasyon kaldırıldı. Geriye dönük çağrı olursa güvenli şekilde tek adımda uygula.
        self.safe_cancel_anim()
        self.animating = False
        self.sidebar_open = opening
        self.sidebar_width = target
        clear(self.sidebar)
        self.sidebar.configure(width=target, fg_color=BG_2)
        self.render_sidebar()

    def render_sidebar(self):
        clear(self.sidebar)
        if self.sidebar_open:
            self.render_sidebar_open()
        else:
            self.render_sidebar_closed()

    def render_sidebar_closed(self):
        try:
            self.sidebar_logo_img = tk.PhotoImage(file=str(LOGO_PNG)).subsample(8, 8)
            tk.Label(self.sidebar, image=self.sidebar_logo_img, bg=BG_2, bd=0, highlightthickness=0).pack(pady=(18, 6))
        except Exception as e:
            print("Sidebar logosu yüklenemedi:", e)
            ctk.CTkFrame(self.sidebar, width=50, height=50, corner_radius=25, fg_color=self.accent).pack(pady=(24, 8))
        lbl(self.sidebar, "", 12, "bold").pack(pady=(0, 8))
        btn(self.sidebar, "☰", self.toggle_sidebar, BG_3, BG_3, 48, 34).pack(padx=14, pady=(0, 10))
        scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", width=70)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        for item in self.menu_items:
            active = item["idx"] == self.active_idx
            b = ctk.CTkButton(
                scroll, text=item["icon"], width=46, height=34, corner_radius=11,
                fg_color=BG_3 if active else "transparent", hover_color=BG_3,
                text_color=self.accent if active else TEXT, font=(FONT, 12, "bold"),
                command=lambda i=item["idx"]: self.select_page(i)
            )
            b.pack(padx=14, pady=4)

    def render_sidebar_open(self):
        top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(16, 10))
        try:
            self.sidebar_open_logo_img = tk.PhotoImage(file=str(LOGO_PNG)).subsample(12, 12)
            tk.Label(top, image=self.sidebar_open_logo_img, bg=BG_2, bd=0, highlightthickness=0).pack(side="left", padx=(0, 8))
        except Exception as e:
            print("Menü logosu yüklenemedi:", e)
        lbl(top, "Menü", 18, "bold").pack(side="left")
        btn(top, "×", self.toggle_sidebar, BG_3, BG_3, 40, 32).pack(side="right")
        # Kullanıcı adı/rol satırı kaldırıldı; menü daha sade dursun.
        scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", width=SIDEBAR_OPEN_W-18)
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        cats = ["Genel", "Dersler", "Akademik", "İletişim", "Kişisel", "Yönetim"]
        for cat in cats:
            items = [m for m in self.menu_items if m["cat"] == cat]
            if not items:
                continue
            head_text = f"{cat} {'▼' if self.category_open.get(cat, True) else '▶'}"
            head = ctk.CTkButton(scroll, text=head_text, height=28, corner_radius=9, fg_color="transparent", hover_color=BG_3, text_color=self.accent, anchor="w", font=(FONT, 11, "bold"), command=lambda c=cat: self.toggle_category(c))
            head.pack(fill="x", padx=8, pady=(8, 2))
            if not self.category_open.get(cat, True):
                continue
            for item in items:
                active = item["idx"] == self.active_idx
                b = ctk.CTkButton(
                    scroll, text=f"   {item['title']}", height=34, corner_radius=10,
                    fg_color=BG_3 if active else "transparent", hover_color=BG_3,
                    text_color=self.accent if active else TEXT, anchor="w", font=(FONT, 11),
                    command=lambda i=item["idx"]: self.select_page(i)
                )
                b.pack(fill="x", padx=8, pady=2)

    def toggle_category(self, cat):
        self.category_open[cat] = not self.category_open.get(cat, True)
        if self.sidebar_open:
            self.render_sidebar()

    def select_page(self, idx):
        self.active_idx = idx
        for i, (page, func) in enumerate(self.pages):
            if i == idx:
                page.pack(fill="both", expand=True, padx=0, pady=0)
                clear(page)
                func(page)
            else:
                page.pack_forget()
        if not self.animating:
            self.render_sidebar()

    def close_profile_dropdown(self):
        if self.profile_dropdown is not None:
            try:
                self.profile_dropdown.destroy()
            except Exception:
                pass
            self.profile_dropdown = None

    def toggle_profile_dropdown(self):
        # Ayrı pencere açma: profil menüsü sağ üst butonun hemen altında panel içinde açılır.
        if self.profile_dropdown is not None and self.profile_dropdown.winfo_exists():
            self.close_profile_dropdown()
            return
        self.profile_dropdown = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER,
            width=260,
            height=300,
        )
        self.profile_dropdown.place(relx=1.0, y=64, x=-24, anchor="ne")
        self.profile_dropdown.pack_propagate(False)
        lbl(self.profile_dropdown, self.user.get("ad", "Kullanıcı"), 17, "bold").pack(pady=(18, 2))
        lbl(self.profile_dropdown, self.user.get("rol", "").capitalize(), 11, "normal", MUTED).pack(pady=(0, 12))
        btn(self.profile_dropdown, "Şifre Değiştir", lambda: toast(self.master, "Şifre değiştirme ekranı hazır."), BG_3, BG_3, 210, 34).pack(pady=4)
        btn(self.profile_dropdown, "Tema Değiştir", self.change_theme, BG_3, BG_3, 210, 34).pack(pady=4)
        btn(self.profile_dropdown, "Takvim", lambda: CalendarDialog(self.master), BG_3, BG_3, 210, 34).pack(pady=4)
        btn(self.profile_dropdown, "Çıkış Yap", self.logout_from_dropdown, RED, RED, 210, 36).pack(pady=(14, 0))
        self.profile_dropdown.lift()

    def change_theme(self):
        # Gece/Beyaz tema arasında gerçek geçiş yapar; panel yeniden çizilir.
        self.close_profile_dropdown()
        current = getattr(self.master, "theme_light", False)
        self.master.theme_light = not current
        apply_theme(self.master.theme_light)
        try:
            self.master.configure(fg_color=BG)
        except Exception:
            pass
        self.master.show_panel(self.user)
        toast(self.master, "Beyaz tema açıldı." if self.master.theme_light else "Gece teması açıldı.", GREEN)

    def logout_from_dropdown(self):
        self.close_profile_dropdown()
        self.master.show_login()

    def header(self, parent, title, subtitle=""):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(28, 18))
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        lbl(left, title, 25, "bold").pack(anchor="w")
        if subtitle:
            lbl(left, subtitle, 12, "normal", MUTED).pack(anchor="w", pady=(3, 0))
        actions = ctk.CTkFrame(top, fg_color="transparent")
        actions.pack(side="right")
        btn(actions, "Takvim", lambda: CalendarDialog(self.master), BLUE_2, BLUE, 96, 36).pack(side="left", padx=5)
        btn(actions, f"{self.user.get('ad','')[:14]} ▾", self.toggle_profile_dropdown, self.accent, self.accent, 150, 36).pack(side="left", padx=5)

    def refresh(self):
        self.select_page(self.active_idx)

    def generic_page(self, parent, title, desc):
        self.header(parent, title, desc)
        c = card(parent, fill="x", padx=8, pady=8)
        lbl(c, desc, 13, "normal", MUTED, wraplength=720, justify="left").pack(anchor="w", padx=18, pady=18)


    def full_scroll_container(self, parent, padx=8, pady=8):
        """Sayfanın altına kadar uzayan sabit yükseklikli dış panel.

        Önemli not: Bu uygulamada sayfalar CTkScrollableFrame içinde açılıyor.
        CTkScrollableFrame'in iç frame'i, pack(expand=True) verilen çocukları
        pencere yüksekliğine kadar büyütmez; sadece içeriğin istediği yükseklik
        kadar oluşturur. Önceki sürümlerde kartların sadece üstte kalmasının
        nedeni buydu. Bu yüzden burada görünür pencere yüksekliğine göre gerçek
        bir `height` hesaplayıp dış karta veriyoruz ve pack_propagate(False)
        kullanıyoruz. Böylece içerik az olsa bile kart kırmızıyla işaretlenen
        alan gibi aşağıya kadar devam eder; içerik çoksa iç scroll çalışır.
        """
        try:
            self.master.update_idletasks()
            parent.update_idletasks()
        except Exception:
            pass

        # Page parent bir CTkScrollableFrame olduğu için kendi yüksekliği bazen
        # 1-10 px dönebilir. Bu durumda ana pencere yüksekliğini baz alıyoruz.
        try:
            ph = int(parent.winfo_height())
        except Exception:
            ph = 0
        try:
            mh = int(self.master.winfo_height())
        except Exception:
            mh = 820

        # Header + üst boşluklar çıktıktan sonra kalan alan. Minimum değer,
        # küçük pencerelerde bile panelin kısa görünmesini engeller.
        h = max(560, (ph if ph > 260 else mh) - 175)

        outer = ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
            height=h,
        )
        outer.pack(fill="x", padx=padx, pady=pady)
        outer.pack_propagate(False)

        wrap = ctk.CTkScrollableFrame(
            outer,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
            height=max(420, h - 26),
        )
        wrap.pack(fill="both", expand=True, padx=10, pady=10)
        return outer, wrap

    def course_card(self, parent, kurs, registered=False):
        c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, width=250, height=292)
        c.pack(side="left", padx=8, pady=8)
        c.pack_propagate(False)
        badge, badge_sub, badge_bg = course_badge(kurs)
        top = ctk.CTkFrame(c, fg_color=badge_bg, height=86, corner_radius=12, border_width=1, border_color=BORDER)
        top.pack(fill="x", padx=10, pady=(10, 8)); top.pack_propagate(False)
        lbl(top, badge, 23, "bold", self.accent).place(relx=0.5, rely=0.40, anchor="center")
        lbl(top, badge_sub, 10, "bold", MUTED).place(relx=0.5, rely=0.72, anchor="center")
        ders_kodu = kurs.get("ders_kodu") or kurs.get("kurs_id", "")
        baslik = kurs.get("kurs_adi", "Kurs")
        if ders_kodu and ders_kodu not in baslik:
            baslik = f"{ders_kodu} {baslik}"
        lbl(c, baslik[:42], 12, "bold", TEXT, wraplength=215, justify="left").pack(anchor="w", padx=12)
        lbl(c, f"Öğretmen: {egitmen_adi(kurs.get('egitmen_id'))}", 10, "normal", MUTED).pack(anchor="w", padx=12, pady=(5,0))
        ekstra = f"{kurs.get('seviye','')} • AKTS {kurs.get('akts','-')}" if kurs.get('akts') is not None else kurs.get('seviye','Başlangıç')
        lbl(c, f"{kurs.get('kategori','Genel')} • {ekstra}", 10, "normal", MUTED, wraplength=215, justify="left").pack(anchor="w", padx=12, pady=(4,0))
        sayi = len(kurs.get("kayitli_ogrenciler", [])); kont = kurs.get("kontenjan", 0)
        lbl(c, f"Kontenjan: {sayi}/{kont}", 10, "normal", MUTED).pack(anchor="w", padx=12, pady=(4,8))
        bar = ctk.CTkProgressBar(c, height=7, fg_color="#D7DEE8", progress_color=self.accent)
        bar.pack(fill="x", padx=12, pady=(0,10))
        try:
            bar.set(min(sayi / max(1, int(kont)), 1))
        except Exception:
            bar.set(0)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 10))
        btn(row, "Detay", lambda k=kurs.get("kurs_id"): CourseRoomDialog(self.master, self.user, k), BLUE, BLUE_2, 72, 32).pack(side="left", padx=2)
        label = "Derse Git" if registered else "Kayıt Ol"
        btn(row, label, lambda k=kurs.get("kurs_id"), r=registered: self.course_action(k, r), GREEN, GREEN_2, 92, 32).pack(side="left", padx=2)

    def course_action(self, kid, registered=False):
        if registered:
            CourseRoomDialog(self.master, self.user, kid)
            return
        ok, msg = db.kursa_kayit(user_id(self.user), kid)
        toast(self.master, msg, GREEN if ok else RED)
        self.refresh()


# ─────────────────────────────────────────────────────────────────────────────
# ÖĞRENCİ PANELİ
# ─────────────────────────────────────────────────────────────────────────────
class OgrenciPanel(BasePanel):
    def __init__(self, master, user):
        super().__init__(master, user, GREEN)
        self.add_menus([
            ("Panel", "P", self.dashboard),
            ("Derslerim", "D", self.my_courses),
            ("Ders Kaydı", "+", self.course_register),
            ("Materyaller", "M", self.materials_page),
            ("Not/Belge", "N", self.grades_page),
            ("Ödevler", "Ö", self.assignments_page),
            ("Sınavlar", "S", self.exams_page),
            ("Yorumlar", "★", self.yorumlar_page),
            ("Yoklama", "✓", self.attendance_page),
            ("Forum", "F", self.forum_page),
            ("Mesajlar", "M", lambda f: self.generic_page(f, "Mesajlar", "Öğretmenlerle mesajlaşma ekranı.")),
            ("Destek", "?", self.support_page),
            ("Hedef/Rozet", "R", self.badges_page),
            ("Yardım", "i", self.help_page),
        ])

    def dashboard(self, f):
        self.header(f, f"Hoş Geldin, {self.user.get('ad','Öğrenci')}!", "Derslerini takip et, ödevlerini teslim et, sınavlarını ve belgelerini yönet.")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=(0,14))
        my = db.ogrenci_kurslarini_getir(user_id(self.user))
        stats = [("Kayıtlı Ders", len(my)), ("Ortalama", self.avg_grade()), ("Sertifika", len(getattr(db, 'belgeleri_getir', lambda x: [])(user_id(self.user)))), ("Devamsızlık", getattr(db, 'devamsizlik_sayisi', lambda x: 0)(user_id(self.user)))]
        for name, val in stats:
            s = ctk.CTkFrame(row, fg_color=CARD, corner_radius=15, height=90, border_width=1, border_color=BORDER)
            s.pack(side="left", fill="x", expand=True, padx=6); s.pack_propagate(False)
            lbl(s, str(val), 20, "bold", self.accent).place(relx=0.9, y=18, anchor="e")
            lbl(s, name, 13, "bold").place(x=16, y=50)
        info = ctk.CTkFrame(f, fg_color="transparent")
        info.pack(fill="x", padx=8, pady=(0,12))
        today_card = card(info, fill="both", expand=True, pady=4)
        today_card.pack(side="left", fill="both", expand=True, padx=(0,6))
        lbl(today_card, "Bugün Ne Var?", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12,4))
        evs = TakvimWidget(today_card)._events_for_day(date.today())
        if evs:
            for ev in evs[:4]:
                lbl(today_card, f"• {ev[0]} - {ev[1][:70]}", 11, "normal", MUTED, wraplength=520).pack(anchor="w", padx=16, pady=2)
        else:
            lbl(today_card, "Bugün için kayıtlı ders/sınav/ödev görünmüyor.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(2,12))
        next_card = card(info, fill="both", expand=True, pady=4)
        next_card.pack(side="left", fill="both", expand=True, padx=(6,0))
        lbl(next_card, "Sıradaki Ders", 15, "bold", BLUE).pack(anchor="w", padx=16, pady=(12,4))
        nxt = self.next_lesson_summary()
        lbl(next_card, nxt, 11, "normal", MUTED, wraplength=520).pack(anchor="w", padx=16, pady=(2,12))
        lbl(f, "Derslerim", 17, "bold").pack(anchor="w", padx=12, pady=(4, 8))
        area = ctk.CTkFrame(f, fg_color="transparent")
        area.pack(fill="x")
        self.render_courses(area, only_mine=True)

    def next_lesson_summary(self):
        my = set(db.ogrenci_kurslarini_getir(user_id(self.user)))
        for k in get_courses():
            if k.get("kurs_id") in my:
                gunler = ", ".join(k.get("takvim_gunler", [])) or "Gün belirtilmedi"
                return f"{k.get('kurs_adi')} • {gunler} • {k.get('takvim_saat','Saat yok')}"
        return "Henüz kayıtlı ders yok. Ders Kaydı ekranından kurs seçebilirsin."

    def avg_grade(self):
        try:
            vals = [float(x.get("not", 0)) for x in db.ogrenci_notlarini_getir(user_id(self.user)).values()]
            return round(sum(vals)/len(vals), 1) if vals else 0
        except Exception:
            return 0

    def render_courses(self, area, only_mine=False):
        my = set(db.ogrenci_kurslarini_getir(user_id(self.user)))
        count = 0
        row = None
        courses = sorted_courses_for_display(get_courses())
        # Ders kaydı ekranında artık Bilgisayar Programcılığı dersleri öne çıkar; eski kurslar varsa en sona düşer.
        for k in courses:
            reg = k.get("kurs_id") in my
            if only_mine and not reg:
                continue
            if count % 4 == 0:
                row = ctk.CTkFrame(area, fg_color="transparent")
                row.pack(fill="x", padx=0, pady=0)
            self.course_card(row, k, registered=reg)
            count += 1
        if count == 0:
            lbl(area, "Liste boş.", 14, "normal", MUTED).pack(pady=40)

    def my_courses(self, f):
        self.header(f, "Derslerim", "Kayıtlı olduğun dersler.")
        area = ctk.CTkFrame(f, fg_color="transparent")
        area.pack(fill="x")
        self.render_courses(area, only_mine=True)

    def course_register(self, f):
        self.header(f, "Ders Kaydı", "Bilgisayar Programcılığı derslerini incele, filtrele ve kayıt ol.")
        area = ctk.CTkFrame(f, fg_color="transparent")
        area.pack(fill="x")
        self.render_courses(area, only_mine=False)

    def grades_page(self, f):
        self.header(f, "Notlar ve Belgeler", "Notlarını, sertifikalarını ve belgelerini buradan takip edebilirsin.")
        try:
            notes = db.ogrenci_notlarini_getir(user_id(self.user))
        except Exception:
            notes = {}
        if not notes:
            lbl(f, "Henüz not kaydı yok.", 13, "normal", MUTED).pack(pady=30)
        courses = {k.get("kurs_id"): k for k in get_courses()}
        for kid, n in notes.items():
            c = card(f, fill="x", padx=8, pady=6)
            cname = courses.get(kid, {}).get("kurs_adi", kid)
            val = n.get("not", n) if isinstance(n, dict) else n
            extra = ""
            if isinstance(n, dict):
                extra = f"  •  Harf: {n.get('harf','-')}  •  Vize: {n.get('vize','-')}  •  Final: {n.get('final','-')}"
            lbl(c, f"{cname}: {val}{extra}", 13, "bold", wraplength=900, justify="left").pack(anchor="w", padx=16, pady=12)

    def yorumlar_page(self, f):
        self.header(f, "Yorumlar", "Yazdığın yorumları ve kayıtlı olduğun derslerdeki son yorumları buradan takip edebilirsin.")
        uid = user_id(self.user)
        try:
            all_comments = db.yorumlari_getir()
        except Exception:
            all_comments = []
        my_courses = set(db.ogrenci_kurslarini_getir(uid))
        courses = {k.get("kurs_id"): k for k in get_courses()}
        my_comments = [y for y in all_comments if y.get("ogrenci_id") == uid]
        course_comments = [y for y in all_comments if y.get("kurs_id") in my_courses]

        # Tüm alanı kaplayan kart: boş kalan yerde arka plan kesilmesin.
        outer, wrap = self.full_scroll_container(f)

        c1 = ctk.CTkFrame(wrap, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
        c1.pack(fill="x", padx=10, pady=(10, 10))
        lbl(c1, "Benim Yorumlarım", 16, "bold", GREEN).pack(anchor="w", padx=16, pady=(14, 6))
        if not my_comments:
            lbl(c1, "Henüz yorum bırakmadın. Bir dersin içindeki Yorum Bırak alanından yorum gönderebilirsin.", 12, "normal", MUTED, wraplength=880).pack(anchor="w", padx=16, pady=(0, 14))
        for y in reversed(my_comments[-20:]):
            k = courses.get(y.get("kurs_id"), {})
            line = f"★ {y.get('puan', '-')}  •  {k.get('kurs_adi', y.get('kurs_id'))}"
            lbl(c1, line, 12, "bold").pack(anchor="w", padx=16, pady=(6, 0))
            lbl(c1, y.get("yorum", ""), 12, "normal", MUTED, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(0, 6))

        c2 = ctk.CTkFrame(wrap, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
        c2.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        lbl(c2, "Kayıtlı Derslerdeki Son Yorumlar", 16, "bold", BLUE).pack(anchor="w", padx=16, pady=(14, 6))
        if not course_comments:
            lbl(c2, "Kayıtlı olduğun derslerde henüz yorum yok.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 14))
        for y in reversed(course_comments[-80:]):
            k = courses.get(y.get("kurs_id"), {})
            ad = ogrenci_adi(y.get("ogrenci_id"))
            lbl(c2, f"{ad} • {k.get('kurs_adi', y.get('kurs_id'))} • ★ {y.get('puan', '-')}", 12, "bold").pack(anchor="w", padx=16, pady=(6, 0))
            lbl(c2, y.get("yorum", ""), 12, "normal", MUTED, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(0, 6))

        # Scroll alanının sayfa sonuna kadar devam ettiği net görünsün.
        ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")

    def calendar_page(self, f):
        self.header(f, "Takvim", "Ders, sınav ve etkinliklerini gör.")
        TakvimWidget(f).pack(fill="both", expand=True, padx=8, pady=8)

    def materials_page(self, f):
        self.header(f, "Materyaller", "Kayıtlı olduğun derslerin materyallerini buradan açabilirsin.")
        uid = user_id(self.user)
        my = set(db.ogrenci_kurslarini_getir(uid))
        courses = [k for k in get_courses() if k.get("kurs_id") in my]

        outer, wrap = self.full_scroll_container(f)

        if not courses:
            lbl(wrap, "Henüz kayıtlı dersin yok. Ders Kaydı ekranından derse kayıt olunca materyaller burada görünür.", 13, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=18)
            ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")
            return

        for k in courses:
            c = ctk.CTkFrame(wrap, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
            c.pack(fill="x", padx=10, pady=8)
            lbl(c, k.get("kurs_adi", "Ders"), 15, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(14, 6))
            mats = k.get("materyaller", [])
            if not mats:
                lbl(c, "Bu derse henüz materyal eklenmemiş.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 14))
            for m in mats:
                row = ctk.CTkFrame(c, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=4)
                lbl(row, f"• {m.get('baslik','Materyal')}  ({m.get('tur','Link')})", 12, "normal", TEXT, wraplength=760).pack(side="left", anchor="w", fill="x", expand=True)
                btn(row, "Aç", lambda link=str(m.get("link", "")): open_material_link(link), BLUE, BLUE_2, 62, 28).pack(side="right")
            ctk.CTkFrame(c, fg_color="transparent", height=6).pack(fill="x")

        ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")

    def assignments_page(self, f):
        self.header(f, "Ödevler", "Ödevlerini görüntüleyip teslim durumunu takip edebilirsin.")
        uid = user_id(self.user)
        try:
            rows = db.odevleri_getir(ogrenci_id=uid)
        except Exception:
            rows = db.veri_yukle().get("odevler", [])
        my_courses = set(db.ogrenci_kurslarini_getir(uid))
        rows = [o for o in rows if o.get("kurs_id") in my_courses]
        courses = {k.get("kurs_id"): k for k in get_courses()}
        teslimler = {t.get("odev_id"): t for t in db.veri_yukle().get("teslimler", []) if t.get("ogrenci_id") == uid}
        outer, wrap = self.full_scroll_container(f)
        if not rows:
            lbl(wrap, "Kayıtlı derslerin için henüz ödev bulunmuyor.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=18)
        for o in rows:
            c = card(wrap, fill="x", pady=7)
            cname = courses.get(o.get("kurs_id"), {}).get("kurs_adi", o.get("kurs_id"))
            status = teslimler.get(o.get("odev_id"), {}).get("durum", "Teslim edilmedi")
            lbl(c, f"{o.get('baslik')}  •  {status}", 15, "bold", GREEN if status != "Teslim edilmedi" else YELLOW, wraplength=900).pack(anchor="w", padx=16, pady=(12,3))
            lbl(c, f"Ders: {cname}  •  Son tarih: {o.get('son_tarih','-')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
            lbl(c, o.get("aciklama", ""), 12, "normal", TEXT, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(2,8))
            entry = ctk.CTkEntry(c, placeholder_text="Teslim notu veya dosya/link açıklaması yaz...", fg_color=BG_3, border_color=BORDER)
            entry.pack(fill="x", padx=16, pady=(0,8))
            btn(c, "Teslim Et", lambda oid=o.get("odev_id"), e=entry: self.submit_assignment(oid, e), GREEN, GREEN_2, 110, 30).pack(anchor="w", padx=16, pady=(0,12))

    def submit_assignment(self, oid, entry):
        txt = entry.get().strip() or "Teslim edildi."
        try:
            ok, msg = db.odev_teslim_et(oid, user_id(self.user), txt)
        except Exception as e:
            ok, msg = False, str(e)
        toast(self.master, msg if isinstance(msg, str) else ("Teslim edildi" if ok else "Teslim edilemedi"), GREEN if ok else RED)
        self.refresh()

    def exams_page(self, f):
        self.header(f, "Sınavlar", "Sınav tarihlerini, kalan günleri ve çalışma kaynaklarını burada görebilirsin.")
        uid = user_id(self.user)
        my_courses = set(db.ogrenci_kurslarini_getir(uid))
        try:
            exams = db.sinavlari_getir(ogrenci_id=uid)
        except Exception:
            exams = [s for s in db.veri_yukle().get("sinavlar", []) if s.get("kurs_id") in my_courses]
        courses = {k.get("kurs_id"): k for k in get_courses()}
        outer, wrap = self.full_scroll_container(f)
        if not exams:
            lbl(wrap, "Kayıtlı derslerin için henüz sınav bulunmuyor.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=18)
        for s in exams:
            c = card(wrap, fill="x", pady=7)
            cname = courses.get(s.get("kurs_id"), {}).get("kurs_adi", s.get("kurs_id"))
            days = self.days_left(s.get("tarih"))
            color = RED if isinstance(days, int) and days <= 3 else YELLOW if isinstance(days, int) and days <= 10 else GREEN
            lbl(c, f"{s.get('baslik')}  •  {cname}", 15, "bold", color, wraplength=900).pack(anchor="w", padx=16, pady=(12,3))
            lbl(c, f"Tarih: {s.get('tarih','-')}  •  Kalan: {days if isinstance(days, str) else str(days) + ' gün'}", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
            btn(c, "Çalışma Kaynakları", lambda sid=s.get("sinav_id"): ExamDetailDialog(self.master, sid), BLUE, BLUE_2, 170, 30).pack(anchor="w", padx=16, pady=(8,12))

    def days_left(self, tarih):
        try:
            return (date.fromisoformat(tarih) - date.today()).days
        except Exception:
            return "Tarih yok"

    def attendance_page(self, f):
        self.header(f, "Yoklama", "Ders yoklama durumlarını ve katılım oranını burada görebilirsin.")
        uid = user_id(self.user)
        rows = db.yoklamalari_getir(ogrenci_id=uid) if hasattr(db, "yoklamalari_getir") else []
        outer, wrap = self.full_scroll_container(f)
        if not rows:
            lbl(wrap, "Henüz yoklama kaydı bulunmuyor.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=16)
        for r in rows:
            status = r.get("durumlar", {}).get(uid, "Belirsiz")
            c = card(wrap, fill="x", pady=5)
            lbl(c, f"{r.get('kurs_id')}  •  {r.get('tarih','-')}  •  {status}", 13, "bold", GREEN if status == "Geldi" else RED).pack(anchor="w", padx=16, pady=12)

    def forum_page(self, f):
        self.header(f, "Forum", "Global forum başlıklarında soru sorabilir ve cevapları okuyabilirsin.")
        topics = db.veri_yukle().get("forum_konulari", [])
        outer, wrap = self.full_scroll_container(f)
        if not topics:
            lbl(wrap, "Henüz forum konusu yok.", 13, "normal", MUTED).pack(anchor="w", padx=16, pady=18)
        for t in topics:
            c = ctk.CTkFrame(wrap, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
            c.pack(fill="x", padx=10, pady=8)
            lbl(c, t.get("baslik", "Konu"), 15, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(12,2))
            lbl(c, f"Açan: {ogrenci_adi(t.get('ogrenci_id'))}  •  {len(t.get('yorumlar', []))} cevap", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,6))
            lbl(c, t.get("aciklama", ""), 12, "normal", TEXT, wraplength=920, justify="left").pack(anchor="w", padx=16, pady=(0,8))
            btn(c, "Konuyu Aç", lambda tid=t.get("konu_id"): ForumTopicDialog(self.master, tid, self.user), BLUE, BLUE_2, 120, 30).pack(anchor="w", padx=16, pady=(0,12))
        ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")

    def support_page(self, f):
        self.header(f, "Destek", "Sorun bildirimi oluşturabilir ve geçmiş taleplerini takip edebilirsin.")
        form = card(f, fill="x", padx=8, pady=8)
        konu = ctk.CTkEntry(form, placeholder_text="Konu başlığı", fg_color=BG_3, border_color=BORDER)
        konu.pack(fill="x", padx=16, pady=(14, 8))
        prio = ctk.CTkOptionMenu(form, values=["Düşük", "Orta", "Yüksek"], fg_color=BLUE, button_color=BLUE_2)
        prio.set("Orta")
        prio.pack(anchor="w", padx=16, pady=4)
        msg = ctk.CTkTextbox(form, height=110, fg_color=BG_3, border_color=BORDER, text_color=TEXT)
        msg.pack(fill="x", padx=16, pady=8)
        def send():
            k = konu.get().strip(); m = msg.get("1.0", "end").strip(); p = prio.get()
            if not k or not m:
                messagebox.showwarning("Eksik", "Konu ve açıklama yazmalısın."); return
            ok, res = db.destek_talebi_ekle(user_id(self.user), self.user.get("rol", "ogrenci"), f"[{p}] {k}", m)
            mail_ok = False
            if mail_servisi:
                try:
                    mail_ok, _ = mail_servisi._mail_gonder(f"[Destek - {p}] {k}", f"Kullanıcı: {self.user.get('ad')} ({user_id(self.user)})\nRol: {self.user.get('rol')}\nÖncelik: {p}\n\n{m}")
                except Exception:
                    mail_ok = False
            toast(self.master, "Destek talebi gönderildi." + (" Mail iletildi." if mail_ok else ""), GREEN)
            self.refresh()
        btn(form, "Gönder", send, GREEN, GREEN_2, 120, 36).pack(anchor="w", padx=16, pady=(2,14))
        outer, wrap = self.full_scroll_container(f)
        lbl(wrap, "Geçmiş Destek Taleplerim", 16, "bold", GREEN).pack(anchor="w", padx=4, pady=(8,6))
        rows = [r for r in db.destek_talepleri_getir(user_id(self.user))] if hasattr(db, "destek_talepleri_getir") else []
        if not rows:
            lbl(wrap, "Henüz destek talebin yok.", 12, "normal", MUTED).pack(anchor="w", padx=4, pady=6)
        for r in reversed(rows):
            c = card(wrap, fill="x", pady=5)
            lbl(c, f"{r.get('konu')}  •  {r.get('durum','Açık')}", 13, "bold", YELLOW if r.get('durum') != 'Cevaplandı' else GREEN, wraplength=860).pack(anchor="w", padx=16, pady=(10,2))
            lbl(c, r.get("mesaj", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0,10))

    def badges_page(self, f):
        self.header(f, "Hedef ve Rozet", "Rozet vitrini, görev ilerlemeleri ve XP tarzı başarı sistemi.")
        uid = user_id(self.user)
        v = db.veri_yukle()
        my_comments = len([y for y in v.get("yorumlar", []) if y.get("ogrenci_id") == uid])
        my_courses = len(db.ogrenci_kurslarini_getir(uid))
        avg = self.avg_grade()
        criteria = [
            ("Yardım Sever", "10 forum/yorum katkısı", my_comments, 10),
            ("Ders Kaşifi", "5 farklı derse kayıt", my_courses, 5),
            ("Matematik Dehası", "Matematik/Fizik derslerinde 80+ ortalama", int(avg), 80),
            ("Mühendis Zekası", "Genel ortalama 75+", int(avg), 75),
            ("Veri Ustası", "Veri tabanı/veri yapıları derslerini takip et", my_courses, 8),
            ("Düzenli Katılımcı", "Katılım oranını yüksek tut", 7, 10),
            ("Ödev Avcısı", "Ödevleri zamanında teslim et", 4, 8),
            ("Sınav Hazırlıkçısı", "Sınav kaynaklarını incele", 3, 6),
            ("Forum Kahramanı", "Forumda aktif ol", my_comments, 20),
            ("Proje Savaşçısı", "Bitirme projesi yolunda ilerle", 2, 5),
        ]
        base_names = ["Algoritma Şövalyesi", "Kod Büyücüsü", "Hata Avcısı", "Python Ustası", "Web Ninjası", "Mobil Kaşifi", "Veritabanı Bekçisi", "Arayüz Sanatçısı", "Takvim Ustası", "Disiplinli Öğrenci"]
        names = base_names + [f"Başarım Koleksiyonu {i:03d}" for i in range(1, 251)]
        all_items = []
        for idx, name in enumerate(names[:260]):
            if idx < len(criteria):
                all_items.append(criteria[idx])
            else:
                all_items.append((name, "Platform görevlerini tamamlayarak açılır.", (idx + my_courses + my_comments) % 12, 10))

        outer, wrap = self.full_scroll_container(f)
        lbl(wrap, "Performans için rozetler sayfa sayfa yüklenir; özellik silinmedi.", 11, "normal", MUTED).pack(anchor="w", padx=10, pady=(8, 6))
        state = {"shown": 0}
        holder = ctk.CTkFrame(wrap, fg_color="transparent")
        holder.pack(fill="both", expand=True)

        def draw_one(title, desc, cur, target):
            won = cur >= target
            c = ctk.CTkFrame(holder, fg_color=BG_3 if won else ("#E5E9F1" if THEME_LIGHT else "#111827"), corner_radius=14, border_width=1, border_color=GREEN if won else ("#CBD5E1" if THEME_LIGHT else "#334155"))
            c.pack(fill="x", padx=10, pady=5)
            lbl(c, ("✦ " if won else "◇ ") + title, 14, "bold", GREEN if won else MUTED).pack(anchor="w", padx=14, pady=(10,2))
            lbl(c, desc, 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=14)
            bar_bg = ctk.CTkFrame(c, fg_color="#233143" if not THEME_LIGHT else "#D6DFEC", height=10, corner_radius=5)
            bar_bg.pack(fill="x", padx=14, pady=(8, 10))
            fill = ctk.CTkFrame(bar_bg, fg_color=GREEN if won else BLUE, height=10, corner_radius=5)
            fill.place(x=0, y=0, relheight=1, relwidth=min(cur/target, 1) if target else 1)
            lbl(c, f"{min(cur, target)}/{target}", 10, "bold", GREEN if won else MUTED).place(relx=0.97, rely=0.5, anchor="e")

        def load_more():
            start_i = state["shown"]
            end_i = min(start_i + 40, len(all_items))
            for item in all_items[start_i:end_i]:
                draw_one(*item)
            state["shown"] = end_i
            status.configure(text=f"{state['shown']}/{len(all_items)} rozet yüklendi")
            if state["shown"] >= len(all_items):
                more.configure(state="disabled", text="Tüm rozetler yüklendi")

        controls = ctk.CTkFrame(wrap, fg_color="transparent")
        controls.pack(fill="x", pady=8)
        status = lbl(controls, "0/260 rozet yüklendi", 11, "normal", MUTED)
        status.pack(side="left", padx=10)
        more = btn(controls, "40 Rozet Daha Yükle", load_more, BLUE, BLUE_2, 170, 32)
        more.pack(side="right", padx=10)
        load_more()
        ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")

    def help_page(self, f):
        self.header(f, "Kullanım Kılavuzu", "Programda yapabileceklerin.")
        texts = [
            "Ders Kaydı ekranından kurslara kayıt olabilirsin.",
            "Kayıtlı olduğun derste Derse Git butonu Ders Odası ekranını açar.",
            "Ders Odasında öğretmen, katılımcılar, mini takvim ve yorum alanı bulunur.",
            "Takvim ekranında ders ve sınav günlerini görebilirsin.",
            "Not/Belge bölümünde notlarını ve sertifikalarını takip edebilirsin.",
        ]
        for t in texts:
            c = card(f, fill="x", padx=8, pady=6)
            lbl(c, "✓ " + t, 12, "normal", TEXT, wraplength=760).pack(anchor="w", padx=16, pady=12)


# ─────────────────────────────────────────────────────────────────────────────
# ÖĞRETMEN PANELİ
# ─────────────────────────────────────────────────────────────────────────────
class EgitmenPanel(BasePanel):
    def __init__(self, master, user):
        super().__init__(master, user, PURPLE)
        self.add_menus([
            ("Panel", "", self.dashboard),
            ("Derslerim", "", self.my_courses),
            ("Ders Kaydı", "", self.add_course_page),
            ("Materyaller", "", self.teacher_materials_page),
            ("Ödevler", "", self.teacher_assignments_page),
            ("Sınavlar", "", self.teacher_exams_page),
            ("Yorumlar", "", self.teacher_comments_page),
            ("Yoklama", "", self.attendance_page),
            ("Forum", "", self.forum_page),
            ("Mesajlar", "", lambda f: self.generic_page(f, "Mesajlar", "Öğrencilere mesaj gönderme ekranı.")),
            ("Destek", "", self.support_page),
            ("Yardım", "", lambda f: self.generic_page(f, "Yardım", "Kurs açma, ders planlama, not ve yoklama işlemleri.")),
        ])

    def dashboard(self, f):
        self.header(f, f"Merhaba, {self.user.get('ad','Öğretmen')}!", "Kurslarını ve öğrencilerini yönet.")
        c = card(f, fill="x", padx=8, pady=(0,10))
        lbl(c, "Bugünkü Derslerim", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12,4))
        bugun = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"][date.today().weekday()]
        items = [k for k in get_courses() if k.get("egitmen_id") == user_id(self.user) and bugun in (k.get("takvim_gunler") or [])]
        if not items:
            lbl(c, "Bugün için planlanmış ders görünmüyor.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,12))
        for k in items[:5]:
            lbl(c, f"• {k.get('takvim_saat','')} - {k.get('kurs_adi')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        self.my_courses(f)

    def my_courses(self, f):
        if not f.winfo_children():
            self.header(f, "Derslerim", "Verdiğin kurslar.")
        area = ctk.CTkFrame(f, fg_color="transparent")
        area.pack(fill="x", padx=8)
        courses = [k for k in get_courses() if k.get("egitmen_id") == user_id(self.user)]
        if not courses:
            lbl(area, "Henüz kurs yok.", 13, "normal", MUTED).pack(pady=30)
        for k in courses:
            self.course_card(area, k, registered=True)

    def add_course_page(self, f):
        self.header(f, "Kurs / Ders Aç", "Yeni kurs açabilir ve ders günlerini belirleyebilirsin.")
        form = card(f, fill="x", padx=8, pady=8)
        entries = {}
        fields = [("kurs_adi", "Kurs adı"), ("kontenjan", "Kontenjan"), ("aciklama", "Açıklama"), ("gunler", "Günler: Pazartesi,Çarşamba"), ("saat", "Saat: 10:00"), ("sinav", "Sınav tarihi: YYYY-AA-GG")]
        for key, ph in fields:
            e = ctk.CTkEntry(form, placeholder_text=ph, width=440, height=40, fg_color=BG_3, border_color=BORDER)
            e.pack(anchor="w", padx=18, pady=6)
            entries[key] = e
        def save():
            name = entries["kurs_adi"].get().strip(); kont = entries["kontenjan"].get().strip() or "30"
            if not name:
                messagebox.showwarning("Eksik", "Kurs adı gerekli."); return
            gunler = [g.strip() for g in entries["gunler"].get().split(",") if g.strip()]
            ok, msg = db.kurs_ekle(name, user_id(self.user), kont, entries["aciklama"].get(), gunler, entries["saat"].get(), entries["sinav"].get())
            toast(self.master, f"Kurs oluşturuldu: {msg}" if ok else str(msg), GREEN if ok else RED)
            self.refresh()
        btn(form, "Kursu Oluştur", save, GREEN, GREEN_2, 180, 42).pack(anchor="w", padx=18, pady=12)


    def teacher_course_list(self):
        return [k for k in get_courses() if k.get("egitmen_id") == user_id(self.user)]

    def course_option_map(self):
        courses = self.teacher_course_list()
        opts = [f"{k.get('kurs_id')} - {k.get('kurs_adi')}" for k in courses]
        mp = {opts[i]: courses[i] for i in range(len(opts))}
        return opts, mp

    def teacher_materials_page(self, f):
        self.header(f, "Materyaller", "Verdiğin derslere materyal ekleyebilir ve mevcut linkleri yönetebilirsin.")
        opts, mp = self.course_option_map()
        form = card(f, fill="x", padx=8, pady=8)
        if not opts:
            lbl(form, "Önce bir kurs oluşturun.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=14)
            return
        course_var = ctk.CTkOptionMenu(form, values=opts, fg_color=BLUE, button_color=BLUE_2)
        course_var.set(opts[0])
        course_var.pack(anchor="w", padx=16, pady=(14, 8))
        name = ctk.CTkEntry(form, placeholder_text="Materyal adı", fg_color=BG_3, border_color=BORDER)
        name.pack(fill="x", padx=16, pady=6)
        link = ctk.CTkEntry(form, placeholder_text="Materyal linki", fg_color=BG_3, border_color=BORDER)
        link.pack(fill="x", padx=16, pady=6)
        def add():
            k = mp.get(course_var.get(), {})
            if not name.get().strip() or not link.get().strip():
                messagebox.showwarning("Eksik", "Materyal adı ve link gir.")
                return
            ok, msg = db.materyal_ekle(k.get("kurs_id"), name.get().strip(), link.get().strip(), "Link")
            toast(self.master, msg if isinstance(msg, str) else "Materyal eklendi.", GREEN if ok else RED)
            self.refresh()
        btn(form, "Materyal Ekle", add, GREEN, GREEN_2, 140, 36).pack(anchor="w", padx=16, pady=(4, 14))
        outer, wrap = self.full_scroll_container(f)
        for k in self.teacher_course_list():
            c = card(wrap, fill="x", pady=6)
            lbl(c, k.get("kurs_adi", "Ders"), 14, "bold", GREEN).pack(anchor="w", padx=16, pady=(10, 4))
            mats = k.get("materyaller", [])
            if not mats:
                lbl(c, "Bu derse henüz materyal yok.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 10))
            for m in mats:
                row = ctk.CTkFrame(c, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=2)
                lbl(row, f"• {m.get('baslik')} ({m.get('tur','Link')})", 11, "normal", TEXT, wraplength=760).pack(side="left", fill="x", expand=True, anchor="w")
                btn(row, "Aç", lambda l=str(m.get("link", "")): open_material_link(l), BLUE, BLUE_2, 55, 26).pack(side="right")

    def teacher_assignments_page(self, f):
        self.header(f, "Ödevler", "Derslerin için ödev oluştur; öğrencilerin takviminde otomatik görünür.")
        opts, mp = self.course_option_map()
        form = card(f, fill="x", padx=8, pady=8)
        if not opts:
            lbl(form, "Önce bir kurs oluşturun.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=14)
            return
        course_var = ctk.CTkOptionMenu(form, values=opts, fg_color=BLUE, button_color=BLUE_2)
        course_var.set(opts[0])
        course_var.pack(anchor="w", padx=16, pady=(14, 8))
        title = ctk.CTkEntry(form, placeholder_text="Ödev başlığı", fg_color=BG_3, border_color=BORDER)
        title.pack(fill="x", padx=16, pady=5)
        due = ctk.CTkEntry(form, placeholder_text="Son tarih: YYYY-AA-GG", fg_color=BG_3, border_color=BORDER)
        due.pack(fill="x", padx=16, pady=5)
        desc = ctk.CTkTextbox(form, height=86, fg_color=BG_3, border_color=BORDER, text_color=TEXT)
        desc.pack(fill="x", padx=16, pady=5)
        def add():
            k = mp.get(course_var.get(), {})
            if not title.get().strip() or not due.get().strip():
                messagebox.showwarning("Eksik", "Başlık ve son tarih gir.")
                return
            ok, msg = db.odev_ekle(k.get("kurs_id"), user_id(self.user), title.get().strip(), desc.get("1.0", "end").strip(), due.get().strip())
            toast(self.master, "Ödev eklendi; takvim güncellendi." if ok else str(msg), GREEN if ok else RED)
            self.refresh()
        btn(form, "Ödev Ekle", add, GREEN, GREEN_2, 130, 36).pack(anchor="w", padx=16, pady=(4, 14))
        outer, wrap = self.full_scroll_container(f)
        rows = db.odevleri_getir(egitmen_id=user_id(self.user)) if hasattr(db, "odevleri_getir") else []
        courses = {k.get("kurs_id"): k for k in get_courses()}
        for o in rows:
            c = card(wrap, fill="x", pady=5)
            lbl(c, f"{o.get('baslik')} • {courses.get(o.get('kurs_id'),{}).get('kurs_adi', o.get('kurs_id'))}", 13, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10,2))
            lbl(c, f"Son tarih: {o.get('son_tarih')}  •  {o.get('aciklama','')}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0,10))

    def teacher_exams_page(self, f):
        self.header(f, "Sınavlar", "Derslerin için sınav oluştur; sınav takvimde anında görünür.")
        opts, mp = self.course_option_map()
        form = card(f, fill="x", padx=8, pady=8)
        if not opts:
            lbl(form, "Önce bir kurs oluşturun.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=14)
            return
        course_var = ctk.CTkOptionMenu(form, values=opts, fg_color=BLUE, button_color=BLUE_2)
        course_var.set(opts[0])
        course_var.pack(anchor="w", padx=16, pady=(14, 8))
        title = ctk.CTkEntry(form, placeholder_text="Sınav başlığı", fg_color=BG_3, border_color=BORDER)
        title.pack(fill="x", padx=16, pady=5)
        when = ctk.CTkEntry(form, placeholder_text="Sınav tarihi: YYYY-AA-GG", fg_color=BG_3, border_color=BORDER)
        when.pack(fill="x", padx=16, pady=5)
        def add():
            k = mp.get(course_var.get(), {})
            if not title.get().strip() or not when.get().strip():
                messagebox.showwarning("Eksik", "Başlık ve tarih gir.")
                return
            sorular = [{"soru": "Bu sınav hangi ders içindir?", "secenekler": [k.get("kurs_adi", "Ders"), "Diğer", "Boş", "Hiçbiri"], "dogru": 0}]
            ok, msg = db.sinav_ekle(k.get("kurs_id"), user_id(self.user), title.get().strip(), when.get().strip(), sorular)
            toast(self.master, "Sınav eklendi; takvim güncellendi." if ok else str(msg), GREEN if ok else RED)
            self.refresh()
        btn(form, "Sınav Ekle", add, GREEN, GREEN_2, 130, 36).pack(anchor="w", padx=16, pady=(4, 14))
        outer, wrap = self.full_scroll_container(f)
        rows = db.sinavlari_getir(egitmen_id=user_id(self.user)) if hasattr(db, "sinavlari_getir") else []
        courses = {k.get("kurs_id"): k for k in get_courses()}
        for s in rows:
            c = card(wrap, fill="x", pady=5)
            lbl(c, f"{s.get('baslik')} • {courses.get(s.get('kurs_id'),{}).get('kurs_adi', s.get('kurs_id'))}", 13, "bold", YELLOW, wraplength=900).pack(anchor="w", padx=16, pady=(10,2))
            lbl(c, f"Tarih: {s.get('tarih')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,10))

    def teacher_comments_page(self, f):
        self.header(f, "Yorumlar", "Verdiğin derslere yazılan öğrenci yorumlarını takip edebilirsin.")
        my_courses = {k.get("kurs_id") for k in self.teacher_course_list()}
        rows = [y for y in db.yorumlari_getir() if y.get("kurs_id") in my_courses] if hasattr(db, "yorumlari_getir") else []
        courses = {k.get("kurs_id"): k for k in get_courses()}
        outer, wrap = self.full_scroll_container(f)
        if not rows:
            lbl(wrap, "Derslerine henüz yorum yazılmamış.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
        for y in reversed(rows[-100:]):
            c = card(wrap, fill="x", pady=5)
            lbl(c, f"{ogrenci_adi(y.get('ogrenci_id'))} • {courses.get(y.get('kurs_id'),{}).get('kurs_adi', y.get('kurs_id'))} • ★ {y.get('puan','-')}", 12, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10,2))
            lbl(c, y.get("yorum", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0,10))

    def forum_page(self, f):
        return OgrenciPanel.forum_page(self, f)

    def support_page(self, f):
        return OgrenciPanel.support_page(self, f)

    def calendar_page(self, f):
        self.header(f, "Takvim", "Ders ve sınav takvimi.")
        TakvimWidget(f).pack(fill="both", expand=True, padx=8, pady=8)

    def attendance_page(self, f):
        self.generic_page(f, "Yoklama", "QR/kod yoklama simülasyonu burada kullanılabilir. Öğretmen kod oluşturur, öğrenciler kodla yoklama verir.")


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN PANELİ
# ─────────────────────────────────────────────────────────────────────────────
class AdminPanel(BasePanel):
    def __init__(self, master, user):
        super().__init__(master, user, BLUE)
        self.add_menus([
            ("Panel", "P", self.dashboard),
            ("Kullanıcılar", "K", self.users_page),
            ("Başvurular", "B", self.applications_page),
            ("Kurslar", "D", self.courses_page),
            ("Duyuru", "D", self.announcement_page),
            ("Destek", "?", lambda f: self.generic_page(f, "Destek", "Destek talepleri ve yanıtları.")),
            ("Yardım", "i", lambda f: self.generic_page(f, "Yardım", "Admin: kullanıcı, başvuru, kurs, rapor ve yedek yönetimi yapar.")),
        ])

    def dashboard(self, f):
        self.header(f, "Sistem Paneli", "Genel sistem durumu.")
        v = db.veri_yukle()
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", padx=8)
        stats = [("Öğrenci", len(v.get("ogrenciler", []))), ("Öğretmen", len(v.get("egitmenler", []))), ("Kurs", len(v.get("kurslar", []))), ("Başvuru", len([e for e in v.get("egitmenler", []) if not e.get("onayli", True)]) + len(v.get("admin_basvurular", [])))]
        for name, val in stats:
            s = ctk.CTkFrame(row, fg_color=CARD, corner_radius=15, height=86, border_width=1, border_color=BORDER)
            s.pack(side="left", fill="x", expand=True, padx=6); s.pack_propagate(False)
            lbl(s, str(val), 20, "bold", self.accent).place(relx=0.88, y=16, anchor="e")
            lbl(s, name, 13, "bold").place(x=16, y=48)
        feed = card(f, fill="x", padx=8, pady=14)
        lbl(feed, "Bugün Yapılan İşlemler / Aktivite Akışı", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12,4))
        logs = v.get("loglar", [])[-8:]
        if not logs:
            lbl(feed, "Henüz log kaydı yok.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,12))
        for lg in reversed(logs):
            lbl(feed, f"• {lg}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)

    def users_page(self, f):
        self.header(f, "Kullanıcı Yönetimi", "Öğrenci, öğretmen ve admin kullanıcıları.")
        v = db.veri_yukle()
        for title, arr in [("Öğrenciler", v.get("ogrenciler", [])), ("Öğretmenler", v.get("egitmenler", [])), ("Adminler", v.get("adminler", []))]:
            lbl(f, title, 16, "bold").pack(anchor="w", padx=8, pady=(12,4))
            for u in arr[:20]:
                c = card(f, fill="x", padx=8, pady=3)
                lbl(c, f"{u.get('id') or u.get('ogrenci_id') or u.get('egitmen_id') or u.get('admin_id')} - {u.get('ad')} - {u.get('email','')}", 11, "normal", MUTED).pack(anchor="w", padx=12, pady=8)

    def applications_page(self, f):
        self.header(f, "Başvuru Onay Sistemi", "Öğretmen ve admin başvurularını onayla/reddet.")
        v = db.veri_yukle()
        pending_teachers = [e for e in v.get("egitmenler", []) if not e.get("onayli", True)]
        lbl(f, "Öğretmen Başvuruları", 15, "bold").pack(anchor="w", padx=8, pady=(10,4))
        if not pending_teachers:
            lbl(f, "Bekleyen öğretmen başvurusu yok.", 11, "normal", MUTED).pack(anchor="w", padx=8)
        for e in pending_teachers:
            c = card(f, fill="x", padx=8, pady=5)
            lbl(c, f"{e.get('egitmen_id')} - {e.get('ad')} - {e.get('uzmanlik','')}", 12, "bold").pack(side="left", padx=12, pady=10)
            btn(c, "Onayla", lambda eid=e.get("egitmen_id"): self.approve_teacher(eid), GREEN, GREEN_2, 90, 30).pack(side="right", padx=10)
        lbl(f, "Admin Başvuruları", 15, "bold").pack(anchor="w", padx=8, pady=(16,4))
        apps = v.get("admin_basvurular", [])
        if not apps:
            lbl(f, "Bekleyen admin başvurusu yok.", 11, "normal", MUTED).pack(anchor="w", padx=8)
        for a in apps:
            c = card(f, fill="x", padx=8, pady=5)
            aid = a.get("admin_id") or a.get("id")
            lbl(c, f"{aid} - {a.get('ad')} - {a.get('email','')}", 12, "bold").pack(side="left", padx=12, pady=10)
            btn(c, "Onayla", lambda x=aid: self.approve_admin(x), GREEN, GREEN_2, 90, 30).pack(side="right", padx=10)

    def approve_teacher(self, eid):
        ok = db.egitmen_onayla(eid)
        toast(self.master, "Öğretmen onaylandı." if ok else "Onaylanamadı", GREEN if ok else RED)
        self.refresh()

    def approve_admin(self, aid):
        ok = db.admin_basvuru_onayla(aid)
        toast(self.master, "Admin onaylandı." if ok else "Onaylanamadı", GREEN if ok else RED)
        self.refresh()

    def courses_page(self, f):
        self.header(f, "Kurs Yönetimi", "Tüm kurslar.")
        area = ctk.CTkFrame(f, fg_color="transparent")
        area.pack(fill="x")
        for k in get_courses():
            self.course_card(area, k, registered=True)

    def calendar_page(self, f):
        self.header(f, "Takvim", "Sistemdeki tüm etkinlikler.")
        TakvimWidget(f).pack(fill="both", expand=True, padx=8, pady=8)

    def announcement_page(self, f):
        self.header(f, "Duyuru Yayınla", "Tüm kullanıcılara duyuru gönder.")
        e = ctk.CTkEntry(f, placeholder_text="Duyuru metni", width=520, height=42, fg_color=BG_3, border_color=BORDER)
        e.pack(anchor="w", padx=8, pady=8)
        def send():
            msg = e.get().strip()
            if msg:
                db.duyuru_ekle(msg)
                toast(self.master, "Duyuru yayınlandı.")
                e.delete(0, "end")
        btn(f, "Yayınla", send, GREEN, GREEN_2, 140, 42).pack(anchor="w", padx=8, pady=6)


# ─────────────────────────────────────────────────────────────────────────────
# DERS ODASI / TAKVİM / DİĞER DİALOGLAR
# ─────────────────────────────────────────────────────────────────────────────
class CourseRoomDialog(ctk.CTkToplevel):
    def __init__(self, master, user, kurs_id):
        super().__init__(master)
        self.user = user
        self.kurs_id = kurs_id
        self.title("Ders Odası")
        self.geometry("880x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def build(self):
        clear(self)
        courses = db.tum_kurslar_getir()
        k = courses.get(self.kurs_id, {}) if isinstance(courses, dict) else {}
        lbl(self, k.get("kurs_adi", "Ders Odası"), 24, "bold").pack(anchor="w", padx=24, pady=(22,4))
        lbl(self, k.get("aciklama", ""), 12, "normal", MUTED, wraplength=800).pack(anchor="w", padx=24)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=18)
        left = ctk.CTkFrame(body, fg_color="transparent", width=260)
        left.pack(side="left", fill="y", padx=(0, 12)); left.pack_propagate(False)
        center = ctk.CTkFrame(body, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True)
        right = ctk.CTkFrame(body, fg_color="transparent", width=230)
        right.pack(side="right", fill="y", padx=(12, 0)); right.pack_propagate(False)

        tcard = card(left, fill="x", pady=(0, 10))
        lbl(tcard, "Öğretmen", 14, "bold").pack(anchor="w", padx=14, pady=(12,2))
        lbl(tcard, egitmen_adi(k.get("egitmen_id")), 12, "normal", MUTED).pack(anchor="w", padx=14, pady=(0,12))

        cal = card(left, fill="x", pady=(0, 10))
        lbl(cal, "Mini Takvim", 14, "bold").pack(anchor="w", padx=14, pady=(12, 6))
        lbl(cal, f"Günler: {', '.join(k.get('takvim_gunler', [])) or 'Belirtilmedi'}", 11, "normal", MUTED, wraplength=210).pack(anchor="w", padx=14, pady=2)
        lbl(cal, f"Saat: {k.get('takvim_saat', '-')}", 11, "normal", MUTED).pack(anchor="w", padx=14, pady=2)
        lbl(cal, f"Sınav: {k.get('sinav_tarihi', '-')}", 11, "normal", MUTED).pack(anchor="w", padx=14, pady=(2,12))

        yc = card(left, fill="x")
        lbl(yc, "Yorum Bırak", 14, "bold").pack(anchor="w", padx=14, pady=(12, 6))
        self.comment = ctk.CTkEntry(yc, placeholder_text="Kısa yorum yaz...", fg_color=BG_3, border_color=BORDER)
        self.comment.pack(fill="x", padx=14, pady=(0, 8))
        btn(yc, "Gönder", self.add_comment, GREEN, GREEN_2, 110, 32).pack(anchor="w", padx=14, pady=(0,12))

        mainc = card(center, fill="both", expand=True)
        lbl(mainc, "Ders İçeriği", 17, "bold").pack(anchor="w", padx=16, pady=(16, 8))
        for i, d in enumerate(k.get("dersler", []) or [{"ders_adi":"Ders bilgisi henüz eklenmedi."}], 1):
            lbl(mainc, f"{i}. {d.get('ders_adi')}", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=4)
        lbl(mainc, "\nMateryaller", 15, "bold").pack(anchor="w", padx=16, pady=(14, 6))
        mats = k.get("materyaller", [])
        if not mats:
            lbl(mainc, "Henüz materyal yok.", 11, "normal", MUTED).pack(anchor="w", padx=16)
        for m in mats:
            row = ctk.CTkFrame(mainc, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            lbl(row, f"- {m.get('baslik', 'Materyal')} ({m.get('tur','Link')})", 11, "normal", MUTED, wraplength=300).pack(side="left", anchor="w")
            btn(row, "Aç", lambda link=str(m.get("link", "")): open_material_link(link), BLUE, BLUE_2, 56, 26).pack(side="right")
        if self.user.get("rol") == "egitmen" and (k.get("egitmen_id") == user_id(self.user) or user_id(self.user) == "taha"):
            addbox = ctk.CTkFrame(mainc, fg_color=BG_3, corner_radius=12, border_width=1, border_color=BORDER)
            addbox.pack(fill="x", padx=16, pady=(12, 8))
            lbl(addbox, "Materyal Ekle", 13, "bold", GREEN).pack(anchor="w", padx=12, pady=(10, 4))
            self.mat_name = ctk.CTkEntry(addbox, placeholder_text="Materyal adı", fg_color=CARD, border_color=BORDER)
            self.mat_name.pack(fill="x", padx=12, pady=4)
            self.mat_link = ctk.CTkEntry(addbox, placeholder_text="Link", fg_color=CARD, border_color=BORDER)
            self.mat_link.pack(fill="x", padx=12, pady=4)
            btn(addbox, "Ekle", self.add_material, GREEN, GREEN_2, 90, 28).pack(anchor="w", padx=12, pady=(4, 10))

        sc = card(right, fill="both", expand=True)
        lbl(sc, "Katılan Öğrenciler", 14, "bold").pack(anchor="w", padx=14, pady=(12, 8))
        students_frame = ctk.CTkScrollableFrame(sc, fg_color="transparent")
        students_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        for oid in k.get("kayitli_ogrenciler", []):
            name = ogrenci_adi(oid)
            b = ctk.CTkButton(
                students_frame,
                text=f"• {name}",
                command=lambda sid=oid: StudentDetailDialog(self, sid),
                fg_color="transparent",
                hover_color=BG_3,
                text_color=MUTED,
                anchor="w",
                height=30,
                corner_radius=8,
                font=(FONT, 11, "normal"),
            )
            b.pack(fill="x", pady=1)

        try:
            yorumlar = db.yorumlari_getir(self.kurs_id)
        except Exception:
            yorumlar = []
        if yorumlar:
            lbl(mainc, "Son Yorumlar", 15, "bold").pack(anchor="w", padx=16, pady=(14, 6))
            for y in reversed(yorumlar[-5:]):
                lbl(mainc, f"{ogrenci_adi(y.get('ogrenci_id'))} • ★ {y.get('puan', '-')}", 11, "bold", TEXT).pack(anchor="w", padx=16, pady=(4, 0))
                lbl(mainc, y.get("yorum", ""), 11, "normal", MUTED, wraplength=350, justify="left").pack(anchor="w", padx=16, pady=(0, 2))

    def add_material(self):
        name = getattr(self, "mat_name", None).get().strip() if hasattr(self, "mat_name") else ""
        link = getattr(self, "mat_link", None).get().strip() if hasattr(self, "mat_link") else ""
        if not name or not link:
            messagebox.showwarning("Eksik", "Materyal adı ve link girmelisin.")
            return
        try:
            ok, msg = db.materyal_ekle(self.kurs_id, name, "Link", link)
        except Exception as e:
            ok, msg = False, str(e)
        toast(self, "Materyal eklendi." if ok else f"Eklenemedi: {msg}", GREEN if ok else RED)
        self.build()

    def add_comment(self):
        txt = self.comment.get().strip()
        if not txt:
            return
        try:
            db.yorum_ekle(self.kurs_id, user_id(self.user), 5, txt)
        except Exception:
            pass
        toast(self, "Yorum kaydedildi.")
        self.comment.delete(0, "end")
        self.build()


class StudentDetailDialog(ctk.CTkToplevel):
    def __init__(self, master, ogrenci_id):
        super().__init__(master)
        self.ogrenci_id = ogrenci_id
        self.title("Öğrenci Profili")
        self.geometry("560x650")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def _student(self):
        try:
            v = db.veri_yukle()
            return next((o for o in v.get("ogrenciler", []) if o.get("ogrenci_id") == self.ogrenci_id or o.get("id") == self.ogrenci_id), {})
        except Exception:
            return {}

    def _avg(self):
        try:
            notes = db.ogrenci_notlarini_getir(self.ogrenci_id)
            vals = []
            for n in notes.values():
                vals.append(float(n.get("not", n) if isinstance(n, dict) else n))
            return round(sum(vals) / len(vals), 1) if vals else 0
        except Exception:
            return 0

    def _attendance_rate(self):
        try:
            rows = db.yoklamalari_getir(ogrenci_id=self.ogrenci_id)
            if not rows:
                return "Veri yok"
            geldi = sum(1 for r in rows if r.get("durumlar", {}).get(self.ogrenci_id) == "Geldi")
            return f"%{round(geldi * 100 / len(rows))}"
        except Exception:
            return "Veri yok"

    def build(self):
        clear(self)
        stu = self._student()
        name = stu.get("ad", self.ogrenci_id)
        lbl(self, name, 24, "bold").pack(anchor="w", padx=24, pady=(22, 4))
        lbl(self, f"Öğrenci ID: {self.ogrenci_id}  •  E-posta: {stu.get('email', '-')}", 12, "normal", MUTED).pack(anchor="w", padx=24)
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=20, pady=18)

        stats = ctk.CTkFrame(sc, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 10))
        for title, value, color in [("Ortalama", self._avg(), GREEN), ("Katılım", self._attendance_rate(), BLUE), ("Kayıtlı Ders", len(db.ogrenci_kurslarini_getir(self.ogrenci_id)), PURPLE)]:
            c = ctk.CTkFrame(stats, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER, height=76)
            c.pack(side="left", fill="x", expand=True, padx=4); c.pack_propagate(False)
            lbl(c, str(value), 18, "bold", color).pack(anchor="w", padx=14, pady=(12, 0))
            lbl(c, title, 11, "normal", MUTED).pack(anchor="w", padx=14)

        courses = {k.get("kurs_id"): k for k in get_courses()}
        c1 = card(sc, fill="x", pady=(0, 10))
        lbl(c1, "Girdiği Kurslar", 16, "bold").pack(anchor="w", padx=16, pady=(14, 6))
        my_courses = db.ogrenci_kurslarini_getir(self.ogrenci_id)
        if not my_courses:
            lbl(c1, "Kayıtlı kurs bulunmuyor.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,14))
        for kid in my_courses:
            k = courses.get(kid, {})
            lbl(c1, f"• {k.get('kurs_adi', kid)}", 12, "normal", MUTED, wraplength=470).pack(anchor="w", padx=16, pady=3)

        c2 = card(sc, fill="x")
        lbl(c2, "Yazdığı Yorumlar", 16, "bold").pack(anchor="w", padx=16, pady=(14, 6))
        try:
            comments = [y for y in db.yorumlari_getir() if y.get("ogrenci_id") == self.ogrenci_id]
        except Exception:
            comments = []
        if not comments:
            lbl(c2, "Henüz yorum yazmamış.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,14))
        for y in reversed(comments[-12:]):
            k = courses.get(y.get("kurs_id"), {})
            lbl(c2, f"{k.get('kurs_adi', y.get('kurs_id'))} • ★ {y.get('puan', '-')}", 12, "bold").pack(anchor="w", padx=16, pady=(6, 0))
            lbl(c2, y.get("yorum", ""), 12, "normal", MUTED, wraplength=470, justify="left").pack(anchor="w", padx=16, pady=(0, 4))


class ExamDetailDialog(ctk.CTkToplevel):
    def __init__(self, master, sinav_id):
        super().__init__(master)
        self.sinav_id = sinav_id
        self.title("Sınav Çalışma Kaynakları")
        self.geometry("620x560")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def build(self):
        v = db.veri_yukle()
        s = next((x for x in v.get("sinavlar", []) if x.get("sinav_id") == self.sinav_id), {})
        courses = {k.get("kurs_id"): k for k in get_courses()}
        k = courses.get(s.get("kurs_id"), {})
        lbl(self, s.get("baslik", "Sınav"), 22, "bold").pack(anchor="w", padx=22, pady=(22, 4))
        try:
            left = (date.fromisoformat(s.get("tarih")) - date.today()).days
            left_text = f"{left} gün kaldı"
        except Exception:
            left_text = "Tarih yok"
        lbl(self, f"Ders: {k.get('kurs_adi', '-')}  •  Tarih: {s.get('tarih','-')}  •  {left_text}", 12, "normal", MUTED).pack(anchor="w", padx=22)
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=18, pady=16)
        topics = s.get("konular") or ["Temel kavramlar", "Uygulama soruları", "Ders notları", "Genel tekrar"]
        c1 = card(sc, fill="x", pady=6)
        lbl(c1, "Çalışılacak Konular", 16, "bold", GREEN).pack(anchor="w", padx=16, pady=(12,6))
        for t in topics:
            lbl(c1, f"• {t}", 12, "normal", TEXT).pack(anchor="w", padx=16, pady=2)
        resources = s.get("kaynaklar") or [
            {"baslik": "Konu anlatım videosu", "link": "https://www.youtube.com/results?search_query=" + (k.get('kurs_adi','ders') + ' konu anlatımı').replace(' ', '+')},
            {"baslik": "Çalışma kağıdı arama", "link": "https://www.google.com/search?q=" + (k.get('kurs_adi','ders') + ' çalışma kağıdı pdf').replace(' ', '+')},
        ]
        c2 = card(sc, fill="x", pady=6)
        lbl(c2, "Konu Anlatım Videoları ve Çalışma Kağıtları", 16, "bold", BLUE).pack(anchor="w", padx=16, pady=(12,6))
        for r in resources:
            row = ctk.CTkFrame(c2, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            lbl(row, f"• {r.get('baslik')}", 12, "normal", TEXT, wraplength=420).pack(side="left", anchor="w")
            btn(row, "Aç", lambda link=str(r.get("link", "")): open_material_link(link), BLUE, BLUE_2, 58, 28).pack(side="right")


class ForumTopicDialog(ctk.CTkToplevel):
    def __init__(self, master, konu_id, user=None):
        super().__init__(master)
        self.konu_id = konu_id
        self.user = user or {"id": "anonim", "ad": "Anonim", "rol": "ogrenci"}
        self.title("Forum Konusu")
        self.geometry("720x680")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def _topic(self):
        for t in db.veri_yukle().get("forum_konulari", []):
            if t.get("konu_id") == self.konu_id:
                return t
        return {}

    def _yorum_ekle(self, textbox):
        try:
            txt = textbox.get("1.0", "end").strip()
        except Exception:
            txt = textbox.get().strip()
        if not txt:
            messagebox.showwarning("Eksik", "Yorum yazmalısın.")
            return
        yeni_yorum = {
            "ogrenci_id": user_id(self.user),
            "yorum": txt,
            "tarih": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        }
        veri = db.veri_yukle()
        for t in veri.setdefault("forum_konulari", []):
            if t.get("konu_id") == self.konu_id:
                t.setdefault("yorumlar", []).append(yeni_yorum)
                break
        db.veri_kaydet(veri)
        # Eski textbox/frame'i hemen yok etmek Tkinter focus_set hatası üretebiliyordu.
        # Bu yüzden pencereyi baştan çizmek yerine yorumu mevcut listeye ekliyoruz.
        try:
            textbox.delete(0, "end")
        except Exception:
            try:
                textbox.delete("1.0", "end")
            except Exception:
                pass
        try:
            self._yorum_karti_ekle(yeni_yorum)
        except Exception:
            pass
        toast(self.master, "Forum yorumu eklendi.", GREEN)

    def _yorum_karti_ekle(self, y):
        if not hasattr(self, "comments_box") or not self.comments_box.winfo_exists():
            return
        c = card(self.comments_box, fill="x", pady=5)
        lbl(c, f"{ogrenci_adi(y.get('ogrenci_id'))}  •  {y.get('tarih','')}", 12, "bold", GREEN).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, y.get("yorum", ""), 12, "normal", MUTED, wraplength=620, justify="left").pack(anchor="w", padx=16, pady=(0,10))

    def build(self):
        t = self._topic()
        lbl(self, t.get("baslik", "Forum Konusu"), 22, "bold").pack(anchor="w", padx=22, pady=(22,4))
        lbl(self, f"Açan: {ogrenci_adi(t.get('ogrenci_id'))}", 12, "normal", MUTED).pack(anchor="w", padx=22)
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=18, pady=12)
        c0 = card(sc, fill="x", pady=6)
        lbl(c0, t.get("aciklama", ""), 13, "normal", TEXT, wraplength=620, justify="left").pack(anchor="w", padx=16, pady=14)

        # Kullanıcı artık forum konusuna cevap yazabilir.
        # CTkTextbox yerine CTkEntry kullanıyoruz; kapanan pencerede focus_set hatasını engeller.
        reply = ctk.CTkFrame(sc, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        reply.pack(fill="x", pady=6)
        lbl(reply, "Cevap Yaz", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12, 4))
        tb = ctk.CTkEntry(reply, placeholder_text="Cevabını yaz...", height=42, fg_color=BG_3, border_color=BORDER, text_color=TEXT)
        tb.pack(fill="x", padx=16, pady=(0, 8))
        tb.bind("<Return>", lambda e, tbox=tb: self._yorum_ekle(tbox))
        btn(reply, "Gönder", lambda tbox=tb: self._yorum_ekle(tbox), GREEN, GREEN_2, 110, 32).pack(anchor="w", padx=16, pady=(0, 12))

        lbl(sc, "Cevaplar", 16, "bold", BLUE).pack(anchor="w", padx=4, pady=(12, 4))
        self.comments_box = ctk.CTkFrame(sc, fg_color="transparent")
        self.comments_box.pack(fill="x")
        for y in t.get("yorumlar", []):
            self._yorum_karti_ekle(y)


class TakvimWidget(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=CARD, corner_radius=18, border_width=1, border_color=BORDER)
        self.today = date.today()
        self.yil = self.today.year
        self.ay = self.today.month
        self.build()

    def build(self):
        clear(self)
        names = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=12)
        btn(top, "‹", self.prev, BG_3, BG_3, 40, 32).pack(side="left")
        lbl(top, f"{names[self.ay]} {self.yil}", 18, "bold").pack(side="left", expand=True)
        btn(top, "Bugün", self.go_today, GREEN, GREEN_2, 86, 32).pack(side="right", padx=(6,0))
        btn(top, "›", self.next, BG_3, BG_3, 40, 32).pack(side="right")
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=14, pady=(0,14))
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for c, d in enumerate(days):
            lbl(grid, d, 11, "bold", MUTED, width=70).grid(row=0, column=c, padx=3, pady=3, sticky="nsew")
            grid.grid_columnconfigure(c, weight=1)
        for r, week in enumerate(calendar.monthcalendar(self.yil, self.ay), start=1):
            grid.grid_rowconfigure(r, weight=1)
            for c, day in enumerate(week):
                fg = BG_3 if day else "transparent"
                hover = "#1B4167"
                if day == self.today.day and self.ay == self.today.month and self.yil == self.today.year:
                    fg = BLUE_2
                    hover = BLUE
                # CustomTkinter border_color transparan kabul etmiyor; boş günlerde de gerçek renk veriyoruz.
                border_col = fg if day else CARD
                cell = ctk.CTkFrame(grid, fg_color=fg, corner_radius=10, height=56, border_width=1 if day else 0, border_color=border_col)
                cell.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
                if day:
                    try:
                        cell.configure(cursor="hand2")
                    except Exception:
                        pass
                    text = lbl(cell, str(day), 13, "bold")
                    text.place(relx=0.5, rely=0.45, anchor="center")
                    dots = self._event_types_for_day(date(self.yil, self.ay, day))
                    if dots:
                        dot_row = ctk.CTkFrame(cell, fg_color="transparent")
                        dot_row.place(relx=0.5, rely=0.78, anchor="center")
                        for renk in dots[:4]:
                            ctk.CTkLabel(dot_row, text="●", text_color=renk, font=(FONT, 9)).pack(side="left", padx=1)
                    self._bind_day_cell(cell, text, day, fg, hover)

    def _event_types_for_day(self, d):
        renkler = []
        for baslik, detay, renk in self._events_for_day(d):
            if renk not in renkler:
                renkler.append(renk)
        return renkler

    def _bind_day_cell(self, cell, text_widget, day, normal_color, hover_color):
        def enter(_=None):
            try:
                cell.configure(fg_color=hover_color, border_color=GREEN, border_width=2)
            except Exception:
                pass
        def leave(_=None):
            try:
                cell.configure(fg_color=normal_color, border_color=normal_color, border_width=1)
            except Exception:
                pass
        def click(_=None):
            self.open_day_detail(day)
        for w in (cell, text_widget):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)

    def open_day_detail(self, day):
        d = date(self.yil, self.ay, day)
        win = ctk.CTkToplevel(self)
        win.title(f"Gün Detayı - {d.isoformat()}")
        win.geometry("520x430")
        win.configure(fg_color=BG)
        win.grab_set()
        lbl(win, f"{d.strftime('%d.%m.%Y')} Gün Detayı", 20, "bold").pack(anchor="w", padx=22, pady=(22, 8))
        box = ctk.CTkScrollableFrame(win, fg_color=BG_2, corner_radius=16)
        box.pack(fill="both", expand=True, padx=22, pady=(8, 22))
        events = self._events_for_day(d)
        if not events:
            lbl(box, "Bu gün için kayıtlı ders, sınav veya ödev yok.", 13, "normal", MUTED).pack(anchor="w", padx=16, pady=18)
        for ev in events:
            c = ctk.CTkFrame(box, fg_color=CARD, corner_radius=13, border_width=1, border_color=BORDER)
            c.pack(fill="x", padx=10, pady=6)
            lbl(c, ev[0], 13, "bold", ev[2]).pack(anchor="w", padx=12, pady=(10, 3))
            lbl(c, ev[1], 11, "normal", MUTED, wraplength=430, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    def _events_for_day(self, d):
        events = []
        weekday_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        weekday = weekday_names[d.weekday()]
        for k in get_courses():
            gunler = k.get("takvim_gunler") or k.get("gunler") or []
            if isinstance(gunler, str):
                gunler = [x.strip() for x in gunler.split(",") if x.strip()]
            if weekday in gunler:
                events.append((f"Ders • {k.get('takvim_saat') or k.get('saat') or 'Saat belirtilmedi'}", f"{k.get('kurs_adi','Kurs')} - Eğitmen: {egitmen_adi(k.get('egitmen_id'))}", GREEN))
            if k.get("sinav_tarihi") == d.isoformat() or k.get("sinav") == d.isoformat():
                events.append(("Sınav", f"{k.get('kurs_adi','Kurs')} sınavı", YELLOW))
        try:
            v = db.veri_yukle()
            for o in v.get("odevler", []):
                if o.get("son_teslim") == d.isoformat() or o.get("son_tarih") == d.isoformat() or o.get("tarih") == d.isoformat():
                    events.append(("Ödev", o.get("baslik", "Ödev teslim tarihi"), ORANGE))
            for ev in v.get("ozel_takvim_etkinlikleri", []):
                if ev.get("tarih") == d.isoformat():
                    renk = BLUE if ev.get("renk") == "mavi" else GREEN if ev.get("renk") == "yesil" else ORANGE
                    events.append((ev.get("tur", "Etkinlik").capitalize(), ev.get("baslik", "Özel etkinlik") + " - " + ev.get("aciklama", ""), renk))
        except Exception:
            pass
        return events

    def go_today(self):
        self.today = date.today()
        self.yil = self.today.year
        self.ay = self.today.month
        self.build()

    def prev(self):
        self.ay -= 1
        if self.ay == 0:
            self.ay = 12; self.yil -= 1
        self.build()

    def next(self):
        self.ay += 1
        if self.ay == 13:
            self.ay = 1; self.yil += 1
        self.build()


class CalendarDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Takvim")
        self.geometry("880x640")
        self.configure(fg_color=BG)
        self.grab_set()
        TakvimWidget(self).pack(fill="both", expand=True, padx=20, pady=20)


class ProfileMenu(ctk.CTkToplevel):
    def __init__(self, master, user, panel):
        super().__init__(master)
        self.user = user
        self.panel = panel
        self.title("Profil")
        self.geometry("260x260")
        self.configure(fg_color=BG_2)
        self.grab_set()
        lbl(self, user.get("ad", "Kullanıcı"), 17, "bold").pack(pady=(24, 4))
        lbl(self, user.get("rol", "").capitalize(), 11, "normal", MUTED).pack(pady=(0, 16))
        btn(self, "Şifre Değiştir", lambda: toast(self, "Şifre değiştirme ekranı hazır."), BG_3, BG_3, 200, 36).pack(pady=5)
        btn(self, "Takvim", lambda: CalendarDialog(master), BG_3, BG_3, 200, 36).pack(pady=5)
        btn(self, "Çıkış Yap", self.logout, RED, RED, 200, 36).pack(pady=16)

    def logout(self):
        self.destroy()
        self.panel.master.show_login()


class AssistantDialog(ctk.CTkToplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.title("Platform Asistanı")
        self.geometry("420x480")
        self.configure(fg_color=BG)
        self.grab_set()
        lbl(self, "Platform Asistanı", 18, "bold", GREEN).pack(anchor="w", padx=18, pady=(18,4))
        self.box = ctk.CTkTextbox(self, fg_color=BG_3, text_color=TEXT, wrap="word")
        self.box.pack(fill="both", expand=True, padx=18, pady=12)
        self.box.insert("end", "Merhaba! Derse kayıt, ders odası, takvim, başvuru ve admin işlemleri hakkında soru sorabilirsin.\n")
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=18, pady=(0, 18))
        self.entry = ctk.CTkEntry(bottom, placeholder_text="Sorunu yaz...", fg_color=BG_3, border_color=BORDER)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        btn(bottom, "Sor", self.answer, GREEN, GREEN_2, 70, 34).pack(side="right")
        self.entry.bind("<Return>", lambda e: self.answer())

    def answer(self):
        q = self.entry.get().strip().lower()
        if not q:
            return
        self.box.insert("end", f"\nSen: {q}\n")
        if "kayıt" in q or "ders" in q:
            a = "Ders Kaydı ekranından kurs seçip Kayıt Ol butonuna bas. Kayıtlı kurslarda Derse Git ders odasını açar."
        elif "admin" in q or "başvuru" in q:
            a = "Admin panelindeki Başvurular ekranından öğretmen/admin başvurularını onaylayabilirsin."
        elif "takvim" in q:
            a = "Takvim ekranında ders ve sınav günlerini görebilirsin."
        else:
            a = "Sol menü kategorilerinden ilgili ekranı açabilirsin. Yardım sayfasında tüm kullanım özetleri var."
        self.box.insert("end", f"Asistan: {a}\n")
        self.entry.delete(0, "end")



# ─────────────────────────────────────────────────────────────────────────────
# SON DESTEK / ADMIN / ASİSTAN GÜNCELLEMELERİ
# ─────────────────────────────────────────────────────────────────────────────

def _safe_get_user_name(kid, role=None):
    if not kid:
        return "Bilinmeyen Kullanıcı"
    try:
        v = db.veri_yukle()
        for o in v.get("ogrenciler", []):
            if kid in [o.get("ogrenci_id"), o.get("id")]:
                return o.get("ad", kid)
        for e in v.get("egitmenler", []):
            if kid in [e.get("egitmen_id"), e.get("id")]:
                return e.get("ad", kid)
        for a in v.get("adminler", []):
            if kid in [a.get("admin_id"), a.get("id")]:
                return a.get("ad", kid)
        adm = v.get("admin", {})
        if kid in [adm.get("admin_id"), adm.get("id"), "admin"]:
            return adm.get("ad", "Admin")
    except Exception:
        pass
    return str(kid)


def _ticket_status_color(status):
    s = str(status or "").lower()
    if "tamam" in s or "kapat" in s or "sonuç" in s:
        return GREEN
    if "işlem" in s or "cevap" in s:
        return YELLOW
    return RED if "yüksek" in s else YELLOW


def _normalize_ticket(t):
    """Eski destek kayıtlarını forum gibi mesajlaşma yapısına çevirir."""
    if "mesajlar" not in t or not isinstance(t.get("mesajlar"), list) or not t.get("mesajlar"):
        t["mesajlar"] = [{
            "yazar_id": t.get("kullanici_id", ""),
            "rol": t.get("rol", "kullanici"),
            "mesaj": t.get("mesaj", ""),
            "tarih": t.get("tarih", "")
        }]
        if t.get("cevap"):
            t["mesajlar"].append({
                "yazar_id": "admin",
                "rol": "admin",
                "mesaj": t.get("cevap"),
                "tarih": t.get("cevap_tarihi", "")
            })
    return t


def _save_ticket_message(talep_id, yazar_id, rol, mesaj):
    veri = db.veri_yukle()
    for t in veri.get("destek_talepleri", []):
        if t.get("talep_id") == talep_id:
            _normalize_ticket(t)
            if str(t.get("durum", "")).lower() in ["tamamlandı", "kapatıldı", "sonuçlandı"]:
                return False
            t.setdefault("mesajlar", []).append({
                "yazar_id": yazar_id,
                "rol": rol,
                "mesaj": mesaj,
                "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            if rol == "admin":
                t["durum"] = "İşlemde"
                t["cevap"] = mesaj
                t["cevap_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            else:
                if str(t.get("durum", "")).lower() not in ["tamamlandı", "kapatıldı"]:
                    t["durum"] = "açık"
            db.veri_kaydet(veri)
            return True
    return False


def _set_ticket_completed(talep_id):
    veri = db.veri_yukle()
    for t in veri.get("destek_talepleri", []):
        if t.get("talep_id") == talep_id:
            _normalize_ticket(t)
            t["durum"] = "Tamamlandı"
            t.setdefault("mesajlar", []).append({
                "yazar_id": "admin",
                "rol": "admin",
                "mesaj": "Destek talebi sonuçlandırıldı.",
                "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            db.veri_kaydet(veri)
            return True
    return False


class SupportThreadDialog(ctk.CTkToplevel):
    def __init__(self, master, talep_id, user, is_admin=False, on_update=None):
        super().__init__(master)
        self.talep_id = talep_id
        self.user = user
        self.is_admin = is_admin
        self.on_update = on_update
        self.title("Destek Görüşmesi")
        self.geometry("760x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def get_ticket(self):
        for t in db.veri_yukle().get("destek_talepleri", []):
            if t.get("talep_id") == self.talep_id:
                return _normalize_ticket(t.copy())
        return None

    def build(self):
        clear(self)
        t = self.get_ticket()
        if not t:
            lbl(self, "Destek talebi bulunamadı.", 16, "bold", RED).pack(padx=20, pady=20)
            return
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(18, 8))
        lbl(header, t.get("konu", "Destek Talebi"), 20, "bold", GREEN).pack(anchor="w")
        status = t.get("durum", "açık")
        who = _safe_get_user_name(t.get("kullanici_id"), t.get("rol"))
        lbl(header, f"Talep sahibi: {who}  •  Durum: {status}", 12, "normal", _ticket_status_color(status)).pack(anchor="w", pady=(4, 0))

        area = ctk.CTkScrollableFrame(self, fg_color=BG_2, corner_radius=16, border_width=1, border_color=BORDER)
        area.pack(fill="both", expand=True, padx=22, pady=10)
        for m in t.get("mesajlar", []):
            role = m.get("rol", "")
            mine = (m.get("yazar_id") == user_id(self.user)) or (self.is_admin and role == "admin")
            bubble = ctk.CTkFrame(area, fg_color=GREEN if role == "admin" else BG_3, corner_radius=14, border_width=1, border_color=BORDER)
            bubble.pack(anchor="e" if mine else "w", fill="x", padx=12, pady=6)
            title = "Admin" if role == "admin" else _safe_get_user_name(m.get("yazar_id"), role)
            lbl(bubble, f"{title}  •  {m.get('tarih','')}", 11, "bold", "white" if role == "admin" else GREEN).pack(anchor="w", padx=12, pady=(8, 2))
            lbl(bubble, m.get("mesaj", ""), 12, "normal", "white" if role == "admin" else TEXT, wraplength=640, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=22, pady=(4, 18))
        completed = str(status).lower() in ["tamamlandı", "kapatıldı", "sonuçlandı"]
        if completed:
            lbl(bottom, "Bu destek talebi tamamlandı. Yeni mesaj yazılamaz.", 12, "bold", GREEN).pack(side="left", padx=6, pady=8)
        else:
            self.entry = ctk.CTkEntry(bottom, placeholder_text="Cevap yaz...", fg_color=BG_3, border_color=BORDER, height=40)
            self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
            btn(bottom, "Gönder", self.send_reply, GREEN, GREEN_2, 90, 40).pack(side="left", padx=(0, 8))
            if self.is_admin:
                btn(bottom, "Sonuçlandı", self.complete_ticket, GREEN, GREEN_2, 118, 40).pack(side="left")
            self.entry.bind("<Return>", lambda e: self.send_reply())

    def send_reply(self):
        if not hasattr(self, "entry"):
            toast(self.master, "Tamamlanan destek talebine mesaj yazılamaz.", YELLOW)
            return
        msg = self.entry.get().strip()
        if not msg:
            return
        ok = _save_ticket_message(self.talep_id, "admin" if self.is_admin else user_id(self.user), "admin" if self.is_admin else self.user.get("rol", "ogrenci"), msg)
        if not ok:
            toast(self.master, "Tamamlanan destek talebine mesaj yazılamaz.", YELLOW)
            self.build()
            return
        if self.on_update:
            try:
                self.on_update()
            except Exception:
                pass
        self.build()

    def complete_ticket(self):
        _set_ticket_completed(self.talep_id)
        toast(self.master, "Destek talebi tamamlandı.", GREEN)
        if self.on_update:
            try:
                self.on_update()
            except Exception:
                pass
        self.build()


def _new_support_page(self, f):
    self.header(f, "Destek", "Sorun bildirimi oluşturabilir ve destek konuşmalarını takip edebilirsin.")
    outer, wrap = self.full_scroll_container(f)

    form = card(wrap, fill="x", padx=6, pady=6)
    lbl(form, "Yeni Destek Talebi", 16, "bold", GREEN).pack(anchor="w", padx=16, pady=(14, 6))
    konu = ctk.CTkEntry(form, placeholder_text="Konu başlığı", fg_color=BG_3, border_color=BORDER)
    konu.pack(fill="x", padx=16, pady=6)
    prio = ctk.CTkOptionMenu(form, values=["Düşük", "Orta", "Yüksek"], fg_color=BLUE, button_color=BLUE_2)
    prio.set("Orta")
    prio.pack(anchor="w", padx=16, pady=6)
    # CTkTextbox bazı Windows/Tk sürümlerinde hızlı refresh sonrası focus hatası üretebiliyor.
    # Bu yüzden destek açıklaması için stabil CTkEntry kullanıyoruz.
    aciklama = ctk.CTkEntry(form, placeholder_text="Açıklama yaz...", fg_color=BG_3, border_color=BORDER, height=42)
    aciklama.pack(fill="x", padx=16, pady=6)

    def send():
        k = konu.get().strip(); m = aciklama.get().strip(); p = prio.get()
        if not k or not m:
            messagebox.showwarning("Eksik", "Konu ve açıklama yazmalısın.")
            return
        ok, res = db.destek_talebi_ekle(user_id(self.user), self.user.get("rol", "ogrenci"), f"[{p}] {k}", m)
        # Yeni destek kaydına mesaj geçmişi ekle.
        try:
            veri = db.veri_yukle()
            for t in reversed(veri.get("destek_talepleri", [])):
                if t.get("kullanici_id") == user_id(self.user) and t.get("konu") == f"[{p}] {k}":
                    _normalize_ticket(t)
                    break
            db.veri_kaydet(veri)
        except Exception:
            pass
        mail_ok = False
        if mail_servisi:
            try:
                mail_ok, _ = mail_servisi._mail_gonder(f"[Destek - {p}] {k}", f"Kullanıcı: {self.user.get('ad')} ({user_id(self.user)})\nRol: {self.user.get('rol')}\nÖncelik: {p}\n\n{m}")
            except Exception:
                mail_ok = False
        toast(self.master, "Destek talebi gönderildi." + (" Mail iletildi." if mail_ok else ""), GREEN)
        self.refresh()

    btn(form, "Gönder", send, GREEN, GREEN_2, 120, 36).pack(anchor="w", padx=16, pady=(4, 14))

    lbl(wrap, "Geçmiş Destek Taleplerim", 16, "bold", GREEN).pack(anchor="w", padx=8, pady=(18, 6))
    rows = db.destek_talepleri_getir(user_id(self.user)) if hasattr(db, "destek_talepleri_getir") else []
    if not rows:
        lbl(wrap, "Henüz destek talebin yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=10)
    for r in rows:
        _normalize_ticket(r)
        durum = r.get("durum", "açık")
        c = card(wrap, fill="x", pady=6)
        c.configure(cursor="hand2")
        lbl(c, f"{r.get('konu')}  •  {durum}", 13, "bold", _ticket_status_color(durum), wraplength=900).pack(anchor="w", padx=16, pady=(10, 2))
        last = (r.get("mesajlar") or [{}])[-1]
        lbl(c, f"Son mesaj: {last.get('mesaj','')}", 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0, 10))
        c.bind("<Button-1>", lambda e, tid=r.get("talep_id"): SupportThreadDialog(self.master, tid, self.user, False, self.refresh))
        for child in c.winfo_children():
            child.bind("<Button-1>", lambda e, tid=r.get("talep_id"): SupportThreadDialog(self.master, tid, self.user, False, self.refresh))


def _admin_support_page(self, f):
    self.header(f, "Destek Yönetimi", "Öğrenci ve öğretmen destek taleplerine cevap verip sonuçlandırabilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.destek_talepleri_getir() if hasattr(db, "destek_talepleri_getir") else db.veri_yukle().get("destek_talepleri", [])
    if not rows:
        lbl(wrap, "Henüz destek talebi yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for r in rows:
        _normalize_ticket(r)
        durum = r.get("durum", "açık")
        c = card(wrap, fill="x", pady=6)
        lbl(c, f"{r.get('konu')}  •  {durum}", 13, "bold", _ticket_status_color(durum), wraplength=900).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Gönderen: {_safe_get_user_name(r.get('kullanici_id'), r.get('rol'))} ({r.get('rol')})", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(4, 12))
        btn(row, "Konuşmayı Aç", lambda tid=r.get("talep_id"): SupportThreadDialog(self.master, tid, self.user, True, self.refresh), BLUE, BLUE_2, 140, 30).pack(side="left", padx=(0, 8))
        if str(durum).lower() not in ["tamamlandı", "kapatıldı", "sonuçlandı"]:
            btn(row, "Sonuçlandı", lambda tid=r.get("talep_id"): ( _set_ticket_completed(tid), toast(self.master, "Destek tamamlandı.", GREEN), self.refresh() ), GREEN, GREEN_2, 110, 30).pack(side="left")
        else:
            lbl(row, "Tamamlandı", 12, "bold", GREEN).pack(side="left", padx=8)


def _admin_delete_user(kid, role):
    veri = db.veri_yukle()
    if role == "ogrenci":
        veri["ogrenciler"] = [o for o in veri.get("ogrenciler", []) if kid not in [o.get("ogrenci_id"), o.get("id")]]
        for k in veri.get("kurslar", []):
            k["kayitli_ogrenciler"] = [x for x in k.get("kayitli_ogrenciler", []) if x != kid]
        veri["kayitlar"] = [x for x in veri.get("kayitlar", []) if x.get("ogrenci_id") != kid]
    elif role == "egitmen":
        veri["egitmenler"] = [e for e in veri.get("egitmenler", []) if kid not in [e.get("egitmen_id"), e.get("id")]]
    elif role == "admin":
        veri["adminler"] = [a for a in veri.get("adminler", []) if kid not in [a.get("admin_id"), a.get("id")]]
    db.veri_kaydet(veri)


def _admin_users_page(self, f):
    self.header(f, "Kullanıcı Yönetimi", "Öğrenci ve öğretmenleri sistemden kaldırabilir, kullanıcıları kontrol edebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    v = db.veri_yukle()
    groups = [("Öğrenciler", "ogrenci", v.get("ogrenciler", [])), ("Öğretmenler", "egitmen", v.get("egitmenler", [])), ("Adminler", "admin", v.get("adminler", []))]
    for title, role, arr in groups:
        lbl(wrap, title, 17, "bold", GREEN).pack(anchor="w", padx=8, pady=(14, 6))
        for u in arr[:80]:
            kid = u.get("ogrenci_id") or u.get("egitmen_id") or u.get("admin_id") or u.get("id")
            c = card(wrap, fill="x", pady=4)
            lbl(c, f"{kid} - {u.get('ad')} - {u.get('email','')}", 12, "normal", TEXT, wraplength=860).pack(side="left", padx=16, pady=10)
            if kid != "admin":
                btn(c, "Kaldır", lambda x=kid, r=role: ( _admin_delete_user(x, r), toast(self.master, "Kullanıcı kaldırıldı.", RED), self.refresh() ), RED, RED, 90, 30).pack(side="right", padx=12, pady=8)


def _admin_close_course(kid):
    veri = db.veri_yukle()
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kid:
            k["kapali"] = True
            k["durum"] = "kapalı"
            k["materyaller"] = []
            k["materyaller_kaldirildi"] = True
    db.veri_kaydet(veri)


def _admin_courses_page(self, f):
    self.header(f, "Kurs Yönetimi", "Kursları inceleyebilir ve kapatabilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for k in get_courses():
        c = card(wrap, fill="x", pady=5)
        durum = "Kapalı" if k.get("kapali") or k.get("durum") == "kapalı" else "Açık"
        lbl(c, f"{k.get('kurs_adi')}  •  {durum}", 13, "bold", RED if durum == "Kapalı" else GREEN, wraplength=860).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Öğretmen: {egitmen_adi(k.get('egitmen_id'))}  •  Öğrenci: {len(k.get('kayitli_ogrenciler', []))}/{k.get('kontenjan')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        btn(c, "Kursu Kapat", lambda kid=k.get("kurs_id"): ( _admin_close_course(kid), toast(self.master, "Kurs kapatıldı.", RED), self.refresh() ), RED, RED, 120, 30).pack(anchor="w", padx=16, pady=(6, 12))


def _delete_forum_topic(tid):
    veri = db.veri_yukle()
    veri["forum_konulari"] = [t for t in veri.get("forum_konulari", []) if t.get("konu_id") != tid]
    db.veri_kaydet(veri)


def _delete_forum_comment(tid, idx):
    veri = db.veri_yukle()
    for t in veri.get("forum_konulari", []):
        if t.get("konu_id") == tid:
            comments = t.get("yorumlar", [])
            if 0 <= idx < len(comments):
                comments.pop(idx)
    db.veri_kaydet(veri)


def _admin_forum_page(self, f):
    self.header(f, "Forum Yönetimi", "Forum konularını ve mesajlarını silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for t in db.veri_yukle().get("forum_konulari", []):
        c = card(wrap, fill="x", pady=7)
        lbl(c, t.get("baslik", "Konu"), 14, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, t.get("aciklama", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Konuyu Sil", lambda tid=t.get("konu_id"): ( _delete_forum_topic(tid), toast(self.master, "Forum konusu silindi.", RED), self.refresh() ), RED, RED, 110, 28).pack(anchor="w", padx=16, pady=(6,6))
        for i, y in enumerate(t.get("yorumlar", [])[:10]):
            row = ctk.CTkFrame(c, fg_color=BG_3, corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            lbl(row, f"{_safe_get_user_name(y.get('ogrenci_id') or y.get('yazar_id'))}: {y.get('yorum') or y.get('mesaj','')}", 11, "normal", TEXT, wraplength=720).pack(side="left", fill="x", expand=True, padx=10, pady=6)
            btn(row, "Sil", lambda tid=t.get("konu_id"), ix=i: ( _delete_forum_comment(tid, ix), toast(self.master, "Forum mesajı silindi.", RED), self.refresh() ), RED, RED, 55, 24).pack(side="right", padx=8)


def _delete_material(kid, idx):
    veri = db.veri_yukle()
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kid:
            mats = k.get("materyaller", [])
            if 0 <= idx < len(mats):
                mats.pop(idx)
    db.veri_kaydet(veri)


def _admin_materials_page(self, f):
    self.header(f, "Materyal Yönetimi", "Ders materyallerini inceleyebilir ve silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for k in get_courses():
        mats = k.get("materyaller", [])
        if not mats:
            continue
        c = card(wrap, fill="x", pady=6)
        lbl(c, k.get("kurs_adi"), 14, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 4))
        for i, m in enumerate(mats):
            row = ctk.CTkFrame(c, fg_color=BG_3, corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            lbl(row, f"{m.get('baslik')}  •  {m.get('link','')}", 11, "normal", TEXT, wraplength=720).pack(side="left", fill="x", expand=True, padx=10, pady=6)
            btn(row, "Sil", lambda kid=k.get("kurs_id"), ix=i: ( _delete_material(kid, ix), toast(self.master, "Materyal silindi.", RED), self.refresh() ), RED, RED, 55, 24).pack(side="right", padx=8)


def _new_admin_init(self, master, user):
    BasePanel.__init__(self, master, user, BLUE)
    self.add_menus([
        ("Panel", "", self.dashboard),
        ("Kullanıcılar", "", self.users_page),
        ("Başvurular", "", self.applications_page),
        ("Kurslar", "", self.courses_page),
        ("Materyaller", "", self.admin_materials_page),
        ("Forum", "", self.admin_forum_page),
        ("Destek", "", self.support_page),
        ("Duyuru", "", self.announcement_page),
        ("Yardım", "", lambda f: self.generic_page(f, "Yardım", "Admin; kullanıcıları, kursları, forumu, materyalleri ve destek taleplerini yönetebilir.")),
    ])


def _assistant_answer(self):
    q_raw = self.entry.get().strip()
    q = q_raw.lower()
    if not q:
        return
    self.box.insert("end", f"\nSen: {q_raw}\n")
    role = self.user.get("rol", "")
    cevaplar = []
    if any(k in q for k in ["rozet", "başarım", "xp", "hedef"]):
        cevaplar.append("Rozetlerini sol menüde Kişisel > Hedef/Rozet bölümünden görebilirsin. Gri rozetler kazanılmamış, parlak rozetler kazanılmıştır. Yeşil bar görev ilerlemeni gösterir.")
    if any(k in q for k in ["forum", "konu", "cevap"]):
        cevaplar.append("Forum ekranında konu başlıklarına tıklayıp cevap yazabilirsin. Admin forumdaki uygunsuz konuları ve mesajları silebilir.")
    if any(k in q for k in ["destek", "talep", "sorun"]):
        cevaplar.append("Destek ekranında konu, öncelik ve açıklama girerek talep açabilirsin. Talebine tıklayınca adminle konuşma gibi mesajlaşabilirsin.")
    if any(k in q for k in ["materyal", "pdf", "link", "kaynak"]):
        cevaplar.append("Materyaller ekranında ders kaynaklarını açabilirsin. Öğretmenler kendi derslerine materyal adı ve link girerek yeni kaynak ekleyebilir.")
    if any(k in q for k in ["ödev", "odev"]):
        cevaplar.append("Ödevler ekranında son teslim tarihlerini ve açıklamaları görebilirsin. Öğretmen ödev eklediğinde takvimde de görünür.")
    if any(k in q for k in ["sınav", "sinav", "quiz"]):
        cevaplar.append("Sınavlar ekranında sınav tarihini, kaç gün kaldığını ve çalışma kaynaklarını görebilirsin. Öğretmen sınav eklediğinde takvim güncellenir.")
    if any(k in q for k in ["takvim", "gün", "gun"]):
        cevaplar.append("Üstteki Takvim butonundan ay görünümünü açabilirsin. Güne tıklayınca ders, sınav ve ödev detayları görünür.")
    if any(k in q for k in ["ders", "kayıt", "kayit", "derse git"]):
        cevaplar.append("Ders Kaydı ekranından dersi seçip Kayıt Ol butonuna bas. Kayıtlı derslerde Derse Git butonu ders odasını açar.")
    if any(k in q for k in ["admin", "sil", "kapat", "yetki"]):
        cevaplar.append("Admin; kullanıcıları kaldırabilir, kursları kapatabilir, forum mesajlarını, materyalleri ve destek taleplerini yönetebilir.")
    if any(k in q for k in ["tema", "beyaz", "gece"]):
        cevaplar.append("Sağ üst profil menüsünden Tema Değiştir butonuyla gece ve gri-açık tema arasında geçebilirsin.")
    if not cevaplar:
        if role == "egitmen":
            cevaplar.append("Öğretmen olarak Derslerim, Materyaller, Ödevler ve Sınavlar ekranlarından ders içeriklerini yönetebilirsin. Destek ve Forum ekranları öğrencilerle iletişim için kullanılabilir.")
        elif role == "admin":
            cevaplar.append("Admin panelinde kullanıcı, kurs, materyal, forum ve destek yönetimi yapabilirsin. Bir destek talebini açıp cevaplayabilir veya Sonuçlandı yapabilirsin.")
        else:
            cevaplar.append("Sol menüden Ders Kaydı, Materyaller, Ödevler, Sınavlar, Forum, Mesajlar, Destek ve Hedef/Rozet ekranlarını kullanabilirsin. Hangi ekranı merak ediyorsan adını yazman yeterli.")
    self.box.insert("end", "Asistan: " + "\n".join(cevaplar) + "\n")
    self.box.see("end")
    self.entry.delete(0, "end")

# Yöntemleri sınıflara bağla
OgrenciPanel.support_page = _new_support_page
EgitmenPanel.support_page = _new_support_page
AdminPanel.support_page = _admin_support_page
AdminPanel.users_page = _admin_users_page
AdminPanel.courses_page = _admin_courses_page
AdminPanel.admin_forum_page = _admin_forum_page
AdminPanel.admin_materials_page = _admin_materials_page
AdminPanel.__init__ = _new_admin_init
AssistantDialog.answer = _assistant_answer



# ─────────────────────────────────────────────────────────────────────────────
# SON BUGFIX PATCH: E-posta/şifre güvenliği, mesajlar, yardım, rozetler, yoklama kaldırma
# ─────────────────────────────────────────────────────────────────────────────
def _valid_email(value):
    value = (value or "").strip()
    return "@" in value and value.index("@") > 0 and value.rindex("@") < len(value) - 1


def _password_strength_value(pw):
    pw = pw or ""
    score = 0
    if len(pw) >= 6: score += 1
    if len(pw) >= 10: score += 1
    if any(c.islower() for c in pw): score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(not c.isalnum() for c in pw): score += 1
    if score <= 2:
        return 0.25, "Düşük güvenlik", RED
    if score <= 4:
        return 0.62, "Orta güvenlik", ORANGE
    return 1.0, "İyi güvenlik", GREEN


def _make_strength_meter(parent):
    box = ctk.CTkFrame(parent, fg_color="transparent")
    label = lbl(box, "Şifre güvenliği: -", 11, "bold", MUTED)
    label.pack(anchor="w", padx=0, pady=(0, 4))
    bar_bg = ctk.CTkFrame(box, fg_color=BG_3, corner_radius=7, height=12, border_width=1, border_color=BORDER)
    bar_bg.pack(fill="x")
    bar_bg.pack_propagate(False)
    fill = ctk.CTkFrame(bar_bg, fg_color=RED, corner_radius=7, width=1)
    fill.place(relx=0, rely=0, relheight=1, relwidth=0.02)
    def update(pw):
        width, text_value, color = _password_strength_value(pw)
        label.configure(text=f"Şifre güvenliği: {text_value}", text_color=color)
        fill.configure(fg_color=color)
        fill.place_configure(relwidth=width)
    return box, update


def _student_register_init(self, master):
    ctk.CTkToplevel.__init__(self, master)
    self.title("Öğrenci Kaydı")
    self.geometry("430x540")
    self.configure(fg_color=BG)
    self.grab_set()
    lbl(self, "Yeni Öğrenci Kaydı", 22, "bold").pack(pady=(28, 12))
    self.entries = []
    for ph in ["Öğrenci ID", "Ad Soyad", "E-posta"]:
        e = ctk.CTkEntry(self, placeholder_text=ph, width=310, height=42, fg_color=BG_3, border_color=BORDER)
        e.pack(pady=6)
        self.entries.append(e)
    meter_box, self._update_strength = _make_strength_meter(self)
    meter_box.pack(fill="x", padx=60, pady=(6, 2))
    self.pass_entry = ctk.CTkEntry(self, placeholder_text="Şifre", show="●", width=310, height=42, fg_color=BG_3, border_color=BORDER)
    self.pass_entry.pack(pady=6)
    self.pass_entry.bind("<KeyRelease>", lambda e: self._update_strength(self.pass_entry.get()))
    self.entries.append(self.pass_entry)
    lbl(self, "E-posta alanında @gmail.com zorunludur.", 10, "normal", MUTED).pack(pady=(4, 0))
    btn(self, "Kaydı Tamamla", self.save, GREEN, GREEN_2, 310, 44).pack(pady=20)


def _student_register_save(self):
    vals = [e.get().strip() for e in self.entries]
    if not all(vals):
        messagebox.showwarning("Eksik bilgi", "Tüm alanları doldurun.")
        return
    if not _valid_email(vals[2]):
        messagebox.showwarning("Geçersiz e-posta", "E-posta adresi @gmail.com ile bitmelidir.")
        return
    ok, msg = db.ogrenci_ekle(vals[0], vals[1], vals[2], vals[3])
    messagebox.showinfo("Bilgi", msg)
    if ok:
        self.destroy()


def _application_init(self, master):
    ctk.CTkToplevel.__init__(self, master)
    self.title("Öğretmen/Admin Başvurusu")
    self.geometry("470x620")
    self.configure(fg_color=BG)
    self.grab_set()
    lbl(self, "Hesap Başvurusu", 22, "bold").pack(pady=(24, 8))
    self.role = ctk.StringVar(value="Öğretmen")
    ctk.CTkSegmentedButton(self, values=["Öğretmen", "Admin"], variable=self.role, fg_color=BG_3, selected_color=GREEN, selected_hover_color=GREEN_2).pack(pady=8)
    self.id_entry = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.name_entry = ctk.CTkEntry(self, placeholder_text="Ad Soyad", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.email_entry = ctk.CTkEntry(self, placeholder_text="E-posta", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.spec_entry = ctk.CTkEntry(self, placeholder_text="Uzmanlık / Açıklama", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    for e in [self.id_entry, self.name_entry, self.email_entry, self.spec_entry]:
        e.pack(pady=6)
    meter_box, self._update_strength = _make_strength_meter(self)
    meter_box.pack(fill="x", padx=60, pady=(6, 2))
    self.pass_entry = ctk.CTkEntry(self, placeholder_text="Şifre", show="●", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.pass_entry.pack(pady=6)
    self.pass_entry.bind("<KeyRelease>", lambda e: self._update_strength(self.pass_entry.get()))
    btn(self, "Başvuru Gönder", self.send, GREEN, GREEN_2, 315, 44).pack(pady=18)
    lbl(self, "E-posta için @gmail.com zorunludur. Başvuru maili ayarlar doğruysa ana e-postana gider.", 10, "normal", MUTED, wraplength=320).pack()


def _application_send(self):
    rid = self.id_entry.get().strip(); name = self.name_entry.get().strip()
    email = self.email_entry.get().strip(); spec = self.spec_entry.get().strip(); pw = self.pass_entry.get().strip()
    if not all([rid, name, email, pw]):
        messagebox.showwarning("Eksik bilgi", "ID, ad, e-posta ve şifre zorunludur.")
        return
    if not _valid_email(email):
        messagebox.showwarning("Geçersiz e-posta", "E-posta adresi @gmail.com ile bitmelidir.")
        return
    if self.role.get() == "Öğretmen":
        ok, msg = db.egitmen_ekle(rid, name, spec or "Belirtilmedi", email, pw)
    else:
        ok, msg = db.admin_basvuru_ekle(rid, name, email, pw, spec or "Admin yetkisi başvurusu")
    messagebox.showinfo("Bilgi", msg)
    if ok:
        self.destroy()


StudentRegisterDialog.__init__ = _student_register_init
StudentRegisterDialog.save = _student_register_save
ApplicationDialog.__init__ = _application_init
ApplicationDialog.send = _application_send


# Mesajlaşma sistemi: öğrenci/öğretmen arasında basit konuşma kutusu.
def _msg_user_id(u):
    return u.get("id") or u.get("ogrenci_id") or u.get("egitmen_id") or u.get("admin_id") or u.get("kullanici_adi") or ""


def _msg_user_name(uid):
    try:
        v = db.veri_yukle()
        for key in ("ogrenciler", "egitmenler", "adminler"):
            for u in v.get(key, []):
                if uid in [u.get("id"), u.get("ogrenci_id"), u.get("egitmen_id"), u.get("admin_id"), u.get("kullanici_adi")]:
                    return u.get("ad", uid)
    except Exception:
        pass
    return uid


def _ensure_message_threads(veri):
    raw = veri.setdefault("mesajlar", [])
    threads = veri.setdefault("mesaj_konusmalari", [])
    # Eski düz mesaj varsa bozmadan konuşma sistemine de gösterilebilir hale getir.
    for m in raw:
        if not isinstance(m, dict):
            continue
        sender = m.get("gonderen") or m.get("from") or m.get("ogrenci_id") or m.get("yazar_id")
        receiver = m.get("alici") or m.get("to") or m.get("egitmen_id")
        if not sender or not receiver:
            continue
        tid = "MSG" + "_".join(sorted([str(sender), str(receiver)]))
        if not any(t.get("konusma_id") == tid for t in threads):
            threads.append({
                "konusma_id": tid,
                "katilimcilar": [sender, receiver],
                "mesajlar": [{"yazar_id": sender, "mesaj": m.get("mesaj", ""), "tarih": m.get("tarih", "")}],
                "tarih": m.get("tarih", datetime.now().strftime("%d.%m.%Y %H:%M")),
            })
    return threads


def _message_threads_for(uid):
    v = db.veri_yukle()
    threads = _ensure_message_threads(v)
    db.veri_kaydet(v)
    return [t for t in threads if uid in t.get("katilimcilar", [])]


def _get_or_create_thread(a, b):
    v = db.veri_yukle()
    threads = _ensure_message_threads(v)
    for t in threads:
        participants = set(t.get("katilimcilar", []))
        if participants == {a, b}:
            db.veri_kaydet(v)
            return t.get("konusma_id")
    tid = f"MSG{len(threads)+1:04d}"
    threads.append({"konusma_id": tid, "katilimcilar": [a, b], "mesajlar": [], "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
    db.veri_kaydet(v)
    return tid


def _send_thread_message(tid, sender, text):
    v = db.veri_yukle()
    threads = _ensure_message_threads(v)
    for t in threads:
        if t.get("konusma_id") == tid:
            t.setdefault("mesajlar", []).append({"yazar_id": sender, "mesaj": text, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
            t["tarih"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            break
    db.veri_kaydet(v)


class MessageThreadDialog(ctk.CTkToplevel):
    def __init__(self, master, tid, user, on_update=None):
        super().__init__(master)
        self.tid = tid
        self.user = user
        self.on_update = on_update
        self.title("Mesajlaşma")
        self.geometry("760x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def _thread(self):
        for t in _message_threads_for(user_id(self.user)):
            if t.get("konusma_id") == self.tid:
                return t
        return None

    def build(self):
        clear(self)
        t = self._thread()
        if not t:
            lbl(self, "Konuşma bulunamadı.", 16, "bold", RED).pack(padx=20, pady=20)
            return
        others = [x for x in t.get("katilimcilar", []) if x != user_id(self.user)]
        title = ", ".join(_msg_user_name(x) for x in others) or "Mesajlaşma"
        lbl(self, title, 22, "bold", GREEN).pack(anchor="w", padx=22, pady=(18, 4))
        lbl(self, "Öğrenci - öğretmen mesajlaşması", 12, "normal", MUTED).pack(anchor="w", padx=22)
        area = ctk.CTkScrollableFrame(self, fg_color=BG_2, corner_radius=16, border_width=1, border_color=BORDER)
        area.pack(fill="both", expand=True, padx=22, pady=12)
        for m in t.get("mesajlar", []):
            mine = m.get("yazar_id") == user_id(self.user)
            bubble = ctk.CTkFrame(area, fg_color=GREEN if mine else BG_3, corner_radius=14, border_width=1, border_color=BORDER)
            bubble.pack(anchor="e" if mine else "w", fill="x", padx=12, pady=6)
            lbl(bubble, f"{_msg_user_name(m.get('yazar_id'))} • {m.get('tarih','')}", 11, "bold", "white" if mine else GREEN).pack(anchor="w", padx=12, pady=(8, 2))
            lbl(bubble, m.get("mesaj", ""), 12, "normal", "white" if mine else TEXT, wraplength=640, justify="left").pack(anchor="w", padx=12, pady=(0, 10))
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=22, pady=(0, 18))
        self.entry = ctk.CTkEntry(bottom, placeholder_text="Mesaj yaz...", fg_color=BG_3, border_color=BORDER, height=40)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        btn(bottom, "Gönder", self.send, GREEN, GREEN_2, 90, 40).pack(side="left")

    def send(self):
        txt = self.entry.get().strip()
        if not txt:
            return
        _send_thread_message(self.tid, user_id(self.user), txt)
        try:
            if self.on_update:
                self.on_update()
        except Exception:
            pass
        self.build()


class NewMessageDialog(ctk.CTkToplevel):
    def __init__(self, master, user, target_role="egitmen", on_created=None):
        super().__init__(master)
        self.user = user
        self.target_role = target_role
        self.on_created = on_created
        self.title("Mesaj Oluştur")
        self.geometry("560x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.search_var = ctk.StringVar(value="")
        self.build()

    def targets(self):
        v = db.veri_yukle()
        arr = v.get("egitmenler", []) if self.target_role == "egitmen" else v.get("ogrenciler", [])
        q = self.search_var.get().lower().strip()
        out = []
        for u in arr:
            uid = _msg_user_id(u)
            name = u.get("ad", uid)
            if not q or q in uid.lower() or q in name.lower() or q in u.get("email", "").lower():
                out.append((uid, name, u.get("email", "")))
        return out

    def build(self):
        clear(self)
        title = "Öğretmen Seç" if self.target_role == "egitmen" else "Öğrenci Seç"
        lbl(self, title, 22, "bold").pack(anchor="w", padx=22, pady=(22, 6))
        lbl(self, "Arama kutusuna isim, ID veya e-posta yazabilirsin.", 11, "normal", MUTED).pack(anchor="w", padx=22)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=12)
        entry = ctk.CTkEntry(row, textvariable=self.search_var, placeholder_text="Ara...", fg_color=BG_3, border_color=BORDER, height=38)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        btn(row, "Ara", self.build, BLUE, BLUE_2, 80, 38).pack(side="left")
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        items = self.targets()
        if not items:
            lbl(sc, "Sonuç bulunamadı.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=10)
        for uid, name, email in items:
            c = card(sc, fill="x", pady=4)
            lbl(c, f"{name}  •  {uid}", 13, "bold", TEXT, wraplength=390).pack(anchor="w", padx=14, pady=(8, 1))
            lbl(c, email or "E-posta yok", 10, "normal", MUTED).pack(anchor="w", padx=14, pady=(0, 7))
            btn(c, "Mesajlaş", lambda x=uid: self.open_thread(x), GREEN, GREEN_2, 110, 30).pack(anchor="w", padx=14, pady=(0, 10))
        try:
            entry.focus_set()
        except Exception:
            pass

    def open_thread(self, target_id):
        tid = _get_or_create_thread(user_id(self.user), target_id)
        try:
            if self.on_created:
                self.on_created()
        except Exception:
            pass
        self.destroy()
        MessageThreadDialog(self.master, tid, self.user, self.on_created)


def _messages_page(self, f, target_role="egitmen"):
    self.header(f, "Mesajlar", "Öğrenci ve öğretmen arasında özel mesajlaşma.")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=8, pady=(0, 8))
    button_text = "Mesaj Oluştur" if target_role == "egitmen" else "Öğrenciye Mesaj Yaz"
    btn(top, button_text, lambda: NewMessageDialog(self.master, self.user, target_role, self.refresh), GREEN, GREEN_2, 170, 36).pack(side="right")
    outer, wrap = self.full_scroll_container(f)
    rows = list(reversed(_message_threads_for(user_id(self.user))))
    if not rows:
        empty = card(wrap, fill="x", pady=10)
        lbl(empty, "Henüz mesajın yok.", 14, "bold", MUTED).pack(anchor="w", padx=16, pady=(14, 4))
        lbl(empty, "Sağ üstteki Mesaj Oluştur butonuyla konuşma başlatabilirsin.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 14))
    for t in rows:
        others = [x for x in t.get("katilimcilar", []) if x != user_id(self.user)]
        title = ", ".join(_msg_user_name(x) for x in others) or "Mesajlaşma"
        last = (t.get("mesajlar") or [{}])[-1]
        c = card(wrap, fill="x", pady=5)
        c.configure(cursor="hand2")
        lbl(c, title, 14, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Son mesaj: {last.get('mesaj','Henüz mesaj yok')}", 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0, 10))
        c.bind("<Button-1>", lambda e, tid=t.get("konusma_id"): MessageThreadDialog(self.master, tid, self.user, self.refresh))
        for child in c.winfo_children():
            child.bind("<Button-1>", lambda e, tid=t.get("konusma_id"): MessageThreadDialog(self.master, tid, self.user, self.refresh))


def _student_messages_page(self, f):
    return _messages_page(self, f, "egitmen")


def _teacher_messages_page(self, f):
    return _messages_page(self, f, "ogrenci")


def _admin_messages_page(self, f):
    self.header(f, "Mesaj Yönetimi", "Öğrenci/öğretmen mesaj konuşmalarını görüntüleyebilir ve silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    veri = db.veri_yukle()
    threads = _ensure_message_threads(veri)
    db.veri_kaydet(veri)
    if not threads:
        lbl(wrap, "Henüz mesaj konuşması yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for t in list(reversed(threads)):
        c = card(wrap, fill="x", pady=5)
        names = " ↔ ".join(_msg_user_name(x) for x in t.get("katilimcilar", []))
        lbl(c, names, 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Mesaj sayısı: {len(t.get('mesajlar', []))}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        btn(c, "Konuşmayı Sil", lambda tid=t.get("konusma_id"): (_delete_message_thread(tid), toast(self.master, "Mesaj konuşması silindi.", RED), self.refresh()), RED, RED, 130, 30).pack(anchor="w", padx=16, pady=(6, 12))


def _delete_message_thread(tid):
    veri = db.veri_yukle()
    veri["mesaj_konusmalari"] = [t for t in veri.get("mesaj_konusmalari", []) if t.get("konusma_id") != tid]
    db.veri_kaydet(veri)


# Yardım sayfaları role göre tüm yetkileri açıklar.
def _student_help_page(self, f):
    self.header(f, "Yardım", "Öğrenci hesabıyla yapabileceğin tüm işlemler.")
    outer, wrap = self.full_scroll_container(f)
    items = [
        ("Panel", "Kayıtlı derslerini, yaklaşan ders/sınav/ödev bilgilerini ve genel durumunu görürsün."),
        ("Derslerim", "Kayıtlı olduğun dersleri listeler; Derse Git ile ders odasına geçersin."),
        ("Ders Kaydı", "Açık dersleri inceler, kontenjan uygunsa kayıt olursun."),
        ("Materyaller", "Ders kaynaklarını, PDF/link/video içeriklerini açarsın."),
        ("Not/Belge", "Ders notlarını ve başarılı olduğun derslere ait belge/sertifika bilgilerini görürsün."),
        ("Ödevler", "Ödev başlığı, açıklama ve son teslim tarihlerini takip edersin."),
        ("Sınavlar", "Sınav tarihini, kaç gün kaldığını ve çalışma kaynaklarını görürsün."),
        ("Yorumlar", "Ders odasında yazdığın yorumları ve ders yorumlarını takip edersin."),
        ("Forum", "Konu başlıklarına girip cevap yazarsın; ders konularında yardım isteyebilirsin."),
        ("Mesajlar", "Mesaj Oluştur ile öğretmen seçip özel mesajlaşma başlatırsın."),
        ("Destek", "Sorun bildirimi açar, admin cevabını konuşma şeklinde takip edersin."),
        ("Hedef/Rozet", "100 farklı başarımı ve ilerleme barlarını görürsün."),
        ("Takvim", "Üst menüden ders, sınav ve ödev tarihlerini takvimde incelersin."),
    ]
    _render_help_items(wrap, items)


def _teacher_help_page(self, f):
    self.header(f, "Yardım", "Öğretmen hesabıyla yapabileceğin tüm işlemler.")
    outer, wrap = self.full_scroll_container(f)
    items = [
        ("Panel", "Bugünkü derslerini ve verdiğin derslerin genel durumunu görürsün."),
        ("Derslerim", "Sana ait dersleri ve kayıtlı öğrencileri incelersin."),
        ("Ders/Kurs Aç", "Ders adı, kontenjan, gün ve saat bilgileriyle yeni kurs oluşturursun."),
        ("Materyaller", "Kendi derslerine materyal adı ve link ekleyebilir, kaynakları yönetebilirsin."),
        ("Ödevler", "Derslerine ödev oluşturur; son teslim tarihini takvimde görünür hale getirirsin."),
        ("Sınavlar", "Sınav başlığı, tarih ve çalışma kaynakları ekleyebilirsin."),
        ("Yorumlar", "Öğrenci yorumlarını ve ders geri bildirimlerini takip edersin."),
        ("Forum", "Öğrencilerin açtığı konulara cevap yazabilir, soru-cevap alanını kullanırsın."),
        ("Mesajlar", "Öğrenci arayıp özel mesaj konuşması başlatabilirsin."),
        ("Destek", "Kendi sorunlarını admin desteğine iletebilirsin."),
        ("Takvim", "Ödev ve sınav tarihlerinin takvimde görünmesini takip edersin."),
    ]
    _render_help_items(wrap, items)


def _admin_help_page(self, f):
    self.header(f, "Yardım", "Admin hesabıyla yapabileceğin tüm işlemler.")
    outer, wrap = self.full_scroll_container(f)
    items = [
        ("Panel", "Sistemdeki öğrenci, öğretmen, kurs ve başvuru sayılarını görürsün."),
        ("Kullanıcılar", "Öğrenci, öğretmen ve adminleri listeler; gerekli kullanıcıları kaldırabilirsin."),
        ("Başvurular", "Öğretmen/admin başvurularını onaylar veya reddedersin."),
        ("Kurslar", "Tüm kursları görür; gerekirse kursları kapatırsın."),
        ("Materyaller", "Ders materyallerini inceler ve silebilirsin."),
        ("Ödevler", "Sistemdeki ödevleri inceler ve silebilirsin."),
        ("Sınavlar", "Sistemdeki sınavları inceler ve silebilirsin."),
        ("Yorumlar", "Ders yorumlarını kontrol eder ve uygunsuz yorumları silebilirsin."),
        ("Forum", "Forum konularını ve forum mesajlarını silebilirsin."),
        ("Mesajlar", "Öğrenci/öğretmen mesaj konuşmalarını yönetebilirsin."),
        ("Destek", "Destek taleplerine cevap verir, sonuçlandırır ve tamamlananları kilitlersin."),
        ("Duyuru", "Sistem duyuruları oluşturursun."),
    ]
    _render_help_items(wrap, items)


def _render_help_items(wrap, items):
    for title, desc in items:
        c = card(wrap, fill="x", pady=5)
        lbl(c, title, 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, desc, 12, "normal", MUTED, wraplength=920, justify="left").pack(anchor="w", padx=16, pady=(0, 10))


# 100 benzersiz başarım/rozet.
_UNIQUE_BADGES = [
    ("İlk Ders Kaydı", "İlk dersine kayıt ol", "ders", 1),
    ("Ders Avcısı", "3 derse kayıt ol", "ders", 3),
    ("Programcı Adayı", "5 derse kayıt ol", "ders", 5),
    ("Akademik Kaşif", "8 derse kayıt ol", "ders", 8),
    ("Kampüs Ustası", "10 derse kayıt ol", "ders", 10),
    ("İlk Yorum", "1 ders yorumu yaz", "yorum", 1),
    ("Geri Bildirimci", "3 yorum yaz", "yorum", 3),
    ("Yorum Uzmanı", "5 yorum yaz", "yorum", 5),
    ("Yardımsever", "10 yorum/forum katkısı yap", "yorum", 10),
    ("Topluluk Lideri", "20 yorum/forum katkısı yap", "yorum", 20),
    ("Forum Merhaba", "1 forum katkısı yap", "forum", 1),
    ("Forum Katılımcısı", "5 forum katkısı yap", "forum", 5),
    ("Soru Çözücü", "10 forum katkısı yap", "forum", 10),
    ("Bilgi Paylaşanı", "15 forum katkısı yap", "forum", 15),
    ("Forum Rehberi", "25 forum katkısı yap", "forum", 25),
    ("Ödev Takipçisi", "1 ödev görüntüle/takip et", "odev", 1),
    ("Ödev Planlayıcı", "3 ödev takip et", "odev", 3),
    ("Ödev Ustası", "5 ödev takip et", "odev", 5),
    ("Teslim Disiplini", "8 ödev takip et", "odev", 8),
    ("Proje Savaşçısı", "10 ödev takip et", "odev", 10),
    ("Sınav Hazırlığı", "1 sınav kaynağı incele", "sinav", 1),
    ("Quiz Takipçisi", "3 sınav takip et", "sinav", 3),
    ("Sınav Avcısı", "5 sınav takip et", "sinav", 5),
    ("Konu Anlatımı Ustası", "8 sınav takip et", "sinav", 8),
    ("Finale Hazır", "10 sınav takip et", "sinav", 10),
    ("Materyal Kaşifi", "1 materyal kullan", "materyal", 1),
    ("Kaynak Toplayıcı", "3 materyal kullan", "materyal", 3),
    ("PDF Avcısı", "5 materyal kullan", "materyal", 5),
    ("Video Takipçisi", "8 materyal kullan", "materyal", 8),
    ("Kaynak Kütüphanesi", "12 materyal kullan", "materyal", 12),
    ("Destek Açan", "1 destek talebi aç", "destek", 1),
    ("Sorun Bildirici", "2 destek talebi aç", "destek", 2),
    ("Çözüm Arayan", "3 destek talebi aç", "destek", 3),
    ("Sistem Takipçisi", "5 destek talebi aç", "destek", 5),
    ("İletişimci", "1 mesaj konuşması başlat", "mesaj", 1),
    ("Mesajlaşan", "3 mesaj gönder", "mesaj", 3),
    ("Dijital İletişimci", "5 mesaj gönder", "mesaj", 5),
    ("Öğretmenle Temas", "10 mesaj gönder", "mesaj", 10),
    ("Not Takipçisi", "Not/Belge ekranını kullan", "not", 1),
    ("Belge Avcısı", "Belge durumunu kontrol et", "not", 2),
    ("Matematik Dehası", "Matematik dersi al", "ders", 2),
    ("Algoritma Kahramanı", "Programlama dersi al", "ders", 2),
    ("Veritabanı Uzmanı", "Veri tabanı dersi al", "ders", 2),
    ("Web Tasarımcısı", "Web dersi al", "ders", 2),
    ("Mobilci", "Mobil programlama dersi al", "ders", 2),
    ("Sistemci", "İşletim sistemi/ağ dersi al", "ders", 2),
    ("Proje Mimarı", "Bitirme/proje dersi al", "ders", 2),
    ("Dil Geliştirici", "İngilizce/mesleki dil dersi al", "ders", 2),
    ("Planlı Öğrenci", "Yapılacaklar ekranını kullan", "ders", 1),
    ("Takvim Kullanıcısı", "Takvimden etkinlik takip et", "ders", 1),
    ("Düzenli Öğrenci", "3 farklı modül kullan", "genel", 3),
    ("Çalışkan", "5 farklı modül kullan", "genel", 5),
    ("Azimli", "8 farklı modül kullan", "genel", 8),
    ("Kararlı", "10 farklı modül kullan", "genel", 10),
    ("Siber Öğrenci", "Platform özelliklerini keşfet", "genel", 6),
    ("Dijital Kampüs", "Tüm ana ekranları gez", "genel", 12),
    ("Kod Meraklısı", "Programlama içeriği takip et", "ders", 3),
    ("Hata Ayıklayıcı", "Forumda teknik soru çöz", "forum", 7),
    ("Mühendis Zekası", "Teknik derslerde ilerle", "ders", 5),
    ("Analitik Düşünür", "Veri/matematik derslerinde ilerle", "ders", 4),
    ("Sunum Hazırı", "Belge/Not ekranını takip et", "not", 3),
    ("Sertifika Yolcusu", "Başarı durumunu takip et", "not", 4),
    ("Kurs Koleksiyoncusu", "12 ders gör/kaydet", "ders", 12),
    ("Akademik Maraton", "15 ders gör/kaydet", "ders", 15),
    ("Kaynak Editörü", "Materyalleri düzenli kontrol et", "materyal", 15),
    ("Soru Avcısı", "Forum katkısı yap", "forum", 12),
    ("Cevap Ustası", "Forumda çok katkı yap", "forum", 20),
    ("Mentor Ruhu", "Yardımcı yorumlar yaz", "yorum", 15),
    ("Ekip Oyuncusu", "Mesaj ve forumu birlikte kullan", "mesaj", 7),
    ("Destek Takipçisi", "Destek konuşmalarını takip et", "destek", 4),
    ("Güvenli Kullanıcı", "Güçlü şifre kullan", "genel", 1),
    ("Profil Bilinci", "Profil menüsünü kullan", "genel", 2),
    ("Tema Kaşifi", "Tema değiştir", "genel", 2),
    ("Ders Odası Gezgin", "Ders odasına gir", "ders", 1),
    ("Öğrenci Profili Kaşifi", "Sınıf öğrencilerini incele", "genel", 4),
    ("Yorum Okuyucusu", "Ders yorumlarını oku", "yorum", 2),
    ("Sınav Stratejisti", "Sınav kaynaklarını takip et", "sinav", 6),
    ("Ödev Stratejisti", "Ödevleri düzenli takip et", "odev", 6),
    ("Haftalık Planlayıcı", "Takvim ve yapılacakları kullan", "genel", 5),
    ("Konu Hakimi", "Ders materyallerini kullan", "materyal", 10),
    ("Dijital Defter", "Yorum ve notları takip et", "yorum", 8),
    ("Akıllı Öğrenci", "Yardım sayfasını kullan", "genel", 1),
    ("Asistan Kullanıcısı", "Asistandan yardım al", "genel", 1),
    ("Ders Seçim Uzmanı", "Ders Kaydı ekranını kullan", "ders", 1),
    ("Çoklu Ders Uzmanı", "Birden fazla derse kayıt ol", "ders", 4),
    ("İleri Seviye Öğrenci", "10 başarıma yaklaş", "genel", 10),
    ("Kampüs Efsanesi", "20 başarıma yaklaş", "genel", 20),
    ("Bilgi Madencisi", "Kaynakları ve forumu kullan", "materyal", 18),
    ("Ders Dedektifi", "Ders detaylarını incele", "ders", 6),
    ("İletişim Ustası", "Mesajlarda aktif ol", "mesaj", 15),
    ("Platform Kaşifi", "Platform modüllerini gez", "genel", 15),
    ("Tam Hazır", "Ders, ödev, sınav, forum ve destek kullan", "genel", 25),
    ("Bilgisayar Programcısı", "Programın ana akademik modüllerini tamamla", "genel", 30),
    ("Sistem Uzmanı", "Tüm ekranlara hakim ol", "genel", 35),
    ("Efsane Öğrenci", "Rozetlerde büyük ilerleme sağla", "genel", 40),
    ("Final Boss", "Platformun tüm özelliklerini keşfet", "genel", 50),
]


def _badge_metric(kind, uid, v):
    if kind == "ders":
        return len(db.ogrenci_kurslarini_getir(uid)) if hasattr(db, "ogrenci_kurslarini_getir") else 0
    if kind == "yorum":
        return len([y for y in v.get("yorumlar", []) if y.get("ogrenci_id") == uid or y.get("yazar_id") == uid])
    if kind == "forum":
        total = 0
        for t in v.get("forum_konulari", []):
            if t.get("ogrenci_id") == uid or t.get("yazar_id") == uid:
                total += 1
            total += len([y for y in t.get("yorumlar", []) if y.get("ogrenci_id") == uid or y.get("yazar_id") == uid])
        return total
    if kind == "odev": return len(v.get("odevler", []))
    if kind == "sinav": return len(v.get("sinavlar", []))
    if kind == "materyal": return sum(len(k.get("materyaller", [])) for k in v.get("kurslar", []))
    if kind == "destek": return len([d for d in v.get("destek_talepleri", []) if d.get("kullanici_id") == uid])
    if kind == "mesaj":
        return sum(len(t.get("mesajlar", [])) for t in v.get("mesaj_konusmalari", []) if uid in t.get("katilimcilar", []))
    if kind == "not": return len(v.get("notlar", []))
    return min(50, len(db.ogrenci_kurslarini_getir(uid)) + len(v.get("odevler", [])) + len(v.get("sinavlar", [])))


def _badges_page_100(self, f):
    self.header(f, "Hedef ve Rozet", "100 benzersiz başarım, görev ilerlemesi ve XP tarzı rozet sistemi.")
    uid = user_id(self.user)
    v = db.veri_yukle()
    outer, wrap = self.full_scroll_container(f)
    lbl(wrap, "Rozetler artık 260 tekrar yerine 100 farklı başarım olarak düzenlendi.", 12, "normal", MUTED).pack(anchor="w", padx=10, pady=(8, 8))
    for idx, (name, desc, kind, target) in enumerate(_UNIQUE_BADGES[:100], 1):
        val = _badge_metric(kind, uid, v)
        pct = min(100, int((val / max(1, target)) * 100))
        earned = pct >= 100
        c = ctk.CTkFrame(wrap, fg_color=CARD if earned else BG_3, corner_radius=14, border_width=1, border_color=GREEN if earned else BORDER)
        c.pack(fill="x", padx=8, pady=5)
        lbl(c, f"{idx:03d}. {'🏆' if earned else '🔒'} {name}", 14, "bold", GREEN if earned else MUTED).pack(anchor="w", padx=16, pady=(10, 1))
        lbl(c, desc, 11, "normal", TEXT if earned else MUTED, wraplength=880).pack(anchor="w", padx=16, pady=1)
        lbl(c, f"İlerleme: {min(val, target)}/{target}", 11, "bold", GREEN if earned else YELLOW).pack(anchor="w", padx=16, pady=(2, 2))
        bar = ctk.CTkProgressBar(c, height=12, progress_color=GREEN if earned else BLUE, fg_color=BG_2)
        bar.pack(fill="x", padx=16, pady=(2, 12))
        try:
            bar.set(pct / 100)
        except Exception:
            pass


# Admin yönetim sayfaları: ödev, sınav, yorum, mesaj ve rozet görüntüleme/silme.
def _delete_list_item(key, idx):
    veri = db.veri_yukle()
    arr = veri.setdefault(key, [])
    if 0 <= idx < len(arr):
        arr.pop(idx)
    db.veri_kaydet(veri)


def _admin_assignments_page(self, f):
    self.header(f, "Ödev Yönetimi", "Sistemdeki ödevleri inceleyebilir ve silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("odevler", [])
    if not rows:
        lbl(wrap, "Henüz ödev yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, o in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{o.get('baslik','Ödev')} • {o.get('kurs_id','')}", 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Son teslim: {o.get('son_teslim', o.get('tarih','-'))} • {o.get('aciklama','')}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item('odevler', ix), toast(self.master, "Ödev silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_exams_page(self, f):
    self.header(f, "Sınav Yönetimi", "Sistemdeki sınavları inceleyebilir ve silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("sinavlar", [])
    if not rows:
        lbl(wrap, "Henüz sınav yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, s in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{s.get('baslik','Sınav')} • {s.get('kurs_id','')}", 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Tarih: {s.get('tarih','-')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item('sinavlar', ix), toast(self.master, "Sınav silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_comments_page(self, f):
    self.header(f, "Yorum Yönetimi", "Ders yorumlarını inceleyebilir ve silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("yorumlar", [])
    if not rows:
        lbl(wrap, "Henüz yorum yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, y in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{_safe_get_user_name(y.get('ogrenci_id') or y.get('yazar_id'))} • {y.get('kurs_id','')}", 13, "bold", GREEN).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, y.get("yorum", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item('yorumlar', ix), toast(self.master, "Yorum silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_badges_page(self, f):
    self.header(f, "Hedef/Rozet Sistemi", "Öğrenci tarafındaki 100 benzersiz başarımı görüntülersin.")
    outer, wrap = self.full_scroll_container(f)
    for i, (name, desc, kind, target) in enumerate(_UNIQUE_BADGES[:100], 1):
        c = card(wrap, fill="x", pady=4)
        lbl(c, f"{i:03d}. {name}", 13, "bold", GREEN).pack(anchor="w", padx=16, pady=(8, 1))
        lbl(c, f"{desc} • Hedef: {target}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 8))


# Yoklama kaldırıldı: menülerden çıkarılıyor. Eski fonksiyonlar durur ama erişim verilmez.
def _new_student_init_final(self, master, user):
    BasePanel.__init__(self, master, user, GREEN)
    self.add_menus([
        ("Panel", "P", self.dashboard),
        ("Derslerim", "D", self.my_courses),
        ("Ders Kaydı", "+", self.course_register),
        ("Materyaller", "M", self.materials_page),
        ("Not/Belge", "N", self.grades_page),
        ("Ödevler", "Ö", self.assignments_page),
        ("Sınavlar", "S", self.exams_page),
        ("Yorumlar", "★", self.yorumlar_page),
        ("Forum", "F", self.forum_page),
        ("Mesajlar", "M", self.messages_page),
        ("Destek", "?", self.support_page),
        ("Hedef/Rozet", "R", self.badges_page),
        ("Yardım", "i", self.help_page),
    ])


def _new_teacher_init_final(self, master, user):
    BasePanel.__init__(self, master, user, PURPLE)
    self.add_menus([
        ("Panel", "", self.dashboard),
        ("Derslerim", "", self.my_courses),
        ("Ders Kaydı", "", self.add_course_page),
        ("Materyaller", "", self.teacher_materials_page),
        ("Ödevler", "", self.teacher_assignments_page),
        ("Sınavlar", "", self.teacher_exams_page),
        ("Yorumlar", "", self.teacher_comments_page),
        ("Forum", "", self.forum_page),
        ("Mesajlar", "", self.messages_page),
        ("Destek", "", self.support_page),
        ("Yardım", "", self.help_page),
    ])


def _new_admin_init_final(self, master, user):
    BasePanel.__init__(self, master, user, BLUE)
    self.add_menus([
        ("Panel", "", self.dashboard),
        ("Kullanıcılar", "", self.users_page),
        ("Başvurular", "", self.applications_page),
        ("Derslerim", "", self.courses_page),
        ("Ders Kaydı", "", self.courses_page),
        ("Kurslar", "", self.courses_page),
        ("Materyaller", "", self.admin_materials_page),
        ("Not/Belge", "", lambda f: self.generic_page(f, "Not/Belge", "Admin not ve belge kayıtlarını sistem verisi üzerinden kontrol eder.")),
        ("Ödevler", "", self.admin_assignments_page),
        ("Sınavlar", "", self.admin_exams_page),
        ("Yorumlar", "", self.admin_comments_page),
        ("Forum", "", self.admin_forum_page),
        ("Mesajlar", "", self.admin_messages_page),
        ("Destek", "", self.support_page),
        ("Duyuru", "", self.announcement_page),
        ("Yardım", "", self.help_page),
    ])


OgrenciPanel.__init__ = _new_student_init_final
EgitmenPanel.__init__ = _new_teacher_init_final
AdminPanel.__init__ = _new_admin_init_final
OgrenciPanel.messages_page = _student_messages_page
EgitmenPanel.messages_page = _teacher_messages_page
AdminPanel.messages_page = _admin_messages_page
OgrenciPanel.help_page = _student_help_page
EgitmenPanel.help_page = _teacher_help_page
AdminPanel.help_page = _admin_help_page
OgrenciPanel.badges_page = _badges_page_100
AdminPanel.admin_assignments_page = _admin_assignments_page
AdminPanel.admin_exams_page = _admin_exams_page
AdminPanel.admin_comments_page = _admin_comments_page
AdminPanel.admin_messages_page = _admin_messages_page

# Eski asistan cevabını da yoklama geçmeyecek ve role göre daha dolu anlatacak şekilde güçlendir.
def _assistant_answer_final(self):
    q_raw = self.entry.get().strip()
    q = q_raw.lower()
    if not q:
        return
    self.box.insert("end", f"\nSen: {q_raw}\n")
    role = self.user.get("rol", "")
    cevaplar = []
    if any(k in q for k in ["mesaj", "öğretmen", "ogretmen", "öğrenci", "ogrenci"]):
        cevaplar.append("Mesajlar ekranında sağ üstteki Mesaj Oluştur butonuyla kişi arayıp özel konuşma başlatabilirsin.")
    if any(k in q for k in ["rozet", "başarım", "basarim", "xp", "hedef"]):
        cevaplar.append("Hedef/Rozet ekranında 100 farklı başarım vardır. Kazanılanlar parlak, kazanılmayanlar gri görünür; bar ilerlemeyi gösterir.")
    if any(k in q for k in ["destek", "talep", "sorun"]):
        cevaplar.append("Destek ekranında konu, öncelik ve açıklama girerek talep açabilirsin. Talebe tıklayınca adminle konuşma şeklinde ilerler; tamamlanan talepler kilitlenir.")
    if any(k in q for k in ["forum", "konu", "cevap"]):
        cevaplar.append("Forumda konu başlıklarına tıklayıp cevap yazabilirsin. Admin forum konularını ve mesajlarını yönetebilir.")
    if any(k in q for k in ["ders", "kayıt", "kayit", "derse git"]):
        cevaplar.append("Ders Kaydı ekranından açık derslere kayıt olursun. Kayıtlı derslerde Derse Git butonu ders odasını açar.")
    if any(k in q for k in ["ödev", "odev"]):
        cevaplar.append("Ödevler ekranında ödev açıklamaları ve son teslim tarihleri görünür. Öğretmen ödev eklediğinde takvimde de takip edilir.")
    if any(k in q for k in ["sınav", "sinav"]):
        cevaplar.append("Sınavlar ekranında sınav tarihi, kalan gün ve çalışma kaynakları görünür.")
    if any(k in q for k in ["materyal", "pdf", "link"]):
        cevaplar.append("Materyaller ekranında ders kaynaklarını açarsın. Öğretmen kendi derslerine materyal ekleyebilir; admin silebilir.")
    if any(k in q for k in ["admin", "sil", "kapat", "yetki"]):
        cevaplar.append("Admin; kullanıcıları kaldırabilir, kursları kapatabilir, ödev/sınav/yorum/forum/mesaj/materyal/destek yönetimi yapabilir.")
    if not cevaplar:
        if role == "egitmen":
            cevaplar.append("Öğretmen olarak derslerini, materyalleri, ödevleri, sınavları, yorumları, forumu, mesajları ve desteği yönetebilirsin.")
        elif role == "admin":
            cevaplar.append("Admin olarak kullanıcılar, başvurular, kurslar, materyaller, ödevler, sınavlar, yorumlar, forum, mesajlar, destek ve duyuru ekranlarını yönetebilirsin.")
        else:
            cevaplar.append("Öğrenci olarak ders kaydı, ders odası, materyaller, ödevler, sınavlar, yorumlar, forum, mesajlar, destek, rozetler ve takvim ekranlarını kullanabilirsin.")
    self.box.insert("end", "Asistan: " + "\n".join(cevaplar) + "\n")
    self.box.see("end")
    self.entry.delete(0, "end")

AssistantDialog.answer = _assistant_answer_final


# ─────────────────────────────────────────────────────────────────────────────
# SON İSTEK PATCH: Admin menüsü, bildirim çanı, yoklama/devamsızlık görünümden kaldırma,
# admin not görüntüleme ve gerekçeli silme işlemleri.
# ─────────────────────────────────────────────────────────────────────────────

def _patched_sidebar_category_for(self, title):
    # Yoklama tamamen görünümden kaldırıldı; Kurslar admin tarafında Dersler kategorisine alındı.
    if title in ["Panel", "Yapılacaklar", "Takvim"]:
        return "Genel"
    if title in ["Derslerim", "Ders Kaydı", "Kurslar", "Materyaller", "Not/Belge"]:
        return "Dersler"
    if title in ["Ödevler", "Sınavlar", "Yorumlar", "Not Girişi", "Risk Analizi"]:
        return "Akademik"
    if title in ["Forum", "Mesajlar", "Destek", "Duyuru"]:
        return "İletişim"
    if title in ["Favoriler", "Hedef/Rozet", "Proje Plus", "Yardım"]:
        return "Kişisel"
    return "Yönetim"

BasePanel.sidebar_category_for = _patched_sidebar_category_for


def _notif_rows(user):
    uid = user_id(user)
    role = user.get("rol", "")
    try:
        rows = db.bildirimleri_getir(uid, role)
    except Exception:
        v = db.veri_yukle()
        rows = [b for b in v.get("bildirimler", []) if (b.get("kullanici_id") == uid and b.get("rol") == role) or b.get("rol") == "all"]
    return rows or []


def _notif_unread_count(user):
    return len([b for b in _notif_rows(user) if not b.get("okundu")])


class NotificationDialog(ctk.CTkToplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self.title("Bildirimler")
        self.geometry("560x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def mark_all_read(self):
        try:
            uid = user_id(self.user); role = self.user.get("rol", "")
            v = db.veri_yukle()
            for b in v.get("bildirimler", []):
                if (b.get("kullanici_id") == uid and b.get("rol") == role) or b.get("rol") == "all":
                    b["okundu"] = True
            db.veri_kaydet(v)
        except Exception:
            pass

    def build(self):
        clear(self)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 8))
        lbl(top, "Bildirimler", 22, "bold", GREEN).pack(side="left")
        btn(top, "Tümünü Okundu Yap", self.mark_read_and_rebuild, BLUE, BLUE_2, 160, 34).pack(side="right")
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        rows = _notif_rows(self.user)
        if not rows:
            c = card(sc, fill="x", pady=8)
            lbl(c, "Henüz bildirimin yok.", 13, "normal", MUTED).pack(anchor="w", padx=16, pady=16)
        for b in rows:
            c = card(sc, fill="x", pady=5)
            color = GREEN if not b.get("okundu") else MUTED
            lbl(c, "Yeni" if not b.get("okundu") else "Okundu", 11, "bold", color).pack(anchor="w", padx=16, pady=(10, 0))
            lbl(c, b.get("mesaj", ""), 12, "normal", TEXT, wraplength=500, justify="left").pack(anchor="w", padx=16, pady=(4, 4))
            lbl(c, b.get("tarih", ""), 10, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 10))
        self.mark_all_read()

    def mark_read_and_rebuild(self):
        self.mark_all_read()
        self.build()


def _header_with_notifications(self, parent, title, subtitle=""):
    top = ctk.CTkFrame(parent, fg_color="transparent")
    top.pack(fill="x", padx=8, pady=(28, 18))
    left = ctk.CTkFrame(top, fg_color="transparent")
    left.pack(side="left", fill="x", expand=True)
    lbl(left, title, 25, "bold").pack(anchor="w")
    if subtitle:
        lbl(left, subtitle, 12, "normal", MUTED).pack(anchor="w", pady=(3, 0))
    actions = ctk.CTkFrame(top, fg_color="transparent")
    actions.pack(side="right")
    if self.user.get("rol") in ["ogrenci", "egitmen"]:
        n = _notif_unread_count(self.user)
        text = f"🔔 {n}" if n else "🔔"
        btn(actions, text, lambda: NotificationDialog(self.master, self.user), BG_3, BG_3, 72, 36, text_color=TEXT).pack(side="left", padx=5)
    btn(actions, "Takvim", lambda: CalendarDialog(self.master), BLUE_2, BLUE, 96, 36).pack(side="left", padx=5)
    btn(actions, f"{self.user.get('ad','')[:14]} ▾", self.toggle_profile_dropdown, self.accent, self.accent, 150, 36).pack(side="left", padx=5)

BasePanel.header = _header_with_notifications


def _student_dashboard_no_absence(self, f):
    self.header(f, f"Hoş Geldin, {self.user.get('ad','Öğrenci')}!", "Derslerini takip et, ödevlerini teslim et, sınavlarını ve belgelerini yönet.")
    row = ctk.CTkFrame(f, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=(0,14))
    my = db.ogrenci_kurslarini_getir(user_id(self.user))
    stats = [
        ("Kayıtlı Ders", len(my)),
        ("Ortalama", self.avg_grade()),
        ("Sertifika", len(getattr(db, 'belgeleri_getir', lambda x: [])(user_id(self.user)))),
        ("Bildirim", _notif_unread_count(self.user)),
    ]
    for name, val in stats:
        s = ctk.CTkFrame(row, fg_color=CARD, corner_radius=15, height=90, border_width=1, border_color=BORDER)
        s.pack(side="left", fill="x", expand=True, padx=6); s.pack_propagate(False)
        lbl(s, str(val), 20, "bold", self.accent).place(relx=0.9, y=18, anchor="e")
        lbl(s, name, 13, "bold").place(x=16, y=50)
    info = ctk.CTkFrame(f, fg_color="transparent")
    info.pack(fill="x", padx=8, pady=(0,12))
    today_card = card(info, fill="both", expand=True, pady=4)
    today_card.pack(side="left", fill="both", expand=True, padx=(0,6))
    lbl(today_card, "Bugün Ne Var?", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12,4))
    evs = TakvimWidget(today_card)._events_for_day(date.today())
    if evs:
        for ev in evs[:4]:
            lbl(today_card, f"• {ev[0]} - {ev[1][:70]}", 11, "normal", MUTED, wraplength=520).pack(anchor="w", padx=16, pady=2)
    else:
        lbl(today_card, "Bugün için kayıtlı ders/sınav/ödev görünmüyor.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(2,12))
    next_card = card(info, fill="both", expand=True, pady=4)
    next_card.pack(side="left", fill="both", expand=True, padx=(6,0))
    lbl(next_card, "Sıradaki Ders", 15, "bold", BLUE).pack(anchor="w", padx=16, pady=(12,4))
    lbl(next_card, self.next_lesson_summary(), 11, "normal", MUTED, wraplength=520).pack(anchor="w", padx=16, pady=(2,12))
    lbl(f, "Derslerim", 17, "bold").pack(anchor="w", padx=12, pady=(4, 8))
    area = ctk.CTkFrame(f, fg_color="transparent")
    area.pack(fill="x")
    self.render_courses(area, only_mine=True)

OgrenciPanel.dashboard = _student_dashboard_no_absence


def _ask_admin_reason(master, action="silme işlemi"):
    try:
        d = ctk.CTkInputDialog(text=f"Bu {action} için neden yazın:", title="Admin İşlem Gerekçesi")
        reason = d.get_input()
    except Exception:
        reason = None
    if reason is None:
        return None
    reason = str(reason).strip()
    if not reason:
        messagebox.showwarning("Gerekçe gerekli", "Admin silme/kapatma işlemlerinde gerekçe yazmalısın.")
        return None
    return reason


def _admin_log_reason(action, reason):
    try:
        v = db.veri_yukle()
        v.setdefault("loglar", []).append(f"{datetime.now().strftime('%d.%m.%Y %H:%M')} - Admin {action}. Neden: {reason}")
        db.veri_kaydet(v)
    except Exception:
        pass


def _safe_notify(uid, role, msg):
    try:
        db.bildirim_ekle(uid, role, msg)
    except Exception:
        try:
            v = db.veri_yukle()
            v.setdefault("bildirimler", []).insert(0, {"bildirim_id": f"BIL{len(v.get('bildirimler', []))+1:04d}", "kullanici_id": uid, "rol": role, "mesaj": msg, "okundu": False, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
            db.veri_kaydet(v)
        except Exception:
            pass


def _admin_close_course_reasoned(self, kid):
    reason = _ask_admin_reason(self.master, "kurs kapatma işlemi")
    if not reason:
        return
    veri = db.veri_yukle()
    course_name = kid
    teacher_id = None
    students = []
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kid:
            k["kapali"] = True
            k["durum"] = "kapalı"
            k["materyaller"] = []
            k["materyaller_kaldirildi"] = True
            k["kapatma_nedeni"] = reason
            k["kapatilma_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            course_name = k.get("kurs_adi", kid)
            teacher_id = k.get("egitmen_id")
            students = list(k.get("kayitli_ogrenciler", []))
            break
    db.veri_kaydet(veri)
    if teacher_id:
        _safe_notify(teacher_id, "egitmen", f"{course_name} dersiniz admin tarafından kaldırıldı/kapatıldı. Neden: {reason}")
    for oid in students:
        _safe_notify(oid, "ogrenci", f"Kayıtlı olduğunuz {course_name} dersi admin tarafından kaldırıldı/kapatıldı. Neden: {reason}")
    _admin_log_reason(f"{course_name} kursunu kapattı", reason)


def _admin_courses_page_reasoned(self, f):
    self.header(f, "Kurs Yönetimi", "Kursları inceleyebilir ve gerekçe yazarak kapatabilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for k in get_courses():
        c = card(wrap, fill="x", pady=5)
        durum = "Kapalı" if k.get("kapali") or k.get("durum") == "kapalı" else "Açık"
        lbl(c, f"{k.get('kurs_adi')}  •  {durum}", 13, "bold", RED if durum == "Kapalı" else GREEN, wraplength=860).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Öğretmen: {egitmen_adi(k.get('egitmen_id'))}  •  Öğrenci: {len(k.get('kayitli_ogrenciler', []))}/{k.get('kontenjan')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        if k.get("kapatma_nedeni"):
            lbl(c, f"Kapatma nedeni: {k.get('kapatma_nedeni')}", 11, "bold", YELLOW, wraplength=860).pack(anchor="w", padx=16, pady=2)
        if durum != "Kapalı":
            btn(c, "Kursu Kapat", lambda kid=k.get("kurs_id"): (_admin_close_course_reasoned(self, kid), toast(self.master, "Kurs kapatıldı ve bildirim gönderildi.", RED), self.refresh()), RED, RED, 120, 30).pack(anchor="w", padx=16, pady=(6, 12))
        else:
            lbl(c, "Bu kurs kapalı.", 11, "bold", RED).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_delete_user_reasoned(self, kid, role):
    reason = _ask_admin_reason(self.master, "kullanıcı kaldırma işlemi")
    if not reason:
        return
    _admin_delete_user(kid, role)
    _admin_log_reason(f"{kid} kullanıcısını kaldırdı", reason)
    try:
        _safe_notify(kid, role, f"Hesabınız admin tarafından kaldırıldı. Neden: {reason}")
    except Exception:
        pass


def _admin_users_page_reasoned(self, f):
    self.header(f, "Kullanıcı Yönetimi", "Öğrenci ve öğretmenleri gerekçe yazarak sistemden kaldırabilir, kullanıcıları kontrol edebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    v = db.veri_yukle()
    groups = [("Öğrenciler", "ogrenci", v.get("ogrenciler", [])), ("Öğretmenler", "egitmen", v.get("egitmenler", [])), ("Adminler", "admin", v.get("adminler", []))]
    for title, role, arr in groups:
        lbl(wrap, title, 17, "bold", GREEN).pack(anchor="w", padx=8, pady=(14, 6))
        for u in arr[:120]:
            kid = u.get("ogrenci_id") or u.get("egitmen_id") or u.get("admin_id") or u.get("id")
            c = card(wrap, fill="x", pady=4)
            lbl(c, f"{kid} - {u.get('ad')} - {u.get('email','')}", 12, "normal", TEXT, wraplength=860).pack(side="left", padx=16, pady=10)
            if kid != "admin":
                btn(c, "Kaldır", lambda x=kid, r=role: (_admin_delete_user_reasoned(self, x, r), toast(self.master, "Kullanıcı kaldırıldı.", RED), self.refresh()), RED, RED, 90, 30).pack(side="right", padx=12, pady=8)


def _admin_grades_page(self, f):
    self.header(f, "Not ve Belge Görüntüleme", "Öğrencilerin hangi dersten kaç aldığını görürsün. Bu ekranda düzenleme yapılamaz.")
    outer, wrap = self.full_scroll_container(f)
    veri = db.veri_yukle()
    students = {}
    for o in veri.get("ogrenciler", []):
        oid = o.get("ogrenci_id") or o.get("id")
        students[oid] = o.get("ad", oid)
    courses = {}
    for k in veri.get("kurslar", []):
        courses[k.get("kurs_id")] = k.get("kurs_adi", k.get("kurs_id"))
    notes = veri.get("notlar", [])
    if not notes:
        lbl(wrap, "Henüz not kaydı yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
        return
    grouped = {}
    for n in notes:
        grouped.setdefault(n.get("kurs_id", "Bilinmeyen"), []).append(n)
    for kid in sorted(grouped, key=lambda x: courses.get(x, x)):
        c = card(wrap, fill="x", pady=6)
        lbl(c, courses.get(kid, kid), 15, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10, 4))
        for n in sorted(grouped[kid], key=lambda x: students.get(x.get("ogrenci_id"), x.get("ogrenci_id", "")))[:120]:
            oid = n.get("ogrenci_id")
            val = n.get("not", "-")
            harf = n.get("harf", "-")
            lbl(c, f"• {students.get(oid, oid)}: {val}  | Harf: {harf}  | Vize: {n.get('vize','-')}  Final: {n.get('final','-')}  Ödev: {n.get('odev','-')}", 11, "normal", TEXT, wraplength=900, justify="left").pack(anchor="w", padx=18, pady=2)


class AdminMessageReadOnlyDialog(ctk.CTkToplevel):
    def __init__(self, master, tid):
        super().__init__(master)
        self.tid = tid
        self.title("Admin Mesaj İnceleme")
        self.geometry("760x620")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def _thread(self):
        v = db.veri_yukle()
        threads = _ensure_message_threads(v)
        db.veri_kaydet(v)
        for t in threads:
            if t.get("konusma_id") == self.tid:
                return t
        return None

    def build(self):
        clear(self)
        t = self._thread()
        if not t:
            lbl(self, "Konuşma bulunamadı.", 16, "bold", RED).pack(padx=20, pady=20)
            return
        names = " ↔ ".join(_msg_user_name(x) for x in t.get("katilimcilar", []))
        lbl(self, names, 21, "bold", GREEN).pack(anchor="w", padx=22, pady=(18, 4))
        lbl(self, "Admin sadece okuyabilir; bu pencereden mesaj yazamaz.", 12, "normal", MUTED).pack(anchor="w", padx=22)
        area = ctk.CTkScrollableFrame(self, fg_color=BG_2, corner_radius=16, border_width=1, border_color=BORDER)
        area.pack(fill="both", expand=True, padx=22, pady=12)
        for m in t.get("mesajlar", []):
            bubble = ctk.CTkFrame(area, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
            bubble.pack(fill="x", padx=12, pady=6)
            lbl(bubble, f"{_msg_user_name(m.get('yazar_id'))} • {m.get('tarih','')}", 11, "bold", GREEN).pack(anchor="w", padx=12, pady=(8, 2))
            lbl(bubble, m.get("mesaj", ""), 12, "normal", TEXT, wraplength=640, justify="left").pack(anchor="w", padx=12, pady=(0, 10))


def _delete_message_thread_reasoned(self, tid):
    reason = _ask_admin_reason(self.master, "mesaj konuşması silme işlemi")
    if not reason:
        return
    v = db.veri_yukle()
    threads = _ensure_message_threads(v)
    target = next((t for t in threads if t.get("konusma_id") == tid), None)
    participants = list(target.get("katilimcilar", [])) if target else []
    v["mesaj_konusmalari"] = [t for t in threads if t.get("konusma_id") != tid]
    db.veri_kaydet(v)
    for pid in participants:
        # Rolü bulup bildirim gönder.
        role = "ogrenci"
        vv = db.veri_yukle()
        if any(pid in [e.get("egitmen_id"), e.get("id")] for e in vv.get("egitmenler", [])):
            role = "egitmen"
        _safe_notify(pid, role, f"Bir mesaj konuşmanız admin tarafından silindi. Neden: {reason}")
    _admin_log_reason(f"{tid} mesaj konuşmasını sildi", reason)


def _admin_messages_page_readonly(self, f):
    self.header(f, "Mesaj Yönetimi", "Öğrenci/öğretmen mesaj konuşmalarını okuyabilir ve gerekçe yazarak silebilirsin. Admin buradan mesaj yazamaz.")
    outer, wrap = self.full_scroll_container(f)
    veri = db.veri_yukle()
    threads = _ensure_message_threads(veri)
    db.veri_kaydet(veri)
    if not threads:
        lbl(wrap, "Henüz mesaj konuşması yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for t in list(reversed(threads)):
        c = card(wrap, fill="x", pady=5)
        names = " ↔ ".join(_msg_user_name(x) for x in t.get("katilimcilar", []))
        lbl(c, names, 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        last = (t.get("mesajlar") or [{}])[-1]
        lbl(c, f"Mesaj sayısı: {len(t.get('mesajlar', []))}  •  Son: {last.get('mesaj','')}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(6, 12))
        btn(row, "Konuşmayı Oku", lambda tid=t.get("konusma_id"): AdminMessageReadOnlyDialog(self.master, tid), BLUE, BLUE_2, 130, 30).pack(side="left", padx=(0, 8))
        btn(row, "Konuşmayı Sil", lambda tid=t.get("konusma_id"): (_delete_message_thread_reasoned(self, tid), toast(self.master, "Mesaj konuşması silindi.", RED), self.refresh()), RED, RED, 130, 30).pack(side="left")


def _delete_list_item_reasoned(self, key, idx, label):
    reason = _ask_admin_reason(self.master, f"{label} silme işlemi")
    if not reason:
        return
    _delete_list_item(key, idx)
    _admin_log_reason(f"{label} sildi", reason)


def _delete_material_reasoned(self, kid, idx):
    reason = _ask_admin_reason(self.master, "materyal silme işlemi")
    if not reason:
        return
    _delete_material(kid, idx)
    _admin_log_reason(f"{kid} materyal sildi", reason)


def _delete_forum_topic_reasoned(self, tid):
    reason = _ask_admin_reason(self.master, "forum konusu silme işlemi")
    if not reason:
        return
    _delete_forum_topic(tid)
    _admin_log_reason(f"{tid} forum konusunu sildi", reason)


def _delete_forum_comment_reasoned(self, tid, ix):
    reason = _ask_admin_reason(self.master, "forum mesajı silme işlemi")
    if not reason:
        return
    _delete_forum_comment(tid, ix)
    _admin_log_reason(f"{tid} forum mesajı sildi", reason)


def _admin_assignments_page_reasoned(self, f):
    self.header(f, "Ödev Yönetimi", "Sistemdeki ödevleri inceleyebilir ve gerekçe yazarak silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("odevler", [])
    if not rows:
        lbl(wrap, "Henüz ödev yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, o in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{o.get('baslik','Ödev')} • {o.get('kurs_id','')}", 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Son teslim: {o.get('son_teslim', o.get('tarih','-'))} • {o.get('aciklama','')}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item_reasoned(self, 'odevler', ix, 'ödev'), toast(self.master, "Ödev silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_exams_page_reasoned(self, f):
    self.header(f, "Sınav Yönetimi", "Sistemdeki sınavları inceleyebilir ve gerekçe yazarak silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("sinavlar", [])
    if not rows:
        lbl(wrap, "Henüz sınav yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, s in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{s.get('baslik','Sınav')} • {s.get('kurs_id','')}", 13, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Tarih: {s.get('tarih','-')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item_reasoned(self, 'sinavlar', ix, 'sınav'), toast(self.master, "Sınav silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_comments_page_reasoned(self, f):
    self.header(f, "Yorum Yönetimi", "Ders yorumlarını inceleyebilir ve gerekçe yazarak silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    rows = db.veri_yukle().get("yorumlar", [])
    if not rows:
        lbl(wrap, "Henüz yorum yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for i, y in enumerate(rows):
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{_safe_get_user_name(y.get('ogrenci_id') or y.get('yazar_id'))} • {y.get('kurs_id','')}", 13, "bold", GREEN).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, y.get("yorum", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Sil", lambda ix=i: (_delete_list_item_reasoned(self, 'yorumlar', ix, 'yorum'), toast(self.master, "Yorum silindi.", RED), self.refresh()), RED, RED, 70, 28).pack(anchor="w", padx=16, pady=(6, 12))


def _admin_materials_page_reasoned(self, f):
    self.header(f, "Materyal Yönetimi", "Ders materyallerini inceleyebilir ve gerekçe yazarak silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for k in get_courses():
        mats = k.get("materyaller", [])
        if not mats:
            continue
        c = card(wrap, fill="x", pady=6)
        lbl(c, k.get("kurs_adi"), 14, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10, 4))
        for i, m in enumerate(mats):
            row = ctk.CTkFrame(c, fg_color=BG_3, corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            lbl(row, f"{m.get('baslik')}  •  {m.get('link','')}", 11, "normal", TEXT, wraplength=720).pack(side="left", fill="x", expand=True, padx=10, pady=6)
            btn(row, "Sil", lambda kid=k.get("kurs_id"), ix=i: (_delete_material_reasoned(self, kid, ix), toast(self.master, "Materyal silindi.", RED), self.refresh()), RED, RED, 55, 24).pack(side="right", padx=8)


def _admin_forum_page_reasoned(self, f):
    self.header(f, "Forum Yönetimi", "Forum konularını ve mesajlarını gerekçe yazarak silebilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for t in db.veri_yukle().get("forum_konulari", []):
        c = card(wrap, fill="x", pady=7)
        lbl(c, t.get("baslik", "Konu"), 14, "bold", GREEN, wraplength=850).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, t.get("aciklama", ""), 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=2)
        btn(c, "Konuyu Sil", lambda tid=t.get("konu_id"): (_delete_forum_topic_reasoned(self, tid), toast(self.master, "Forum konusu silindi.", RED), self.refresh()), RED, RED, 110, 28).pack(anchor="w", padx=16, pady=(6,6))
        for i, y in enumerate(t.get("yorumlar", [])[:10]):
            row = ctk.CTkFrame(c, fg_color=BG_3, corner_radius=8)
            row.pack(fill="x", padx=16, pady=3)
            lbl(row, f"{_safe_get_user_name(y.get('ogrenci_id') or y.get('yazar_id'))}: {y.get('yorum') or y.get('mesaj','')}", 11, "normal", TEXT, wraplength=720).pack(side="left", fill="x", expand=True, padx=10, pady=6)
            btn(row, "Sil", lambda tid=t.get("konu_id"), ix=i: (_delete_forum_comment_reasoned(self, tid, ix), toast(self.master, "Forum mesajı silindi.", RED), self.refresh()), RED, RED, 55, 24).pack(side="right", padx=8)


def _admin_help_page_final(self, f):
    self.header(f, "Yardım", "Admin hesabıyla yapabileceğin tüm işlemler.")
    outer, wrap = self.full_scroll_container(f)
    items = [
        ("Panel", "Sistem sayıları, kullanıcılar, kurslar, başvurular ve aktivite akışını görürsün."),
        ("Kurslar", "Tüm kursları görüntüler; gerekçe yazarak kurs kapatır ve öğretmene/öğrencilere bildirim gönderirsin."),
        ("Materyaller", "Ders materyallerini görüntüler; gerekçe yazarak silebilirsin."),
        ("Not/Belge", "Her öğrencinin hangi dersten kaç aldığını görürsün; bu ekranda düzenleme yapamazsın."),
        ("Ödevler", "Sistemdeki ödevleri görüntüler ve gerekçe yazarak silebilirsin."),
        ("Sınavlar", "Sistemdeki sınavları görüntüler ve gerekçe yazarak silebilirsin."),
        ("Yorumlar", "Ders yorumlarını inceler ve gerekçe yazarak silebilirsin."),
        ("Forum", "Forum konularını/mesajlarını inceler ve gerekçe yazarak silebilirsin."),
        ("Mesajlar", "Öğrenci-öğretmen konuşmalarını sadece okur; mesaj yazamazsın. Gerekçe yazarak konuşma silebilirsin."),
        ("Destek", "Destek taleplerini konuşma şeklinde açar, cevaplar ve sonuçlandırırsın."),
        ("Duyuru", "Tüm kullanıcılara duyuru yayınlarsın."),
        ("Kullanıcılar", "Öğrenci, öğretmen ve adminleri görür; gerekçe yazarak kullanıcı kaldırabilirsin."),
        ("Başvurular", "Öğretmen ve admin başvurularını onaylarsın."),
    ]
    for title, desc in items:
        c = card(wrap, fill="x", pady=5)
        lbl(c, title, 14, "bold", GREEN).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, desc, 12, "normal", MUTED, wraplength=900, justify="left").pack(anchor="w", padx=16, pady=(0,10))


def _new_admin_init_requested(self, master, user):
    BasePanel.__init__(self, master, user, BLUE)
    self.add_menus([
        ("Panel", "", self.dashboard),
        ("Kurslar", "", self.courses_page),
        ("Materyaller", "", self.admin_materials_page),
        ("Not/Belge", "", self.admin_grades_page),
        ("Ödevler", "", self.admin_assignments_page),
        ("Sınavlar", "", self.admin_exams_page),
        ("Yorumlar", "", self.admin_comments_page),
        ("Forum", "", self.admin_forum_page),
        ("Mesajlar", "", self.admin_messages_page),
        ("Destek", "", self.support_page),
        ("Duyuru", "", self.announcement_page),
        ("Yardım", "", self.help_page),
        ("Kullanıcılar", "", self.users_page),
        ("Başvurular", "", self.applications_page),
    ])

# Atamalar: Eski görünür yoklama/devamsızlık öğeleri ve admin menü tekrarları kaldırılır.
AdminPanel.__init__ = _new_admin_init_requested
AdminPanel.courses_page = _admin_courses_page_reasoned
AdminPanel.users_page = _admin_users_page_reasoned
AdminPanel.admin_grades_page = _admin_grades_page
AdminPanel.admin_messages_page = _admin_messages_page_readonly
AdminPanel.messages_page = _admin_messages_page_readonly
AdminPanel.admin_assignments_page = _admin_assignments_page_reasoned
AdminPanel.admin_exams_page = _admin_exams_page_reasoned
AdminPanel.admin_comments_page = _admin_comments_page_reasoned
AdminPanel.admin_materials_page = _admin_materials_page_reasoned
AdminPanel.admin_forum_page = _admin_forum_page_reasoned
AdminPanel.help_page = _admin_help_page_final



# ─────────────────────────────────────────────────────────────────────────────
# EK BUGFIX PATCH: mesaj arama, forum konu açma, şifre göz butonu,
# kurs formu seçiciler, bildirim güncelleme, dersten çıkış başvurusu
# ─────────────────────────────────────────────────────────────────────────────

# Tkinter/CustomTkinter kapanmış Entry iç değişkenleri için "invalid command name"
# hatası basabiliyor. Gerçek hataları göstermeye devam edip bu kapanmış widget
# uyarılarını susturuyoruz.
def _safe_report_callback_exception_v2(self, exc, val, tb):
    if exc is tk.TclError and ("bad window path name" in str(val) or "invalid command name" in str(val)):
        return
    traceback.print_exception(exc, val, tb)
try:
    tk.Tk.report_callback_exception = _safe_report_callback_exception_v2
    tk.Toplevel.report_callback_exception = _safe_report_callback_exception_v2
    ctk.CTk.report_callback_exception = _safe_report_callback_exception_v2
    ctk.CTkToplevel.report_callback_exception = _safe_report_callback_exception_v2
except Exception:
    pass


def _password_box(parent, placeholder="Şifre", width=280, height=44):
    """Şifre alanı + göz butonu. Frame döner; entry `box.entry` içindedir."""
    box = ctk.CTkFrame(parent, fg_color="transparent")
    entry = ctk.CTkEntry(box, placeholder_text=placeholder, show="●", width=max(80, width-50), height=height, corner_radius=12, fg_color=BG_3, border_color=BORDER)
    entry.pack(side="left", fill="x", expand=True)
    state = {"show": False}
    def toggle():
        state["show"] = not state["show"]
        entry.configure(show="" if state["show"] else "●")
        eye.configure(text="🙈" if state["show"] else "👁")
    eye = btn(box, "👁", toggle, BG_3, BG_3, 44, height, text_color=TEXT)
    eye.pack(side="left", padx=(6,0))
    box.entry = entry
    return box


def _login_dialog_init_eye(self, master, role, callback):
    ctk.CTkToplevel.__init__(self, master)
    self.role = role
    self.callback = callback
    self.title("Giriş Yap")
    self.geometry("390x560")
    self.configure(fg_color=BG)
    self.grab_set()
    self.resizable(False, False)
    role_names = {"ogrenci":"Öğrenci", "egitmen":"Öğretmen", "admin":"Admin"}
    lbl(self, f"{role_names.get(role, role)} Girişi", 24, "bold").pack(pady=(34, 8))
    lbl(self, "Kullanıcı ID ve şifrenizi girin", 12, "normal", MUTED).pack(pady=(0, 22))
    self.e_user = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=280, height=44, corner_radius=12, fg_color=BG_3, border_color=BORDER)
    self.e_user.pack(pady=7)
    pass_box = _password_box(self, "Şifre", 280, 44)
    pass_box.pack(pady=7, padx=54, fill="x")
    self.e_pass = pass_box.entry
    self.remember = ctk.CTkCheckBox(self, text="Beni hatırla", fg_color=GREEN, hover_color=GREEN_2)
    self.remember.pack(pady=(8, 4))
    self.e_pass.bind("<Return>", lambda e: self.try_login())
    btn(self, "Giriş Yap", self.try_login, GREEN, GREEN_2, 280, 44).pack(pady=(18, 8))
    self.render_remembered_accounts()

LoginDialog.__init__ = _login_dialog_init_eye


def _student_register_init_eye(self, master):
    ctk.CTkToplevel.__init__(self, master)
    self.title("Öğrenci Kaydı")
    self.geometry("430x560")
    self.configure(fg_color=BG)
    self.grab_set()
    lbl(self, "Yeni Öğrenci Kaydı", 22, "bold").pack(pady=(28, 12))
    self.entries = []
    for ph in ["Öğrenci ID", "Ad Soyad", "E-posta"]:
        e = ctk.CTkEntry(self, placeholder_text=ph, width=310, height=42, fg_color=BG_3, border_color=BORDER)
        e.pack(pady=6)
        self.entries.append(e)
    meter_box, self._update_strength = _make_strength_meter(self)
    meter_box.pack(fill="x", padx=60, pady=(6, 2))
    pass_box = _password_box(self, "Şifre", 310, 42)
    pass_box.pack(pady=6, padx=60, fill="x")
    self.pass_entry = pass_box.entry
    self.pass_entry.bind("<KeyRelease>", lambda e: self._update_strength(self.pass_entry.get()))
    self.entries.append(self.pass_entry)
    lbl(self, "E-posta alanında @gmail.com zorunludur.", 10, "normal", MUTED).pack(pady=(4, 0))
    btn(self, "Kaydı Tamamla", self.save, GREEN, GREEN_2, 310, 44).pack(pady=20)

StudentRegisterDialog.__init__ = _student_register_init_eye


def _application_init_eye(self, master):
    ctk.CTkToplevel.__init__(self, master)
    self.title("Öğretmen/Admin Başvurusu")
    self.geometry("470x640")
    self.configure(fg_color=BG)
    self.grab_set()
    lbl(self, "Hesap Başvurusu", 22, "bold").pack(pady=(24, 8))
    self.role = ctk.StringVar(value="Öğretmen")
    ctk.CTkSegmentedButton(self, values=["Öğretmen", "Admin"], variable=self.role, fg_color=BG_3, selected_color=GREEN, selected_hover_color=GREEN_2).pack(pady=8)
    self.id_entry = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.name_entry = ctk.CTkEntry(self, placeholder_text="Ad Soyad", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.email_entry = ctk.CTkEntry(self, placeholder_text="E-posta", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    self.spec_entry = ctk.CTkEntry(self, placeholder_text="Uzmanlık / Açıklama", width=315, height=42, fg_color=BG_3, border_color=BORDER)
    for e in [self.id_entry, self.name_entry, self.email_entry, self.spec_entry]:
        e.pack(pady=6)
    meter_box, self._update_strength = _make_strength_meter(self)
    meter_box.pack(fill="x", padx=60, pady=(6, 2))
    pass_box = _password_box(self, "Şifre", 315, 42)
    pass_box.pack(pady=6, padx=76, fill="x")
    self.pass_entry = pass_box.entry
    self.pass_entry.bind("<KeyRelease>", lambda e: self._update_strength(self.pass_entry.get()))
    btn(self, "Başvuru Gönder", self.send, GREEN, GREEN_2, 315, 44).pack(pady=18)
    lbl(self, "E-posta için @gmail.com zorunludur. Başvuru maili ayarlar doğruysa ana e-postana gider.", 10, "normal", MUTED, wraplength=320).pack()

ApplicationDialog.__init__ = _application_init_eye


def _is_course_active(k):
    return not (k.get("kapali") or str(k.get("durum", "")).lower() in ["kapalı", "kapali", "silindi", "pasif"])


def _active_courses():
    return [k for k in get_courses() if _is_course_active(k)]


def _active_student_course_ids(uid):
    ids = set(db.ogrenci_kurslarini_getir(uid))
    active = {k.get("kurs_id") for k in _active_courses()}
    return ids & active


def _pending_exit_request(uid, kid):
    v = db.veri_yukle()
    for r in v.setdefault("ders_cikis_basvurulari", []):
        if r.get("ogrenci_id") == uid and r.get("kurs_id") == kid and r.get("durum") == "bekliyor":
            return r
    return None


def _course_by_id(kid):
    for k in get_courses():
        if k.get("kurs_id") == kid:
            return k
    return {}


def _remove_pending_exit_notification(req_id):
    v = db.veri_yukle()
    v["bildirimler"] = [b for b in v.get("bildirimler", []) if b.get("cikis_basvuru_id") != req_id]
    db.veri_kaydet(v)


def _request_course_exit(master, user, kid):
    uid = user_id(user)
    if _pending_exit_request(uid, kid):
        toast(master, "Bu ders için zaten bekleyen çıkış başvurun var.", YELLOW)
        return
    reason = ctk.CTkInputDialog(text="Dersten çıkma nedenini yaz:", title="Dersten Çıkma Başvurusu").get_input()
    if reason is None:
        return
    reason = str(reason).strip()
    if not reason:
        messagebox.showwarning("Neden gerekli", "Dersten çıkma nedeni yazmalısın.")
        return
    v = db.veri_yukle()
    course = next((k for k in v.get("kurslar", []) if k.get("kurs_id") == kid), {})
    reqs = v.setdefault("ders_cikis_basvurulari", [])
    req_id = f"DCB{len(reqs)+1:04d}"
    req = {
        "basvuru_id": req_id,
        "ogrenci_id": uid,
        "ogrenci_ad": user.get("ad", uid),
        "kurs_id": kid,
        "kurs_adi": course.get("kurs_adi", kid),
        "egitmen_id": course.get("egitmen_id"),
        "neden": reason,
        "durum": "bekliyor",
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    reqs.append(req)
    # Öğretmen bildirimine işlem ID'si eklenir; öğrenci iptal ederse bu bildirim silinir.
    if course.get("egitmen_id"):
        bid = f"BIL{len(v.get('bildirimler', []))+1:04d}"
        v.setdefault("bildirimler", []).insert(0, {
            "bildirim_id": bid,
            "kullanici_id": course.get("egitmen_id"),
            "rol": "egitmen",
            "mesaj": f"{user.get('ad', uid)} öğrencisi {course.get('kurs_adi', kid)} dersinden çıkmak istiyor. Neden: {reason}",
            "okundu": False,
            "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "cikis_basvuru_id": req_id,
        })
    db.veri_kaydet(v)
    toast(master, "Dersten çıkma başvurusu gönderildi.", GREEN)


def _cancel_course_exit(master, user, req_id):
    v = db.veri_yukle()
    for r in v.setdefault("ders_cikis_basvurulari", []):
        if r.get("basvuru_id") == req_id and r.get("ogrenci_id") == user_id(user) and r.get("durum") == "bekliyor":
            r["durum"] = "iptal"
            r["iptal_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            break
    v["bildirimler"] = [b for b in v.get("bildirimler", []) if b.get("cikis_basvuru_id") != req_id]
    db.veri_kaydet(v)
    toast(master, "Çıkış başvurusu iptal edildi.", YELLOW)


def _process_exit_request(master, req_id, approve=True):
    v = db.veri_yukle()
    req = None
    for r in v.setdefault("ders_cikis_basvurulari", []):
        if r.get("basvuru_id") == req_id:
            req = r
            break
    if not req or req.get("durum") != "bekliyor":
        messagebox.showwarning("Başvuru", "Bu başvuru artık beklemede değil.")
        return
    uid = req.get("ogrenci_id"); kid = req.get("kurs_id")
    if approve:
        req["durum"] = "onaylandı"
        v["kayitlar"] = [x for x in v.get("kayitlar", []) if not (x.get("ogrenci_id") == uid and x.get("kurs_id") == kid)]
        for k in v.get("kurslar", []):
            if k.get("kurs_id") == kid and uid in k.get("kayitli_ogrenciler", []):
                k["kayitli_ogrenciler"].remove(uid)
        msg = f"{req.get('kurs_adi', kid)} dersi için çıkış başvurun onaylandı."
    else:
        req["durum"] = "reddedildi"
        msg = f"{req.get('kurs_adi', kid)} dersi için çıkış başvurun reddedildi."
    req["sonuc_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    # ilgili öğretmen bildirimini okundu yap
    for b in v.get("bildirimler", []):
        if b.get("cikis_basvuru_id") == req_id:
            b["okundu"] = True
    bid = f"BIL{len(v.get('bildirimler', []))+1:04d}"
    v.setdefault("bildirimler", []).insert(0, {"bildirim_id": bid, "kullanici_id": uid, "rol": "ogrenci", "mesaj": msg, "okundu": False, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
    db.veri_kaydet(v)
    toast(master, "Başvuru sonucu kaydedildi.", GREEN if approve else YELLOW)
    try:
        if hasattr(master, "current"):
            master.current.refresh()
    except Exception:
        pass


def _notification_dialog_build_actions(self):
    clear(self)
    top = ctk.CTkFrame(self, fg_color="transparent")
    top.pack(fill="x", padx=20, pady=(20, 8))
    lbl(top, "Bildirimler", 22, "bold", GREEN).pack(side="left")
    btn(top, "Tümünü Okundu Yap", self.mark_read_and_rebuild, BLUE, BLUE_2, 160, 34).pack(side="right")
    sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
    sc.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    rows = _notif_rows(self.user)
    if not rows:
        c = card(sc, fill="x", pady=8)
        lbl(c, "Henüz bildirimin yok.", 13, "normal", MUTED).pack(anchor="w", padx=16, pady=16)
    for b in rows:
        c = card(sc, fill="x", pady=5)
        color = GREEN if not b.get("okundu") else MUTED
        lbl(c, "Yeni" if not b.get("okundu") else "Okundu", 11, "bold", color).pack(anchor="w", padx=16, pady=(10, 0))
        lbl(c, b.get("mesaj", ""), 12, "normal", TEXT, wraplength=500, justify="left").pack(anchor="w", padx=16, pady=(4, 4))
        if self.user.get("rol") == "egitmen" and b.get("cikis_basvuru_id"):
            row = ctk.CTkFrame(c, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=(4, 8))
            btn(row, "Onayla", lambda rid=b.get("cikis_basvuru_id"): (_process_exit_request(self.master, rid, True), self.build()), GREEN, GREEN_2, 90, 30).pack(side="left", padx=(0, 8))
            btn(row, "Reddet", lambda rid=b.get("cikis_basvuru_id"): (_process_exit_request(self.master, rid, False), self.build()), RED, RED, 90, 30).pack(side="left")
        lbl(c, b.get("tarih", ""), 10, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 10))


def _notification_mark_read_and_rebuild_v2(self):
    self.mark_all_read()
    self.build()
    try:
        if hasattr(self.master, "current"):
            self.master.current.refresh()
    except Exception:
        pass

NotificationDialog.build = _notification_dialog_build_actions
NotificationDialog.mark_read_and_rebuild = _notification_mark_read_and_rebuild_v2


class NewMessageDialog(ctk.CTkToplevel):
    """Textvariable kullanmaz; kapanan Entry callback hatası üretmez."""
    def __init__(self, master, user, target_role="egitmen", on_created=None):
        super().__init__(master)
        self.user = user
        self.target_role = target_role or "egitmen"
        self.on_created = on_created
        self.search_text = ""
        self.title("Mesaj Oluştur")
        self.geometry("590x650")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def set_role(self, role):
        self.target_role = role
        self.search_text = ""
        self.build()

    def targets(self):
        v = db.veri_yukle()
        if self.target_role == "ogrenci":
            arr = v.get("ogrenciler", [])
        else:
            arr = v.get("egitmenler", [])
        q = (self.search_text or "").lower().strip()
        out = []
        me = user_id(self.user)
        for u in arr:
            uid = _msg_user_id(u)
            if uid == me:
                continue
            name = u.get("ad", uid)
            if not q or q in uid.lower() or q in name.lower() or q in u.get("email", "").lower():
                out.append((uid, name, u.get("email", "")))
        return out

    def build(self):
        clear(self)
        lbl(self, "Mesaj Oluştur", 22, "bold").pack(anchor="w", padx=22, pady=(22, 6))
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=22, pady=(0, 8))
        btn(tabs, "Öğretmenler", lambda: self.set_role("egitmen"), GREEN if self.target_role == "egitmen" else BG_3, GREEN_2 if self.target_role == "egitmen" else BG_3, 130, 34, text_color="white" if self.target_role == "egitmen" else TEXT).pack(side="left", padx=(0, 8))
        btn(tabs, "Öğrenciler", lambda: self.set_role("ogrenci"), GREEN if self.target_role == "ogrenci" else BG_3, GREEN_2 if self.target_role == "ogrenci" else BG_3, 130, 34, text_color="white" if self.target_role == "ogrenci" else TEXT).pack(side="left")
        title = "Öğretmen Seç" if self.target_role == "egitmen" else "Öğrenci Seç"
        lbl(self, title, 15, "bold", TEXT).pack(anchor="w", padx=22)
        lbl(self, "Arama kutusuna isim, ID veya e-posta yazabilirsin.", 11, "normal", MUTED).pack(anchor="w", padx=22)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=12)
        entry = ctk.CTkEntry(row, placeholder_text="Ara...", fg_color=BG_3, border_color=BORDER, height=38)
        entry.insert(0, self.search_text)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        def do_search(event=None):
            try:
                self.search_text = entry.get()
            except Exception:
                self.search_text = ""
            self.build()
        entry.bind("<KeyRelease>", lambda e: self.after(80, do_search))
        btn(row, "Ara", do_search, BLUE, BLUE_2, 80, 38).pack(side="left")
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        items = self.targets()
        if not items:
            lbl(sc, "Sonuç bulunamadı.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=10)
        for uid, name, email in items:
            c = card(sc, fill="x", pady=4)
            lbl(c, f"{name}  •  {uid}", 13, "bold", TEXT, wraplength=420).pack(anchor="w", padx=14, pady=(8, 1))
            lbl(c, email or "E-posta yok", 10, "normal", MUTED).pack(anchor="w", padx=14, pady=(0, 7))
            btn(c, "Mesajlaş", lambda x=uid: self.open_thread(x), GREEN, GREEN_2, 110, 30).pack(anchor="w", padx=14, pady=(0, 10))

    def open_thread(self, target_id):
        tid = _get_or_create_thread(user_id(self.user), target_id)
        try:
            if self.on_created:
                self.on_created()
        except Exception:
            pass
        self.destroy()
        MessageThreadDialog(self.master, tid, self.user, self.on_created)


def _messages_page_v2(self, f, target_role="egitmen"):
    self.header(f, "Mesajlar", "Öğrenci ve öğretmenler arasında özel mesajlaşma.")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=8, pady=(0, 8))
    btn(top, "Mesaj Oluştur", lambda: NewMessageDialog(self.master, self.user, target_role, self.refresh), GREEN, GREEN_2, 170, 36).pack(side="right")
    outer, wrap = self.full_scroll_container(f)
    rows = list(reversed(_message_threads_for(user_id(self.user))))
    if not rows:
        empty = card(wrap, fill="x", pady=10)
        lbl(empty, "Henüz mesajın yok.", 14, "bold", MUTED).pack(anchor="w", padx=16, pady=(14, 4))
        lbl(empty, "Sağ üstteki Mesaj Oluştur butonuyla öğretmen veya öğrenci seçip konuşma başlatabilirsin.", 12, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 14))
    for t in rows:
        others = [x for x in t.get("katilimcilar", []) if x != user_id(self.user)]
        title = ", ".join(_msg_user_name(x) for x in others) or "Mesajlaşma"
        last = (t.get("mesajlar") or [{}])[-1]
        c = card(wrap, fill="x", pady=5)
        c.configure(cursor="hand2")
        lbl(c, title, 14, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Son mesaj: {last.get('mesaj','Henüz mesaj yok')}", 12, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0, 10))
        c.bind("<Button-1>", lambda e, tid=t.get("konusma_id"): MessageThreadDialog(self.master, tid, self.user, self.refresh))
        for child in c.winfo_children():
            child.bind("<Button-1>", lambda e, tid=t.get("konusma_id"): MessageThreadDialog(self.master, tid, self.user, self.refresh))

OgrenciPanel.messages_page = lambda self, f: _messages_page_v2(self, f, "egitmen")
EgitmenPanel.messages_page = lambda self, f: _messages_page_v2(self, f, "ogrenci")


def _forum_topic_create(master, user, refresh=None):
    win = ctk.CTkToplevel(master)
    win.title("Forum Konusu Aç")
    win.geometry("560x430")
    win.configure(fg_color=BG)
    win.grab_set()
    lbl(win, "Yeni Forum Konusu", 22, "bold", GREEN).pack(anchor="w", padx=22, pady=(22, 8))
    title = ctk.CTkEntry(win, placeholder_text="Konu başlığı", fg_color=BG_3, border_color=BORDER, height=42)
    title.pack(fill="x", padx=22, pady=8)
    desc = ctk.CTkTextbox(win, height=170, fg_color=BG_3, border_color=BORDER, text_color=TEXT)
    desc.pack(fill="both", expand=True, padx=22, pady=8)
    def save():
        baslik = title.get().strip()
        aciklama = desc.get("1.0", "end").strip()
        if not baslik or not aciklama:
            messagebox.showwarning("Eksik", "Konu başlığı ve açıklama yazmalısın.")
            return
        v = db.veri_yukle()
        arr = v.setdefault("forum_konulari", [])
        tid = f"FOR{len(arr)+1:04d}"
        arr.insert(0, {"konu_id": tid, "baslik": baslik, "aciklama": aciklama, "ogrenci_id": user_id(user), "rol": user.get("rol", "ogrenci"), "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"), "yorumlar": []})
        db.veri_kaydet(v)
        win.destroy()
        toast(master, "Forum konusu açıldı.", GREEN)
        try:
            if refresh: refresh()
        except Exception:
            pass
    btn(win, "Konuyu Aç", save, GREEN, GREEN_2, 140, 38).pack(anchor="w", padx=22, pady=(4, 18))


def _forum_page_with_create(self, f):
    self.header(f, "Forum", "Global forum başlıklarında soru sorabilir ve cevapları okuyabilirsin.")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=8, pady=(0, 8))
    btn(top, "Konu Aç", lambda: _forum_topic_create(self.master, self.user, self.refresh), GREEN, GREEN_2, 130, 36).pack(side="right")
    topics = db.veri_yukle().get("forum_konulari", [])
    outer, wrap = self.full_scroll_container(f)
    if not topics:
        lbl(wrap, "Henüz forum konusu yok. Sağ üstten konu açabilirsin.", 13, "normal", MUTED).pack(anchor="w", padx=16, pady=18)
    for t in topics:
        c = ctk.CTkFrame(wrap, fg_color=BG_3, corner_radius=14, border_width=1, border_color=BORDER)
        c.pack(fill="x", padx=10, pady=8)
        lbl(c, t.get("baslik", "Konu"), 15, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(12,2))
        lbl(c, f"Açan: {_msg_user_name(t.get('ogrenci_id'))}  •  {len(t.get('yorumlar', []))} cevap", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,6))
        lbl(c, t.get("aciklama", ""), 12, "normal", TEXT, wraplength=920, justify="left").pack(anchor="w", padx=16, pady=(0,8))
        btn(c, "Konuyu Aç", lambda tid=t.get("konu_id"): ForumTopicDialog(self.master, tid, self.user), BLUE, BLUE_2, 120, 30).pack(anchor="w", padx=16, pady=(0,12))
    ctk.CTkFrame(wrap, fg_color="transparent", height=520).pack(fill="x")

BasePanel.forum_page = _forum_page_with_create
OgrenciPanel.forum_page = _forum_page_with_create
EgitmenPanel.forum_page = _forum_page_with_create


def _pick_future_date(master, entry):
    win = ctk.CTkToplevel(master)
    win.title("Sınav Tarihi Seç")
    win.geometry("420x430")
    win.configure(fg_color=BG)
    win.grab_set()
    state = {"y": date.today().year, "m": date.today().month}
    holder = ctk.CTkFrame(win, fg_color="transparent")
    holder.pack(fill="both", expand=True, padx=16, pady=16)
    def draw():
        clear(holder)
        names = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        top = ctk.CTkFrame(holder, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        def prev():
            # geçmiş aya dönmeyi engelle
            if state["y"] == date.today().year and state["m"] <= date.today().month:
                return
            state["m"] -= 1
            if state["m"] < 1:
                state["m"] = 12; state["y"] -= 1
            draw()
        def nxt():
            state["m"] += 1
            if state["m"] > 12:
                state["m"] = 1; state["y"] += 1
            draw()
        btn(top, "‹", prev, BG_3, BG_3, 40, 30, text_color=TEXT).pack(side="left")
        lbl(top, f"{names[state['m']]} {state['y']}", 18, "bold").pack(side="left", expand=True)
        btn(top, "›", nxt, BG_3, BG_3, 40, 30, text_color=TEXT).pack(side="right")
        grid = ctk.CTkFrame(holder, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        for i, day in enumerate(["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"]):
            lbl(grid, day, 11, "bold", MUTED).grid(row=0, column=i, padx=4, pady=4)
        import calendar as _cal
        cal = _cal.Calendar(firstweekday=0)
        today = date.today()
        for r, week in enumerate(cal.monthdayscalendar(state["y"], state["m"]), start=1):
            for c, d in enumerate(week):
                if not d:
                    ctk.CTkLabel(grid, text="", width=44, height=36).grid(row=r, column=c, padx=3, pady=3)
                    continue
                dt = date(state["y"], state["m"], d)
                disabled = dt < today
                color = BG_3 if not disabled else "#1A2435"
                txt_color = TEXT if not disabled else MUTED
                def choose(day=d, y=state["y"], m=state["m"]):
                    picked = date(y, m, day)
                    if picked < date.today():
                        return
                    entry.delete(0, "end"); entry.insert(0, picked.isoformat())
                    win.destroy()
                b = btn(grid, str(d), choose, color, BLUE_2 if not disabled else color, 44, 34, text_color=txt_color)
                b.grid(row=r, column=c, padx=3, pady=3)
    draw()


def _teacher_add_course_page_v2(self, f):
    self.header(f, "Kurs / Ders Aç", "Yeni kurs açabilir; gün, saat ve sınav tarihini seçerek planlayabilirsin.")
    form = card(f, fill="x", padx=8, pady=8)
    vcmd = (form.register(lambda p: p.isdigit() or p == ""), "%P")
    name = ctk.CTkEntry(form, placeholder_text="Kurs adı", width=460, height=40, fg_color=BG_3, border_color=BORDER)
    name.pack(anchor="w", padx=18, pady=(16, 6))
    kont = ctk.CTkEntry(form, placeholder_text="Kontenjan (sadece rakam)", width=220, height=40, fg_color=BG_3, border_color=BORDER, validate="key", validatecommand=vcmd)
    kont.pack(anchor="w", padx=18, pady=6)
    aciklama = ctk.CTkEntry(form, placeholder_text="Açıklama", width=460, height=40, fg_color=BG_3, border_color=BORDER)
    aciklama.pack(anchor="w", padx=18, pady=6)
    lbl(form, "Ders günleri", 12, "bold", GREEN).pack(anchor="w", padx=18, pady=(10, 4))
    days_frame = ctk.CTkFrame(form, fg_color="transparent")
    days_frame.pack(anchor="w", padx=18, pady=(0, 6))
    selected_days = set()
    day_buttons = {}
    def toggle_day(day):
        if day in selected_days:
            selected_days.remove(day)
        else:
            selected_days.add(day)
        for d, b in day_buttons.items():
            b.configure(fg_color=GREEN if d in selected_days else BG_3, text_color="white" if d in selected_days else TEXT)
    for d in ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]:
        b = btn(days_frame, d, lambda x=d: toggle_day(x), BG_3, BG_3, 96, 32, text_color=TEXT)
        b.pack(side="left", padx=3, pady=3)
        day_buttons[d] = b
    time_frame = ctk.CTkFrame(form, fg_color="transparent")
    time_frame.pack(anchor="w", padx=18, pady=8)
    lbl(time_frame, "Saat:", 12, "bold", MUTED).pack(side="left", padx=(0, 8))
    hour = ctk.StringVar(value="10")
    minute = ctk.StringVar(value="00")
    ctk.CTkOptionMenu(time_frame, values=[f"{i:02d}" for i in range(8, 23)], variable=hour, width=80, fg_color=BLUE, button_color=BLUE_2).pack(side="left", padx=3)
    ctk.CTkOptionMenu(time_frame, values=["00", "15", "30", "45"], variable=minute, width=80, fg_color=BLUE, button_color=BLUE_2).pack(side="left", padx=3)
    date_frame = ctk.CTkFrame(form, fg_color="transparent")
    date_frame.pack(anchor="w", padx=18, pady=8)
    sinav = ctk.CTkEntry(date_frame, placeholder_text="Sınav tarihi: YYYY-AA-GG", width=260, height=40, fg_color=BG_3, border_color=BORDER)
    sinav.pack(side="left", padx=(0, 8))
    btn(date_frame, "Takvimden Seç", lambda: _pick_future_date(self.master, sinav), BLUE, BLUE_2, 130, 40).pack(side="left")
    def save():
        n = name.get().strip()
        k = kont.get().strip() or "30"
        if not n:
            messagebox.showwarning("Eksik", "Kurs adı gerekli."); return
        if not k.isdigit():
            messagebox.showwarning("Kontenjan hatalı", "Kontenjan alanına sadece rakam yazabilirsin."); return
        if not selected_days:
            messagebox.showwarning("Gün seç", "En az bir ders günü seçmelisin."); return
        exam_date = sinav.get().strip()
        if exam_date:
            try:
                dt = date.fromisoformat(exam_date)
                if dt < date.today():
                    messagebox.showwarning("Tarih hatalı", "Geçmiş sınav tarihi seçilemez."); return
            except Exception:
                messagebox.showwarning("Tarih hatalı", "Sınav tarihini YYYY-AA-GG formatında seç."); return
        saat = f"{hour.get()}:{minute.get()}"
        try:
            ok, msg = db.kurs_ekle(n, user_id(self.user), int(k), aciklama.get(), list(selected_days), saat, exam_date)
        except Exception as e:
            ok, msg = False, str(e)
        toast(self.master, f"Kurs oluşturuldu: {msg}" if ok else str(msg), GREEN if ok else RED)
        if ok:
            self.refresh()
    btn(form, "Kursu Oluştur", save, GREEN, GREEN_2, 180, 42).pack(anchor="w", padx=18, pady=14)

EgitmenPanel.add_course_page = _teacher_add_course_page_v2


def _render_courses_v2(self, area, only_mine=False):
    my = _active_student_course_ids(user_id(self.user))
    count = 0
    row = None
    courses = sorted_courses_for_display(_active_courses())
    for k in courses:
        reg = k.get("kurs_id") in my
        if only_mine and not reg:
            continue
        if count % 4 == 0:
            row = ctk.CTkFrame(area, fg_color="transparent")
            row.pack(fill="x", padx=0, pady=0)
        self.course_card(row, k, registered=reg)
        count += 1
    if count == 0:
        lbl(area, "Liste boş.", 14, "normal", MUTED).pack(pady=40)

OgrenciPanel.render_courses = _render_courses_v2


def _next_lesson_summary_v2(self):
    my = _active_student_course_ids(user_id(self.user))
    for k in _active_courses():
        if k.get("kurs_id") in my:
            gunler = ", ".join(k.get("takvim_gunler", [])) or "Gün belirtilmedi"
            return f"{k.get('kurs_adi')} • {gunler} • {k.get('takvim_saat','Saat yok')}"
    return "Henüz kayıtlı ders yok. Ders Kaydı ekranından kurs seçebilirsin."

OgrenciPanel.next_lesson_summary = _next_lesson_summary_v2


def _teacher_my_courses_v2(self, f):
    if not f.winfo_children():
        self.header(f, "Derslerim", "Verdiğin aktif kurslar.")
    area = ctk.CTkFrame(f, fg_color="transparent")
    area.pack(fill="x", padx=8)
    courses = [k for k in _active_courses() if k.get("egitmen_id") == user_id(self.user)]
    if not courses:
        lbl(area, "Henüz aktif kurs yok.", 13, "normal", MUTED).pack(pady=30)
    for k in courses:
        self.course_card(area, k, registered=True)

EgitmenPanel.my_courses = _teacher_my_courses_v2


def _course_card_v2(self, parent, kurs, registered=False):
    c = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, width=250, height=292)
    c.pack(side="left", padx=8, pady=8)
    c.pack_propagate(False)
    badge, badge_sub, badge_bg = course_badge(kurs)
    top = ctk.CTkFrame(c, fg_color=badge_bg, height=86, corner_radius=12, border_width=1, border_color=BORDER)
    top.pack(fill="x", padx=10, pady=(10, 8)); top.pack_propagate(False)
    lbl(top, badge, 23, "bold", self.accent).place(relx=0.5, rely=0.40, anchor="center")
    lbl(top, badge_sub, 10, "bold", MUTED).place(relx=0.5, rely=0.72, anchor="center")
    ders_kodu = kurs.get("ders_kodu") or kurs.get("kurs_id", "")
    baslik = kurs.get("kurs_adi", "Kurs")
    if ders_kodu and ders_kodu not in baslik:
        baslik = f"{ders_kodu} {baslik}"
    lbl(c, baslik[:42], 12, "bold", TEXT, wraplength=215, justify="left").pack(anchor="w", padx=12)
    lbl(c, f"Öğretmen: {egitmen_adi(kurs.get('egitmen_id'))}", 10, "normal", MUTED).pack(anchor="w", padx=12, pady=(5,0))
    ekstra = f"{kurs.get('seviye','')} • AKTS {kurs.get('akts','-')}" if kurs.get('akts') is not None else kurs.get('seviye','Başlangıç')
    lbl(c, f"{kurs.get('kategori','Genel')} • {ekstra}", 10, "normal", MUTED, wraplength=215, justify="left").pack(anchor="w", padx=12, pady=(4,0))
    sayi = len(kurs.get("kayitli_ogrenciler", [])); kont = kurs.get("kontenjan", 0)
    lbl(c, f"Kontenjan: {sayi}/{kont}", 10, "normal", MUTED).pack(anchor="w", padx=12, pady=(4,8))
    bar = ctk.CTkProgressBar(c, height=7, fg_color="#D7DEE8", progress_color=self.accent)
    bar.pack(fill="x", padx=12, pady=(0,10))
    try: bar.set(min(sayi / max(1, int(kont)), 1))
    except Exception: bar.set(0)
    row = ctk.CTkFrame(c, fg_color="transparent")
    row.pack(fill="x", padx=10, pady=(0, 10))
    kid = kurs.get("kurs_id")
    if self.user.get("rol") == "ogrenci" and registered:
        pending = _pending_exit_request(user_id(self.user), kid)
        if pending:
            lbl(row, "Başvuru bekleniyor", 10, "bold", YELLOW).pack(side="left", padx=2)
            btn(row, "Başvuruyu İptal Et", lambda rid=pending.get("basvuru_id"): (_cancel_course_exit(self.master, self.user, rid), self.refresh()), RED, RED, 138, 32).pack(side="left", padx=2)
        else:
            btn(row, "Derse Git", lambda k=kid: self.course_action(k, True), GREEN, GREEN_2, 92, 32).pack(side="left", padx=2)
            btn(row, "Dersten Çık", lambda k=kid: (_request_course_exit(self.master, self.user, k), self.refresh()), RED, RED, 105, 32).pack(side="left", padx=2)
    else:
        label = "Derse Git" if registered else "Kayıt Ol"
        btn(row, label, lambda k=kid, r=registered: self.course_action(k, r), GREEN, GREEN_2, 105, 32).pack(side="left", padx=2)

BasePanel.course_card = _course_card_v2


def _admin_close_course_reasoned_v2(self, kid):
    reason = _ask_admin_reason(self.master, "kurs kapatma işlemi")
    if not reason:
        return False
    veri = db.veri_yukle()
    course_name = kid
    teacher_id = None
    students = []
    removed_material_count = 0
    found = False
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kid:
            found = True
            if k.get("kapali") or k.get("durum") == "kapalı":
                db.veri_kaydet(veri)
                return False

            # Kurs kapatılırken o derse ait materyaller de sistemden kaldırılır.
            removed_material_count = len(k.get("materyaller", []) or [])
            k["materyaller"] = []

            k["kapali"] = True
            k["durum"] = "kapalı"
            k["kapatma_nedeni"] = reason
            k["kapatilma_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            k["materyaller_kaldirildi"] = True
            k["kaldirilan_materyal_sayisi"] = removed_material_count
            course_name = k.get("kurs_adi", kid)
            teacher_id = k.get("egitmen_id")
            students = list(k.get("kayitli_ogrenciler", []))
            break
    if not found:
        return False
    db.veri_kaydet(veri)
    if teacher_id:
        _safe_notify(teacher_id, "egitmen", f"{course_name} dersiniz admin tarafından kaldırıldı/kapatıldı. Neden: {reason}")
    for oid in students:
        _safe_notify(oid, "ogrenci", f"Kayıtlı olduğunuz {course_name} dersi admin tarafından kaldırıldı/kapatıldı. Neden: {reason}")
    _admin_log_reason(f"{course_name} kursunu kapattı; {removed_material_count} materyal kaldırıldı", reason)
    return True


def _admin_courses_page_reasoned_v2(self, f):
    self.header(f, "Kurs Yönetimi", "Kursları inceleyebilir ve gerekçe yazarak kapatabilirsin.")
    outer, wrap = self.full_scroll_container(f)
    for k in get_courses():
        c = card(wrap, fill="x", pady=5)
        durum = "Kapalı" if k.get("kapali") or k.get("durum") == "kapalı" else "Açık"
        lbl(c, f"{k.get('kurs_adi')}  •  {durum}", 13, "bold", RED if durum == "Kapalı" else GREEN, wraplength=860).pack(anchor="w", padx=16, pady=(10, 2))
        lbl(c, f"Öğretmen: {egitmen_adi(k.get('egitmen_id'))}  •  Öğrenci: {len(k.get('kayitli_ogrenciler', []))}/{k.get('kontenjan')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
        if k.get("kapatma_nedeni"):
            lbl(c, f"Kapatma nedeni: {k.get('kapatma_nedeni')}", 11, "bold", YELLOW, wraplength=860).pack(anchor="w", padx=16, pady=2)
        if durum != "Kapalı":
            def close_one(kid=k.get("kurs_id")):
                if _admin_close_course_reasoned_v2(self, kid):
                    toast(self.master, "Kurs kapatıldı ve bildirim gönderildi.", RED)
                    self.refresh()
            btn(c, "Kursu Kapat", close_one, RED, RED, 120, 30).pack(anchor="w", padx=16, pady=(6, 12))
        else:
            lbl(c, "Bu kurs kapalı. Öğretmen/öğrenci panellerinde görünmez; materyalleri de kaldırıldı.", 11, "bold", RED).pack(anchor="w", padx=16, pady=(6, 12))

AdminPanel.courses_page = _admin_courses_page_reasoned_v2


def _admin_users_page_search(self, f):
    self.header(f, "Kullanıcı Yönetimi", "Öğrenci ve öğretmenleri arayabilir, gerekçe yazarak sistemden kaldırabilirsin.")
    search_box = ctk.CTkFrame(f, fg_color="transparent")
    search_box.pack(fill="x", padx=8, pady=(0, 8))
    q_entry = ctk.CTkEntry(search_box, placeholder_text="İsim, ID veya e-posta ara...", fg_color=BG_3, border_color=BORDER, height=38)
    q_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    outer, wrap = self.full_scroll_container(f)
    def draw():
        clear(wrap)
        q = q_entry.get().lower().strip()
        v = db.veri_yukle()
        groups = [("Öğrenciler", "ogrenci", v.get("ogrenciler", [])), ("Öğretmenler", "egitmen", v.get("egitmenler", [])), ("Adminler", "admin", v.get("adminler", []))]
        for title, role, arr in groups:
            filtered = []
            for u in arr:
                kid = u.get("ogrenci_id") or u.get("egitmen_id") or u.get("admin_id") or u.get("id") or u.get("kullanici_adi", "")
                hay = f"{kid} {u.get('ad','')} {u.get('email','')}".lower()
                if not q or q in hay:
                    filtered.append((kid, u))
            if not filtered:
                continue
            lbl(wrap, title, 17, "bold", GREEN).pack(anchor="w", padx=8, pady=(14, 6))
            for kid, u in filtered[:200]:
                c = card(wrap, fill="x", pady=4)
                lbl(c, f"{kid} - {u.get('ad')} - {u.get('email','')}", 12, "normal", TEXT, wraplength=860).pack(side="left", padx=16, pady=10)
                if kid != "admin":
                    btn(c, "Kaldır", lambda x=kid, r=role: (_admin_delete_user_reasoned(self, x, r), toast(self.master, "Kullanıcı kaldırıldı.", RED), self.refresh()), RED, RED, 90, 30).pack(side="right", padx=12, pady=8)
    btn(search_box, "Ara", draw, BLUE, BLUE_2, 80, 38).pack(side="left")
    q_entry.bind("<KeyRelease>", lambda e: draw())
    draw()

AdminPanel.users_page = _admin_users_page_search



# ─────────────────────────────────────────────────────────────────────────────
# KÜÇÜK BUGFIX PATCH: kapalı kursların öğretmende görünmemesi ve çıkış
# başvuru bildirimlerinin işlemden sonra kaldırılması.
# ─────────────────────────────────────────────────────────────────────────────
def _teacher_course_list_active_final(self):
    return [k for k in _active_courses() if k.get("egitmen_id") == user_id(self.user)]

EgitmenPanel.teacher_course_list = _teacher_course_list_active_final


def _teacher_dashboard_active_final(self, f):
    self.header(f, f"Merhaba, {self.user.get('ad','Öğretmen')}!", "Kurslarını ve öğrencilerini yönet.")
    c = card(f, fill="x", padx=8, pady=(0, 10))
    lbl(c, "Bugünkü Derslerim", 15, "bold", GREEN).pack(anchor="w", padx=16, pady=(12, 4))
    bugun = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][date.today().weekday()]
    items = [k for k in self.teacher_course_list() if bugun in (k.get("takvim_gunler") or [])]
    if not items:
        lbl(c, "Bugün için planlanmış aktif ders görünmüyor.", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0, 12))
    for k in items[:5]:
        lbl(c, f"• {k.get('takvim_saat','')} - {k.get('kurs_adi')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=2)
    self.my_courses(f)

EgitmenPanel.dashboard = _teacher_dashboard_active_final


def _teacher_assignments_page_active_final(self, f):
    self.header(f, "Ödevler", "Derslerin için ödev oluştur; öğrencilerin takviminde otomatik görünür.")
    opts, mp = self.course_option_map()
    form = card(f, fill="x", padx=8, pady=8)
    if not opts:
        lbl(form, "Önce bir kurs oluşturun.", 13, "bold", MUTED).pack(anchor="w", padx=16, pady=16)
        return
    course_var = ctk.CTkOptionMenu(form, values=opts, fg_color=BLUE, button_color=BLUE_2)
    course_var.set(opts[0])
    course_var.pack(anchor="w", padx=16, pady=(14, 8))
    title = ctk.CTkEntry(form, placeholder_text="Ödev başlığı", fg_color=BG_3, border_color=BORDER)
    title.pack(fill="x", padx=16, pady=5)
    due = ctk.CTkEntry(form, placeholder_text="Son tarih: YYYY-AA-GG", fg_color=BG_3, border_color=BORDER)
    due.pack(fill="x", padx=16, pady=5)
    desc = ctk.CTkTextbox(form, height=86, fg_color=BG_3, border_color=BORDER, text_color=TEXT)
    desc.pack(fill="x", padx=16, pady=5)
    def add():
        k = mp.get(course_var.get(), {})
        if not title.get().strip() or not due.get().strip():
            messagebox.showwarning("Eksik", "Başlık ve son tarih gir.")
            return
        ok, msg = db.odev_ekle(k.get("kurs_id"), user_id(self.user), title.get().strip(), desc.get("1.0", "end").strip(), due.get().strip())
        toast(self.master, "Ödev eklendi; takvim güncellendi." if ok else str(msg), GREEN if ok else RED)
        self.refresh()
    btn(form, "Ödev Ekle", add, GREEN, GREEN_2, 130, 36).pack(anchor="w", padx=16, pady=(4, 14))

    active_ids = {k.get("kurs_id") for k in self.teacher_course_list()}
    outer, wrap = self.full_scroll_container(f)
    rows = db.odevleri_getir(egitmen_id=user_id(self.user)) if hasattr(db, "odevleri_getir") else []
    rows = [o for o in rows if o.get("kurs_id") in active_ids]
    courses = {k.get("kurs_id"): k for k in self.teacher_course_list()}
    if not rows:
        lbl(wrap, "Bu aktif kurslar için henüz ödev yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for o in rows:
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{o.get('baslik')} • {courses.get(o.get('kurs_id'),{}).get('kurs_adi', o.get('kurs_id'))}", 13, "bold", GREEN, wraplength=900).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, f"Son tarih: {o.get('son_tarih')}  •  {o.get('aciklama','')}", 11, "normal", MUTED, wraplength=900).pack(anchor="w", padx=16, pady=(0,10))

EgitmenPanel.teacher_assignments_page = _teacher_assignments_page_active_final


def _teacher_exams_page_active_final(self, f):
    self.header(f, "Sınavlar", "Derslerin için sınav oluştur; sınav takvimde anında görünür.")
    opts, mp = self.course_option_map()
    form = card(f, fill="x", padx=8, pady=8)
    if not opts:
        lbl(form, "Önce bir kurs oluşturun.", 13, "bold", MUTED).pack(anchor="w", padx=16, pady=16)
        return
    course_var = ctk.CTkOptionMenu(form, values=opts, fg_color=BLUE, button_color=BLUE_2)
    course_var.set(opts[0])
    course_var.pack(anchor="w", padx=16, pady=(14, 8))
    title = ctk.CTkEntry(form, placeholder_text="Sınav başlığı", fg_color=BG_3, border_color=BORDER)
    title.pack(fill="x", padx=16, pady=5)
    when = ctk.CTkEntry(form, placeholder_text="Sınav tarihi: YYYY-AA-GG", fg_color=BG_3, border_color=BORDER)
    when.pack(fill="x", padx=16, pady=5)
    def add():
        k = mp.get(course_var.get(), {})
        if not title.get().strip() or not when.get().strip():
            messagebox.showwarning("Eksik", "Başlık ve tarih gir.")
            return
        sorular = [{"soru": "Bu sınav hangi ders içindir?", "secenekler": [k.get("kurs_adi", "Ders"), "Diğer", "Boş", "Hiçbiri"], "dogru": 0}]
        ok, msg = db.sinav_ekle(k.get("kurs_id"), user_id(self.user), title.get().strip(), when.get().strip(), sorular)
        toast(self.master, "Sınav eklendi; takvim güncellendi." if ok else str(msg), GREEN if ok else RED)
        self.refresh()
    btn(form, "Sınav Ekle", add, GREEN, GREEN_2, 130, 36).pack(anchor="w", padx=16, pady=(4, 14))

    active_ids = {k.get("kurs_id") for k in self.teacher_course_list()}
    outer, wrap = self.full_scroll_container(f)
    rows = db.sinavlari_getir(egitmen_id=user_id(self.user)) if hasattr(db, "sinavlari_getir") else []
    rows = [s for s in rows if s.get("kurs_id") in active_ids]
    courses = {k.get("kurs_id"): k for k in self.teacher_course_list()}
    if not rows:
        lbl(wrap, "Bu aktif kurslar için henüz sınav yok.", 12, "normal", MUTED).pack(anchor="w", padx=12, pady=12)
    for s in rows:
        c = card(wrap, fill="x", pady=5)
        lbl(c, f"{s.get('baslik')} • {courses.get(s.get('kurs_id'),{}).get('kurs_adi', s.get('kurs_id'))}", 13, "bold", YELLOW, wraplength=900).pack(anchor="w", padx=16, pady=(10,2))
        lbl(c, f"Tarih: {s.get('tarih')}", 11, "normal", MUTED).pack(anchor="w", padx=16, pady=(0,10))

EgitmenPanel.teacher_exams_page = _teacher_exams_page_active_final


def _process_exit_request(master, req_id, approve=True):
    """Öğretmen onay/red verdikten sonra işlem bildirimi artık öğretmende kalmaz."""
    v = db.veri_yukle()
    req = None
    for r in v.setdefault("ders_cikis_basvurulari", []):
        if r.get("basvuru_id") == req_id:
            req = r
            break
    if not req or req.get("durum") != "bekliyor":
        messagebox.showwarning("Başvuru", "Bu başvuru artık beklemede değil.")
        return
    uid = req.get("ogrenci_id")
    kid = req.get("kurs_id")
    if approve:
        req["durum"] = "onaylandı"
        v["kayitlar"] = [x for x in v.get("kayitlar", []) if not (x.get("ogrenci_id") == uid and x.get("kurs_id") == kid)]
        for k in v.get("kurslar", []):
            if k.get("kurs_id") == kid and uid in k.get("kayitli_ogrenciler", []):
                k["kayitli_ogrenciler"].remove(uid)
        msg = f"{req.get('kurs_adi', kid)} dersi için çıkış başvurun onaylandı."
    else:
        req["durum"] = "reddedildi"
        msg = f"{req.get('kurs_adi', kid)} dersi için çıkış başvurun reddedildi."
    req["sonuc_tarihi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    # İşlem yapılan başvuru bildirimi öğretmenin bildirim listesinden kaldırılır.
    v["bildirimler"] = [b for b in v.get("bildirimler", []) if b.get("cikis_basvuru_id") != req_id]
    bid = f"BIL{len(v.get('bildirimler', []))+1:04d}"
    v.setdefault("bildirimler", []).insert(0, {
        "bildirim_id": bid,
        "kullanici_id": uid,
        "rol": "ogrenci",
        "mesaj": msg,
        "okundu": False,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
    })
    db.veri_kaydet(v)
    toast(master, "Başvuru sonucu kaydedildi.", GREEN if approve else YELLOW)
    try:
        if hasattr(master, "current"):
            master.current.refresh()
    except Exception:
        pass




# ─────────────────────────────────────────────────────────────────────────────
# SON DÜZELTME PATCH: sidebar üst kayma, mesaj bildirimi, güvenli mesaj arama,
# gerçek şifre değiştirme ekranı.
# ─────────────────────────────────────────────────────────────────────────────

def _stable_render_sidebar_open(self):
    """Sidebar içeriğini her çizimde en üstten başlatır; mouse wheel ile üst boşluğa kaçmayı engeller."""
    top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
    top.pack(fill="x", padx=14, pady=(22, 12))
    lbl(top, "Menü", 18, "bold").pack(side="left")
    btn(top, "×", self.toggle_sidebar, BG_3, BG_3, 40, 32).pack(side="right")

    scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", width=SIDEBAR_OPEN_W-18)
    scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    cats = ["Genel", "Dersler", "Akademik", "İletişim", "Kişisel", "Yönetim"]
    for cat in cats:
        items = [m for m in self.menu_items if m["cat"] == cat]
        if not items:
            continue
        head_text = f"{cat} {'▼' if self.category_open.get(cat, True) else '▶'}"
        head = ctk.CTkButton(
            scroll, text=head_text, height=28, corner_radius=9,
            fg_color="transparent", hover_color=BG_3, text_color=self.accent,
            anchor="w", font=(FONT, 11, "bold"),
            command=lambda c=cat: self.toggle_category(c)
        )
        head.pack(fill="x", padx=8, pady=(8, 2))
        if not self.category_open.get(cat, True):
            continue
        for item in items:
            active = item["idx"] == self.active_idx
            b = ctk.CTkButton(
                scroll, text=f"   {item['title']}", height=34, corner_radius=10,
                fg_color=BG_3 if active else "transparent", hover_color=BG_3,
                text_color=self.accent if active else TEXT, anchor="w", font=(FONT, 11),
                command=lambda i=item["idx"]: self.select_page(i)
            )
            b.pack(fill="x", padx=8, pady=2)

    def _clamp_sidebar_scroll(event=None):
        try:
            canvas = getattr(scroll, "_parent_canvas", None)
            if canvas:
                first, last = canvas.yview()
                if first <= 0 and event is not None and getattr(event, "delta", 0) > 0:
                    canvas.yview_moveto(0)
                    return "break"
        except Exception:
            pass
        return None

    try:
        canvas = getattr(scroll, "_parent_canvas", None)
        if canvas:
            canvas.yview_moveto(0)
            canvas.bind("<MouseWheel>", _clamp_sidebar_scroll, add="+")
    except Exception:
        pass

BasePanel.render_sidebar_open = _stable_render_sidebar_open


def _role_for_uid(uid):
    try:
        v = db.veri_yukle()
        for o in v.get("ogrenciler", []):
            if uid in [o.get("id"), o.get("ogrenci_id"), o.get("kullanici_adi")]:
                return "ogrenci"
        for e in v.get("egitmenler", []):
            if uid in [e.get("id"), e.get("egitmen_id"), e.get("kullanici_adi")]:
                return "egitmen"
        for a in v.get("adminler", []):
            if uid in [a.get("id"), a.get("admin_id"), a.get("kullanici_adi")]:
                return "admin"
        adm = v.get("admin", {})
        if uid in [adm.get("id"), adm.get("admin_id"), adm.get("kullanici_adi")]:
            return "admin"
    except Exception:
        pass
    return "ogrenci"


def _send_thread_message(tid, sender, text):
    """Mesajı kaydeder ve diğer katılımcılara bildirim düşürür."""
    v = db.veri_yukle()
    threads = _ensure_message_threads(v)
    hedefler = []
    for t in threads:
        if t.get("konusma_id") == tid:
            t.setdefault("mesajlar", []).append({"yazar_id": sender, "mesaj": text, "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
            t["tarih"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            hedefler = [x for x in t.get("katilimcilar", []) if x != sender]
            break
    for hid in hedefler:
        bid = f"BIL{len(v.get('bildirimler', []))+1:04d}"
        v.setdefault("bildirimler", []).insert(0, {
            "bildirim_id": bid,
            "kullanici_id": hid,
            "rol": _role_for_uid(hid),
            "mesaj": f"Yeni mesaj: {_msg_user_name(sender)} sana mesaj gönderdi.",
            "okundu": False,
            "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "mesaj_konusma_id": tid,
        })
    db.veri_kaydet(v)


class NewMessageDialog(ctk.CTkToplevel):
    """Arama sırasında pencereyi komple yeniden çizmez; kapanmış Entry hatası üretmez."""
    def __init__(self, master, user, target_role="egitmen", on_created=None):
        super().__init__(master)
        self.user = user
        self.target_role = target_role or "egitmen"
        self.on_created = on_created
        self.search_text = ""
        self.title("Mesaj Oluştur")
        self.geometry("590x650")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def set_role(self, role):
        self.target_role = role
        self.search_text = ""
        try:
            self.search_entry.delete(0, "end")
        except Exception:
            pass
        self.refresh_targets()
        self.update_tabs()

    def update_tabs(self):
        try:
            self.teacher_btn.configure(fg_color=GREEN if self.target_role == "egitmen" else BG_3)
            self.student_btn.configure(fg_color=GREEN if self.target_role == "ogrenci" else BG_3)
            self.title_label.configure(text="Öğretmen Seç" if self.target_role == "egitmen" else "Öğrenci Seç")
        except Exception:
            pass

    def targets(self):
        v = db.veri_yukle()
        arr = v.get("ogrenciler", []) if self.target_role == "ogrenci" else v.get("egitmenler", [])
        q = (self.search_text or "").lower().strip()
        out = []
        me = user_id(self.user)
        for u in arr:
            uid = _msg_user_id(u)
            if uid == me:
                continue
            name = u.get("ad", uid)
            if not q or q in uid.lower() or q in name.lower() or q in u.get("email", "").lower():
                out.append((uid, name, u.get("email", "")))
        return out

    def build(self):
        clear(self)
        lbl(self, "Mesaj Oluştur", 22, "bold").pack(anchor="w", padx=22, pady=(22, 6))
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=22, pady=(0, 8))
        self.teacher_btn = btn(tabs, "Öğretmenler", lambda: self.set_role("egitmen"), GREEN if self.target_role == "egitmen" else BG_3, GREEN_2 if self.target_role == "egitmen" else BG_3, 130, 34, text_color="white" if self.target_role == "egitmen" else TEXT)
        self.teacher_btn.pack(side="left", padx=(0, 8))
        self.student_btn = btn(tabs, "Öğrenciler", lambda: self.set_role("ogrenci"), GREEN if self.target_role == "ogrenci" else BG_3, GREEN_2 if self.target_role == "ogrenci" else BG_3, 130, 34, text_color="white" if self.target_role == "ogrenci" else TEXT)
        self.student_btn.pack(side="left")
        self.title_label = lbl(self, "Öğretmen Seç" if self.target_role == "egitmen" else "Öğrenci Seç", 15, "bold", TEXT)
        self.title_label.pack(anchor="w", padx=22)
        lbl(self, "Arama kutusuna isim, ID veya e-posta yazabilirsin.", 11, "normal", MUTED).pack(anchor="w", padx=22)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=12)
        self.search_entry = ctk.CTkEntry(row, placeholder_text="Ara...", fg_color=BG_3, border_color=BORDER, height=38)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.on_search_key)
        btn(row, "Ara", self.on_search_key, BLUE, BLUE_2, 80, 38).pack(side="left")
        self.sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.sc.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.refresh_targets()

    def on_search_key(self, event=None):
        try:
            if not self.winfo_exists():
                return
            self.search_text = self.search_entry.get()
            self.refresh_targets()
        except Exception:
            pass

    def refresh_targets(self):
        try:
            clear(self.sc)
        except Exception:
            return
        items = self.targets()
        if not items:
            lbl(self.sc, "Sonuç bulunamadı.", 13, "normal", MUTED).pack(anchor="w", padx=8, pady=10)
            return
        for uid, name, email in items:
            c = card(self.sc, fill="x", pady=4)
            lbl(c, f"{name}  •  {uid}", 13, "bold", TEXT, wraplength=420).pack(anchor="w", padx=14, pady=(8, 1))
            lbl(c, email or "E-posta yok", 10, "normal", MUTED).pack(anchor="w", padx=14, pady=(0, 7))
            btn(c, "Mesajlaş", lambda x=uid: self.open_thread(x), GREEN, GREEN_2, 110, 30).pack(anchor="w", padx=14, pady=(0, 10))

    def open_thread(self, target_id):
        tid = _get_or_create_thread(user_id(self.user), target_id)
        try:
            if self.on_created:
                self.on_created()
        except Exception:
            pass
        self.destroy()
        MessageThreadDialog(self.master, tid, self.user, self.on_created)


class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, panel):
        super().__init__(master)
        self.panel = panel
        self.user = panel.user
        self.show_passwords = False
        self.title("Şifre Değiştir")
        self.geometry("460x390")
        self.configure(fg_color=BG)
        self.grab_set()
        self.build()

    def build(self):
        lbl(self, "Şifre Değiştir", 22, "bold", GREEN).pack(anchor="w", padx=24, pady=(24, 6))
        lbl(self, "Mevcut şifreni doğrulayıp yeni şifreni belirle.", 12, "normal", MUTED).pack(anchor="w", padx=24, pady=(0, 16))
        self.old_entry = self._password_row("Mevcut şifre")
        self.new_entry = self._password_row("Yeni şifre")
        self.repeat_entry = self._password_row("Yeni şifre tekrar")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(8, 0))
        btn(row, "Göster / Gizle", self.toggle_show, BG_3, BG_3, 130, 34).pack(side="left")
        btn(row, "Kaydet", self.save, GREEN, GREEN_2, 130, 34).pack(side="right")

    def _password_row(self, placeholder):
        e = ctk.CTkEntry(self, placeholder_text=placeholder, show="•", fg_color=BG_3, border_color=BORDER, height=42)
        e.pack(fill="x", padx=24, pady=6)
        return e

    def toggle_show(self):
        self.show_passwords = not self.show_passwords
        show = "" if self.show_passwords else "•"
        for e in (self.old_entry, self.new_entry, self.repeat_entry):
            try:
                e.configure(show=show)
            except Exception:
                pass

    def save(self):
        old = self.old_entry.get().strip()
        new = self.new_entry.get().strip()
        rep = self.repeat_entry.get().strip()
        current = str(self.user.get("sifre", ""))
        if old != current:
            messagebox.showwarning("Şifre", "Mevcut şifre hatalı.")
            return
        if len(new) < 3:
            messagebox.showwarning("Şifre", "Yeni şifre en az 3 karakter olmalı.")
            return
        if new != rep:
            messagebox.showwarning("Şifre", "Yeni şifreler eşleşmiyor.")
            return
        uid = user_id(self.user)
        role = self.user.get("rol", "")
        v = db.veri_yukle()
        changed = False
        def _try_update(arr):
            nonlocal changed
            for u in arr:
                if uid in [u.get("id"), u.get("ogrenci_id"), u.get("egitmen_id"), u.get("admin_id"), u.get("kullanici_adi")]:
                    u["sifre"] = new
                    changed = True
        if role == "ogrenci":
            _try_update(v.get("ogrenciler", []))
        elif role == "egitmen":
            _try_update(v.get("egitmenler", []))
        else:
            _try_update(v.get("adminler", []))
            adm = v.get("admin", {})
            if uid in [adm.get("id"), adm.get("admin_id"), adm.get("kullanici_adi")]:
                adm["sifre"] = new
                changed = True
        if not changed:
            messagebox.showerror("Şifre", "Kullanıcı kaydı bulunamadı.")
            return
        db.veri_kaydet(v)
        self.user["sifre"] = new
        self.destroy()
        toast(self.master, "Şifren başarıyla değiştirildi.", GREEN)


def _open_change_password(self):
    self.close_profile_dropdown()
    ChangePasswordDialog(self.master, self)


def _profile_dropdown_with_password_dialog(self):
    if self.profile_dropdown is not None and self.profile_dropdown.winfo_exists():
        self.close_profile_dropdown()
        return
    self.profile_dropdown = ctk.CTkFrame(
        self,
        fg_color=CARD,
        corner_radius=16,
        border_width=1,
        border_color=BORDER,
        width=260,
        height=300,
    )
    self.profile_dropdown.place(relx=1.0, y=64, x=-24, anchor="ne")
    self.profile_dropdown.pack_propagate(False)
    lbl(self.profile_dropdown, self.user.get("ad", "Kullanıcı"), 17, "bold").pack(pady=(18, 2))
    lbl(self.profile_dropdown, self.user.get("rol", "").capitalize(), 11, "normal", MUTED).pack(pady=(0, 12))
    btn(self.profile_dropdown, "Şifre Değiştir", lambda: _open_change_password(self), BG_3, BG_3, 210, 34).pack(pady=4)
    btn(self.profile_dropdown, "Tema Değiştir", self.change_theme, BG_3, BG_3, 210, 34).pack(pady=4)
    btn(self.profile_dropdown, "Takvim", lambda: CalendarDialog(self.master), BG_3, BG_3, 210, 34).pack(pady=4)
    btn(self.profile_dropdown, "Çıkış Yap", self.logout_from_dropdown, RED, RED, 210, 36).pack(pady=(14, 0))
    self.profile_dropdown.lift()

BasePanel.toggle_profile_dropdown = _profile_dropdown_with_password_dialog




# ─────────────────────────────────────────────────────────────────────────────
# FINAL PATCH: Sidebar scrollbar kaldırma + kayıt e-postasında @gmail.com zorunluluğu
# ─────────────────────────────────────────────────────────────────────────────

def _valid_email(value):
    """Hesap açma/başvuru ekranlarında yalnızca Gmail adresi kabul edilir."""
    value = (value or "").strip().lower()
    return value.endswith("@gmail.com") and value.count("@") == 1 and value.split("@", 1)[0].strip() != ""


def _sidebar_open_without_scrollbar(self):
    """Sol menüdeki görünür scrollbar'ı tamamen kaldırır; menü sabit ve temiz kalır."""
    top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
    top.pack(fill="x", padx=14, pady=(22, 12))
    lbl(top, "Menü", 18, "bold").pack(side="left")
    btn(top, "×", self.toggle_sidebar, BG_3, BG_3, 40, 32).pack(side="right")

    # Scrollbar istemediğimiz için CTkScrollableFrame yerine normal frame kullanıyoruz.
    menu_body = ctk.CTkFrame(self.sidebar, fg_color="transparent", width=SIDEBAR_OPEN_W-18)
    menu_body.pack(fill="both", expand=True, padx=8, pady=(0, 12))
    menu_body.pack_propagate(False)

    cats = ["Genel", "Dersler", "Akademik", "İletişim", "Kişisel", "Yönetim"]
    for cat in cats:
        items = [m for m in self.menu_items if m["cat"] == cat]
        if not items:
            continue
        head_text = f"{cat} {'▼' if self.category_open.get(cat, True) else '▶'}"
        head = ctk.CTkButton(
            menu_body, text=head_text, height=28, corner_radius=9,
            fg_color="transparent", hover_color=BG_3, text_color=self.accent,
            anchor="w", font=(FONT, 11, "bold"),
            command=lambda c=cat: self.toggle_category(c)
        )
        head.pack(fill="x", padx=8, pady=(8, 2))
        if not self.category_open.get(cat, True):
            continue
        for item in items:
            active = item["idx"] == self.active_idx
            b = ctk.CTkButton(
                menu_body, text=f"   {item['title']}", height=34, corner_radius=10,
                fg_color=BG_3 if active else "transparent", hover_color=BG_3,
                text_color=self.accent if active else TEXT, anchor="w", font=(FONT, 11),
                command=lambda i=item["idx"]: self.select_page(i)
            )
            b.pack(fill="x", padx=8, pady=2)

BasePanel.render_sidebar_open = _sidebar_open_without_scrollbar




# ─────────────────────────────────────────────────────────────────────────────
# FINAL PATCH: Girişte Şifremi Unuttum / kullanıcı adıyla şifre sıfırlama
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordDialog(ctk.CTkToplevel):
    """Kullanıcı adı yazılarak şifre değiştirme ekranı.
    Not: Kullanıcının istediği gibi mevcut şifre sormaz; sadece ID ile yeni şifre belirler.
    """
    def __init__(self, master, role=None):
        super().__init__(master)
        self.role = role
        self.show_passwords = False
        self.title("Şifremi Unuttum")
        self.geometry("440x380")
        self.configure(fg_color=BG)
        self.grab_set()
        self.resizable(False, False)
        self.build()

    def build(self):
        lbl(self, "Şifremi Unuttum", 22, "bold", GREEN).pack(anchor="w", padx=24, pady=(24, 6))
        role_txt = {"ogrenci": "Öğrenci", "egitmen": "Öğretmen", "admin": "Admin"}.get(self.role, "Kullanıcı")
        lbl(self, f"{role_txt} kullanıcı adını yazıp yeni şifre belirleyebilirsin.", 12, "normal", MUTED, wraplength=380).pack(anchor="w", padx=24, pady=(0, 16))
        self.uid_entry = ctk.CTkEntry(self, placeholder_text="Kullanıcı adı / ID", fg_color=BG_3, border_color=BORDER, height=42)
        self.uid_entry.pack(fill="x", padx=24, pady=6)
        self.new_entry = ctk.CTkEntry(self, placeholder_text="Yeni şifre", show="●", fg_color=BG_3, border_color=BORDER, height=42)
        self.new_entry.pack(fill="x", padx=24, pady=6)
        self.rep_entry = ctk.CTkEntry(self, placeholder_text="Yeni şifre tekrar", show="●", fg_color=BG_3, border_color=BORDER, height=42)
        self.rep_entry.pack(fill="x", padx=24, pady=6)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(10, 0))
        btn(row, "Göster / Gizle", self.toggle_show, BG_3, BG_3, 130, 34).pack(side="left")
        btn(row, "Şifreyi Değiştir", self.save, GREEN, GREEN_2, 165, 34).pack(side="right")
        lbl(self, "Sadece kullanıcı adı yeterlidir; eski şifre sorulmaz.", 10, "normal", MUTED).pack(anchor="w", padx=24, pady=(14, 0))

    def toggle_show(self):
        self.show_passwords = not self.show_passwords
        show = "" if self.show_passwords else "●"
        for e in (self.new_entry, self.rep_entry):
            try:
                e.configure(show=show)
            except Exception:
                pass

    def _matches_uid(self, u, uid):
        vals = [
            u.get("id"), u.get("ogrenci_id"), u.get("egitmen_id"),
            u.get("admin_id"), u.get("kullanici_adi"), u.get("username")
        ]
        return uid in [str(x) for x in vals if x is not None]

    def save(self):
        uid = self.uid_entry.get().strip()
        new = self.new_entry.get().strip()
        rep = self.rep_entry.get().strip()
        if not uid or not new or not rep:
            messagebox.showwarning("Eksik bilgi", "Kullanıcı adı ve yeni şifre alanlarını doldur.")
            return
        if len(new) < 3:
            messagebox.showwarning("Şifre", "Yeni şifre en az 3 karakter olmalı.")
            return
        if new != rep:
            messagebox.showwarning("Şifre", "Yeni şifreler eşleşmiyor.")
            return

        v = db.veri_yukle()
        changed = False
        role_arrays = []
        if self.role == "ogrenci":
            role_arrays = [("ogrenci", v.get("ogrenciler", []))]
        elif self.role == "egitmen":
            role_arrays = [("egitmen", v.get("egitmenler", []))]
        elif self.role == "admin":
            role_arrays = [("admin", v.get("adminler", []))]
        else:
            role_arrays = [
                ("ogrenci", v.get("ogrenciler", [])),
                ("egitmen", v.get("egitmenler", [])),
                ("admin", v.get("adminler", [])),
            ]

        for _role, arr in role_arrays:
            for u in arr:
                if self._matches_uid(u, uid):
                    u["sifre"] = new
                    changed = True
        # Eski sistemde tekil admin kaydı da bulunabiliyor.
        if self.role in (None, "admin"):
            adm = v.get("admin", {})
            if isinstance(adm, dict) and self._matches_uid(adm, uid):
                adm["sifre"] = new
                changed = True

        if not changed:
            messagebox.showerror("Kullanıcı bulunamadı", "Bu kullanıcı adıyla kayıt bulunamadı.")
            return
        db.veri_kaydet(v)
        messagebox.showinfo("Başarılı", "Şifren değiştirildi. Yeni şifrenle giriş yapabilirsin.")
        self.destroy()


def _login_dialog_init_eye_forgot(self, master, role, callback):
    ctk.CTkToplevel.__init__(self, master)
    self.role = role
    self.callback = callback
    self.title("Giriş Yap")
    self.geometry("390x610")
    self.configure(fg_color=BG)
    self.grab_set()
    self.resizable(False, False)
    role_names = {"ogrenci":"Öğrenci", "egitmen":"Öğretmen", "admin":"Admin"}
    lbl(self, f"{role_names.get(role, role)} Girişi", 24, "bold").pack(pady=(34, 8))
    lbl(self, "Kullanıcı ID ve şifrenizi girin", 12, "normal", MUTED).pack(pady=(0, 22))
    self.e_user = ctk.CTkEntry(self, placeholder_text="Kullanıcı ID", width=280, height=44, corner_radius=12, fg_color=BG_3, border_color=BORDER)
    self.e_user.pack(pady=7)
    pass_box = _password_box(self, "Şifre", 280, 44)
    pass_box.pack(pady=7, padx=54, fill="x")
    self.e_pass = pass_box.entry
    self.remember = ctk.CTkCheckBox(self, text="Beni hatırla", fg_color=GREEN, hover_color=GREEN_2)
    self.remember.pack(pady=(8, 4))
    self.e_pass.bind("<Return>", lambda e: self.try_login())
    btn(self, "Giriş Yap", self.try_login, GREEN, GREEN_2, 280, 44).pack(pady=(18, 6))
    forgot = lbl(self, "Şifremi unuttum", 11, "bold", GREEN)
    forgot.pack(pady=(0, 8))
    forgot.configure(cursor="hand2")
    forgot.bind("<Button-1>", lambda e: ForgotPasswordDialog(self, self.role))
    self.render_remembered_accounts()

LoginDialog.__init__ = _login_dialog_init_eye_forgot

# ─────────────────────────────────────────────────────────────────────────────
# UYGULAMA
# ─────────────────────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hextech Akademi - Tam Sürüm")
        setup_app_icon(self)
        self.geometry("1380x860")
        self.minsize(1100, 700)
        self.theme_light = False
        apply_theme(False)
        self.configure(fg_color=BG)
        try:
            db.veri_yukle()
        except Exception:
            pass
        self.current = None
        self.show_login()

    def show_login(self):
        if self.current:
            self.current.destroy()
        self.configure(fg_color=BG)
        self.current = LoginScreen(self)
        self.current.pack(fill="both", expand=True)

    def show_panel(self, user):
        if self.current:
            self.current.destroy()
        role = user.get("rol")
        if role == "ogrenci":
            self.current = OgrenciPanel(self, user)
        elif role == "egitmen":
            self.current = EgitmenPanel(self, user)
        else:
            self.current = AdminPanel(self, user)
        self.current.pack(fill="both", expand=True)


def uygulamayi_baslat():
    app = App()
    app.mainloop()
