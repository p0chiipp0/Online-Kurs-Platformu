# coding: utf-8
"""
veritabani.py - Online Kurs Platformu TAM ÖZELLİKLİ Veri Katmanı

Mevcut JSON tabanlı yapı korunur; eski veriler silinmeden yeni alanlar otomatik eklenir.
Eklenen modüller: ilerleme, sertifika, rozet, ödev, quiz/sınav, yoklama,
duyuru, bildirim, mesajlaşma, yorum-puan, favori, hedef, materyal,
ders planı, forum, rapor/export, kullanıcı durumu, takvim.
"""

import csv
import json
import os
import shutil
from datetime import datetime, date, timedelta
from statistics import mean

try:
    from mail_servisi import basvuru_maili_gonder
except Exception:
    basvuru_maili_gonder = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOSYA_ADI = os.path.join(BASE_DIR, "platform_verisi.json")
DOSYA_KISA_ADI = "platform_verisi.json"

VARSAYILAN_ADMIN = {
    "kullanici_adi": "admin",
    "sifre": "123",
    "ad": "Sistem Yöneticisi",
    "rol": "admin",
    "durum": "aktif",
}

ANAHTARLAR = {
    "ogrenciler": [],
    "egitmenler": [],
    "adminler": [],
    "kurslar": [],
    "kayitlar": [],
    "notlar": [],
    "loglar": [],
    "duyurular": [],
    "bildirimler": [],
    "mesajlar": [],
    "odevler": [],
    "teslimler": [],
    "sinavlar": [],
    "sinav_sonuclari": [],
    "yoklamalar": [],
    "yorumlar": [],
    "favoriler": [],
    "hedefler": [],
    "rozetler": [],
    "exportlar": [],
    "takvim_iptaller": [],
    "yapilacaklar": [],
    "yardim_kayitlari": [],
    "destek_talepleri": [],
    "admin_basvurular": [],
    "cop_kutusu": [],
    "kullanici_hareketleri": [],
    "kurs_onaylari": [],
    "proje_testleri": [],
    "kilavuz_kayitlari": [],
    "sistem_ayarlari": {"tema": "light", "renk": "yesil", "beni_hatirla": None, "yazi_olcegi": 1.0, "sidebar": "genis"},
}

DEMO_OGRENCILER = [
    {"ogrenci_id": "ogr001", "id": "ogr001", "ad": "Ali Veli", "email": "ali@mail.com", "sifre": "sifre123", "rol": "ogrenci", "durum": "aktif", "ilerleme": {"KURS001": 45, "KURS002": 80}},
    {"ogrenci_id": "ogr002", "id": "ogr002", "ad": "Ayşe Nur", "email": "ayse@mail.com", "sifre": "sifre123", "rol": "ogrenci", "durum": "aktif", "ilerleme": {"KURS001": 90, "KURS003": 30}},
    {"ogrenci_id": "ogr003", "id": "ogr003", "ad": "Emre Can", "email": "emre@mail.com", "sifre": "sifre123", "rol": "ogrenci", "durum": "aktif", "ilerleme": {"KURS004": 60}},
    {"ogrenci_id": "ogr004", "id": "ogr004", "ad": "Zeynep Su", "email": "zeynep@mail.com", "sifre": "sifre123", "rol": "ogrenci", "durum": "aktif", "ilerleme": {"KURS001": 20, "KURS005": 35}},
]

DEMO_EGITMENLER = [
    {"egitmen_id": "taha", "id": "taha", "ad": "Taha Hoca", "uzmanlik": "Programlama", "email": "taha@kurs.com", "sifre": "123", "rol": "egitmen", "onayli": True, "durum": "aktif"},
]

TODAY = date.today()
DEMO_KURSLAR = [
    {
        "kurs_id": "KURS001", "kurs_adi": "Python Projesi 5: Online Kurs Platformu", "egitmen_id": "taha",
        "kontenjan": 35, "aciklama": "Python, OOP ve CustomTkinter ile online kurs platformu geliştirme.",
        "kayitli_ogrenciler": ["ogr001", "ogr002", "ogr004"],
        "takvim_gunler": ["Pazartesi", "Çarşamba"], "takvim_saat": "10:00", "sinav_tarihi": str(TODAY + timedelta(days=9)),
        "dersler": [{"ders_id": "D001", "ders_adi": "OOP ve Tkinter Arayüz", "kisi_sayisi": 35, "gunler": ["Pazartesi", "Çarşamba"], "saat": "10:00"}],
        "materyaller": [{"baslik": "Ders Notu PDF", "tur": "PDF", "link": "ders_notlari.pdf"}],
        "forum": [],
        "ders_planlari": [
            {"hafta": 1, "baslik": "Sınıflar ve Nesneler", "aciklama": "Kullanıcı, Kurs ve Ders sınıfları."},
            {"hafta": 2, "baslik": "GUI Tasarımı", "aciklama": "CustomTkinter ile panel tasarımı."},
        ],
    },
    {
        "kurs_id": "KURS002", "kurs_adi": "Tarih 101", "egitmen_id": "egitmen02",
        "kontenjan": 25, "aciklama": "Temel tarih okuma ve analiz dersi.",
        "kayitli_ogrenciler": ["ogr001"],
        "takvim_gunler": ["Salı"], "takvim_saat": "13:30", "sinav_tarihi": str(TODAY + timedelta(days=15)),
        "dersler": [{"ders_id": "D001", "ders_adi": "Osmanlı Tarihi Giriş", "kisi_sayisi": 25, "gunler": ["Salı"], "saat": "13:30"}],
        "materyaller": [], "forum": [], "ders_planlari": [],
    },
    {
        "kurs_id": "KURS003", "kurs_adi": "Grafik Tasarım", "egitmen_id": "egitmen03",
        "kontenjan": 35, "aciklama": "Figma ile modern UI/UX tasarımı.",
        "kayitli_ogrenciler": ["ogr003"],
        "takvim_gunler": ["Perşembe"], "takvim_saat": "16:00", "sinav_tarihi": str(TODAY + timedelta(days=22)),
        "dersler": [{"ders_id": "D001", "ders_adi": "Renk ve Kompozisyon", "kisi_sayisi": 35, "gunler": ["Perşembe"], "saat": "16:00"}],
        "materyaller": [], "forum": [], "ders_planlari": [],
    },
    {
        "kurs_id": "KURS004", "kurs_adi": "React ile Frontend Geliştirme", "egitmen_id": "egitmen02",
        "kontenjan": 28, "aciklama": "Modern React arayüz mantığı.",
        "kayitli_ogrenciler": ["ogr004"],
        "takvim_gunler": ["Cuma"], "takvim_saat": "09:30", "sinav_tarihi": str(TODAY + timedelta(days=28)),
        "dersler": [{"ders_id": "D001", "ders_adi": "Component Yapısı", "kisi_sayisi": 28, "gunler": ["Cuma"], "saat": "09:30"}],
        "materyaller": [], "forum": [], "ders_planlari": [],
    },
]

DEMO_NOTLAR = [
    {"ogrenci_id": "ogr001", "kurs_id": "KURS001", "not": 85.0, "vize": 80, "final": 88, "odev": 90},
    {"ogrenci_id": "ogr001", "kurs_id": "KURS002", "not": 72.5, "vize": 70, "final": 75, "odev": 72},
    {"ogrenci_id": "ogr002", "kurs_id": "KURS001", "not": 91.0, "vize": 90, "final": 92, "odev": 91},
    {"ogrenci_id": "ogr003", "kurs_id": "KURS003", "not": 78.0, "vize": 76, "final": 80, "odev": 78},
    {"ogrenci_id": "ogr004", "kurs_id": "KURS001", "not": 55.0, "vize": 55, "final": 56, "odev": 54},
]


def _now():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def _today_str():
    return date.today().isoformat()


def _bos_veri():
    veri = {}
    for k, v in ANAHTARLAR.items():
        veri[k] = dict(v) if isinstance(v, dict) else list(v)
    veri["admin"] = dict(VARSAYILAN_ADMIN)
    return veri


def _sayac_id(prefix, liste, key):
    sayilar = []
    for item in liste:
        val = str(item.get(key, ""))
        if val.startswith(prefix) and val[len(prefix):].isdigit():
            sayilar.append(int(val[len(prefix):]))
    return f"{prefix}{(max(sayilar) + 1) if sayilar else 1:03d}"


def _migrate(veri):
    degisti = False
    for k, v in ANAHTARLAR.items():
        if k not in veri:
            veri[k] = dict(v) if isinstance(v, dict) else list(v)
            degisti = True
    if "admin" not in veri:
        veri["admin"] = dict(VARSAYILAN_ADMIN)
        degisti = True
    veri["admin"].setdefault("durum", "aktif")
    if not isinstance(veri.get("adminler"), list):
        veri["adminler"] = []
        degisti = True
    for a in veri.get("adminler", []):
        a.setdefault("admin_id", a.get("id", a.get("kullanici_adi", "")))
        a.setdefault("id", a.get("admin_id", a.get("kullanici_adi", "")))
        a.setdefault("kullanici_adi", a.get("admin_id", a.get("id", "")))
        a.setdefault("rol", "admin")
        a.setdefault("durum", "aktif")
        a.setdefault("ad", a.get("kullanici_adi", "Admin"))

    if not veri.get("ogrenciler"):
        veri["ogrenciler"] = [dict(o) for o in DEMO_OGRENCILER]
        degisti = True
    for o in veri.get("ogrenciler", []):
        o.setdefault("id", o.get("ogrenci_id", ""))
        o.setdefault("rol", "ogrenci")
        o.setdefault("durum", "aktif")
        o.setdefault("ilerleme", {})
        o.setdefault("avatar", "🎓")

    mevcut_eg = {e.get("egitmen_id") for e in veri.get("egitmenler", [])}
    if not veri.get("egitmenler"):
        veri["egitmenler"] = []
    for e in veri.get("egitmenler", []):
        e.setdefault("id", e.get("egitmen_id", ""))
        e.setdefault("rol", "egitmen")
        e.setdefault("onayli", True)
        e.setdefault("durum", "aktif")
        e.setdefault("avatar", "👨‍🏫")
    for e in DEMO_EGITMENLER:
        if e["egitmen_id"] not in mevcut_eg:
            veri["egitmenler"].append(dict(e))
            degisti = True

    if not veri.get("kurslar"):
        veri["kurslar"] = [json.loads(json.dumps(k, ensure_ascii=False)) for k in DEMO_KURSLAR]
        degisti = True
    gunler_varsayilan = [["Pazartesi", "Çarşamba"], ["Salı"], ["Perşembe"], ["Cuma"], ["Cumartesi"]]
    saatler = ["10:00", "13:30", "16:00", "09:30", "18:00"]
    for i, k in enumerate(veri.get("kurslar", []), start=1):
        k.setdefault("kurs_id", f"KURS{i:03d}")
        k.setdefault("kurs_adi", "Adsız Kurs")
        k.setdefault("egitmen_id", "taha")
        k.setdefault("kontenjan", 30)
        k.setdefault("aciklama", "")
        k.setdefault("kayitli_ogrenciler", [])
        k.setdefault("takvim_gunler", gunler_varsayilan[(i - 1) % len(gunler_varsayilan)])
        k.setdefault("takvim_saat", saatler[(i - 1) % len(saatler)])
        k.setdefault("sinav_tarihi", str(date.today() + timedelta(days=7 + i * 3)))
        k.setdefault("dersler", [])
        k.setdefault("materyaller", [])
        k.setdefault("forum", [])
        k.setdefault("ders_planlari", [])
        k.setdefault("durum", "aktif")
        k.setdefault("onay_durumu", "onaylandi")
        k.setdefault("kapak", "📚")
        k.setdefault("kategori", "Genel")
        k.setdefault("seviye", "Başlangıç")
        k.setdefault("iptaller", [])
        if not k["dersler"]:
            k["dersler"].append({"ders_id": "D001", "ders_adi": k["kurs_adi"], "kisi_sayisi": k.get("kontenjan", 30), "gunler": k.get("takvim_gunler", []), "saat": k.get("takvim_saat", "")})
            degisti = True

    if not veri.get("kayitlar"):
        for k in veri.get("kurslar", []):
            for oid in k.get("kayitli_ogrenciler", []):
                veri["kayitlar"].append({"ogrenci_id": oid, "kurs_id": k["kurs_id"], "tarih": _today_str()})
        degisti = True
    if not veri.get("notlar"):
        veri["notlar"] = [dict(n) for n in DEMO_NOTLAR]
        degisti = True

    # Demo ödev, sınav, duyuru, mesaj, yorumlar tek seferlik eklenir.
    if not veri.get("odevler"):
        veri["odevler"] = [
            {"odev_id": "ODV001", "kurs_id": "KURS001", "egitmen_id": "taha", "baslik": "Sınıf Diyagramı", "aciklama": "Kurs, Öğrenci ve Eğitmen sınıflarını çiziniz.", "son_tarih": str(date.today() + timedelta(days=5)), "created_at": _now()},
            {"odev_id": "ODV002", "kurs_id": "KURS003", "egitmen_id": "egitmen03", "baslik": "Renk Paleti", "aciklama": "Bir arayüz için renk paleti hazırlayınız.", "son_tarih": str(date.today() + timedelta(days=8)), "created_at": _now()},
        ]
        degisti = True
    if not veri.get("sinavlar"):
        veri["sinavlar"] = [{
            "sinav_id": "SNV001", "kurs_id": "KURS001", "egitmen_id": "taha", "baslik": "Python OOP Quiz", "tarih": str(date.today() + timedelta(days=9)),
            "sorular": [
                {"soru": "Python'da sınıf tanımlamak için hangi anahtar kelime kullanılır?", "secenekler": ["def", "class", "import", "return"], "dogru": 1},
                {"soru": "Liste veri yapısı hangi parantezle yazılır?", "secenekler": ["[]", "{}", "()", "<>"], "dogru": 0},
            ], "created_at": _now()
        }]
        degisti = True
    if not veri.get("duyurular"):
        veri["duyurular"] = [{"duyuru_id": "DUY001", "mesaj": "Yeni dönem dersleri ve sınav takvimi sisteme eklenmiştir.", "yazar": "admin", "tarih": _now()}]
        degisti = True
    if not veri.get("yorumlar"):
        veri["yorumlar"] = [
            {"yorum_id": "YRM001", "kurs_id": "KURS001", "ogrenci_id": "ogr001", "puan": 5, "yorum": "Arayüz projesi için çok faydalı.", "tarih": _now()},
            {"yorum_id": "YRM002", "kurs_id": "KURS003", "ogrenci_id": "ogr003", "puan": 4, "yorum": "Tasarım örnekleri güzel.", "tarih": _now()},
        ]
        degisti = True
    return veri, degisti


def veri_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                veri = json.load(f)
            veri, degisti = _migrate(veri)
            if degisti:
                veri_kaydet(veri)
            return veri
        except Exception:
            pass
    veri, _ = _migrate(_bos_veri())
    veri_kaydet(veri)
    return veri


