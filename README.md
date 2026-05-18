# Hextech Akademi — Kod Açıklaması

## Genel Bakış

**Hextech Akademi**, Python ve CustomTkinter ile geliştirilmiş rol tabanlı bir online kurs platformudur. Projede üç temel kullanıcı rolü vardır:

- **Öğrenci**
- **Öğretmen**
- **Admin**

Uygulama; kurs kaydı, ders odası, materyal yönetimi, ödev/sınav sistemi, yorumlar, forum, mesajlaşma, destek talepleri, duyuru sistemi ve admin yönetim ekranlarını tek masaüstü uygulamasında toplar.

Bu dosya, projenin kod yapısını, dosyaların görevlerini, sınıfları, metodları ve veri akışını açıklamak için hazırlanmıştır.

---

## Dosya Yapısı

| Dosya / Klasör | Sorumluluk |
|---|---|
| `main.py` | Uygulamayı başlatan ana dosya |
| `gui.py` | CustomTkinter arayüzü, ekranlar, paneller ve kullanıcı etkileşimleri |
| `veritabani.py` | JSON veri okuma/yazma, kurs, kullanıcı, materyal, mesaj, destek ve admin işlemleri |
| `siniflar.py` | Projedeki temel OOP sınıfları ve veri modelleri |
| `mail_servisi.py` | Mail gönderme mantığını ayrı tutan servis dosyası |
| `platform_verisi.json` | Kurslar, kullanıcılar, materyaller, ödevler, sınavlar, mesajlar ve destek taleplerinin tutulduğu ana veri dosyası |
| `assets/` | Logo ve görsel dosyalar |
| `KULLANIM_KILAVUZU.txt` | Hocaya yönelik kullanım açıklaması |

---

## 1. `main.py` — Başlatıcı Dosya

`main.py`, uygulamanın başlangıç noktasıdır. Bu dosyanın temel görevi, arayüz dosyasındaki başlatma fonksiyonunu çağırmaktır.

### Temel Sorumluluklar

- Uygulamayı başlatır.
- Ana pencere oluşturma işlemini `gui.py` tarafına bırakır.
- Kodun tek bir yerden çalıştırılmasını sağlar.

### Örnek Mantık

```python
from gui import uygulamayi_baslat

if __name__ == "__main__":
    uygulamayi_baslat()
```

Bu yapı sayesinde proje doğrudan `python main.py` komutuyla çalıştırılabilir.

---

## 2. `gui.py` — Arayüz ve Panel Yönetimi

`gui.py`, projenin en büyük ve en önemli dosyalarından biridir. Kullanıcının gördüğü bütün ekranlar burada oluşturulur.

### Genel Sorumluluklar

| Bölüm | Açıklama |
|---|---|
| Tema sabitleri | Renkler, yazı tipleri, buton stilleri |
| Giriş ekranı | Kullanıcı girişi ve hesap başvuruları |
| Öğrenci paneli | Ders kaydı, ders odası, materyaller, ödevler, sınavlar |
| Öğretmen paneli | Kurs açma, materyal ekleme, ödev/sınav yönetimi |
| Admin paneli | Kullanıcı, kurs, materyal, forum, destek, duyuru yönetimi |
| Dialog pencereleri | Başvuru, materyal ekleme, kurs kapatma gibi ek pencereler |
| Bildirimler | Kullanıcıya işlem sonucu gösteren mesajlar |

---

## 2.1 `App` Sınıfı

`App`, uygulamanın ana pencere sınıfıdır.

### Özellikler

- CustomTkinter ana penceresini oluşturur.
- Pencere başlığını ayarlar.
- Uygulama logosunu pencereye ve görev çubuğuna ekler.
- Giriş ekranını açar.
- Başarılı girişten sonra kullanıcı rolüne göre doğru paneli gösterir.

### Önemli Metodlar

