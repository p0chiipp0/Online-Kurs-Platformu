# coding: utf-8
"""
mail_servisi.py - Hextech Akademi Mail Bildirim Sistemi

Öğretmen/Admin başvurusu olduğunda belirlediğin ana e-postaya mail gönderir.
Gmail için normal şifre değil, Google Uygulama Şifresi kullanılmalıdır.

Ayar dosyası önceliği:
1) mail_ayarlari.env
2) .env
3) Sistem ortam değişkenleri
"""

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _env_yukle():
    """mail_ayarlari.env veya .env içindeki KEY=VALUE satırlarını os.environ'a yükler."""
    for dosya_adi in ("mail_ayarlari.env", ".env"):
        dosya = BASE_DIR / dosya_adi
        if not dosya.exists():
            continue
        for satir in dosya.read_text(encoding="utf-8").splitlines():
            satir = satir.strip()
            if not satir or satir.startswith("#") or "=" not in satir:
                continue
            key, value = satir.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


def mail_ayarlari_getir():
    _env_yukle()
    return {
        "gonderen": os.getenv("MAIL_GONDEREN", "").strip(),
        "sifre": os.getenv("MAIL_SIFRE", "").strip(),
        "alici": os.getenv("MAIL_ALICI", "").strip(),
        "smtp_sunucu": os.getenv("MAIL_SMTP", "smtp.gmail.com").strip(),
        "smtp_port": int(os.getenv("MAIL_PORT", "587").strip() or 587),
    }


def mail_ayarlari_tamam_mi():
    a = mail_ayarlari_getir()
    return bool(a["gonderen"] and a["sifre"] and a["alici"] and "BURAYA" not in a["sifre"])


def _mail_gonder(konu, icerik, yanit_adresi=None):
    a = mail_ayarlari_getir()
    if not a["gonderen"] or not a["sifre"] or not a["alici"]:
        return False, "Mail ayarları eksik. mail_ayarlari.env dosyasını doldurun."
    if "BURAYA" in a["sifre"]:
        return False, "MAIL_SIFRE alanına Google Uygulama Şifresi yazılmamış."

    mesaj = EmailMessage()
    mesaj["Subject"] = konu
    mesaj["From"] = a["gonderen"]
    mesaj["To"] = a["alici"]
    if yanit_adresi:
        mesaj["Reply-To"] = yanit_adresi
    mesaj.set_content(icerik)

    try:
        with smtplib.SMTP(a["smtp_sunucu"], a["smtp_port"], timeout=20) as smtp:
            smtp.starttls()
            smtp.login(a["gonderen"], a["sifre"])
            smtp.send_message(mesaj)
        return True, "Mail gönderildi."
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail giriş hatası: normal şifre değil, Google Uygulama Şifresi kullanmalısın."
    except Exception as e:
        return False, f"Mail gönderilemedi: {e}"


def basvuru_maili_gonder(rol, kullanici_id, ad, email, uzmanlik="Belirtilmedi", ek_not=""):
    """Öğretmen/Admin başvurusunu ana e-postaya yollar."""
    rol_goster = "Öğretmen" if str(rol).lower().startswith(("ö", "o", "egit", "eğit")) else "Admin"
    konu = f"[Hextech Akademi] Yeni {rol_goster} Başvurusu"
    icerik = f"""Yeni {rol_goster} başvurusu alındı.

Ad Soyad      : {ad}
Kullanıcı ID  : {kullanici_id}
E-posta       : {email}
Uzmanlık/Not  : {uzmanlik}
Rol           : {rol_goster}
Tarih         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

Ek Not:
{ek_not or '-'}

Bu başvuruyu programdaki Admin Paneli üzerinden inceleyebilirsin.
"""
    return _mail_gonder(konu, icerik, yanit_adresi=email)


def test_maili_gonder():
    """Ayarların doğru olup olmadığını test etmek için kullanılır."""
    konu = "[Hextech Akademi] Test Maili"
    icerik = f"""Merhaba,

Hextech Akademi mail sistemi çalışıyor.

Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

Bu maili aldıysan başvuru bildirimleri de gönderilebilir.
"""
    return _mail_gonder(konu, icerik)

# ─────────────────────────────────────────────────────────────────────
# EK: Başvurana / kullanıcıya doğrudan bilgilendirme maili gönderme
# ─────────────────────────────────────────────────────────────────────
def kullanici_bilgilendirme_maili_gonder(alici_email, konu, icerik):
    """Sistem hesabından belirli kullanıcıya mail gönderir."""
    a = mail_ayarlari_getir()
    if not alici_email:
        return False, "Alıcı e-posta boş."
    if not a["gonderen"] or not a["sifre"]:
        return False, "Gönderen mail ayarları eksik."
    if "BURAYA" in a["sifre"]:
        return False, "MAIL_SIFRE alanına Google Uygulama Şifresi yazılmamış."

    mesaj = EmailMessage()
    mesaj["Subject"] = konu
    mesaj["From"] = a["gonderen"]
    mesaj["To"] = alici_email
    mesaj.set_content(icerik)
    try:
        with smtplib.SMTP(a["smtp_sunucu"], a["smtp_port"], timeout=20) as smtp:
            smtp.starttls()
            smtp.login(a["gonderen"], a["sifre"])
            smtp.send_message(mesaj)
        return True, "Kullanıcı bilgilendirme maili gönderildi."
    except Exception as e:
        return False, f"Kullanıcı maili gönderilemedi: {e}"