def veri_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def log_ekle(islem):
    veri = veri_yukle()
    veri.setdefault("loglar", []).append(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {islem}")
    veri_kaydet(veri)


# ─────────────────────────────────────────────────────────────────────
# Kullanıcılar
# ─────────────────────────────────────────────────────────────────────

def sifre_degistir(kullanici_id, rol, eski_sifre, yeni_sifre):
    veri = veri_yukle()
    if rol == "admin" and veri["admin"].get("sifre") == eski_sifre:
        veri["admin"]["sifre"] = yeni_sifre
        veri_kaydet(veri); log_ekle("Admin şifresini değiştirdi.")
        return True, "Şifre güncellendi."
    liste = veri["ogrenciler"] if rol == "ogrenci" else veri["egitmenler"]
    key = "ogrenci_id" if rol == "ogrenci" else "egitmen_id"
    for k in liste:
        if k.get(key) == kullanici_id and k.get("sifre") == eski_sifre:
            k["sifre"] = yeni_sifre
            veri_kaydet(veri); log_ekle(f"{kullanici_id} şifresini değiştirdi.")
            return True, "Şifre güncellendi."
    return False, "Eski şifre hatalı."


def ogrenci_ekle(ogrenci_id, ad, email, sifre):
    veri = veri_yukle()
    if any(o.get("ogrenci_id") == ogrenci_id or o.get("email") == email for o in veri["ogrenciler"]):
        return False, "ID veya E-posta kullanımda."
    veri["ogrenciler"].append({"ogrenci_id": ogrenci_id, "id": ogrenci_id, "ad": ad, "email": email, "sifre": sifre, "rol": "ogrenci", "durum": "aktif", "ilerleme": {}, "avatar": "🎓"})
    veri_kaydet(veri); log_ekle(f"Yeni öğrenci kayıt oldu: {ad}")
    return True, "Kayıt başarılı."


def egitmen_ekle(egitmen_id, ad, uzmanlik, email, sifre):
    veri = veri_yukle()
    if any(e.get("egitmen_id") == egitmen_id for e in veri["egitmenler"]):
        return False, "Bu ID zaten kayıtlı."
    veri["egitmenler"].append({"egitmen_id": egitmen_id, "id": egitmen_id, "ad": ad, "uzmanlik": uzmanlik, "email": email, "sifre": sifre, "rol": "egitmen", "onayli": False, "durum": "aktif", "avatar": "👨‍🏫"})
    veri_kaydet(veri); log_ekle(f"Yeni eğitmen başvurdu: {ad}")
    mail_mesaji = ""
    if basvuru_maili_gonder:
        ok_mail, mail_msg = basvuru_maili_gonder("öğretmen", egitmen_id, ad, email, uzmanlik)
        log_ekle(f"Başvuru maili {'gönderildi' if ok_mail else 'gönderilemedi'}: {mail_msg}")
        mail_mesaji = " Mail bildirimi gönderildi." if ok_mail else f" Mail bildirimi gönderilemedi: {mail_msg}"
    return True, "Başvurunuz alındı. Admin onayından sonra giriş yapabilirsiniz." + mail_mesaji


def admin_basvuru_ekle(admin_id, ad, email, sifre, aciklama="Admin yetkisi başvurusu"):
    """Admin olmak isteyen kullanıcıyı bekleyen başvuru listesine ekler ve mail gönderir."""
    veri = veri_yukle()
    veri.setdefault("admin_basvurular", [])
    if any(a.get("admin_id") == admin_id or a.get("email") == email for a in veri["admin_basvurular"]):
        return False, "Bu admin başvurusu zaten kayıtlı."
    basvuru = {
        "admin_id": admin_id,
        "id": admin_id,
        "ad": ad,
        "email": email,
        "sifre": sifre,
        "rol": "admin_basvuru",
        "aciklama": aciklama,
        "durum": "bekliyor",
        "tarih": _now(),
    }
    veri["admin_basvurular"].append(basvuru)
    veri_kaydet(veri); log_ekle(f"Yeni admin başvurusu alındı: {ad}")
    mail_mesaji = ""
    if basvuru_maili_gonder:
        ok_mail, mail_msg = basvuru_maili_gonder("admin", admin_id, ad, email, aciklama)
        log_ekle(f"Admin başvuru maili {'gönderildi' if ok_mail else 'gönderilemedi'}: {mail_msg}")
        mail_mesaji = " Mail bildirimi gönderildi." if ok_mail else f" Mail bildirimi gönderilemedi: {mail_msg}"
    return True, "Admin başvurunuz alındı. Yetkili onayından sonra değerlendirilecektir." + mail_mesaji


def admin_basvurulari_getir():
    return veri_yukle().get("admin_basvurular", [])


def admin_basvuru_onayla(admin_id):
    """Bekleyen admin başvurusunu gerçek giriş yapılabilir admin hesabına dönüştürür."""
    veri = veri_yukle()
    veri.setdefault("admin_basvurular", [])
    veri.setdefault("adminler", [])
    for a in veri["admin_basvurular"]:
        if a.get("admin_id") == admin_id or a.get("id") == admin_id:
            a["durum"] = "onaylandi"
            yeni_admin = {
                "admin_id": a.get("admin_id", admin_id),
                "id": a.get("admin_id", admin_id),
                "kullanici_adi": a.get("admin_id", admin_id),
                "ad": a.get("ad", "Admin"),
                "email": a.get("email", ""),
                "sifre": a.get("sifre", ""),
                "rol": "admin",
                "durum": "aktif",
                "tarih": _now(),
            }
            if not any(x.get("admin_id") == yeni_admin["admin_id"] or x.get("kullanici_adi") == yeni_admin["kullanici_adi"] for x in veri["adminler"]):
                veri["adminler"].append(yeni_admin)
            veri_kaydet(veri)
            log_ekle(f"Admin başvurusu onaylandı: {admin_id}")
            bildirim_ekle(admin_id, "admin", "Admin başvurunuz onaylandı. Artık admin girişi yapabilirsiniz.")
            return True, "Admin başvurusu onaylandı. Artık admin olarak giriş yapabilir."
    return False, "Admin başvurusu bulunamadı."


def admin_basvuru_reddet(admin_id):
    veri = veri_yukle()
    for a in veri.get("admin_basvurular", []):
        if a.get("admin_id") == admin_id or a.get("id") == admin_id:
            a["durum"] = "reddedildi"
            veri_kaydet(veri)
            log_ekle(f"Admin başvurusu reddedildi: {admin_id}")
            return True, "Admin başvurusu reddedildi."
    return False, "Admin başvurusu bulunamadı."


def egitmen_onayla(egitmen_id):
    veri = veri_yukle()
    for e in veri["egitmenler"]:
        if e.get("egitmen_id") == egitmen_id:
            e["onayli"] = True
            veri_kaydet(veri); log_ekle(f"Eğitmen onaylandı: {egitmen_id}")
            bildirim_ekle(egitmen_id, "egitmen", "Hesabınız admin tarafından onaylandı.")
            return True
    return False


def kullanici_durum_degistir(kullanici_id, rol, durum):
    veri = veri_yukle()
    if rol == "admin":
        veri["admin"]["durum"] = durum
        veri_kaydet(veri)
        return True, "Admin durumu güncellendi."
    liste = veri["ogrenciler"] if rol == "ogrenci" else veri["egitmenler"]
    key = "ogrenci_id" if rol == "ogrenci" else "egitmen_id"
    for u in liste:
        if u.get(key) == kullanici_id:
            u["durum"] = durum
            veri_kaydet(veri); log_ekle(f"Kullanıcı durumu değişti: {kullanici_id} -> {durum}")
            return True, "Kullanıcı durumu güncellendi."
    return False, "Kullanıcı bulunamadı."


def kullanici_sil(kullanici_id, rol):
    veri = veri_yukle()
    if rol == "ogrenci":
        veri["ogrenciler"] = [o for o in veri["ogrenciler"] if o.get("ogrenci_id") != kullanici_id]
        veri["kayitlar"] = [k for k in veri["kayitlar"] if k.get("ogrenci_id") != kullanici_id]
        for k in veri["kurslar"]:
            if kullanici_id in k.get("kayitli_ogrenciler", []):
                k["kayitli_ogrenciler"].remove(kullanici_id)
    elif rol == "egitmen":
        veri["egitmenler"] = [e for e in veri["egitmenler"] if e.get("egitmen_id") != kullanici_id]
    veri_kaydet(veri); log_ekle(f"Kullanıcı silindi: {kullanici_id}")
    return True, "Silindi."


def kullanici_dogrula(kullanici_id, sifre, rol):
    veri = veri_yukle()
    if rol == "admin":
        admin = veri.get("admin", VARSAYILAN_ADMIN)
        if kullanici_id == admin.get("kullanici_adi") and sifre == admin.get("sifre"):
            if admin.get("durum", "aktif") != "aktif":
                return False, None
            log_ekle("Admin sisteme giriş yaptı.")
            return True, {**admin, "id": "admin", "rol": "admin"}
        # Sonradan onaylanan admin başvuruları burada kontrol edilir.
        for a in veri.get("adminler", []):
            aid = a.get("admin_id") or a.get("id") or a.get("kullanici_adi")
            if kullanici_id == aid and sifre == a.get("sifre"):
                if a.get("durum", "aktif") != "aktif":
                    return False, None
                log_ekle(f"Admin sisteme giriş yaptı: {aid}")
                return True, {**a, "id": aid, "kullanici_adi": aid, "rol": "admin"}
    else:
        liste = veri["ogrenciler"] if rol == "ogrenci" else veri["egitmenler"]
        id_key = "ogrenci_id" if rol == "ogrenci" else "egitmen_id"
        for k in liste:
            if k.get(id_key) == kullanici_id and k.get("sifre") == sifre:
                if k.get("durum", "aktif") != "aktif":
                    return False, None
                if rol == "egitmen" and not k.get("onayli", False):
                    return False, None
                log_ekle(f"{kullanici_id} giriş yaptı.")
                return True, {**k, "id": k.get(id_key), "rol": rol}
    return False, None


def tum_kullanicilar_getir():
    v = veri_yukle()
    return {
        "ogrenciler": {o["ogrenci_id"]: o for o in v["ogrenciler"]},
        "egitmenler": {e["egitmen_id"]: e for e in v["egitmenler"]},
        "admin": v.get("admin", VARSAYILAN_ADMIN),
        "adminler": {a.get("admin_id", a.get("id", "")): a for a in v.get("adminler", [])},
    }


# ─────────────────────────────────────────────────────────────────────
# Kurs, kayıt, ders planı, materyal, forum
# ─────────────────────────────────────────────────────────────────────

def tum_kurslar_getir():
    return {k["kurs_id"]: k for k in veri_yukle()["kurslar"]}


def egitmen_kurslari_getir(egitmen_id):
    return {k["kurs_id"]: k for k in veri_yukle()["kurslar"] if k.get("egitmen_id") == egitmen_id}


def _siradaki_kurs_id(veri):
    return _sayac_id("KURS", veri.get("kurslar", []), "kurs_id")


def kurs_ekle(kurs_adi, egitmen_id, kontenjan, aciklama="", gunler=None, saat="", sinav_tarihi="", kategori="Genel", seviye="Başlangıç"):
    veri = veri_yukle()
    try:
        kontenjan_int = int(kontenjan or 0)
    except Exception:
        return False, "Kontenjan sadece rakam olmalıdır."
    if kontenjan_int <= 0:
        return False, "Kontenjan 1 veya daha büyük olmalıdır."
    k_id = _siradaki_kurs_id(veri)
    veri["kurslar"].append({
        "kurs_id": k_id, "kurs_adi": kurs_adi, "egitmen_id": egitmen_id,
        "kontenjan": kontenjan_int, "aciklama": aciklama, "kategori": kategori or "Genel", "seviye": seviye or "Başlangıç",
        "kayitli_ogrenciler": [], "takvim_gunler": gunler or [], "takvim_saat": saat,
        "sinav_tarihi": sinav_tarihi, "dersler": [], "materyaller": [], "forum": [], "ders_planlari": [], "durum": "aktif",
    })
    veri_kaydet(veri); log_ekle(f"{egitmen_id} yeni kurs açtı: {kurs_adi}")
    return True, k_id


def kurs_sil(kurs_id):
    veri = veri_yukle()

    # Kurs silinmeden önce o kursun kendi içindeki materyaller de temizlenir.
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kurs_id:
            k["materyaller"] = []
            k["materyaller_kaldirildi"] = True

    veri["kurslar"] = [k for k in veri["kurslar"] if k.get("kurs_id") != kurs_id]
    for key in ["kayitlar", "notlar", "odevler", "sinavlar", "yorumlar", "yoklamalar", "teslimler", "favoriler", "hedefler"]:
        if key in veri and isinstance(veri[key], list):
            veri[key] = [x for x in veri[key] if x.get("kurs_id") != kurs_id]

    # Bazı eski sürümlerde materyaller ayrı listede tutulmuş olabilir; varsa onu da temizle.
    if isinstance(veri.get("materyaller"), list):
        veri["materyaller"] = [x for x in veri["materyaller"] if x.get("kurs_id") != kurs_id]

    veri_kaydet(veri); log_ekle(f"Kurs silindi ve materyalleri kaldırıldı: {kurs_id}")
    return True, "Silindi."


def kursa_kayit(ogrenci_id, kurs_id):
    veri = veri_yukle()
    if any(k.get("ogrenci_id") == ogrenci_id and k.get("kurs_id") == kurs_id for k in veri["kayitlar"]):
        return False, "Zaten kayıtlısınız."
    hedef = next((k for k in veri["kurslar"] if k.get("kurs_id") == kurs_id), None)
    if not hedef:
        return False, "Kurs bulunamadı."
    if len(hedef.get("kayitli_ogrenciler", [])) >= int(hedef.get("kontenjan", 0)):
        return False, "Kontenjan dolu."
    veri["kayitlar"].append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "tarih": _today_str()})
    hedef.setdefault("kayitli_ogrenciler", []).append(ogrenci_id)
    for o in veri["ogrenciler"]:
        if o.get("ogrenci_id") == ogrenci_id:
            o.setdefault("ilerleme", {})[kurs_id] = 0
    veri_kaydet(veri); log_ekle(f"{ogrenci_id}, {kurs_id} kursuna kayıt oldu.")
    bildirim_ekle(ogrenci_id, "ogrenci", f"{hedef.get('kurs_adi')} kursuna kaydınız tamamlandı.")
    return True, "Kayıt başarılı."


def kayit_iptal(ogrenci_id, kurs_id):
    veri = veri_yukle()
    veri["kayitlar"] = [k for k in veri["kayitlar"] if not (k.get("ogrenci_id") == ogrenci_id and k.get("kurs_id") == kurs_id)]
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id and ogrenci_id in k.get("kayitli_ogrenciler", []):
            k["kayitli_ogrenciler"].remove(ogrenci_id)
    veri_kaydet(veri); log_ekle(f"{ogrenci_id}, {kurs_id} kaydını iptal etti.")
    return True, "Kayıt iptal edildi."


def ogrenci_kurslarini_getir(ogrenci_id):
    return [k["kurs_id"] for k in veri_yukle()["kayitlar"] if k.get("ogrenci_id") == ogrenci_id]


def ders_ekle(kurs_id, ders_adi, kisi_sayisi, gunler, saat, sinav_tarihi=""):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            ders_id = _sayac_id("D", k.setdefault("dersler", []), "ders_id")
            k["dersler"].append({"ders_id": ders_id, "ders_adi": ders_adi, "kisi_sayisi": int(kisi_sayisi or 0), "gunler": gunler, "saat": saat})
            k["takvim_gunler"] = gunler; k["takvim_saat"] = saat
            if sinav_tarihi:
                k["sinav_tarihi"] = sinav_tarihi
            veri_kaydet(veri); log_ekle(f"{kurs_id} için ders eklendi: {ders_adi}")
            for oid in k.get("kayitli_ogrenciler", []):
                bildirim_ekle(oid, "ogrenci", f"{k.get('kurs_adi')} için yeni ders eklendi: {ders_adi}")
            return True, "Ders eklendi."
    return False, "Kurs bulunamadı."


def ders_takvim_ekle(kurs_id, gunler, saat, sinav_tarihi=None):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            k["takvim_gunler"] = gunler; k["takvim_saat"] = saat
            if sinav_tarihi:
                k["sinav_tarihi"] = sinav_tarihi
            veri_kaydet(veri)
            return True
    return False


def materyal_ekle(kurs_id, baslik, tur, link):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            k.setdefault("materyaller", []).append({"baslik": baslik, "tur": tur, "link": link, "tarih": _now()})
            veri_kaydet(veri); log_ekle(f"{kurs_id} materyal eklendi: {baslik}")
            for oid in k.get("kayitli_ogrenciler", []):
                bildirim_ekle(oid, "ogrenci", f"{k.get('kurs_adi')} için yeni materyal: {baslik}")
            return True, "Materyal eklendi."
    return False, "Kurs bulunamadı."


