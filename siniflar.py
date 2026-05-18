# coding: utf-8
"""siniflar.py - Online Kurs Platformu için ana nesne sınıfları."""

class Platform:
    """Online kurs platformu ana sınıfı."""
    def __init__(self, platform_id, platform_adi, url, aciklama=None):
        self.platform_id = platform_id
        self.platform_adi = platform_adi
        self.url = url
        self.aciklama = aciklama
        self.kurslar = []
        self.egitmenler = []

    def platform_bilgisi(self):
        return f"{self.platform_adi} ({self.url})"

    def kurs_ekle(self, kurs):
        if isinstance(kurs, Kurs):
            self.kurslar.append(kurs)
            return True
        return False

class Kullanici:
    """Öğrenci, eğitmen ve admin için ortak kullanıcı sınıfı."""
    def __init__(self, kullanici_id, ad, soyad, email, sifre):
        self.kullanici_id = kullanici_id
        self.ad = ad
        self.soyad = soyad
        self.email = email
        self.__sifre = sifre
        self.aktif_mi = True

    def tam_ad(self):
        return f"{self.ad} {self.soyad}"

    def giris_yap(self, email, sifre):
        return self.email == email and self.__sifre == sifre

    def profil_bilgisi(self):
        return {"ID": self.kullanici_id, "Ad": self.ad, "Soyad": self.soyad, "E-posta": self.email}

class Ogrenci(Kullanici):
    def __init__(self, kullanici_id, ad, soyad, email, sifre, ogrenci_no):
        super().__init__(kullanici_id, ad, soyad, email, sifre)
        self.ogrenci_no = ogrenci_no
        self.kayitli_kurslar = {}
        self.rozetler = []

    def kurs_listesi(self):
        return self.kayitli_kurslar

    def kursa_kaydol(self, kurs_id):
        if kurs_id not in self.kayitli_kurslar:
            self.kayitli_kurslar[kurs_id] = 0
            return True
        return False

    def ilerleme_guncelle(self, kurs_id, yuzde):
        if kurs_id in self.kayitli_kurslar:
            self.kayitli_kurslar[kurs_id] = max(0, min(100, int(yuzde)))
            return True
        return False

    def profil_bilgisi(self):
        bilgi = super().profil_bilgisi()
        bilgi["Öğrenci No"] = self.ogrenci_no
        bilgi["Kurs Sayısı"] = len(self.kayitli_kurslar)
        return bilgi

class Egitmen(Kullanici):
    def __init__(self, kullanici_id, ad, soyad, email, sifre, uzmanlik):
        super().__init__(kullanici_id, ad, soyad, email, sifre)
        self.uzmanlik = uzmanlik
        self.verdigi_kurslar = []

    def kurs_olustur(self, kurs_id, kurs_adi, kontenjan):
        yeni_kurs = Kurs(kurs_id, kurs_adi, self, kontenjan)
        self.verdigi_kurslar.append(yeni_kurs)
        return yeni_kurs

    def profil_bilgisi(self):
        bilgi = super().profil_bilgisi()
        bilgi["Uzmanlık"] = self.uzmanlik
        bilgi["Kurs Sayısı"] = len(self.verdigi_kurslar)
        return bilgi

class Admin(Kullanici):
    def __init__(self, kullanici_id, ad, soyad, email, sifre):
        super().__init__(kullanici_id, ad, soyad, email, sifre)
        self.yetkiler = ["kullanici_yonetimi", "kurs_yonetimi", "rapor", "yedekleme"]

    def kullanici_onayla(self, kullanici):
        kullanici.aktif_mi = True
        return True

class Kurs:
    def __init__(self, kurs_id, kurs_adi, egitmen, kontenjan, platform_adi="Platform Belirtilmemiş"):
        self.kurs_id = kurs_id
        self.kurs_adi = kurs_adi
        self.egitmen = egitmen
        self.kontenjan = kontenjan
        self.ogrenciler = []
        self.dersler = []
        self.materyaller = []
        self.yorumlar = []
        self.platform_adi = platform_adi

    def kurs_bilgisi(self):
        return f"{self.kurs_adi} (Eğitmen: {self.egitmen.tam_ad()})"

    def ogrenci_kaydet(self, ogrenci):
        if isinstance(ogrenci, Ogrenci) and len(self.ogrenciler) < self.kontenjan and ogrenci not in self.ogrenciler:
            self.ogrenciler.append(ogrenci)
            ogrenci.kursa_kaydol(self.kurs_id)
            return True
        return False

    def ders_ekle(self, ders):
        if isinstance(ders, Ders):
            self.dersler.append(ders)
            return True
        return False

    def kalan_kontenjan(self):
        return self.kontenjan - len(self.ogrenciler)

class Ders:
    def __init__(self, ders_id, ders_adi, icerik, sure, gunler=None, saat=""):
        self.ders_id = ders_id
        self.ders_adi = ders_adi
        self.icerik = icerik
        self.sure = sure
        self.gunler = gunler or []
        self.saat = saat

    def ders_bilgisi(self):
        return f"{self.ders_adi} ({self.sure} dk.)"

class TakvimEtkinligi:
    def __init__(self, tur, baslik, tarih=None, gunler=None, saat=""):
        self.tur = tur
        self.baslik = baslik
        self.tarih = tarih
        self.gunler = gunler or []
        self.saat = saat

class Sertifika:
    def __init__(self, belge_no, ogrenci_ad, kurs_adi, not_degeri, tarih):
        self.belge_no = belge_no
        self.ogrenci_ad = ogrenci_ad
        self.kurs_adi = kurs_adi
        self.not_degeri = not_degeri
        self.tarih = tarih

class Odev:
    def __init__(self, odev_id, kurs_id, baslik, aciklama, son_tarih):
        self.odev_id = odev_id
        self.kurs_id = kurs_id
        self.baslik = baslik
        self.aciklama = aciklama
        self.son_tarih = son_tarih

class Sinav:
    def __init__(self, sinav_id, kurs_id, baslik, tarih, sorular=None):
        self.sinav_id = sinav_id
        self.kurs_id = kurs_id
        self.baslik = baslik
        self.tarih = tarih
        self.sorular = sorular or []

class Duyuru:
    def __init__(self, mesaj, yazar="admin"):
        self.mesaj = mesaj
        self.yazar = yazar