| Metod | Açıklama |
|---|---|
| `show_login()` | Giriş ekranını açar |
| `login_success(user, role)` | Giriş başarılı olunca kullanıcıyı rolüne göre panele yönlendirir |
| `show_panel()` | Öğrenci, öğretmen veya admin panelini gösterir |

### Kod Mantığı

Kullanıcı giriş yaptığında `role` bilgisi kontrol edilir:

- `ogrenci` ise öğrenci paneli açılır.
- `egitmen` ise öğretmen paneli açılır.
- `admin` ise admin paneli açılır.

Bu yapı, projede rol bazlı yetkilendirmenin temelidir.

---

## 2.2 `LoginScreen` Sınıfı

`LoginScreen`, uygulamanın giriş ekranıdır.

### Görevleri

- Kullanıcıdan e-posta ve şifre alır.
- Giriş bilgilerini `veritabani.py` üzerinden kontrol eder.
- Yanlış girişte hata mesajı gösterir.
- Öğrenci kayıt ekranına yönlendirme yapar.
- Öğretmen/Admin başvuru ekranını açar.

### Giriş Akışı

1. Kullanıcı e-posta ve şifre girer.
2. `veritabani.py` içindeki doğrulama fonksiyonu çağrılır.
3. Kullanıcı bulunursa rolü alınır.
4. Rol bilgisine göre ilgili panel açılır.
5. Hatalı girişte kullanıcı uyarılır.

### Neden Ayrı Sınıf?

Giriş ekranı ayrı sınıf olarak tasarlandığı için ana pencere kodu karışmaz. Bu sayede arayüz daha okunabilir ve yönetilebilir olur.

---

## 2.3 `ApplicationDialog` Sınıfı

Öğretmen veya admin olmak isteyen kullanıcıların başvuru yaptığı penceredir.

### Görevleri

- Başvuru rolünü seçtirir.
- Kullanıcıdan ad, e-posta, şifre ve açıklama gibi bilgiler alır.
- Başvuruyu JSON verisine kaydeder.
- Admin panelinde onaylanabilecek hale getirir.

### İş Akışı

1. Kullanıcı başvuru formunu doldurur.
2. Form boş alan kontrolünden geçer.
3. Başvuru `platform_verisi.json` içine kaydedilir.
4. Admin panelinde bekleyen başvuru olarak görünür.

---

## 2.4 `OgrenciPanel` Sınıfı

Öğrencinin uygulama içinde kullandığı ana paneldir.

### Öğrencinin Yapabildiği İşlemler

| İşlem | Açıklama |
|---|---|
| Dersleri görüntüleme | Kayıtlı olduğu dersleri listeler |
| Ders kaydı | Açık kurslara kayıt olabilir |
| Derse Git | Ders odasına girer |
| Materyal açma | Kayıtlı derslere ait materyalleri açar |
| Ödevleri görme | Ödev açıklaması ve teslim tarihlerini takip eder |
| Sınavları görme | Yaklaşan sınavları takip eder |
| Yorum yazma | Kayıtlı olduğu derslere yorum bırakabilir |
| Forum | Konu açabilir veya cevap yazabilir |
| Mesajlaşma | Öğretmenlerle mesajlaşabilir |
| Destek talebi | Sorun bildirebilir |
| Bildirim | Sistem bildirimlerini takip eder |

### Panel Mantığı

Sol menü üzerinden farklı sayfalara geçilir. Her sayfa kendi fonksiyonu ile oluşturulur. Örneğin:

- `derslerim_page()`
- `ders_kaydi_page()`
- `materyaller_page()`
- `odevler_page()`
- `sinavlar_page()`
- `forum_page()`
- `mesajlar_page()`
- `destek_page()`

Bu yapı sayesinde öğrenci paneli modüler hale getirilmiştir.

---

## 2.5 `EgitmenPanel` Sınıfı

Öğretmenin kendi kurslarını yönetmesini sağlayan paneldir.

### Öğretmenin Yapabildiği İşlemler