def materyalleri_getir(kurs_id):
    for k in veri_yukle()["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            return k.get("materyaller", [])
    return []


def ders_plani_ekle(kurs_id, hafta, baslik, aciklama):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            k.setdefault("ders_planlari", []).append({"hafta": int(hafta or 0), "baslik": baslik, "aciklama": aciklama})
            veri_kaydet(veri); log_ekle(f"{kurs_id} ders planı eklendi: {baslik}")
            return True, "Ders planı eklendi."
    return False, "Kurs bulunamadı."


def ders_planlari_getir(kurs_id):
    for k in veri_yukle()["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            return sorted(k.get("ders_planlari", []), key=lambda x: int(x.get("hafta", 0)))
    return []


def forum_mesaji_ekle(kurs_id, yazar, mesaj):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            k.setdefault("forum", []).append({"yazar": yazar, "mesaj": mesaj, "tarih": _now()})
            veri_kaydet(veri)
            return True
    return False


def forum_mesajlari_getir(kurs_id):
    for k in veri_yukle()["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            return k.get("forum", [])
    return []


# ─────────────────────────────────────────────────────────────────────
# Not, ilerleme, belge, rozet
# ─────────────────────────────────────────────────────────────────────

def harf_notu(puan):
    p = float(puan or 0)
    if p >= 90: return "AA"
    if p >= 85: return "BA"
    if p >= 80: return "BB"
    if p >= 70: return "CB"
    if p >= 60: return "CC"
    if p >= 50: return "DC"
    return "FF"


def not_gir(ogrenci_id, kurs_id, not_degeri=None, vize=None, final=None, odev=None):
    veri = veri_yukle()
    if not_degeri is None:
        vize = float(vize or 0); final = float(final or 0); odev = float(odev or 0)
        not_degeri = round(vize * 0.3 + final * 0.5 + odev * 0.2, 2)
    not_degeri = float(not_degeri)
    for n in veri["notlar"]:
        if n.get("ogrenci_id") == ogrenci_id and n.get("kurs_id") == kurs_id:
            n.update({"not": not_degeri, "vize": vize if vize is not None else n.get("vize"), "final": final if final is not None else n.get("final"), "odev": odev if odev is not None else n.get("odev"), "harf": harf_notu(not_degeri)})
            veri_kaydet(veri); bildirim_ekle(ogrenci_id, "ogrenci", f"{kurs_id} notunuz güncellendi: {not_degeri}")
            return True, "Not güncellendi."
    veri["notlar"].append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "not": not_degeri, "vize": vize, "final": final, "odev": odev, "harf": harf_notu(not_degeri)})
    veri_kaydet(veri); bildirim_ekle(ogrenci_id, "ogrenci", f"{kurs_id} notunuz açıklandı: {not_degeri}")
    return True, "Not işlendi."


def ogrenci_notlarini_getir(ogrenci_id):
    return {n["kurs_id"]: n for n in veri_yukle()["notlar"] if n.get("ogrenci_id") == ogrenci_id}


def kurs_notlarini_getir(kurs_id):
    return {n["ogrenci_id"]: n for n in veri_yukle()["notlar"] if n.get("kurs_id") == kurs_id}


def ilerleme_getir(ogrenci_id, kurs_id=None):
    for o in veri_yukle()["ogrenciler"]:
        if o.get("ogrenci_id") == ogrenci_id:
            il = o.get("ilerleme", {})
            return il.get(kurs_id, 0) if kurs_id else il
    return 0 if kurs_id else {}


def ilerleme_guncelle(ogrenci_id, kurs_id, yuzde):
    veri = veri_yukle()
    yuzde = max(0, min(100, int(yuzde or 0)))
    for o in veri["ogrenciler"]:
        if o.get("ogrenci_id") == ogrenci_id:
            o.setdefault("ilerleme", {})[kurs_id] = yuzde
            veri_kaydet(veri)
            if yuzde >= 100:
                bildirim_ekle(ogrenci_id, "ogrenci", f"{kurs_id} kursunu tamamladınız. Tebrikler!")
            return True, "İlerleme güncellendi."
    return False, "Öğrenci bulunamadı."


def belgeleri_getir(ogrenci_id):
    veri = veri_yukle(); kurslar = {k["kurs_id"]: k for k in veri["kurslar"]}
    belgeler = []
    for n in veri["notlar"]:
        if n.get("ogrenci_id") == ogrenci_id and float(n.get("not", 0)) >= 60:
            kurs = kurslar.get(n.get("kurs_id"), {})
            tur = "Üstün Başarı Sertifikası" if float(n.get("not", 0)) >= 85 else "Başarı Sertifikası"
            belgeler.append({"kurs_id": n.get("kurs_id"), "kurs_adi": kurs.get("kurs_adi", n.get("kurs_id")), "not": n.get("not"), "harf": harf_notu(n.get("not")), "tur": tur, "belge_no": f"BLG-{ogrenci_id}-{n.get('kurs_id')}", "tarih": _today_str()})
    return belgeler


def rozetleri_getir(ogrenci_id):
    kurslar = ogrenci_kurslarini_getir(ogrenci_id)
    notlar = ogrenci_notlarini_getir(ogrenci_id)
    ilerleme = ilerleme_getir(ogrenci_id)
    rozetler = []
    if kurslar: rozetler.append({"ad": "İlk Kurs Rozeti", "ikon": "🎒", "aciklama": "İlk kurs kaydı tamamlandı."})
    if len(kurslar) >= 3: rozetler.append({"ad": "Çok Yönlü Öğrenci", "ikon": "🌟", "aciklama": "3 veya daha fazla kursa kayıtlı."})
    if any(float(n.get("not", 0)) >= 90 for n in notlar.values()): rozetler.append({"ad": "90+ Başarı Rozeti", "ikon": "🏆", "aciklama": "Bir kursta 90 ve üzeri not."})
    if any(int(v) >= 100 for v in ilerleme.values()): rozetler.append({"ad": "Kurs Bitirme Rozeti", "ikon": "✅", "aciklama": "Bir kursu %100 tamamladı."})
    if devamsizlik_sayisi(ogrenci_id) == 0 and kurslar: rozetler.append({"ad": "Devamsızlık Yapmayan", "ikon": "🟢", "aciklama": "Kayıtlı derslerde devamsızlık yok."})
    return rozetler


def liderlik_tablosu():
    v = veri_yukle(); isim = {o["ogrenci_id"]: o.get("ad", o["ogrenci_id"]) for o in v["ogrenciler"]}
    grup = {}
    for n in v["notlar"]:
        grup.setdefault(n.get("ogrenci_id"), []).append(float(n.get("not", 0)))
    return sorted([{"ogrenci_id": oid, "ad": isim.get(oid, oid), "ort": round(mean(vals), 2)} for oid, vals in grup.items() if vals], key=lambda x: x["ort"], reverse=True)[:10]


# ─────────────────────────────────────────────────────────────────────
# Ödev / Quiz / Yoklama
# ─────────────────────────────────────────────────────────────────────

def odev_ekle(kurs_id, egitmen_id, baslik, aciklama, son_tarih):
    veri = veri_yukle(); oid = _sayac_id("ODV", veri["odevler"], "odev_id")
    veri["odevler"].append({"odev_id": oid, "kurs_id": kurs_id, "egitmen_id": egitmen_id, "baslik": baslik, "aciklama": aciklama, "son_tarih": son_tarih, "created_at": _now()})
    veri_kaydet(veri); log_ekle(f"Ödev eklendi: {baslik}")
    kurs = tum_kurslar_getir().get(kurs_id, {})
    for ogr in kurs.get("kayitli_ogrenciler", []):
        bildirim_ekle(ogr, "ogrenci", f"Yeni ödev: {baslik} ({son_tarih})")
    return True, "Ödev eklendi."


def odevleri_getir(kurs_id=None, egitmen_id=None, ogrenci_id=None):
    v = veri_yukle(); odevler = v["odevler"]
    if kurs_id: odevler = [o for o in odevler if o.get("kurs_id") == kurs_id]
    if egitmen_id: odevler = [o for o in odevler if o.get("egitmen_id") == egitmen_id]
    if ogrenci_id:
        kurslar = set(ogrenci_kurslarini_getir(ogrenci_id))
        odevler = [o for o in odevler if o.get("kurs_id") in kurslar]
    return odevler


def odev_teslim_et(odev_id, ogrenci_id, cevap):
    veri = veri_yukle()
    mevcut = next((t for t in veri["teslimler"] if t.get("odev_id") == odev_id and t.get("ogrenci_id") == ogrenci_id), None)
    odev = next((o for o in veri["odevler"] if o.get("odev_id") == odev_id), {})
    gec = False
    try: gec = date.today() > date.fromisoformat(odev.get("son_tarih", _today_str()))
    except Exception: pass
    data = {"odev_id": odev_id, "ogrenci_id": ogrenci_id, "cevap": cevap, "tarih": _now(), "durum": "Geç teslim" if gec else "Teslim edildi"}
    if mevcut: mevcut.update(data)
    else: veri["teslimler"].append(data)
    veri_kaydet(veri); log_ekle(f"Ödev teslim edildi: {odev_id} / {ogrenci_id}")
    return True, data["durum"]


def teslimleri_getir(odev_id=None, ogrenci_id=None):
    t = veri_yukle()["teslimler"]
    if odev_id: t = [x for x in t if x.get("odev_id") == odev_id]
    if ogrenci_id: t = [x for x in t if x.get("ogrenci_id") == ogrenci_id]
    return t


def sinav_ekle(kurs_id, egitmen_id, baslik, tarih, sorular):
    veri = veri_yukle(); sid = _sayac_id("SNV", veri["sinavlar"], "sinav_id")
    veri["sinavlar"].append({"sinav_id": sid, "kurs_id": kurs_id, "egitmen_id": egitmen_id, "baslik": baslik, "tarih": tarih, "sorular": sorular, "created_at": _now()})
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id:
            k["sinav_tarihi"] = tarih
            for ogr in k.get("kayitli_ogrenciler", []): bildirim_ekle(ogr, "ogrenci", f"Yeni sınav: {baslik} ({tarih})")
    veri_kaydet(veri); log_ekle(f"Sınav eklendi: {baslik}")
    return True, "Sınav eklendi."


def test_ekle(kurs_id, soru, secenekler, dogru_indeks):
    # Eski kod uyumluluğu: kursa tek soruluk küçük quiz ekler.
    return sinav_ekle(kurs_id, "sistem", "Mini Quiz", _today_str(), [{"soru": soru, "secenekler": secenekler, "dogru": int(dogru_indeks)}])


def sinavlari_getir(kurs_id=None, egitmen_id=None, ogrenci_id=None):
    s = veri_yukle()["sinavlar"]
    if kurs_id: s = [x for x in s if x.get("kurs_id") == kurs_id]
    if egitmen_id: s = [x for x in s if x.get("egitmen_id") == egitmen_id]
    if ogrenci_id:
        kurslar = set(ogrenci_kurslarini_getir(ogrenci_id)); s = [x for x in s if x.get("kurs_id") in kurslar]
    return s


def testleri_getir(kurs_id):
    sorular = []
    for s in sinavlari_getir(kurs_id=kurs_id):
        sorular.extend(s.get("sorular", []))
    return sorular


def sinav_coz(sinav_id, ogrenci_id, cevaplar):
    veri = veri_yukle(); sinav = next((s for s in veri["sinavlar"] if s.get("sinav_id") == sinav_id), None)
    if not sinav: return False, "Sınav bulunamadı."
    sorular = sinav.get("sorular", [])
    dogru = 0
    for i, soru in enumerate(sorular):
        try:
            if int(cevaplar[i]) == int(soru.get("dogru")): dogru += 1
        except Exception: pass
    puan = round((dogru / len(sorular)) * 100, 2) if sorular else 0
    mevcut = next((r for r in veri["sinav_sonuclari"] if r.get("sinav_id") == sinav_id and r.get("ogrenci_id") == ogrenci_id), None)
    data = {"sinav_id": sinav_id, "ogrenci_id": ogrenci_id, "puan": puan, "dogru": dogru, "toplam": len(sorular), "tarih": _now()}
    if mevcut: mevcut.update(data)
    else: veri["sinav_sonuclari"].append(data)
    veri_kaydet(veri); bildirim_ekle(ogrenci_id, "ogrenci", f"{sinav.get('baslik')} sonucunuz: {puan}")
    return True, f"Sınav tamamlandı. Puan: {puan}"


def sinav_sonuclari_getir(sinav_id=None, ogrenci_id=None):
    r = veri_yukle()["sinav_sonuclari"]
    if sinav_id: r = [x for x in r if x.get("sinav_id") == sinav_id]
    if ogrenci_id: r = [x for x in r if x.get("ogrenci_id") == ogrenci_id]
    return r


def yoklama_kaydet(kurs_id, tarih, durumlar):
    # durumlar: {ogrenci_id: "Geldi"/"Gelmedi"}
    veri = veri_yukle()
    veri["yoklamalar"] = [y for y in veri["yoklamalar"] if not (y.get("kurs_id") == kurs_id and y.get("tarih") == tarih)]
    veri["yoklamalar"].append({"yoklama_id": _sayac_id("YOK", veri["yoklamalar"], "yoklama_id"), "kurs_id": kurs_id, "tarih": tarih, "durumlar": durumlar, "created_at": _now()})
    veri_kaydet(veri); log_ekle(f"Yoklama kaydedildi: {kurs_id} / {tarih}")
    return True, "Yoklama kaydedildi."


def yoklamalari_getir(kurs_id=None, ogrenci_id=None):
    y = veri_yukle()["yoklamalar"]
    if kurs_id: y = [x for x in y if x.get("kurs_id") == kurs_id]
    if ogrenci_id: y = [x for x in y if ogrenci_id in x.get("durumlar", {})]
    return y


def devamsizlik_sayisi(ogrenci_id):
    return sum(1 for y in yoklamalari_getir(ogrenci_id=ogrenci_id) if y.get("durumlar", {}).get(ogrenci_id) == "Gelmedi")


# ─────────────────────────────────────────────────────────────────────
# Duyuru, bildirim, mesaj, yorum, favori, hedef
# ─────────────────────────────────────────────────────────────────────

def duyuru_ekle(mesaj, yazar="admin"):
    veri = veri_yukle(); did = _sayac_id("DUY", veri["duyurular"], "duyuru_id")
    veri["duyurular"].insert(0, {"duyuru_id": did, "mesaj": mesaj, "yazar": yazar, "tarih": _now()})
    veri_kaydet(veri); log_ekle("Yeni duyuru yayınlandı.")
    return True, "Duyuru yayınlandı."


def duyurulari_getir():
    d = veri_yukle().get("duyurular", [])
    # Eski string duyurular için uyumluluk
    return [{"mesaj": x, "tarih": ""} if isinstance(x, str) else x for x in d]


def bildirim_ekle(kullanici_id, rol, mesaj):
    veri = veri_yukle(); bid = _sayac_id("BIL", veri["bildirimler"], "bildirim_id")
    veri["bildirimler"].insert(0, {"bildirim_id": bid, "kullanici_id": kullanici_id, "rol": rol, "mesaj": mesaj, "okundu": False, "tarih": _now()})
    veri_kaydet(veri); return True


def toplu_bildirim(mesaj, rol="all"):
    veri = veri_yukle()
    if rol in ("all", "ogrenci"):
        for o in veri["ogrenciler"]: bildirim_ekle(o["ogrenci_id"], "ogrenci", mesaj)
    if rol in ("all", "egitmen"):
        for e in veri["egitmenler"]: bildirim_ekle(e["egitmen_id"], "egitmen", mesaj)
    return True, "Bildirim gönderildi."


def bildirimleri_getir(kullanici_id, rol):
    return [b for b in veri_yukle()["bildirimler"] if (b.get("kullanici_id") == kullanici_id and b.get("rol") == rol) or b.get("rol") == "all"]


def mesaj_gonder(gonderen_id, alici_id, konu, mesaj):
    veri = veri_yukle(); mid = _sayac_id("MSG", veri["mesajlar"], "mesaj_id")
    veri["mesajlar"].insert(0, {"mesaj_id": mid, "gonderen_id": gonderen_id, "alici_id": alici_id, "konu": konu, "mesaj": mesaj, "tarih": _now()})
    veri_kaydet(veri); bildirim_ekle(alici_id, "ogrenci", f"Yeni mesaj: {konu}"); bildirim_ekle(alici_id, "egitmen", f"Yeni mesaj: {konu}")
    return True, "Mesaj gönderildi."


def mesajlari_getir(kullanici_id):
    return [m for m in veri_yukle()["mesajlar"] if m.get("gonderen_id") == kullanici_id or m.get("alici_id") == kullanici_id]


def yorum_ekle(kurs_id, ogrenci_id, puan, yorum):
    veri = veri_yukle()
    mevcut = next((y for y in veri["yorumlar"] if y.get("kurs_id") == kurs_id and y.get("ogrenci_id") == ogrenci_id), None)
    data = {"yorum_id": _sayac_id("YRM", veri["yorumlar"], "yorum_id"), "kurs_id": kurs_id, "ogrenci_id": ogrenci_id, "puan": int(puan), "yorum": yorum, "tarih": _now()}
    if mevcut: mevcut.update(data)
    else: veri["yorumlar"].append(data)
    veri_kaydet(veri); return True, "Yorum kaydedildi."


def yorumlari_getir(kurs_id=None):
    y = veri_yukle()["yorumlar"]
    if kurs_id: y = [x for x in y if x.get("kurs_id") == kurs_id]
    return y


def kurs_puani(kurs_id):
    y = yorumlari_getir(kurs_id)
    return round(mean([int(x.get("puan", 0)) for x in y]), 2) if y else 0


def favori_degistir(ogrenci_id, kurs_id):
    veri = veri_yukle(); found = next((f for f in veri["favoriler"] if f.get("ogrenci_id") == ogrenci_id and f.get("kurs_id") == kurs_id), None)
    if found:
        veri["favoriler"].remove(found); msg = "Favorilerden çıkarıldı."
    else:
        veri["favoriler"].append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "tarih": _now()}); msg = "Favorilere eklendi."
    veri_kaydet(veri); return True, msg


def favorileri_getir(ogrenci_id):
    return [f["kurs_id"] for f in veri_yukle()["favoriler"] if f.get("ogrenci_id") == ogrenci_id]


def hedef_ekle(ogrenci_id, baslik, hedef_deger):
    veri = veri_yukle(); hid = _sayac_id("HEF", veri["hedefler"], "hedef_id")
    veri["hedefler"].append({"hedef_id": hid, "ogrenci_id": ogrenci_id, "baslik": baslik, "hedef_deger": int(hedef_deger or 0), "tamamlanan": 0, "durum": "Devam", "tarih": _now()})
    veri_kaydet(veri); return True, "Hedef eklendi."


def hedefleri_getir(ogrenci_id):
    return [h for h in veri_yukle()["hedefler"] if h.get("ogrenci_id") == ogrenci_id]


def hedef_guncelle(hedef_id, tamamlanan):
    veri = veri_yukle()
    for h in veri["hedefler"]:
        if h.get("hedef_id") == hedef_id:
            h["tamamlanan"] = int(tamamlanan or 0)
            h["durum"] = "Tamamlandı" if h["tamamlanan"] >= int(h.get("hedef_deger", 0)) else "Devam"
            veri_kaydet(veri); return True, "Hedef güncellendi."
    return False, "Hedef bulunamadı."


# ─────────────────────────────────────────────────────────────────────
# Takvim / İstatistik / Yedek / Export / Arama
# ─────────────────────────────────────────────────────────────────────

def takvim_etkinlikleri_getir():
    veri = veri_yukle(); egs = {e["egitmen_id"]: e.get("ad", e["egitmen_id"]) for e in veri["egitmenler"]}
    etkinlikler = []
    for k in veri["kurslar"]:
        if k.get("takvim_gunler"):
            etkinlikler.append({"tur": "ders", "ad": k.get("kurs_adi"), "egitmen": egs.get(k.get("egitmen_id"), ""), "gunler": k.get("takvim_gunler", []), "saat": k.get("takvim_saat", ""), "kurs_id": k.get("kurs_id")})
        if k.get("sinav_tarihi"):
            etkinlikler.append({"tur": "sinav", "ad": k.get("kurs_adi"), "egitmen": egs.get(k.get("egitmen_id"), ""), "tarih": k.get("sinav_tarihi"), "kurs_id": k.get("kurs_id")})
    for o in veri["odevler"]:
        etkinlikler.append({"tur": "odev", "ad": o.get("baslik"), "tarih": o.get("son_tarih"), "kurs_id": o.get("kurs_id")})
    for s in veri["sinavlar"]:
        etkinlikler.append({"tur": "sinav", "ad": s.get("baslik"), "tarih": s.get("tarih"), "kurs_id": s.get("kurs_id")})
    return etkinlikler


