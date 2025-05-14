# -*- coding: utf-8 -*-
"""Konsol arayüzü (CLI)."""
from datetime import datetime

from appointment import Appointment
from clinic_manager import ClinicManager
from patient import Patient


def _tarih(prompt):
    while True:
        s = input(f"{prompt} (YYYY-MM-DD): ")
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print("❌ Tarih formatı hatalı!")


def _tarih_saat(prompt):
    while True:
        s = input(f"{prompt} (YYYY-MM-DD HH:MM): ")
        try:
            datetime.strptime(s, "%Y-%m-%d %H:%M")
            return s
        except ValueError:
            print("❌ Tarih-saat formatı hatalı!")


def main():
    cm = ClinicManager()

    menu = """
╔═══════════════════════════════╗
║ 1-Hasta Ekle                  ║
║ 2-Randevu Oluştur             ║
║ 3-Randevu Listele             ║
║ 4-Ödeme Hesapla               ║
║ 0-Çıkış                       ║
╚═══════════════════════════════╝
"""
    while True:
        print(menu)
        sec = input("Seçim: ").strip()
        try:
            if sec == "1":
                p = Patient(
                    input("Ad: "),
                    input("Soyad: "),
                    input("TC: "),
                    _tarih("Doğum Tarihi"),
                    input("Telefon: "),
                    input("E-posta: "),
                    input("Not (ops.): "),
                )
                cm.add_patient(p)
                print("✅ Hasta kaydedildi.")

            elif sec == "2":
                tc = input("Hasta TC: ")
                r = Appointment(
                    tc,
                    _tarih_saat("Randevu Tarih-Saat"),
                    input("Diş Hekimi Adı: "),
                    input("İşlem Açıklaması: "),
                    float(input("İşlem Ücreti (KDV hariç): ")),
                )
                cm.add_appointment(r)
                print("✅ Randevu oluşturuldu.")

            elif sec == "3":
                print("Tümü için ENTER bırak.")
                start = input("Başlangıç (YYYY-MM-DD): ").strip() or None
                end = input("Bitiş (YYYY-MM-DD): ").strip() or None
                for a in cm.list_appointments(start, end):
                    print(a)
                print("📋 Liste sonu.")

            elif sec == "4":
                tutar = float(input("Ücret (KDV hariç): "))
                print(
                    f"KDV dahil toplam: {cm.kdv_haric_to_dahil(tutar):.2f} ₺"
                )

            elif sec == "0":
                print("🔒 Kapatılıyor, yedek alınıyor…")
                cm.backup()
                break
            else:
                print("❗ Hatalı seçim")
        except Exception as e:
            print(f"💥 Hata: {e}")


if __name__ == "__main__":
    main()