| İşlem | Açıklama |
|---|---|
| Kurs açma | Yeni ders/kurs oluşturur |
| Kursları görüntüleme | Kendi açtığı kursları listeler |
| Materyal ekleme | Derslere materyal bağlantısı ekler |
| Ödev oluşturma | Ders için ödev tanımlar |
| Sınav oluşturma | Ders için sınav tarihi ve açıklaması ekler |
| Yorumları inceleme | Öğrencilerin ders yorumlarını görür |
| Mesajlaşma | Öğrencilerle iletişim kurar |
| Forum | Forum konularını takip eder |
| Destek | Admin tarafına destek talebi iletebilir |

### Önemli Nokta

Öğretmen panelinde gereksiz rozet sistemi kaldırılmıştır. Bu sayede panel daha ders odaklı ve sade hale getirilmiştir.

---

## 2.6 `AdminPanel` Sınıfı

Admin paneli, sistemin yönetim merkezidir. Admin, platformdaki kritik işlemleri kontrol eder.

### Adminin Yapabildiği İşlemler

| Alan | Açıklama |
|---|---|
| Kullanıcı yönetimi | Öğrenci, öğretmen ve adminleri listeler |
| Başvuru yönetimi | Öğretmen/admin başvurularını onaylar veya reddeder |
| Kurs yönetimi | Kursları görüntüler, kapatır veya kaldırır |
| Materyal yönetimi | Materyalleri inceler ve silebilir |
| Ödev yönetimi | Ödevleri kontrol eder |
| Sınav yönetimi | Sınav kayıtlarını kontrol eder |
| Yorum yönetimi | Uygunsuz yorumları silebilir |
| Forum yönetimi | Konuları ve mesajları yönetebilir |
| Mesaj yönetimi | Sistem mesajlarını inceleyebilir |
| Destek talepleri | Destek taleplerini cevaplar |
| Duyuru sistemi | Sistem genelinde duyuru oluşturur |

### Admin Kurs Kapatma Mantığı

Admin bir kursu kapattığında:

1. Kurs ID’si bulunur.
2. Kursun `kapali` veya `durum` alanı güncellenir.
3. Kapatma nedeni kaydedilir.
4. Kapatılma tarihi kaydedilir.
5. Kursun materyaller listesi temizlenir.
6. Öğretmene ve öğrencilere bildirim gönderilir.
7. Admin işlem logu oluşturulur.

Bu mantık sayesinde kapatılan kursun materyalleri sistemde kalmaz.

---

## 2.7 `CourseRoomDialog` Sınıfı

Derse Git butonuna basıldığında açılan ders odası penceresidir.

### Ders Odasında Gösterilenler

- Kurs adı
- Kurs açıklaması
- Öğretmen bilgisi
- Ders günü ve saati
- Sınav tarihi
- Materyaller
- Katılan öğrenciler
- Yorum alanı

### Materyal Açma Mantığı

Her materyal butonu, kendi linkini parametre olarak alır.

Bu hata özellikle düzeltilmiştir:

> Önceden materyal butonlarından biri başka materyali açabiliyordu.  
> Artık her buton kendi linkini sabit olarak aldığı için sadece ilgili materyal açılır.

### Örnek Mantık

```python
lambda link=materyal_linki: open_material_link(link)
```

Bu yapı döngü içinde yanlış link tutulmasını engeller.

---

## 2.8 `open_material_link()` Fonksiyonu

Materyal bağlantılarını güvenli açmak için kullanılan yardımcı fonksiyondur.

### Çalışma Mantığı

| Link Türü | Davranış |
|---|---|
| `http://` veya `https://` | Tarayıcıda açılır |
| `file://` | Yerel dosya olarak açılır |
| Normal dosya yolu | Proje klasörüne göre aranır |
| Boş link | Kullanıcı uyarılır |
| Hatalı link | Hata mesajı gösterilir |