def yaklasan_etkinlikler(limit=8):
    evs = []
    for e in takvim_etkinlikleri_getir():
        tarih = e.get("tarih")
        if tarih:
            try:
                d = date.fromisoformat(tarih)
                evs.append((d, e))
            except Exception: pass
    evs.sort(key=lambda x: x[0])
    return [e for _, e in evs if _ >= date.today()][:limit]


def istatistikleri_getir():
    v = veri_yukle(); notlar = [float(n.get("not", 0)) for n in v["notlar"]]
    doluluklar = []
    for k in v["kurslar"]:
        cap = max(1, int(k.get("kontenjan", 1) or 1)); doluluklar.append(len(k.get("kayitli_ogrenciler", [])) / cap * 100)
    return {
        "toplam_ogrenci": len(v["ogrenciler"]),
        "toplam_egitmen": len(v["egitmenler"]),
        "toplam_kurs": len(v["kurslar"]),
        "toplam_kayit": len(v["kayitlar"]),
        "toplam_odev": len(v["odevler"]),
        "toplam_sinav": len(v["sinavlar"]),
        "ortalama_not": round(mean(notlar), 2) if notlar else 0.0,
        "ortalama_doluluk": round(mean(doluluklar), 2) if doluluklar else 0.0,
        "en_kalabalik_kurs": max(v["kurslar"], key=lambda k: len(k.get("kayitli_ogrenciler", [])), default={}).get("kurs_adi", "-"),
    }


def sistem_raporu():
    s = istatistikleri_getir(); lider = liderlik_tablosu(); kurslar = tum_kurslar_getir()
    satir = ["ONLINE KURS PLATFORMU RAPORU", f"Tarih: {_now()}", ""]
    for k, v in s.items(): satir.append(f"{k}: {v}")
    satir.append("\nKurslar:")
    for kid, k in kurslar.items(): satir.append(f"- {kid} | {k.get('kurs_adi')} | {len(k.get('kayitli_ogrenciler', []))}/{k.get('kontenjan')}")
    satir.append("\nLiderlik:")
    for i, x in enumerate(lider, 1): satir.append(f"{i}. {x['ad']} - {x['ort']}")
    return "\n".join(satir)


def export_rapor(format="txt"):
    veri = veri_yukle(); zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    if format == "json":
        path = f"rapor_{zaman}.json"
        with open(path, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=2)
    elif format == "csv":
        path = f"kurs_raporu_{zaman}.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["kurs_id", "kurs_adi", "egitmen_id", "kayitli", "kontenjan"])
            for k in veri["kurslar"]: w.writerow([k.get("kurs_id"), k.get("kurs_adi"), k.get("egitmen_id"), len(k.get("kayitli_ogrenciler", [])), k.get("kontenjan")])
    else:
        path = f"sistem_raporu_{zaman}.txt"
        with open(path, "w", encoding="utf-8") as f: f.write(sistem_raporu())
    veri.setdefault("exportlar", []).append({"dosya": path, "format": format, "tarih": _now()})
    veri_kaydet(veri); log_ekle(f"Rapor dışa aktarıldı: {path}")
    return True, path


def veritabani_yedekle():
    if not os.path.exists(DOSYA_ADI):
        return False, "Yedeklenecek veri bulunamadı."
    path = os.path.join(BASE_DIR, f"yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{DOSYA_KISA_ADI}")
    shutil.copy(DOSYA_ADI, path); log_ekle("Admin veritabanını yedekledi.")
    return True, f"Yedek başarıyla alındı:\n{path}"


def loglari_getir():
    return veri_yukle().get("loglar", [])


def kurs_ara(metin="", egitmen_id=None, sirala="Ad", kategori=None, seviye=None):
    metin = (metin or "").lower().strip(); kurslar = list(tum_kurslar_getir().values())
    if metin:
        kurslar = [k for k in kurslar if metin in k.get("kurs_adi", "").lower() or metin in k.get("aciklama", "").lower()]
    if egitmen_id:
        kurslar = [k for k in kurslar if k.get("egitmen_id") == egitmen_id]
    if kategori and kategori != "Tümü":
        kurslar = [k for k in kurslar if k.get("kategori", "Genel") == kategori]
    if seviye and seviye != "Tümü":
        kurslar = [k for k in kurslar if k.get("seviye", "Başlangıç") == seviye]
    if sirala == "Kontenjan":
        kurslar.sort(key=lambda k: int(k.get("kontenjan", 0)), reverse=True)
    elif sirala == "Puan":
        kurslar.sort(key=lambda k: kurs_puani(k.get("kurs_id")), reverse=True)
    else:
        kurslar.sort(key=lambda k: k.get("kurs_adi", ""))
    return kurslar


# ─────────────────────────────────────────────────────────────────────
# Yeni ek modüller: beni hatırla, şifre sıfırlama, PDF sertifika,
# ders iptal, yapılacaklar, canlı durum ve yardım asistanı kayıtları
# ─────────────────────────────────────────────────────────────────────

def beni_hatirla_kaydet(kullanici_id, rol, aktif=True):
    veri = veri_yukle()
    veri.setdefault("sistem_ayarlari", {})["beni_hatirla"] = {"kullanici_id": kullanici_id, "rol": rol, "tarih": _now()} if aktif else None
    veri_kaydet(veri)
    return True, "Beni hatırla ayarı güncellendi."


def beni_hatirla_getir():
    return veri_yukle().get("sistem_ayarlari", {}).get("beni_hatirla")


def sifre_sifirla(kullanici_id, rol, yeni_sifre="1234"):
    veri = veri_yukle()
    if rol == "admin":
        if kullanici_id in ("admin", veri.get("admin", {}).get("kullanici_adi")):
            veri["admin"]["sifre"] = yeni_sifre
            veri_kaydet(veri); log_ekle("Admin şifresi sıfırlandı.")
            return True, f"Şifre sıfırlandı. Yeni şifre: {yeni_sifre}"
        return False, "Admin bulunamadı."
    liste = veri["ogrenciler"] if rol == "ogrenci" else veri["egitmenler"]
    key = "ogrenci_id" if rol == "ogrenci" else "egitmen_id"
    for k in liste:
        if k.get(key) == kullanici_id or k.get("id") == kullanici_id:
            k["sifre"] = yeni_sifre
            veri_kaydet(veri); log_ekle(f"Şifre sıfırlandı: {rol}/{kullanici_id}")
            return True, f"Şifre sıfırlandı. Yeni şifre: {yeni_sifre}"
    return False, "Kullanıcı bulunamadı."


def _pdf_escape(text):
    cevir = str.maketrans("ğĞüÜşŞıİöÖçÇ", "gGuUsSiIoOcC")
    return str(text).translate(cevir).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def sertifika_pdf_olustur(ogrenci_id, kurs_id):
    belgeler = [b for b in belgeleri_getir(ogrenci_id) if b.get("kurs_id") == kurs_id]
    if not belgeler:
        return False, "Bu kurs için sertifika bulunamadı."
    b = belgeler[0]
    ogr = tum_kullanicilar_getir()["ogrenciler"].get(ogrenci_id, {})
    dosya = f"sertifika_{ogrenci_id}_{kurs_id}.pdf"
    satirlar = [
        "ONLINE KURS PLATFORMU",
        b.get("tur", "Sertifika"),
        f"Ogrenci: {ogr.get('ad', ogrenci_id)}",
        f"Kurs: {b.get('kurs_adi', kurs_id)}",
        f"Not: {b.get('not')} / Harf: {b.get('harf')}",
        f"Belge No: {b.get('belge_no')}",
        f"Tarih: {b.get('tarih')}",
        "Bu belge sistem tarafindan otomatik olusturulmustur.",
    ]
    # Harici kütüphane gerekmeden çalışan basit PDF üretimi.
    text_cmds = ["BT", "/F1 24 Tf", "70 760 Td", f"({_pdf_escape(satirlar[0])}) Tj"]
    y_sizes = [18, 14, 14, 14, 14, 12, 12]
    for i, line in enumerate(satirlar[1:], start=1):
        text_cmds.append(f"0 -{52 if i == 1 else 34} Td")
        text_cmds.append(f"/F1 {y_sizes[min(i-1, len(y_sizes)-1)]} Tf")
        text_cmds.append(f"({_pdf_escape(line)}) Tj")
    text_cmds.append("ET")
    stream = "\n".join(text_cmds).encode("latin-1", "ignore")
    objs = []
    objs.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objs.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objs.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
    objs.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj\n")
    objs.append(b"5 0 obj << /Length " + str(len(stream)).encode() + b" >> stream\n" + stream + b"\nendstream endobj\n")
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objs:
        offsets.append(len(pdf)); pdf.extend(obj)
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
    for off in offsets[1:]: pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    with open(dosya, "wb") as f: f.write(pdf)
    log_ekle(f"Sertifika PDF oluşturuldu: {dosya}")
    return True, dosya


def ders_iptal_et(kurs_id, egitmen_id, tarih, neden=""):
    veri = veri_yukle()
    for k in veri["kurslar"]:
        if k.get("kurs_id") == kurs_id and k.get("egitmen_id") == egitmen_id:
            kayit = {"tarih": tarih or _today_str(), "neden": neden or "Belirtilmedi", "created_at": _now()}
            k.setdefault("iptaller", []).append(kayit)
            veri.setdefault("takvim_iptaller", []).append({"kurs_id": kurs_id, "egitmen_id": egitmen_id, **kayit})
            veri_kaydet(veri)
            for oid in k.get("kayitli_ogrenciler", []):
                bildirim_ekle(oid, "ogrenci", f"{k.get('kurs_adi')} dersi {kayit['tarih']} tarihinde iptal edildi. Neden: {kayit['neden']}")
            log_ekle(f"Ders iptal edildi: {kurs_id} / {kayit['tarih']}")
            return True, "Ders iptali kaydedildi ve öğrencilere bildirildi."
    return False, "Kurs bulunamadı veya yetkiniz yok."


def yapilacak_ekle(ogrenci_id, baslik, son_tarih=""):
    veri = veri_yukle(); tid = _sayac_id("TODO", veri.setdefault("yapilacaklar", []), "todo_id")
    veri["yapilacaklar"].append({"todo_id": tid, "ogrenci_id": ogrenci_id, "baslik": baslik, "son_tarih": son_tarih, "durum": "Bekliyor", "created_at": _now()})
    veri_kaydet(veri); return True, "Yapılacak eklendi."


def yapilacaklari_getir(ogrenci_id):
    return [x for x in veri_yukle().get("yapilacaklar", []) if x.get("ogrenci_id") == ogrenci_id]


def yapilacak_tamamla(todo_id, ogrenci_id):
    veri = veri_yukle()
    for x in veri.get("yapilacaklar", []):
        if x.get("todo_id") == todo_id and x.get("ogrenci_id") == ogrenci_id:
            x["durum"] = "Tamamlandı" if x.get("durum") != "Tamamlandı" else "Bekliyor"
            veri_kaydet(veri); return True, "Durum güncellendi."
    return False, "Kayıt bulunamadı."


def canli_sistem_durumu_getir():
    veri = veri_yukle(); bugun1 = datetime.now().strftime("%d-%m-%Y"); bugun2 = _today_str()
    return {
        "bugunku_log": len([l for l in veri.get("loglar", []) if bugun1 in l]),
        "bugunku_kayit": len([k for k in veri.get("kayitlar", []) if k.get("tarih") == bugun2]),
        "bugunku_odev_teslim": len([t for t in veri.get("teslimler", []) if bugun1.replace('-', '.') in t.get("tarih", "") or bugun2 in t.get("tarih", "")]),
        "bekleyen_egitmen": len([e for e in veri.get("egitmenler", []) if not e.get("onayli")]),
        "pasif_kullanici": len([u for u in veri.get("ogrenciler", []) + veri.get("egitmenler", []) if u.get("durum") == "pasif"]),
    }


def yardim_sorusu_kaydet(kullanici_id, soru, cevap):
    veri = veri_yukle(); veri.setdefault("yardim_kayitlari", []).append({"kullanici_id": kullanici_id, "soru": soru, "cevap": cevap, "tarih": _now()})
    veri_kaydet(veri)
    return True


def ayar_guncelle(anahtar, deger):
    veri = veri_yukle(); veri.setdefault("sistem_ayarlari", {})[anahtar] = deger; veri_kaydet(veri)
    return True, "Ayar güncellendi."



# ══════════════════════════════════════════════════════════════════════
# MEGA FİNAL EK ÖZELLİKLERİ
# Akıllı rehber, destek sistemi, çöp kutusu, proje dokümantasyonu,
# çakışma kontrolleri, haftalık takvim, gün detayları ve PDF raporları.
# ══════════════════════════════════════════════════════════════════════

def kullanici_hareket_ekle(kullanici_id, rol, islem):
    veri = veri_yukle()
    veri.setdefault("kullanici_hareketleri", []).append({
        "hareket_id": _sayac_id("HRK", veri.get("kullanici_hareketleri", []), "hareket_id"),
        "kullanici_id": kullanici_id, "rol": rol, "islem": islem, "tarih": _now()
    })
    veri_kaydet(veri)
    return True


def kullanici_hareketleri_getir(kullanici_id=None, limit=50):
    veri = veri_yukle()
    rows = veri.get("kullanici_hareketleri", [])
    if kullanici_id:
        rows = [r for r in rows if r.get("kullanici_id") == kullanici_id]
    return rows[-limit:][::-1]


def destek_talebi_ekle(kullanici_id, rol, konu, mesaj):
    if not konu or not mesaj:
        return False, "Konu ve mesaj boş olamaz."
    veri = veri_yukle()
    tid = _sayac_id("DST", veri.get("destek_talepleri", []), "talep_id")
    veri.setdefault("destek_talepleri", []).append({
        "talep_id": tid, "kullanici_id": kullanici_id, "rol": rol,
        "konu": konu, "mesaj": mesaj, "durum": "açık", "cevap": "", "tarih": _now()
    })
    veri_kaydet(veri); log_ekle(f"Destek talebi oluşturuldu: {tid}")
    return True, f"Destek talebi oluşturuldu: {tid}"


def destek_talepleri_getir(kullanici_id=None):
    rows = veri_yukle().get("destek_talepleri", [])
    if kullanici_id:
        rows = [r for r in rows if r.get("kullanici_id") == kullanici_id]
    return rows[::-1]


def destek_talebi_cevapla(talep_id, cevap):
    veri = veri_yukle()
    for t in veri.get("destek_talepleri", []):
        if t.get("talep_id") == talep_id:
            t["cevap"] = cevap; t["durum"] = "cevaplandı"; t["cevap_tarihi"] = _now()
            veri_kaydet(veri); log_ekle(f"Destek talebi cevaplandı: {talep_id}")
            return True, "Destek talebi cevaplandı."
    return False, "Talep bulunamadı."


def cop_kutusuna_ekle(tur, veri_objesi, silen="admin"):
    veri = veri_yukle()
    veri.setdefault("cop_kutusu", []).append({
        "cop_id": _sayac_id("COP", veri.get("cop_kutusu", []), "cop_id"),
        "tur": tur, "veri": veri_objesi, "silen": silen, "tarih": _now()
    })
    veri_kaydet(veri)
    return True


def cop_kutusu_getir():
    return veri_yukle().get("cop_kutusu", [])[::-1]


def cop_geri_yukle(cop_id):
    veri = veri_yukle()
    item = None
    kalan = []
    for x in veri.get("cop_kutusu", []):
        if x.get("cop_id") == cop_id:
            item = x
        else:
            kalan.append(x)
    if not item:
        return False, "Çöp kutusu öğesi bulunamadı."
    tur = item.get("tur")
    obj = item.get("veri", {})
    if tur == "kurs":
        veri.setdefault("kurslar", []).append(obj)
    elif tur == "ogrenci":
        veri.setdefault("ogrenciler", []).append(obj)
    elif tur == "egitmen":
        veri.setdefault("egitmenler", []).append(obj)
    else:
        return False, "Bu veri türü geri yüklenemiyor."
    veri["cop_kutusu"] = kalan
    veri_kaydet(veri); log_ekle(f"Çöp kutusundan geri yüklendi: {cop_id}")
    return True, "Geri yükleme tamamlandı."


def kurs_onay_bekleyenler():
    return {k.get("kurs_id"): k for k in veri_yukle().get("kurslar", []) if k.get("onay_durumu") == "bekliyor"}


def kurs_onay_durumu_degistir(kurs_id, durum="onaylandi"):
    veri = veri_yukle()
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kurs_id:
            k["onay_durumu"] = durum
            veri.setdefault("kurs_onaylari", []).append({"kurs_id": kurs_id, "durum": durum, "tarih": _now()})
            veri_kaydet(veri); log_ekle(f"Kurs onay durumu değişti: {kurs_id} -> {durum}")
            return True, "Kurs durumu güncellendi."
    return False, "Kurs bulunamadı."


def sistem_sagligi_getir():
    size = os.path.getsize(DOSYA_ADI) if os.path.exists(DOSYA_ADI) else 0
    veri = veri_yukle()
    return {
        "JSON dosyası": "Var" if os.path.exists(DOSYA_ADI) else "Yok",
        "Dosya boyutu": f"{size} bayt",
        "Yedek sayısı": len([f for f in os.listdir('.') if f.startswith('yedek_') and f.endswith('.json')]),
        "Toplam tablo": len(veri.keys()),
        "Log sayısı": len(veri.get("loglar", [])),
        "Destek talebi": len(veri.get("destek_talepleri", [])),
    }


