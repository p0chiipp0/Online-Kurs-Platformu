# coding: utf-8
from mail_servisi import test_maili_gonder, mail_ayarlari_getir

print("Mail ayarları:")
a = mail_ayarlari_getir()
print("Gönderen:", a["gonderen"])
print("Alıcı   :", a["alici"])
print("SMTP    :", a["smtp_sunucu"], a["smtp_port"])

ok, msg = test_maili_gonder()
print("Sonuç:", "BAŞARILI" if ok else "HATA")
print(msg)