Bu fonksiyon sayesinde materyal açma işlemi tek merkezden yönetilir.

---

## 3. `veritabani.py` — Veri Katmanı

`veritabani.py`, projenin backend mantığına en yakın dosyasıdır. Arayüzden gelen işlemler bu dosya üzerinden JSON verisine yazılır veya JSON verisinden okunur.

### Temel Görevleri

- Veriyi JSON dosyasından okumak
- Veriyi JSON dosyasına kaydetmek
- Kullanıcı doğrulamak
- Kurs oluşturmak
- Kursa kayıt yapmak
- Materyal eklemek
- Ödev ve sınav eklemek
- Mesaj kaydetmek
- Destek talebi oluşturmak
- Admin işlemlerini uygulamak

---

## 3.1 Veri Okuma/Yazma Fonksiyonları

| Fonksiyon | Açıklama |
|---|---|
| `veri_yukle()` | `platform_verisi.json` dosyasını okur |
| `veri_kaydet(veri)` | Güncel veriyi JSON dosyasına yazar |
| `log_ekle(islem)` | Admin veya sistem işlemini log kaydına ekler |

### Veri Akışı

```text
GUI ekranı
   ↓
veritabani.py fonksiyonu
   ↓
platform_verisi.json
   ↓
Tekrar GUI ekranında güncel veri
```

---

## 3.2 Kullanıcı İşlemleri

Kullanıcı işlemleri JSON içindeki kullanıcı listeleri üzerinden yapılır.

### Desteklenen Roller

- `ogrenci`
- `egitmen`
- `admin`

### Kullanıcı İşlem Mantığı

- E-posta ve şifre kontrol edilir.
- Role göre panel açılır.
- Yeni öğrenci hesabı oluşturulabilir.
- Öğretmen ve admin başvuruları onay sistemiyle ilerler.

---

## 3.3 Kurs İşlemleri

Kurslar JSON içinde liste halinde tutulur.

### Kurs Alanları

| Alan | Açıklama |
|---|---|
| `kurs_id` | Benzersiz kurs kimliği |
| `kurs_adi` | Kurs adı |
| `egitmen_id` | Kursu açan öğretmen |
| `kontenjan` | Maksimum öğrenci sayısı |
| `kayitli_ogrenciler` | Derse kayıtlı öğrenciler |
| `materyaller` | Kursa ait materyaller |
| `kapali` | Kursun kapalı olup olmadığı |
| `durum` | Açık / kapalı durumu |

### Kurs Kapatma

Admin kurs kapattığında sadece kurs kapalı görünmez; aynı zamanda materyalleri de temizlenir. Bu, sistemde gereksiz materyal kalmasını engeller.

---

## 3.4 Materyal İşlemleri

Materyaller genellikle kurs nesnesinin içinde tutulur.

### Materyal Alanları

| Alan | Açıklama |
|---|---|
| `baslik` | Materyal adı |
| `link` | Materyal bağlantısı |
| `tarih` | Eklenme tarihi |
| `egitmen_id` | Ekleyen öğretmen |

### Materyal Eklenince

- Kursun materyaller listesine eklenir.
- Öğrencilere bildirim gönderilebilir.
- Ders odasında görünür hale gelir.

### Materyal Silinince

- İlgili kurstan kaldırılır.
- Öğrencinin ders odasında görünmez.

---

## 3.5 Destek, Forum ve Mesaj İşlemleri

`veritabani.py`, platformdaki iletişim sistemlerini de yönetir.

### Destek

- Kullanıcı destek talebi açar.
- Admin talebe cevap verir.
- Talep tamamlandı olarak işaretlenebilir.

### Forum

- Konu açılır.
- Cevap yazılır.
- Admin uygunsuz içerikleri silebilir.

### Mesajlaşma

- Öğrenci ve öğretmen mesajlaşabilir.
- Mesajlar JSON içinde saklanır.
- Konuşma geçmişi tekrar görüntülenebilir.