def profil_tamamlama(kullanici_id, rol):
    veri = veri_yukle()
    obj = None
    if rol == "ogrenci":
        obj = next((o for o in veri.get("ogrenciler", []) if o.get("ogrenci_id") == kullanici_id), None)
        alanlar = ["ad", "email", "sifre", "avatar", "ilerleme"]
    elif rol == "egitmen":
        obj = next((e for e in veri.get("egitmenler", []) if e.get("egitmen_id") == kullanici_id), None)
        alanlar = ["ad", "email", "sifre", "avatar", "uzmanlik", "onayli"]
    else:
        obj = veri.get("admin")
        alanlar = ["ad", "sifre", "rol"]
    if not obj:
        return 0
    dolu = sum(1 for a in alanlar if obj.get(a) not in (None, "", [], {}))
    return int((dolu / max(1, len(alanlar))) * 100)


def gun_etkinlikleri_getir(iso_tarih):
    rows = []
    for e in takvim_etkinlikleri_getir():
        if e.get("tarih") == iso_tarih:
            rows.append(e)
        elif e.get("tur") == "ders":
            try:
                d = date.fromisoformat(iso_tarih)
                if GUNLER[d.weekday()] in e.get("gunler", []):
                    rows.append(e)
            except Exception:
                pass
    return rows


def haftalik_etkinlikler_getir(baslangic=None):
    if başlangıç := baslangic:
        start = başlangıç if isinstance(başlangıç, date) else date.fromisoformat(str(başlangıç))
    else:
        today = date.today(); start = today - timedelta(days=today.weekday())
    return {str(start + timedelta(days=i)): gun_etkinlikleri_getir(str(start + timedelta(days=i))) for i in range(7)}


def ogretmen_cakisma_kontrolu(egitmen_id, gunler, saat, haric_kurs_id=None):
    sorunlar = []
    for k in egitmen_kurslari_getir(egitmen_id).values():
        if haric_kurs_id and k.get("kurs_id") == haric_kurs_id:
            continue
        if k.get("takvim_saat") == saat and set(gunler or []) & set(k.get("takvim_gunler", [])):
            sorunlar.append(f"{k.get('kurs_adi')} aynı gün/saatte görünüyor.")
    return sorunlar


def ogrenci_cakisma_kontrolu(ogrenci_id, kurs_id):
    kurslar = tum_kurslar_getir()
    yeni = kurslar.get(kurs_id, {})
    sorunlar = []
    for kid in ogrenci_kurslarini_getir(ogrenci_id):
        eski = kurslar.get(kid, {})
        if eski.get("takvim_saat") == yeni.get("takvim_saat") and set(eski.get("takvim_gunler", [])) & set(yeni.get("takvim_gunler", [])):
            sorunlar.append(f"{yeni.get('kurs_adi')} ile {eski.get('kurs_adi')} çakışıyor.")
    return sorunlar


def proje_dokumantasyonu():
    return {
        "Sınıflar": ["Kullanici", "Ogrenci", "Egitmen", "Admin", "Kurs", "Ders", "Odev", "Sinav", "TakvimEtkinligi", "Sertifika", "DestekTalebi"],
        "Veri Yapıları": ["List: öğrenciler, kurslar, ödevler", "Dictionary: kurs_id -> kurs, ayarlar", "JSON: kalıcı veri dosyası", "Set: çakışma kontrolünde ortak günler"],
        "Test Senaryoları": ["Öğrenci kayıt olur ve kursa yazılır", "Öğretmen kurs/ders açar", "Admin eğitmen/kurs onaylar", "Öğrenci ödev teslim eder", "Sınav otomatik puanlanır", "Takvim gün detayını gösterir", "Tema ve renk değiştirir"],
        "Kullanım": ["Sol menüden modül seçilir", "Sağ üst profil menüsünden ayarlar açılır", "Sağ alttaki asistan uygulamayı öğretir"]
    }


def sinif_diyagram_verisi():
    return [
        ("Kullanici", "Ogrenci", "kalıtım"), ("Kullanici", "Egitmen", "kalıtım"),
        ("Egitmen", "Kurs", "oluşturur"), ("Kurs", "Ders", "içerir"),
        ("Kurs", "Odev", "içerir"), ("Kurs", "Sinav", "içerir"),
        ("Ogrenci", "Sertifika", "kazanır"), ("Ogrenci", "Yoklama", "katılır")
    ]


def test_senaryolari_getir():
    return proje_dokumantasyonu()["Test Senaryoları"]


def _basit_pdf(path, baslik, satirlar):
    # Harici kütüphane istemeden basit PDF çıktısı üretir.
    lines = [baslik, "", *[str(x) for x in satirlar]]
    stream = "BT /F1 14 Tf 50 780 Td "
    first = True
    for line in lines[:45]:
        esc = _pdf_escape(line)
        if first:
            stream += f"({esc}) Tj "
            first = False
        else:
            stream += f"0 -22 Td ({esc}) Tj "
    stream += "ET"
    objects = []
    objects.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
    objects.append("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
    objects.append("3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj")
    objects.append("4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")
    objects.append(f"5 0 obj << /Length {len(stream.encode('latin-1','ignore'))} >> stream\n{stream}\nendstream endobj")
    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode('latin-1')))
        pdf += obj + "\n"
    xref = len(pdf.encode('latin-1'))
    pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n"
    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n"
    pdf += f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    with open(path, "wb") as f:
        f.write(pdf.encode("latin-1", errors="ignore"))
    return path


def sistem_raporu_pdf_olustur():
    rapor = sistem_raporu().splitlines()
    path = f"sistem_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    _basit_pdf(path, "Online Kurs Platformu - Sistem Raporu", rapor)
    log_ekle("Admin PDF sistem raporu oluşturdu.")
    return True, path


def kullanim_kilavuzu_pdf_olustur():
    doc = proje_dokumantasyonu()
    satirlar = []
    for baslik, items in doc.items():
        satirlar.append(baslik)
        satirlar.extend([f"- {x}" for x in items])
        satirlar.append("")
    path = f"kullanim_kilavuzu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    _basit_pdf(path, "Online Kurs Platformu - Kullanim Kilavuzu", satirlar)
    return True, path


def demo_veri_sifirla():
    veri = _bos_veri()
    veri["ogrenciler"] = [dict(o) for o in DEMO_OGRENCILER]
    veri["egitmenler"] = [dict(e) for e in DEMO_EGITMENLER]
    veri["kurslar"] = [json.loads(json.dumps(k, ensure_ascii=False)) for k in DEMO_KURSLAR]
    veri["notlar"] = [dict(n) for n in DEMO_NOTLAR]
    veri, _ = _migrate(veri)
    veri_kaydet(veri); log_ekle("Veri sıfırlandı.")
    return True, "Veri sıfırlandı."

# ══════════════════════════════════════════════════════════════════════
# TAKVİM PLUS + İLERİ SEVİYE PLATFORM ÖZELLİKLERİ
# Bu bölüm eski fonksiyonları silmeden, eksik kalan fikirleri sisteme ekler.
# ══════════════════════════════════════════════════════════════════════

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

try:
    from mail_servisi import kullanici_bilgilendirme_maili_gonder
except Exception:
    kullanici_bilgilendirme_maili_gonder = None


def _ensure_plus_keys(veri):
    for key, default in {
        "ozel_takvim_etkinlikleri": [],
        "profil_medya": [],
        "ders_tamamlamalari": [],
        "calisma_sureleri": [],
        "soru_bankasi": [],
        "rol_yetkileri": [],
        "yedek_gecmisi": [],
        "sunum_kayitlari": [],
        "dosya_teslimleri": [],
        "ayar_gecmisi": [],
    }.items():
        veri.setdefault(key, default)
    return veri


def plus_veri_yukle():
    veri = veri_yukle()
    changed = False
    once = set(veri.keys())
    _ensure_plus_keys(veri)
    if set(veri.keys()) != once:
        changed = True
    if changed:
        veri_kaydet(veri)
    return veri


# ─────────────────────────────────────────────────────────────────────
# Başvuru takip + onay/red sonrası otomatik mail
# ─────────────────────────────────────────────────────────────────────

def basvuru_durumu_sorgula(kullanici_id="", email=""):
    """Öğretmen/admin başvurusunun durumunu döndürür."""
    kullanici_id = (kullanici_id or "").strip()
    email = (email or "").strip().lower()
    veri = plus_veri_yukle()
    sonuclar = []
    for e in veri.get("egitmenler", []):
        if (kullanici_id and e.get("egitmen_id") == kullanici_id) or (email and e.get("email", "").lower() == email):
            sonuclar.append({"tur": "Öğretmen", "id": e.get("egitmen_id"), "ad": e.get("ad"), "email": e.get("email"), "durum": "onaylandı" if e.get("onayli") else "bekliyor"})
    for a in veri.get("admin_basvurular", []):
        if (kullanici_id and a.get("admin_id") == kullanici_id) or (email and a.get("email", "").lower() == email):
            sonuclar.append({"tur": "Admin", "id": a.get("admin_id"), "ad": a.get("ad"), "email": a.get("email"), "durum": a.get("durum", "bekliyor")})
    return sonuclar


def _basvuru_sonuc_maili_gonder(email, ad, rol, durum, not_metni=""):
    if not kullanici_bilgilendirme_maili_gonder or not email:
        return False, "Mail servisi aktif değil veya e-posta yok."
    konu = f"[Online Kurs Platformu] {rol} başvurunuz {durum}"
    icerik = f"""Merhaba {ad},

Online Kurs Platformu {rol} başvurunuzun durumu: {durum}

{not_metni or ''}

Onaylandıysa artık ilgili giriş ekranından kendi kullanıcı ID ve şifrenizle giriş yapabilirsiniz.

Online Kurs Platformu
"""
    return kullanici_bilgilendirme_maili_gonder(email, konu, icerik)


# Eski onay fonksiyonlarını saklayıp genişletiyoruz.
_egitmen_onayla_eski_plus = egitmen_onayla

def egitmen_onayla(egitmen_id):
    veri = plus_veri_yukle()
    hedef = None
    for e in veri.get("egitmenler", []):
        if e.get("egitmen_id") == egitmen_id or e.get("id") == egitmen_id:
            e["onayli"] = True
            e["durum"] = "aktif"
            hedef = e
            break
    if not hedef:
        return False
    veri_kaydet(veri)
    log_ekle(f"Eğitmen onaylandı: {egitmen_id}")
    ok_mail, mail_msg = _basvuru_sonuc_maili_gonder(hedef.get("email"), hedef.get("ad", egitmen_id), "Öğretmen", "onaylandı")
    log_ekle(f"Öğretmen onay maili {'gönderildi' if ok_mail else 'gönderilemedi'}: {mail_msg}")
    return True


def admin_basvuru_onayla(admin_id):
    veri = plus_veri_yukle()
    veri.setdefault("admin_basvurular", [])
    veri.setdefault("adminler", [])
    for a in veri["admin_basvurular"]:
        if a.get("admin_id") == admin_id or a.get("id") == admin_id:
            a["durum"] = "onaylandi"
            if not any(x.get("admin_id") == a.get("admin_id", admin_id) or x.get("id") == a.get("admin_id", admin_id) for x in veri.get("adminler", [])):
                veri["adminler"].append({
                    "admin_id": a.get("admin_id", admin_id), "id": a.get("admin_id", admin_id),
                    "kullanici_adi": a.get("admin_id", admin_id), "ad": a.get("ad", "Admin"),
                    "email": a.get("email", ""), "sifre": a.get("sifre", ""), "rol": "admin",
                    "durum": "aktif", "yetkiler": ["kullanici", "kurs", "rapor", "duyuru", "ayar"], "tarih": _now()
                })
            veri_kaydet(veri)
            log_ekle(f"Admin başvurusu onaylandı: {admin_id}")
            ok_mail, mail_msg = _basvuru_sonuc_maili_gonder(a.get("email"), a.get("ad", admin_id), "Admin", "onaylandı")
            log_ekle(f"Admin onay maili {'gönderildi' if ok_mail else 'gönderilemedi'}: {mail_msg}")
            return True, "Admin başvurusu onaylandı. Başvurana mail gönderilmeye çalışıldı."
    return False, "Admin başvurusu bulunamadı."


def admin_basvuru_reddet(admin_id, gerekce="Başvuru uygun bulunmadı."):
    veri = plus_veri_yukle()
    for a in veri.get("admin_basvurular", []):
        if a.get("admin_id") == admin_id or a.get("id") == admin_id:
            a["durum"] = "reddedildi"
            a["red_gerekcesi"] = gerekce
            veri_kaydet(veri)
            log_ekle(f"Admin başvurusu reddedildi: {admin_id}")
            _basvuru_sonuc_maili_gonder(a.get("email"), a.get("ad", admin_id), "Admin", "reddedildi", gerekce)
            return True, "Admin başvurusu reddedildi."
    return False, "Admin başvurusu bulunamadı."


# ─────────────────────────────────────────────────────────────────────
# Detaylı takvim: özel etkinlik, gün/hafta/ay özeti, filtreleme
# ─────────────────────────────────────────────────────────────────────

_takvim_etkinlikleri_getir_eski_plus = takvim_etkinlikleri_getir


def takvim_etkinligi_ekle(tur, ad, tarih, saat="", aciklama="", kurs_id="", kullanici_id="", rol="genel", renk=""):
    if not ad or not tarih:
        return False, "Etkinlik adı ve tarih zorunlu."
    try:
        date.fromisoformat(str(tarih))
    except Exception:
        return False, "Tarih formatı YYYY-MM-DD olmalı."
    veri = plus_veri_yukle()
    eid = _sayac_id("ETK", veri.get("ozel_takvim_etkinlikleri", []), "etkinlik_id")
    veri.setdefault("ozel_takvim_etkinlikleri", []).append({
        "etkinlik_id": eid, "tur": tur or "özel", "ad": ad, "tarih": str(tarih), "saat": saat,
        "aciklama": aciklama, "kurs_id": kurs_id, "kullanici_id": kullanici_id, "rol": rol, "renk": renk,
        "olusturma_tarihi": _now()
    })
    veri_kaydet(veri)
    log_ekle(f"Takvime özel etkinlik eklendi: {ad}")
    return True, f"Etkinlik eklendi: {eid}"


def takvim_etkinligi_sil(etkinlik_id):
    veri = plus_veri_yukle()
    once = len(veri.get("ozel_takvim_etkinlikleri", []))
    veri["ozel_takvim_etkinlikleri"] = [e for e in veri.get("ozel_takvim_etkinlikleri", []) if e.get("etkinlik_id") != etkinlik_id]
    if len(veri["ozel_takvim_etkinlikleri"]) == once:
        return False, "Etkinlik bulunamadı."
    veri_kaydet(veri)
    return True, "Etkinlik silindi."


def takvim_etkinlikleri_getir():
    veri = plus_veri_yukle()
    etkinlikler = []
    # Eski ders/sınav/ödev etkinliklerini koru.
    try:
        etkinlikler.extend(_takvim_etkinlikleri_getir_eski_plus())
    except Exception:
        pass
    # Duyuruları da takvime bilgi olarak ekle.
    for d in veri.get("duyurular", [])[:30]:
        tarih = d.get("tarih") or d.get("created_at") or ""
        if tarih and len(str(tarih)) >= 10:
            tarih = str(tarih)[:10]
            etkinlikler.append({"tur": "duyuru", "ad": d.get("mesaj", "Duyuru")[:80], "tarih": tarih, "saat": "", "aciklama": d.get("mesaj", "")})
    # İptal edilen dersler.
    for iptal in veri.get("takvim_iptaller", []):
        etkinlikler.append({"tur": "iptal", "ad": iptal.get("mesaj", "Ders iptal"), "tarih": iptal.get("tarih", ""), "saat": iptal.get("saat", ""), "kurs_id": iptal.get("kurs_id", "")})
    # Özel etkinlikler.
    etkinlikler.extend(veri.get("ozel_takvim_etkinlikleri", []))
    return etkinlikler


def gun_etkinlikleri_getir(iso_tarih):
    rows = []
    try:
        d = date.fromisoformat(str(iso_tarih))
    except Exception:
        return []
    for e in takvim_etkinlikleri_getir():
        if e.get("tarih") == str(iso_tarih):
            rows.append(e)
        elif e.get("tur") == "ders":
            if GUNLER[d.weekday()] in e.get("gunler", []):
                # Her hafta tekrar eden ders için o güne kopya bilgi göster.
                x = dict(e); x["tarih"] = str(iso_tarih); rows.append(x)
    rows.sort(key=lambda x: (x.get("saat") or "99:99", x.get("tur") or ""))
    return rows


def haftalik_etkinlikler_getir(baslangic=None):
    if baslangic:
        start = baslangic if isinstance(baslangic, date) else date.fromisoformat(str(baslangic))
    else:
        today = date.today(); start = today - timedelta(days=today.weekday())
    return {str(start + timedelta(days=i)): gun_etkinlikleri_getir(str(start + timedelta(days=i))) for i in range(7)}


def takvim_aylik_istatistik(yil=None, ay=None):
    today = date.today(); yil = yil or today.year; ay = ay or today.month
    sayac = {"ders": 0, "sinav": 0, "odev": 0, "duyuru": 0, "iptal": 0, "özel": 0, "diger": 0}
    _, son = __import__("calendar").monthrange(int(yil), int(ay))
    for day in range(1, son + 1):
        iso = date(int(yil), int(ay), day).isoformat()
        for e in gun_etkinlikleri_getir(iso):
            tur = e.get("tur", "diger")
            sayac[tur if tur in sayac else "diger"] += 1
    return sayac


