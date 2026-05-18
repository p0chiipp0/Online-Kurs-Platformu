import veritabani as db
from siniflar import Platform
import sys

def main():
    db.veri_yukle()
    try:
        from gui import uygulamayi_baslat
        uygulamayi_baslat()
    except ImportError as e:
        print(f"GUI yuklenemedi ({e}). Konsol moduna geciliyor...")
        # Platform sınıfını doğru argümanlarla başlatıyoruz
        platform = Platform("P01", "Hextech Akademi", "http://localhost")
        print(f"{platform.platform_adi} Konsol Modu Aktif.")

if __name__ == "__main__":
    main()