---

## 4. `siniflar.py` — OOP Veri Modelleri

`siniflar.py`, hocanın istediği nesne tabanlı yapı için temel sınıfları içerir.

### Örnek Sınıflar

| Sınıf | Görevi |
|---|---|
| `Kurs` | Kurs bilgilerini temsil eder |
| `Ogrenci` | Öğrenci bilgilerini temsil eder |
| `Egitmen` | Öğretmen bilgilerini temsil eder |
| `Admin` | Admin kullanıcı mantığını temsil eder |
| `Materyal` | Ders materyali bilgisini temsil eder |
| `Odev` | Ödev bilgisini temsil eder |
| `Sinav` | Sınav bilgisini temsil eder |

---

## 4.1 `Kurs` Sınıfı

Bir kursu temsil eder.

### Özellikler

- `kurs_id`
- `kurs_adi`
- `egitmen`
- `kontenjan`
- `kayitli_ogrenciler`
- `materyaller`

### Metodlar

| Metod | Açıklama |
|---|---|
| `ogrenci_kaydet()` | Öğrenciyi kursa ekler |
| `kontenjan_dolu_mu()` | Kontenjan durumunu kontrol eder |
| `materyal_ekle()` | Kursa materyal ekler |
| `kurs_bilgisi()` | Kurs özetini döndürür |

Bu sınıf, hocanın proje listesinde belirttiği `Kurs` sınıfı gereksinimini karşılar.

---

## 4.2 `Ogrenci` Sınıfı

Öğrenci kullanıcısını temsil eder.

### Özellikler

- `ogrenci_id`
- `ad`
- `email`
- `kayitli_kurslar`

### Metodlar

| Metod | Açıklama |
|---|---|
| `kurs_listesi()` | Öğrencinin kayıtlı kurslarını döndürür |
| `kursa_kayit_ol()` | Öğrenciyi kursa kaydeder |
| `yorum_yaz()` | Ders için yorum oluşturur |

Bu sınıf, hocanın istediği `Öğrenci` sınıfı mantığını karşılar.

---

## 4.3 `Egitmen` Sınıfı

Öğretmen kullanıcısını temsil eder.

### Özellikler

- `ad`
- `uzmanlik`
- `kurslar`

### Metodlar

| Metod | Açıklama |
|---|---|
| `kurs_olustur()` | Yeni kurs oluşturur |
| `materyal_ekle()` | Derse materyal ekler |
| `odev_olustur()` | Ders için ödev oluşturur |
| `sinav_olustur()` | Ders için sınav oluşturur |

---

## 5. `mail_servisi.py` — Mail Servisi

Bu dosya e-posta gönderme mantığını ayrı tutmak için kullanılır.

### Amaç

Ana arayüz kodunu kalabalıklaştırmadan mail işlemlerini ayrı yönetmek.

### Kullanım Senaryosu

- Yeni başvuru bildirimi
- Şifre sıfırlama
- Sistem duyurusu
- Destek cevabı
- Materyal eklendi bildirimi

Gerçek SMTP bilgileri girildiğinde bu servis mail göndermeye uygun yapıdadır.

---

## 6. `platform_verisi.json` — Veri Dosyası

Uygulamanın ana veri kaynağıdır.

### İçinde Tutulan Veriler

| Veri | Açıklama |
|---|---|
| `ogrenciler` | Öğrenci hesapları |
| `egitmenler` | Öğretmen hesapları |
| `adminler` | Admin hesapları |
| `kurslar` | Kurs listesi |
| `basvurular` | Öğretmen/admin başvuruları |
| `odevler` | Ödev kayıtları |
| `sinavlar` | Sınav kayıtları |
| `yorumlar` | Ders yorumları |
| `forum` | Forum konuları |
| `mesajlar` | Kullanıcı mesajları |
| `destek` | Destek talepleri |
| `duyurular` | Sistem duyuruları |
| `bildirimler` | Kullanıcı bildirimleri |
| `loglar` | Admin işlem kayıtları |