def takvim_filtrele(tur=None, kurs_id=None, metin=None):
    rows = takvim_etkinlikleri_getir()
    if tur and tur != "Tümü":
        rows = [e for e in rows if e.get("tur") == tur]
    if kurs_id:
        rows = [e for e in rows if e.get("kurs_id") == kurs_id]
    if metin:
        m = metin.lower()
        rows = [e for e in rows if m in str(e.get("ad", "")).lower() or m in str(e.get("aciklama", "")).lower()]
    return rows


# ─────────────────────────────────────────────────────────────────────
# Profil, kapak görseli, dosya teslim, materyal seçme
# ─────────────────────────────────────────────────────────────────────

def profil_fotografi_guncelle(kullanici_id, rol, foto_yolu):
    veri = plus_veri_yukle()
    hedef = None
    if rol == "ogrenci":
        hedef = next((o for o in veri.get("ogrenciler", []) if o.get("ogrenci_id") == kullanici_id), None)
    elif rol == "egitmen":
        hedef = next((e for e in veri.get("egitmenler", []) if e.get("egitmen_id") == kullanici_id), None)
    else:
        hedef = veri.get("admin")
    if not hedef:
        return False, "Kullanıcı bulunamadı."
    hedef["profil_foto"] = foto_yolu
    hedef["avatar"] = "🖼️"
    veri_kaydet(veri)
    return True, "Profil fotoğrafı kaydedildi."


def kurs_kapak_guncelle(kurs_id, kapak):
    veri = plus_veri_yukle()
    for k in veri.get("kurslar", []):
        if k.get("kurs_id") == kurs_id:
            k["kapak"] = kapak or "📚"
            veri_kaydet(veri)
            return True, "Kurs kapak bilgisi güncellendi."
    return False, "Kurs bulunamadı."


def materyal_dosya_ekle(kurs_id, baslik, dosya_yolu, tur="Dosya"):
    return materyal_ekle(kurs_id, baslik, tur or "Dosya", dosya_yolu)


def odev_dosya_teslim_et(odev_id, ogrenci_id, dosya_yolu, not_mesaji=""):
    veri = plus_veri_yukle()
    ok, msg = odev_teslim_et(odev_id, ogrenci_id, dosya_yolu or not_mesaji)
    if ok:
        veri = plus_veri_yukle()
        veri.setdefault("dosya_teslimleri", []).append({"odev_id": odev_id, "ogrenci_id": ogrenci_id, "dosya_yolu": dosya_yolu, "mesaj": not_mesaji, "tarih": _now()})
        veri_kaydet(veri)
    return ok, msg


def odev_geri_bildirim_ver(odev_id, ogrenci_id, not_degeri, geri_bildirim):
    veri = plus_veri_yukle()
    for t in veri.get("teslimler", []):
        if t.get("odev_id") == odev_id and t.get("ogrenci_id") == ogrenci_id:
            t["not"] = float(not_degeri or 0)
            t["geri_bildirim"] = geri_bildirim
            t["durum"] = "Değerlendirildi"
            veri_kaydet(veri)
            bildirim_ekle(ogrenci_id, "ogrenci", f"{odev_id} ödevin değerlendirildi. Not: {not_degeri}")
            return True, "Ödev geri bildirimi kaydedildi."
    return False, "Teslim bulunamadı."


# ─────────────────────────────────────────────────────────────────────
# Öğrenci öğrenme ekranı, transkript, çalışma süresi, haftalık rapor
# ─────────────────────────────────────────────────────────────────────

def ders_izle_tamamla(ogrenci_id, kurs_id, ders_id="", dakika=30):
    veri = plus_veri_yukle()
    did = ders_id or "GENEL"
    if not any(x.get("ogrenci_id") == ogrenci_id and x.get("kurs_id") == kurs_id and x.get("ders_id") == did for x in veri.get("ders_tamamlamalari", [])):
        veri.setdefault("ders_tamamlamalari", []).append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "ders_id": did, "tarih": _now()})
    veri.setdefault("calisma_sureleri", []).append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "dakika": int(dakika or 0), "tarih": _now(), "gun": _today_str()})
    # Ders sayısına göre otomatik ilerleme.
    kurs = tum_kurslar_getir().get(kurs_id, {})
    ders_sayisi = max(1, len(kurs.get("dersler", [])))
    tamam = len([x for x in veri.get("ders_tamamlamalari", []) if x.get("ogrenci_id") == ogrenci_id and x.get("kurs_id") == kurs_id])
    oran = min(100, int(tamam / ders_sayisi * 100))
    veri_kaydet(veri)
    ilerleme_guncelle(ogrenci_id, kurs_id, oran)
    return True, f"Ders tamamlandı. Yeni ilerleme: %{oran}"


def calisma_suresi_getir(ogrenci_id, gun_sayisi=7):
    veri = plus_veri_yukle(); bugun = date.today(); toplam = 0
    for c in veri.get("calisma_sureleri", []):
        if c.get("ogrenci_id") != ogrenci_id: continue
        try:
            d = date.fromisoformat(c.get("gun"))
            if (bugun - d).days < int(gun_sayisi): toplam += int(c.get("dakika", 0))
        except Exception: pass
    return toplam


def transkript_getir(ogrenci_id):
    kurslar = tum_kurslar_getir(); notlar = ogrenci_notlarini_getir(ogrenci_id); rows = []
    for kid in ogrenci_kurslarini_getir(ogrenci_id):
        n = notlar.get(kid, {})
        ort = float(n.get("not", 0) or 0)
        harf = "AA" if ort >= 90 else "BA" if ort >= 80 else "BB" if ort >= 70 else "CB" if ort >= 60 else "FF"
        rows.append({"kurs_id": kid, "kurs_adi": kurslar.get(kid, {}).get("kurs_adi", kid), "not": ort, "harf": harf, "ilerleme": ilerleme_getir(ogrenci_id, kid)})
    genel = round(mean([r["not"] for r in rows]), 2) if rows else 0
    return {"ogrenci_id": ogrenci_id, "genel_ortalama": genel, "dersler": rows}


def haftalik_ogrenci_raporu(ogrenci_id):
    sure = calisma_suresi_getir(ogrenci_id, 7)
    bugun = date.today(); hafta = bugun - timedelta(days=bugun.weekday())
    tamamlanan = len([x for x in plus_veri_yukle().get("ders_tamamlamalari", []) if x.get("ogrenci_id") == ogrenci_id and str(x.get("tarih", ""))[:10] >= str(hafta)])
    teslim = len([t for t in teslimleri_getir(ogrenci_id=ogrenci_id) if str(t.get("tarih", ""))[:10] >= str(hafta)])
    sinav = len([s for s in sinav_sonuclari_getir(ogrenci_id=ogrenci_id) if str(s.get("tarih", ""))[:10] >= str(hafta)])
    return {"calisma_dakika": sure, "tamamlanan_ders": tamamlanan, "teslim_edilen_odev": teslim, "girilen_sinav": sinav, "genel_ortalama": transkript_getir(ogrenci_id)["genel_ortalama"]}


# ─────────────────────────────────────────────────────────────────────
# Öğretmen araçları: toplu mesaj, risk analizi, soru bankası, sınav analizi
# ─────────────────────────────────────────────────────────────────────

def ogretmen_toplu_mesaj(egitmen_id, kurs_id, mesaj):
    kurs = tum_kurslar_getir().get(kurs_id, {})
    if kurs.get("egitmen_id") != egitmen_id:
        return False, "Bu kurs size ait değil."
    say = 0
    for oid in kurs.get("kayitli_ogrenciler", []):
        bildirim_ekle(oid, "ogrenci", mesaj)
        say += 1
    log_ekle(f"Toplu mesaj gönderildi: {egitmen_id}/{kurs_id}")
    return True, f"{say} öğrenciye bildirim gönderildi."


def riskli_ogrenciler_getir(egitmen_id=None):
    kurslar = tum_kurslar_getir(); rows = []
    for kid, k in kurslar.items():
        if egitmen_id and k.get("egitmen_id") != egitmen_id: continue
        notlar = kurs_notlarini_getir(kid)
        for oid in k.get("kayitli_ogrenciler", []):
            n = float(notlar.get(oid, {}).get("not", 0) or 0)
            dev = devamsizlik_sayisi(oid)
            odevler = odevleri_getir(kurs_id=kid)
            teslimler = teslimleri_getir(ogrenci_id=oid)
            teslim_ids = {t.get("odev_id") for t in teslimler}
            eksik = len([o for o in odevler if o.get("odev_id") not in teslim_ids])
            neden = []
            if n and n < 50: neden.append("not düşük")
            if dev >= 2: neden.append("devamsızlık")
            if eksik > 0: neden.append(f"{eksik} eksik ödev")
            if neden:
                rows.append({"ogrenci_id": oid, "ad": tum_kullanicilar_getir()["ogrenciler"].get(oid, {}).get("ad", oid), "kurs_id": kid, "kurs_adi": k.get("kurs_adi"), "not": n, "devamsizlik": dev, "neden": ", ".join(neden)})
    return rows


def soru_bankasi_ekle(egitmen_id, kurs_id, soru, secenekler, dogru):
    veri = plus_veri_yukle()
    sid = _sayac_id("SOR", veri.get("soru_bankasi", []), "soru_id")
    veri.setdefault("soru_bankasi", []).append({"soru_id": sid, "egitmen_id": egitmen_id, "kurs_id": kurs_id, "soru": soru, "secenekler": secenekler, "dogru": int(dogru or 0), "tarih": _now()})
    veri_kaydet(veri)
    return True, f"Soru bankasına eklendi: {sid}"


def soru_bankasi_getir(egitmen_id=None, kurs_id=None):
    rows = plus_veri_yukle().get("soru_bankasi", [])
    if egitmen_id: rows = [r for r in rows if r.get("egitmen_id") == egitmen_id]
    if kurs_id: rows = [r for r in rows if r.get("kurs_id") == kurs_id]
    return rows


def rastgele_quiz_olustur(egitmen_id, kurs_id, baslik, tarih, adet=5, sure_dk=20):
    import random
    sorular = soru_bankasi_getir(egitmen_id, kurs_id)
    if not sorular:
        return False, "Soru bankasında soru yok."
    secilen = random.sample(sorular, min(int(adet or 5), len(sorular)))
    sorular2 = [{"soru": s.get("soru"), "secenekler": s.get("secenekler"), "dogru": int(s.get("dogru", 0))} for s in secilen]
    ok, msg = sinav_ekle(kurs_id, egitmen_id, baslik, tarih, sorular2)
    if ok:
        veri = plus_veri_yukle()
        for s in veri.get("sinavlar", []):
            if s.get("sinav_id") == msg:
                s["sure_dk"] = int(sure_dk or 20)
        veri_kaydet(veri)
    return ok, msg


def sinav_analizi_getir(sinav_id):
    sonuclar = sinav_sonuclari_getir(sinav_id=sinav_id)
    puanlar = [float(x.get("puan", 0) or 0) for x in sonuclar]
    return {
        "sinav_id": sinav_id,
        "katilim": len(sonuclar),
        "ortalama": round(mean(puanlar), 2) if puanlar else 0,
        "en_yuksek": max(puanlar) if puanlar else 0,
        "en_dusuk": min(puanlar) if puanlar else 0,
        "basari_orani": round(len([p for p in puanlar if p >= 60]) / max(1, len(puanlar)) * 100, 1),
    }


# ─────────────────────────────────────────────────────────────────────
# Admin gelişmiş araçları: yetki, arama, yedek, ayarlar, sunum/demo
# ─────────────────────────────────────────────────────────────────────

def rol_yetkileri_getir(kullanici_id):
    veri = plus_veri_yukle()
    for y in veri.get("rol_yetkileri", []):
        if y.get("kullanici_id") == kullanici_id:
            return y.get("yetkiler", [])
    return []


def rol_yetkileri_guncelle(kullanici_id, yetkiler):
    veri = plus_veri_yukle(); veri.setdefault("rol_yetkileri", [])
    for y in veri["rol_yetkileri"]:
        if y.get("kullanici_id") == kullanici_id:
            y["yetkiler"] = yetkiler; veri_kaydet(veri); return True, "Yetkiler güncellendi."
    veri["rol_yetkileri"].append({"kullanici_id": kullanici_id, "yetkiler": yetkiler, "tarih": _now()})
    veri_kaydet(veri); return True, "Yetkiler kaydedildi."


def gelismis_arama(metin):
    m = (metin or "").lower(); veri = plus_veri_yukle(); rows = []
    for tablo, idkey, namekey in [("ogrenciler", "ogrenci_id", "ad"), ("egitmenler", "egitmen_id", "ad"), ("kurslar", "kurs_id", "kurs_adi"), ("admin_basvurular", "admin_id", "ad")]:
        for x in veri.get(tablo, []):
            if m in json.dumps(x, ensure_ascii=False).lower():
                rows.append({"tur": tablo, "id": x.get(idkey, x.get("id", "")), "ad": x.get(namekey, ""), "ozet": str(x)[:180]})
    return rows


def yedekleri_listele():
    files = []
    for f in os.listdir('.'):
        if f.startswith('yedek_') and f.endswith('.json'):
            try: files.append({"dosya": f, "boyut": os.path.getsize(f), "tarih": datetime.fromtimestamp(os.path.getmtime(f)).strftime("%d.%m.%Y %H:%M")})
            except Exception: pass
    return sorted(files, key=lambda x: x["tarih"], reverse=True)


def yedekten_geri_yukle(dosya):
    if not os.path.exists(dosya): return False, "Yedek dosyası bulunamadı."
    shutil.copy(dosya, DOSYA_ADI)
    log_ekle(f"Yedekten geri yüklendi: {dosya}")
    return True, "Yedekten geri yüklendi."


def otomatik_yedekle(neden="otomatik"):
    ok, msg = veritabani_yedekle()
    veri = plus_veri_yukle()
    veri.setdefault("yedek_gecmisi", []).append({"neden": neden, "sonuc": msg, "tarih": _now()})
    veri_kaydet(veri)
    return ok, msg


def sistem_ayarlari_getir():
    return plus_veri_yukle().get("sistem_ayarlari", {})


def sistem_ayarlari_guncelle(**kwargs):
    veri = plus_veri_yukle()
    veri.setdefault("sistem_ayarlari", {}).update({k: v for k, v in kwargs.items() if v is not None})
    veri.setdefault("ayar_gecmisi", []).append({"ayarlar": kwargs, "tarih": _now()})
    veri_kaydet(veri)
    return True, "Sistem ayarları güncellendi."


def sunum_modu_verisi():
    return [
        "1. Öğrenci kayıt olur ve sisteme giriş yapar.",
        "2. Öğretmen/admin başvurusu mail ile yöneticiye gider.",
        "3. Admin başvuruyu onaylar; başvurana otomatik mail gider.",
        "4. Öğretmen kurs/ders açar ve takvime saat ekler.",
        "5. Öğrenci derse kayıt olur; çakışma kontrol edilir.",
        "6. Öğretmen ödev, materyal, quiz ve yoklama yönetir.",
        "7. Öğrenci ders izler, ödev teslim eder, sınav çözer.",
        "8. Takvim; ders, sınav, ödev, duyuru, iptal ve özel etkinlikleri gösterir.",
        "9. Admin rapor, yedek, JSON, destek ve sistem ayarlarını yönetir.",
        "10. Platform asistanı kullanıcıya adım adım rehberlik eder.",
    ]


def otomatik_demo_senaryosu():
    # Sunumda hızlı demo için birkaç özel etkinlik ve bildirim ekler.
    today = date.today()
    takvim_etkinligi_ekle("özel", "Sunum Demo Etkinliği", str(today), "14:00", "Otomatik demo senaryosu")
    toplu_bildirim("Demo senaryosu hazırlandı. Takvim ve Proje Plus sayfasını kontrol edin.", "all")
    log_ekle("Otomatik demo senaryosu çalıştırıldı.")
    return True, "Demo senaryosu oluşturuldu."


def otomatik_proje_raporu_olustur():
    satirlar = ["ONLINE KURS PLATFORMU PROJE RAPORU", f"Tarih: {_now()}", ""]
    satirlar.extend(sunum_modu_verisi())
    satirlar.append("")
    satirlar.append("Ek Modüller: detaylı takvim, mail başvuru, soru bankası, risk analizi, dosya teslim, transkript, sistem ayarları")
    path = f"proje_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    _basit_pdf(path, "Online Kurs Platformu - Proje Raporu", satirlar)
    return True, path


# Program açılışında bir kez özel anahtarları oluştur.
try:
    v = plus_veri_yukle(); _ensure_plus_keys(v); veri_kaydet(v)
except Exception:
    pass


# ══════════════════════════════════════════════════════════════════════
# YARATICI FINAL MODÜLLER
# QR yoklama, XP/seviye, sertifika doğrulama, kariyer yolu,
# ders odası, süreli sınav, haftalık mail özeti, gelişmiş destek,
# sunum demo akışı ve kullanım rehberi veri katmanı.
# ══════════════════════════════════════════════════════════════════════

CREATIVE_KEYS = {
    "xp_kayitlari": [],
    "qr_yoklama_kodlari": [],
    "sertifika_dogrulamalari": [],
    "ogrenci_kariyer_yollari": [],
    "sinav_oturumlari": [],
    "haftalik_mail_loglari": [],
    "ders_odasi_gunlukleri": [],
    "destek_mesajlari": [],
    "sunum_demo_loglari": [],
}


def _ensure_creative_keys(veri):
    degisti = False
    for k, v in CREATIVE_KEYS.items():
        if k not in veri:
            veri[k] = list(v)
            degisti = True
    return degisti


def creative_veri_yukle():
    veri = veri_yukle()
    if _ensure_creative_keys(veri):
        veri_kaydet(veri)
    return veri


# ── XP / Seviye / Liderlik ───────────────────────────────────────────
def xp_ekle(kullanici_id, sebep, puan):
    veri = creative_veri_yukle()
    try:
        puan = int(puan)
    except Exception:
        puan = 0
    if not kullanici_id or puan == 0:
        return False, "XP kaydı için kullanıcı veya puan eksik."
    veri.setdefault("xp_kayitlari", []).append({
        "kullanici_id": kullanici_id,
        "sebep": sebep,
        "puan": puan,
        "tarih": _now(),
    })
    veri_kaydet(veri)
    return True, f"+{puan} XP: {sebep}"


def xp_toplam(kullanici_id):
    return sum(int(x.get("puan", 0) or 0) for x in creative_veri_yukle().get("xp_kayitlari", []) if x.get("kullanici_id") == kullanici_id)


def seviye_hesapla(xp):
    xp = int(xp or 0)
    seviyeler = [
        (0, "Yeni Öğrenci"),
        (100, "Aktif Öğrenci"),
        (250, "Başarılı Öğrenci"),
        (500, "Uzman Adayı"),
        (900, "Platform Yıldızı"),
        (1400, "Akademi Elçisi"),
    ]
    aktif = seviyeler[0]
    sonraki = None
    for i, item in enumerate(seviyeler):
        if xp >= item[0]:
            aktif = item
            sonraki = seviyeler[i + 1] if i + 1 < len(seviyeler) else None
    hedef = sonraki[0] if sonraki else max(aktif[0], xp)
    onceki = aktif[0]
    ilerleme = 100 if not sonraki else round((xp - onceki) / max(1, hedef - onceki) * 100, 1)
    return {"xp": xp, "seviye": aktif[1], "sonraki": sonraki[1] if sonraki else "Maksimum seviye", "sonraki_xp": hedef, "ilerleme": max(0, min(100, ilerleme))}


def xp_ozeti(kullanici_id):
    veri = creative_veri_yukle()
    kayitlar = [x for x in veri.get("xp_kayitlari", []) if x.get("kullanici_id") == kullanici_id]
    oz = seviye_hesapla(sum(int(x.get("puan", 0) or 0) for x in kayitlar))
    oz["kayitlar"] = list(reversed(kayitlar[-20:]))
    return oz


def xp_liderlik_tablosu(limit=10):
    veri = creative_veri_yukle()
    adlar = {}
    for o in veri.get("ogrenciler", []):
        adlar[o.get("ogrenci_id")] = o.get("ad", o.get("ogrenci_id"))
    toplamlar = {}
    for x in veri.get("xp_kayitlari", []):
        kid = x.get("kullanici_id")
        toplamlar[kid] = toplamlar.get(kid, 0) + int(x.get("puan", 0) or 0)
    rows = []
    for kid, xp in toplamlar.items():
        rows.append({"kullanici_id": kid, "ad": adlar.get(kid, kid), **seviye_hesapla(xp)})
    return sorted(rows, key=lambda r: r.get("xp", 0), reverse=True)[:int(limit or 10)]


# Mevcut işlemlere küçük oyunlaştırma puanları bağlanır.
try:
    _creative_old_kursa_kayit = kursa_kayit
    def kursa_kayit(ogrenci_id, kurs_id):
        ok, msg = _creative_old_kursa_kayit(ogrenci_id, kurs_id)
        if ok:
            xp_ekle(ogrenci_id, f"{kurs_id} kursuna kayıt", 15)
        return ok, msg
except Exception:
    pass

try:
    _creative_old_odev_teslim_et = odev_teslim_et
    def odev_teslim_et(odev_id, ogrenci_id, cevap):
        ok, msg = _creative_old_odev_teslim_et(odev_id, ogrenci_id, cevap)
        if ok:
            xp_ekle(ogrenci_id, f"{odev_id} ödev teslimi", 20)
        return ok, msg
except Exception:
    pass

try:
    _creative_old_sinav_coz = sinav_coz
    def sinav_coz(sinav_id, ogrenci_id, cevaplar):
        ok, msg = _creative_old_sinav_coz(sinav_id, ogrenci_id, cevaplar)
        if ok:
            xp_ekle(ogrenci_id, f"{sinav_id} sınavı çözüldü", 25)
        return ok, msg
except Exception:
    pass

try:
    _creative_old_ilerleme_guncelle = ilerleme_guncelle
    def ilerleme_guncelle(ogrenci_id, kurs_id, yuzde):
        onceki = ilerleme_getir(ogrenci_id, kurs_id)
        ok, msg = _creative_old_ilerleme_guncelle(ogrenci_id, kurs_id, yuzde)
        if ok and int(yuzde or 0) > int(onceki or 0):
            xp_ekle(ogrenci_id, f"{kurs_id} ilerleme artışı", max(5, int((int(yuzde or 0)-int(onceki or 0))/2)))
            if int(yuzde or 0) >= 100 and int(onceki or 0) < 100:
                xp_ekle(ogrenci_id, f"{kurs_id} tamamlandı", 50)
        return ok, msg
except Exception:
    pass


# ── QR Yoklama Simülasyonu ──────────────────────────────────────────
def qr_yoklama_kodu_olustur(egitmen_id, kurs_id, tarih=None, sure_dk=15):
    import random, string
    veri = creative_veri_yukle()
    tarih = tarih or _today_str()
    kurs = tum_kurslar_getir().get(kurs_id, {})
    if kurs and kurs.get("egitmen_id") != egitmen_id:
        return False, "Bu kurs size ait değil."
    kod = f"{str(kurs_id).replace('KURS','K')}-{''.join(random.choice(string.digits) for _ in range(4))}"
    veri.setdefault("qr_yoklama_kodlari", []).append({
        "kod": kod,
        "egitmen_id": egitmen_id,
        "kurs_id": kurs_id,
        "tarih": tarih,
        "sure_dk": int(sure_dk or 15),
        "aktif": True,
        "created_at": _now(),
    })
    veri_kaydet(veri)
    log_ekle(f"QR yoklama kodu üretildi: {kurs_id}/{kod}")
    return True, kod


def qr_yoklama_kodu_kullan(ogrenci_id, kod):
    veri = creative_veri_yukle()
    kayit = next((x for x in reversed(veri.get("qr_yoklama_kodlari", [])) if str(x.get("kod", "")).lower() == str(kod).strip().lower() and x.get("aktif", True)), None)
    if not kayit:
        return False, "Kod bulunamadı veya pasif."
    kurs_id = kayit.get("kurs_id")
    if kurs_id not in ogrenci_kurslarini_getir(ogrenci_id):
        return False, "Bu yoklama kodu kayıtlı olmadığınız bir kursa ait."
    tarih = kayit.get("tarih", _today_str())
    mevcut = next((y for y in veri.get("yoklamalar", []) if y.get("kurs_id") == kurs_id and y.get("tarih") == tarih), None)
    if not mevcut:
        mevcut = {"yoklama_id": _sayac_id("YOK", veri.get("yoklamalar", []), "yoklama_id"), "kurs_id": kurs_id, "tarih": tarih, "durumlar": {}, "created_at": _now()}
        veri.setdefault("yoklamalar", []).append(mevcut)
    mevcut.setdefault("durumlar", {})[ogrenci_id] = "Geldi"
    veri_kaydet(veri)
    xp_ekle(ogrenci_id, f"{kurs_id} QR yoklama", 10)
    return True, "Yoklamanız 'Geldi' olarak işlendi."


def aktif_qr_yoklama_kodlari(egitmen_id=None, kurs_id=None):
    rows = [x for x in creative_veri_yukle().get("qr_yoklama_kodlari", []) if x.get("aktif", True)]
    if egitmen_id:
        rows = [x for x in rows if x.get("egitmen_id") == egitmen_id]
    if kurs_id:
        rows = [x for x in rows if x.get("kurs_id") == kurs_id]
    return list(reversed(rows))


# ── Sertifika doğrulama ──────────────────────────────────────────────
def _sertifika_kod_hesapla(ogrenci_id, kurs_id):
    import hashlib
    raw = f"{ogrenci_id}|{kurs_id}|ONLINE-KURS-PLATFORMU".encode("utf-8")
    return "CERT-" + hashlib.sha1(raw).hexdigest()[:10].upper()