---

## 7. Veri Akışı

```text
Kullanıcı butona basar
        ↓
gui.py ilgili metodu çalıştırır
        ↓
veritabani.py veri işlemini yapar
        ↓
platform_verisi.json güncellenir
        ↓
gui.py ekranı yeniler
```

Örnek: Öğretmen materyal eklediğinde

```text
Materyal Ekle butonu
        ↓
EgitmenPanel materyal formu
        ↓
veritabani.py materyal_ekle()
        ↓
kurs["materyaller"] listesi güncellenir
        ↓
platform_verisi.json kaydedilir
        ↓
öğrenci ders odasında materyali görür
```

---

## 8. Rol Bazlı Yetkilendirme

| İşlem | Öğrenci | Öğretmen | Admin |
|---|---|---|---|
| Derslere kayıt olma | ✓ | ✗ | ✗ |
| Ders materyali açma | ✓ | ✓ | ✓ |
| Kurs açma | ✗ | ✓ | ✗ |
| Materyal ekleme | ✗ | ✓ | ✓ |
| Ödev/sınav oluşturma | ✗ | ✓ | ✓ |
| Kurs kapatma | ✗ | ✗ | ✓ |
| Kullanıcı yönetimi | ✗ | ✗ | ✓ |
| Başvuru onayı | ✗ | ✗ | ✓ |
| Forum kullanımı | ✓ | ✓ | ✓ |
| Destek talebi | ✓ | ✓ | ✓ |
| Duyuru oluşturma | ✗ | ✗ | ✓ |

---

## 9. Önemli Kod Düzeltmeleri

### 9.1 Rozet Sistemi Kaldırma

Admin ve öğretmen tarafındaki rozet sistemi gereksiz olduğu için kaldırılmıştır.

Amaç:

- Admin panelini sadeleştirmek
- Öğretmen panelini ders yönetimine odaklamak
- Gereksiz menü kalabalığını azaltmak

---

### 9.2 Kurs Kapanınca Materyal Temizleme

Admin kurs kapattığında artık o kursa ait materyaller de temizlenir.

Mantık:

```python
kurs["materyaller"] = []
kurs["materyaller_kaldirildi"] = True
```

Bu sayede kapatılmış bir derse ait eski materyaller sistemde kalmaz.

---

### 9.3 Materyal Linkinin Yanlış Açılmasını Engelleme

Döngü içinde buton oluştururken her butona kendi linki sabitlenmiştir.

Doğru mantık:

```python
lambda link=materyal_linki: open_material_link(link)
```

Bu yöntem, Python'daki geç bağlama probleminden kaynaklanabilecek yanlış materyal açılmasını önler.

---

### 9.4 Logo ve Görev Çubuğu Düzeltmesi

Logo için hem PNG hem ICO desteği eklenmiştir.

- PNG: Uygulama içinde gösterim
- ICO: Windows görev çubuğu ve pencere ikonu

---

## 10. Hocaya Teknik Açıklama İçin Kısa Özet

Bu proje; Python, CustomTkinter ve JSON kullanılarak yapılmış rol tabanlı bir online kurs platformudur. Arayüz tarafı `gui.py`, veri işlemleri `veritabani.py`, OOP sınıfları ise `siniflar.py` içinde tutulmuştur. Öğrenci, öğretmen ve admin rolleri birbirinden ayrılmıştır. Her rolün kendi yetkileri vardır. Veriler JSON dosyasında saklanır ve program kapanıp açılsa bile korunur.

Proje, hocanın istediği `Kurs`, `Egitmen` ve `Ogrenci` sınıf mantığını karşılar. Bunun yanında materyal, ödev, sınav, yorum, forum, mesaj, destek, duyuru ve admin yönetimi gibi ek özelliklerle daha kapsamlı hale getirilmiştir.