def sertifika_dogrulama_kodu_olustur(ogrenci_id, kurs_id):
    belgeler = belgeleri_getir(ogrenci_id)
    belge = next((b for b in belgeler if b.get("kurs_id") == kurs_id), None)
    if not belge:
        return False, "Bu öğrenci bu kurs için sertifika şartını sağlamıyor."
    veri = creative_veri_yukle()
    kod = _sertifika_kod_hesapla(ogrenci_id, kurs_id)
    if not any(x.get("kod") == kod for x in veri.get("sertifika_dogrulamalari", [])):
        veri.setdefault("sertifika_dogrulamalari", []).append({"kod": kod, "ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "tarih": _now(), "gecerli": True})
        veri_kaydet(veri)
    return True, kod


def sertifika_dogrula(kod):
    kod = str(kod or "").strip().upper()
    veri = creative_veri_yukle()
    kayit = next((x for x in veri.get("sertifika_dogrulamalari", []) if str(x.get("kod", "")).upper() == kod), None)
    if not kayit:
        # Daha önce kaydedilmemiş olsa bile mevcut belge listesinden hesaplanabilir.
        for o in veri.get("ogrenciler", []):
            for b in belgeleri_getir(o.get("ogrenci_id")):
                if _sertifika_kod_hesapla(o.get("ogrenci_id"), b.get("kurs_id")) == kod:
                    kayit = {"kod": kod, "ogrenci_id": o.get("ogrenci_id"), "kurs_id": b.get("kurs_id"), "tarih": b.get("tarih"), "gecerli": True}
                    break
            if kayit:
                break
    if not kayit:
        return False, "Sertifika kodu bulunamadı."
    ogr = tum_kullanicilar_getir()["ogrenciler"].get(kayit.get("ogrenci_id"), {})
    kurs = tum_kurslar_getir().get(kayit.get("kurs_id"), {})
    notlar = ogrenci_notlarini_getir(kayit.get("ogrenci_id"))
    n = notlar.get(kayit.get("kurs_id"), {})
    return True, {"kod": kod, "ogrenci": ogr.get("ad", kayit.get("ogrenci_id")), "kurs": kurs.get("kurs_adi", kayit.get("kurs_id")), "not": n.get("not", "—"), "harf": n.get("harf", harf_notu(n.get("not", 0))), "tarih": kayit.get("tarih"), "gecerli": kayit.get("gecerli", True)}


# ── Kariyer yolu ─────────────────────────────────────────────────────
def kariyer_yollari_getir():
    return [
        {"id": "web", "ad": "Web Geliştirici", "ikon": "💻", "adimlar": ["Python", "Django", "React", "Veritabanı", "Bitirme Projesi"], "aciklama": "Backend + frontend temelleriyle tam yığın web geliştirme rotası."},
        {"id": "veri", "ad": "Veri Bilimci", "ikon": "📊", "adimlar": ["Python", "Veri Analizi", "Makine Öğrenmesi", "Yapay Zeka", "Bitirme Projesi"], "aciklama": "Python, analiz ve makine öğrenmesi odaklı rota."},
        {"id": "tasarim", "ad": "UI/UX Tasarımcı", "ikon": "🎨", "adimlar": ["Grafik Tasarım", "Figma", "Kullanıcı Deneyimi", "Portfolyo", "Bitirme Projesi"], "aciklama": "Arayüz, görsel tasarım ve portfolyo oluşturma rotası."},
    ]


def kariyer_yolu_sec(ogrenci_id, yol_id):
    veri = creative_veri_yukle()
    if yol_id not in [y["id"] for y in kariyer_yollari_getir()]:
        return False, "Geçersiz kariyer yolu."
    mevcut = next((x for x in veri.get("ogrenci_kariyer_yollari", []) if x.get("ogrenci_id") == ogrenci_id), None)
    if mevcut:
        mevcut.update({"yol_id": yol_id, "tarih": _now()})
    else:
        veri.setdefault("ogrenci_kariyer_yollari", []).append({"ogrenci_id": ogrenci_id, "yol_id": yol_id, "tarih": _now()})
    veri_kaydet(veri)
    xp_ekle(ogrenci_id, "Kariyer yolu seçildi", 10)
    return True, "Kariyer yolu kaydedildi."


def kariyer_ilerleme_getir(ogrenci_id):
    veri = creative_veri_yukle()
    secim = next((x for x in veri.get("ogrenci_kariyer_yollari", []) if x.get("ogrenci_id") == ogrenci_id), None)
    yol = next((y for y in kariyer_yollari_getir() if y["id"] == (secim or {}).get("yol_id")), None)
    if not yol:
        yol = kariyer_yollari_getir()[0]
    kurslar = [tum_kurslar_getir().get(kid, {}) for kid in ogrenci_kurslarini_getir(ogrenci_id)]
    adimlar = []
    for adim in yol["adimlar"]:
        done = False
        matched = ""
        for k in kurslar:
            metin = (k.get("kurs_adi", "") + " " + k.get("kategori", "") + " " + k.get("aciklama", "")).lower()
            if adim.lower().split()[0] in metin or (adim == "Veritabanı" and "data" in metin):
                done = True; matched = k.get("kurs_adi", ""); break
        adimlar.append({"adim": adim, "tamam": done, "eslesen_kurs": matched})
    yuzde = round(len([a for a in adimlar if a["tamam"]]) / max(1, len(adimlar)) * 100, 1)
    return {"yol": yol, "adimlar": adimlar, "yuzde": yuzde}


# ── Ders odası ───────────────────────────────────────────────────────
def ders_odasi_verisi(ogrenci_id, kurs_id):
    kurs = tum_kurslar_getir().get(kurs_id, {})
    if not kurs:
        return None
    return {
        "kurs": kurs,
        "egitmen": tum_kullanicilar_getir()["egitmenler"].get(kurs.get("egitmen_id"), {}),
        "ilerleme": ilerleme_getir(ogrenci_id, kurs_id),
        "materyaller": kurs.get("materyaller", []),
        "dersler": kurs.get("dersler", []),
        "odevler": odevleri_getir(kurs_id=kurs_id),
        "sinavlar": sinavlari_getir(kurs_id=kurs_id),
        "yorumlar": yorumlari_getir(kurs_id),
        "sonraki_adimlar": ["Ders materyalini incele", "Dersi tamamlandı işaretle", "Ödevi teslim et", "Quiz/Sınav çöz", "Sertifika şartını tamamla"],
    }


def ders_odasi_gunluk_ekle(ogrenci_id, kurs_id, islem):
    veri = creative_veri_yukle()
    veri.setdefault("ders_odasi_gunlukleri", []).append({"ogrenci_id": ogrenci_id, "kurs_id": kurs_id, "islem": islem, "tarih": _now()})
    veri_kaydet(veri)
    return True, "Ders odası etkinliği kaydedildi."


# ── Süreli sınav ─────────────────────────────────────────────────────
def sinav_sureli_baslat(sinav_id, ogrenci_id):
    veri = creative_veri_yukle()
    sinav = next((s for s in veri.get("sinavlar", []) if s.get("sinav_id") == sinav_id), None)
    if not sinav:
        return False, "Sınav bulunamadı."
    sure = int(sinav.get("sure_dk", 20) or 20)
    mevcut = next((o for o in veri.get("sinav_oturumlari", []) if o.get("sinav_id") == sinav_id and o.get("ogrenci_id") == ogrenci_id and o.get("durum") == "basladi"), None)
    if mevcut:
        return True, mevcut
    oturum = {"oturum_id": _sayac_id("OTO", veri.get("sinav_oturumlari", []), "oturum_id"), "sinav_id": sinav_id, "ogrenci_id": ogrenci_id, "baslangic": datetime.now().isoformat(timespec="seconds"), "sure_dk": sure, "durum": "basladi"}
    veri.setdefault("sinav_oturumlari", []).append(oturum)
    veri_kaydet(veri)
    return True, oturum


def sinav_sureli_kalan_saniye(sinav_id, ogrenci_id):
    veri = creative_veri_yukle()
    oturum = next((o for o in reversed(veri.get("sinav_oturumlari", [])) if o.get("sinav_id") == sinav_id and o.get("ogrenci_id") == ogrenci_id and o.get("durum") == "basladi"), None)
    if not oturum:
        return 0
    try:
        bas = datetime.fromisoformat(oturum.get("baslangic"))
        gecen = (datetime.now() - bas).total_seconds()
        return max(0, int(int(oturum.get("sure_dk", 20)) * 60 - gecen))
    except Exception:
        return 0


def sinav_sureli_teslim_et(sinav_id, ogrenci_id, cevaplar):
    veri = creative_veri_yukle()
    kalan = sinav_sureli_kalan_saniye(sinav_id, ogrenci_id)
    ok, msg = sinav_coz(sinav_id, ogrenci_id, cevaplar)
    for o in veri.get("sinav_oturumlari", []):
        if o.get("sinav_id") == sinav_id and o.get("ogrenci_id") == ogrenci_id and o.get("durum") == "basladi":
            o["durum"] = "teslim_edildi"
            o["teslim"] = _now()
            o["sure_bitti"] = kalan <= 0
    veri_kaydet(veri)
    return ok, msg + ("\nSüre dolmuştu; otomatik teslim kabul edildi." if kalan <= 0 else "")


# ── Haftalık mail özeti ──────────────────────────────────────────────
def haftalik_mail_ozeti_olustur(kullanici_id, rol):
    rol = rol or "ogrenci"
    kullanicilar = tum_kullanicilar_getir()
    if rol == "ogrenci":
        kisi = kullanicilar["ogrenciler"].get(kullanici_id, {})
        rap = haftalik_ogrenci_raporu(kullanici_id) if 'haftalik_ogrenci_raporu' in globals() else {}
        konu = "[Online Kurs Platformu] Haftalık Öğrenci Özeti"
        icerik = f"""Merhaba {kisi.get('ad', kullanici_id)},

Bu haftaki özetiniz:
- Çalışma süresi: {rap.get('calisma_dakika', 0)} dakika
- Tamamlanan ders: {rap.get('tamamlanan_ders', 0)}
- Teslim edilen ödev: {rap.get('teslim_edilen_odev', 0)}
- Girilen sınav: {rap.get('girilen_sinav', 0)}
- Genel ortalama: {rap.get('genel_ortalama', 0)}
- XP / seviye: {xp_ozeti(kullanici_id).get('xp')} XP, {xp_ozeti(kullanici_id).get('seviye')}

Takvimden yaklaşan ders, sınav ve ödevleri kontrol etmeyi unutmayın.
"""
        return konu, icerik, kisi.get("email", "")
    if rol == "egitmen":
        kisi = kullanicilar["egitmenler"].get(kullanici_id, {})
        risk = riskli_ogrenciler_getir(kullanici_id) if 'riskli_ogrenciler_getir' in globals() else []
        konu = "[Online Kurs Platformu] Haftalık Öğretmen Özeti"
        icerik = f"""Merhaba {kisi.get('ad', kullanici_id)},

Bu haftaki öğretmen özetiniz:
- Verdiğiniz kurs sayısı: {len(egitmen_kurslari_getir(kullanici_id))}
- Riskli öğrenci sayısı: {len(risk)}
- Yaklaşan etkinlikler: {len(yaklasan_etkinlikler(7)) if 'yaklasan_etkinlikler' in globals() else 0}

Ödev teslimleri, sınav analizleri ve yoklamaları Proje Plus ekranından kontrol edebilirsiniz.
"""
        return konu, icerik, kisi.get("email", "")
    konu = "[Online Kurs Platformu] Haftalık Admin Özeti"
    ist = sistem_istatistikleri()
    icerik = f"""Admin haftalık sistem özeti:
- Öğrenci: {ist.get('toplam_ogrenci')}
- Öğretmen: {ist.get('toplam_egitmen')}
- Kurs: {ist.get('toplam_kurs')}
- Kayıt: {ist.get('toplam_kayit')}
- Destek talepleri: {len(destek_talepleri_getir()) if 'destek_talepleri_getir' in globals() else 0}
- Yaklaşan etkinlikler: {len(yaklasan_etkinlikler(7)) if 'yaklasan_etkinlikler' in globals() else 0}
"""
    return konu, icerik, ""


def haftalik_mail_ozeti_gonder(kullanici_id, rol):
    try:
        from mail_servisi import kullanici_bilgilendirme_maili_gonder, mail_ayarlari_getir
    except Exception as e:
        return False, f"Mail servisi yüklenemedi: {e}"
    konu, icerik, alici = haftalik_mail_ozeti_olustur(kullanici_id, rol)
    if not alici:
        alici = mail_ayarlari_getir().get("alici", "")
    ok, msg = kullanici_bilgilendirme_maili_gonder(alici, konu, icerik)
    veri = creative_veri_yukle()
    veri.setdefault("haftalik_mail_loglari", []).append({"kullanici_id": kullanici_id, "rol": rol, "alici": alici, "ok": ok, "mesaj": msg, "tarih": _now()})
    veri_kaydet(veri)
    return ok, msg


# ── Gelişmiş destek bileti ───────────────────────────────────────────
def destek_talebi_durum_guncelle(talep_id, durum):
    veri = creative_veri_yukle()
    for t in veri.get("destek_talepleri", []):
        if t.get("talep_id") == talep_id:
            t["durum"] = durum
            t.setdefault("gecmis", []).append({"islem": f"Durum: {durum}", "tarih": _now()})
            veri_kaydet(veri)
            return True, "Destek talebi durumu güncellendi."
    return False, "Destek talebi bulunamadı."


def destek_talebine_mesaj_ekle(talep_id, yazar_id, rol, mesaj):
    veri = creative_veri_yukle()
    for t in veri.get("destek_talepleri", []):
        if t.get("talep_id") == talep_id:
            t.setdefault("mesajlar", []).append({"yazar_id": yazar_id, "rol": rol, "mesaj": mesaj, "tarih": _now()})
            t["durum"] = "İşlemde" if rol == "admin" else "Açık"
            veri_kaydet(veri)
            return True, "Destek mesajı eklendi."
    return False, "Destek talebi bulunamadı."


def gelismis_destek_ozeti():
    rows = destek_talepleri_getir() if 'destek_talepleri_getir' in globals() else []
    say = {"Açık": 0, "İşlemde": 0, "Cevaplandı": 0, "Kapatıldı": 0}
    for r in rows:
        d = r.get("durum", "Açık")
        say[d] = say.get(d, 0) + 1
    return say


# ── Sunum demo akışı ─────────────────────────────────────────────────
def sunum_demo_akisi_detayli():
    return [
        {"adim": 1, "baslik": "Giriş ve Roller", "aciklama": "Öğrenci, öğretmen ve admin ayrı giriş yapar; her rolün paneli farklıdır."},
        {"adim": 2, "baslik": "Mail Başvurusu", "aciklama": "Öğretmen/admin başvurusu yapılır ve sistem hesabından yöneticiye gerçek mail gider."},
        {"adim": 3, "baslik": "Admin Onayı", "aciklama": "Admin başvuruyu onaylar; başvurana otomatik sonuç maili gönderilir."},
        {"adim": 4, "baslik": "Kurs ve Ders Açma", "aciklama": "Öğretmen kurs, ders günü, saat, kontenjan ve sınav tarihi belirler."},
        {"adim": 5, "baslik": "Detaylı Takvim", "aciklama": "Ay/hafta/liste görünümü; ders, sınav, ödev, iptal ve özel etkinlikler renklerle gösterilir."},
        {"adim": 6, "baslik": "QR Yoklama", "aciklama": "Öğretmen kod üretir, öğrenci kodu girince yoklama otomatik işlensin."},
        {"adim": 7, "baslik": "Ders Odası", "aciklama": "Öğrenci kurs odasında materyal, ödev, sınav, ilerleme ve sonraki adımları görür."},
        {"adim": 8, "baslik": "Süreli Sınav", "aciklama": "Quiz için süre başlatılır, kalan süre takip edilir ve bitince teslim edilir."},
        {"adim": 9, "baslik": "XP ve Liderlik", "aciklama": "Kayıt, ödev, sınav, yoklama ve kurs tamamlama XP kazandırır; liderlik tablosu oluşur."},
        {"adim": 10, "baslik": "Sertifika Doğrulama", "aciklama": "Belgeye benzersiz doğrulama kodu verilir; admin veya öğrenci kodla doğrulama yapabilir."},
        {"adim": 11, "baslik": "Haftalık Mail Özeti", "aciklama": "Öğrenci/öğretmen/admin için haftalık durum maili gönderilebilir."},
        {"adim": 12, "baslik": "Destek ve Rapor", "aciklama": "Destek biletleri durum bazlı izlenir, admin rapor ve sunum demo akışı oluşturur."},
    ]


def otomatik_demo_senaryosu():
    today = date.today()
    takvim_etkinligi_ekle("özel", "Sunum Demo: Canlı Proje Akışı", str(today), "14:00", "Mail başvurusu, QR yoklama, XP, sertifika doğrulama ve kariyer yolu gösterimi")
    takvim_etkinligi_ekle("toplantı", "Sunum Demo: Soru-Cevap", str(today + timedelta(days=1)), "11:00", "Hocaya proje özellikleri anlatılır")
    toplu_bildirim("Sunum demo akışı hazırlandı. Yaratıcı Mod ve Takvim ekranlarını kontrol edin.", "all")
    veri = creative_veri_yukle()
    veri.setdefault("sunum_demo_loglari", []).append({"tarih": _now(), "adimlar": sunum_demo_akisi_detayli()})
    veri_kaydet(veri)
    log_ekle("Yaratıcı final demo senaryosu çalıştırıldı.")
    return True, "Yaratıcı demo senaryosu oluşturuldu."


# ── Uygulama kullanım rehberi metni ─────────────────────────────────
def uygulama_detayli_kullanim_rehberi(rol="genel"):
    rol = (rol or "genel").lower()
    genel = [
        "Online Kurs Platformu; öğrenci, öğretmen ve admin rolleriyle çalışan JSON tabanlı bir eğitim yönetim sistemidir.",
        "Sağ üst profil menüsünden şifre değiştirme, tema değiştirme, belgeler ve çıkış işlemleri yapılır.",
        "Sağ alttaki asistan uygulamanın bölümlerini anlatır ve bazı ekranları komutla açar.",
        "Takvimde ders, sınav, ödev, duyuru, iptal, toplantı ve özel etkinlikler renkli gösterilir.",
        "Proje Plus/Yaratıcı Mod ekranında QR yoklama, XP, kariyer yolu, ders odası, sertifika doğrulama ve haftalık mail özeti bulunur.",
    ]
    ogr = [
        "Öğrenci; Ders Kaydı ekranından kurs arar, kontenjan uygunsa kayıt olur ve çakışma kontrolünden geçer.",
        "Derslerim ve Ders Odası bölümlerinde materyal, ders planı, ödev, sınav ve ilerleme takip edilir.",
        "Ödevler sayfasından metin veya dosya yolu ile teslim yapılır; geç teslim durumu sistemde görünür.",
        "Sınavlar sayfasından quiz çözülür; süreli sınav modunda kalan süre takip edilir ve puan otomatik hesaplanır.",
        "QR Yoklama alanına öğretmenin verdiği kod girilirse yoklama otomatik 'Geldi' olur.",
        "Not/Belge ekranında notlar, harf notu, PDF sertifika ve sertifika doğrulama kodu görüntülenir.",
        "XP, seviye, rozet, liderlik tablosu ve kariyer yolu öğrencinin gelişimini oyunlaştırır.",
    ]
    eg = [
        "Öğretmen; Kurs/Ders Aç ekranında kurs adı, kontenjan, gün, saat, kategori, seviye ve sınav tarihi girer.",
        "Ödev, quiz/sınav, materyal, ders planı ve yoklama yönetimi öğretmen panelindedir.",
        "QR Yoklama alanından ders için geçici kod üretir; öğrenciler kodu girince yoklama işlenir.",
        "Soru bankası ile sorular kaydedilir, rastgele quiz oluşturulur ve sınav sonuç analizi görüntülenir.",
        "Risk analizi düşük not, devamsızlık ve eksik ödevlere göre problemli öğrencileri listeler.",
        "Toplu mesajla kurs öğrencilerine bildirim gönderilebilir; ders iptali takvim ve bildirimlere düşer.",
    ]
    adm = [
        "Admin; kullanıcıları, öğretmen/admin başvurularını, kurs onaylarını, destek taleplerini ve sistem ayarlarını yönetir.",
        "Başvuru onay/red işlemlerinde başvurana otomatik mail gönderilebilir.",
        "Admin raporları, sistem sağlığı, yedekleme, JSON görüntüleme, dışa aktarma ve proje raporu ekranları bulunur.",
        "Sertifika doğrulama kodu sorgulanarak belgenin geçerli olup olmadığı kontrol edilir.",
        "Sunum Demo Akışı butonu hocaya gösterilecek senaryoyu takvime ve bildirimlere hazırlar.",
    ]
    if rol == "ogrenci": return genel + ogr
    if rol == "egitmen": return genel + eg
    if rol == "admin": return genel + adm
    return genel + ogr + eg + adm


try:
    v = creative_veri_yukle(); _ensure_creative_keys(v); veri_kaydet(v)
except Exception:
    pass


# ══════════════════════════════════════════════════════════════════════
#  GLOBAL HESAP TEKRARI ENGELİ
#  Aynı ID/e-posta artık öğrenci, öğretmen, admin veya başvuru olarak
#  ikinci kez açılamaz.
# ══════════════════════════════════════════════════════════════════════

def _normalize_deger(v):
    return str(v or "").strip().lower()

def _global_hesap_var_mi(veri, kullanici_id="", email=""):
    kid = _normalize_deger(kullanici_id)
    mail = _normalize_deger(email)
    adaylar = []

    admin = veri.get("admin", {})
    adaylar.append((admin.get("kullanici_adi"), admin.get("email", ""), "admin"))

    for tablo, idler, rol in [
        ("ogrenciler", ["ogrenci_id", "id"], "öğrenci"),
        ("egitmenler", ["egitmen_id", "id"], "öğretmen"),
        ("adminler", ["admin_id", "id", "kullanici_adi"], "admin"),
        ("admin_basvurular", ["admin_id", "id", "kullanici_adi"], "admin başvurusu"),
    ]:
        for kayit in veri.get(tablo, []):
            for idkey in idler:
                adaylar.append((kayit.get(idkey), kayit.get("email", ""), rol))

    for mevcut_id, mevcut_mail, rol in adaylar:
        if kid and _normalize_deger(mevcut_id) == kid:
            return True, f"Bu kullanıcı ID zaten {rol} olarak kayıtlı: {mevcut_id}"
        if mail and mevcut_mail and _normalize_deger(mevcut_mail) == mail:
            return True, f"Bu e-posta zaten {rol} hesabında kullanılıyor: {mevcut_mail}"
    return False, ""

_orijinal_ogrenci_ekle_global = ogrenci_ekle
_orijinal_egitmen_ekle_global = egitmen_ekle
_orijinal_admin_basvuru_ekle_global = admin_basvuru_ekle

def ogrenci_ekle(ogrenci_id, ad, email, sifre):
    veri = veri_yukle()
    var, msg = _global_hesap_var_mi(veri, ogrenci_id, email)
    if var:
        return False, msg
    return _orijinal_ogrenci_ekle_global(ogrenci_id, ad, email, sifre)

def egitmen_ekle(egitmen_id, ad, uzmanlik, email, sifre):
    veri = veri_yukle()
    var, msg = _global_hesap_var_mi(veri, egitmen_id, email)
    if var:
        return False, msg
    return _orijinal_egitmen_ekle_global(egitmen_id, ad, uzmanlik, email, sifre)

def admin_basvuru_ekle(admin_id, ad, email, sifre, aciklama="Admin yetkisi başvurusu"):
    veri = veri_yukle()
    var, msg = _global_hesap_var_mi(veri, admin_id, email)
    if var:
        return False, msg
    return _orijinal_admin_basvuru_ekle_global(admin_id, ad, email, sifre, aciklama)


# FINAL DEMO HESAP PATCH: öğrencilerde hira / 123 hesabı her zaman bulunsun.
_ORIG_VERI_YUKLE_FINAL_A = veri_yukle

def veri_yukle():
    veri = _ORIG_VERI_YUKLE_FINAL_A()
    try:
        degisti = False
        # Eski demo hesap varsa yeni kullanıcı adına taşı.
        for o in veri.get("ogrenciler", []):
            if o.get("ogrenci_id") == "a" or o.get("id") == "a" or o.get("email") == "a@kurs.com":
                eski_id = o.get("ogrenci_id") or o.get("id")
                o.update({
                    "ogrenci_id": "hira", "id": "hira", "ad": "Hira Yağmur",
                    "email": "hira.yagmur@ogrenci.local", "sifre": "123", "rol": "ogrenci",
                    "durum": "aktif", "avatar": "🎓"
                })
                if eski_id == "a":
                    for k in veri.get("kurslar", []):
                        k["kayitli_ogrenciler"] = ["hira" if x == "a" else x for x in k.get("kayitli_ogrenciler", [])]
                    for tablo in ["kayitlar", "notlar", "yorumlar"]:
                        for item in veri.get(tablo, []):
                            if item.get("ogrenci_id") == "a":
                                item["ogrenci_id"] = "hira"
                    for item in veri.get("destek_talepleri", []):
                        if item.get("kullanici_id") == "a":
                            item["kullanici_id"] = "hira"
                degisti = True
        var_mi = any(o.get("ogrenci_id") == "hira" or o.get("id") == "hira" or o.get("email") == "hira.yagmur@ogrenci.local" for o in veri.get("ogrenciler", []))
        if not var_mi:
            veri.setdefault("ogrenciler", []).append({
                "ogrenci_id": "hira", "id": "hira", "ad": "Hira Yağmur",
                "email": "hira.yagmur@ogrenci.local", "sifre": "123", "rol": "ogrenci",
                "durum": "aktif", "ilerleme": {}, "avatar": "🎓"
            })
            degisti = True
        if veri.get("admin", {}).get("sifre") != "123":
            veri.setdefault("admin", {})["sifre"] = "123"
            degisti = True
        veri.setdefault("sistem_ayarlari", {})["yapimci"] = "E.Hira YAĞMUR"
        if degisti:
            veri_kaydet(veri)
    except Exception:
        pass
    return veri
