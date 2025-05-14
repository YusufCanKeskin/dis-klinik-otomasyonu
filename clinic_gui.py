#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
clinic_gui.py • Tkinter arayüzü (açık mavi & beyaz tema)
v3 – ücret alanı prosedürle çakışmıyor + işlem seçince ücret otomatik doluyor
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from patient import Patient
from appointment import Appointment
from clinic_manager import ClinicManager


# ----------------------------- Tema renkleri ----------------------------------
PRIMARY = "#cfe9ff"   # açık mavi
WHITE   = "#ffffff"


# İşlem ➜ varsayılan ücret eşlemesi (₺, KDV hariç)
PROCEDURE_FEES = {
    "Dolgu": 800,
    "Diş Çekimi": 600,
    "Kanal Tedavisi": 1500,
    "Diş Taşı Temizliği": 400,
    "Kontrol": 200,
}


def iso_date(date_str, time_str="00:00"):
    """YYYY-MM-DD (+ HH:MM) birleşimini ISO döndürür."""
    return f"{date_str.strip()} {time_str.strip()}"


def alert(title, msg, kind="info"):
    mapping = {"info": "showinfo", "warning": "showwarning", "error": "showerror"}
    getattr(messagebox, mapping.get(kind, "showinfo"))(title, msg)


# ----------------------------- Ana uygulama -----------------------------------
class ClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diş Klinik Otomasyonu")
        self.geometry("820x480")
        self.configure(bg=PRIMARY)
        self.cm = ClinicManager()

        # ttk stile renkleri enjekte
        style = ttk.Style(self)
        style.theme_use("default")
        for w in ("TFrame", "TLabel", "TButton"):
            style.configure(w, background=PRIMARY, foreground="black")
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        nb.add(self.hasta_ekle_tab(), text="Hasta Ekle")
        nb.add(self.randevu_tab(),   text="Randevu Oluştur")
        nb.add(self.liste_tab(),     text="Randevu Listele")
        nb.add(self.ucret_tab(),     text="Ödeme Hesapla")
        nb.add(self.hasta_liste_tab(), text="Hastaları Listele")

    # ------------------------- TAB – Hasta Ekle --------------------------------
    def hasta_ekle_tab(self):
        f = ttk.Frame(self)

        labels = ["Ad", "Soyad", "TC", "Doğum (YYYY-MM-DD)",
                  "Telefon", "E-posta", "Not"]
        self.h_vars = {k: tk.StringVar() for k in labels}

        for i, k in enumerate(labels):
            ttk.Label(f, text=k + ":").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            ttk.Entry(f, textvariable=self.h_vars[k], width=40).grid(row=i, column=1, pady=3)

        ttk.Button(f, text="Kaydet", command=self.hasta_kaydet)\
            .grid(row=len(labels), column=0, columnspan=2, pady=10)

        return f

    def hasta_kaydet(self):
        v = {k: s.get() for k, s in self.h_vars.items()}
        try:
            p = Patient(v["Ad"], v["Soyad"], v["TC"],
                        v["Doğum (YYYY-MM-DD)"], v["Telefon"],
                        v["E-posta"], v["Not"])
            self.cm.add_patient(p)
            alert("Başarılı", "Hasta kaydedildi.")
            for s in self.h_vars.values():
                s.set("")
        except Exception as e:
            alert("Hata", str(e), "error")

    # ----------------------- TAB – Randevu Oluştur -----------------------------
    def randevu_tab(self):
        f = ttk.Frame(self)

        # --- giriş alanları ---
        ttk.Label(f, text="Hasta TC:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        self.tc_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.tc_var, width=25).grid(row=0, column=1, pady=3)

        ttk.Label(f, text="Tarih (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.date_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.date_var, width=25).grid(row=1, column=1, pady=3)

        ttk.Label(f, text="Saat (HH:MM):").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.time_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.time_var, width=25).grid(row=2, column=1, pady=3)

        ttk.Label(f, text="Diş Hekimi:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.dentist_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.dentist_var, width=25).grid(row=3, column=1, pady=3)

        # --- işlem combobox ---
        ttk.Label(f, text="İşlem:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.proc_var = tk.StringVar(value=list(PROCEDURE_FEES.keys())[0])
        self.proc_cb = ttk.Combobox(
            f, textvariable=self.proc_var, state="readonly",
            values=list(PROCEDURE_FEES.keys()), width=22
        )
        self.proc_cb.grid(row=4, column=1, pady=3)
        self.proc_cb.bind("<<ComboboxSelected>>", self.procedure_changed)

        # --- ücret alanı (ayrı satır) ---
        ttk.Label(f, text="Ücret (KDV hariç):").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        self.fee_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.fee_var, width=25).grid(row=5, column=1, pady=3)

        # ilk defa ücret doldur
        self.fee_var.set(str(PROCEDURE_FEES[self.proc_var.get()]))

        ttk.Button(f, text="Randevu Kaydet", command=self.randevu_kaydet)\
            .grid(row=6, column=0, columnspan=2, pady=10)

        return f

    def procedure_changed(self, *_):
        """İşlem seçilince ücret alanını otomatik doldur."""
        self.fee_var.set(str(PROCEDURE_FEES[self.proc_var.get()]))

    def randevu_kaydet(self):
        try:
            fee = float(self.fee_var.get())
            dt_iso = iso_date(self.date_var.get(), self.time_var.get())
            r = Appointment(
                self.tc_var.get(), dt_iso,
                self.dentist_var.get(), self.proc_var.get(), fee
            )
            self.cm.add_appointment(r)
            alert("Başarılı", "Randevu kaydedildi.")
            # alanları temizle
            for v in (self.tc_var, self.date_var, self.time_var,
                      self.dentist_var):
                v.set("")
            self.proc_cb.current(0)
            self.fee_var.set(str(PROCEDURE_FEES[self.proc_var.get()]))
        except ValueError:
            alert("Hata", "Ücret sayısal olmalı.", "error")
        except Exception as e:
            alert("Hata", str(e), "error")

    # ----------------------- TAB – Randevu Listele -----------------------------
    def liste_tab(self):
        f = ttk.Frame(self)

        self.start_var = tk.StringVar()
        self.end_var   = tk.StringVar()

        ttk.Label(f, text="Başlangıç (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(f, textvariable=self.start_var, width=15).grid(row=0, column=1, pady=5)
        ttk.Label(f, text="Bitiş (YYYY-MM-DD):").grid(row=0, column=2, padx=5, sticky="e")
        ttk.Entry(f, textvariable=self.end_var, width=15).grid(row=0, column=3, pady=5)
        ttk.Button(f, text="Listele", command=self.randevu_listele)\
            .grid(row=0, column=4, padx=5)

        cols = ("Tarih-Saat", "TC", "Hekim", "İşlem", "Ücret")
        self.ap_tree = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.ap_tree.heading(c, text=c)
            self.ap_tree.column(c, anchor="center")
        self.ap_tree.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=5)
        f.rowconfigure(1, weight=1)
        for i in range(5):
            f.columnconfigure(i, weight=1)

        return f

    def randevu_listele(self):
        for i in self.ap_tree.get_children():
            self.ap_tree.delete(i)

        start = self.start_var.get() or None
        end   = self.end_var.get() or None
        try:
            items = self.cm.list_appointments(start, end)
            for a in items:
                self.ap_tree.insert("", "end", values=(
                    a.tarih_saat, a.hasta_tc, a.dis_hekim_adi, a.islem, f"{a.ucret:.2f}"
                ))
            if not items:
                alert("Bilgi", "Belirtilen aralıkta randevu bulunamadı.", "info")
        except Exception as e:
            alert("Hata", str(e), "error")

    # -------------------------- TAB – Ödeme Hesapla ----------------------------
    def ucret_tab(self):
        f = ttk.Frame(self)

        ttk.Label(f, text="Ücret (KDV hariç):").grid(row=0, column=0, padx=5, pady=20)
        self.ucret_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.ucret_var, width=15).grid(row=0, column=1)

        ttk.Button(f, text="Hesapla", command=self.kdv_hesapla)\
            .grid(row=0, column=2, padx=10)

        self.toplam_lbl = ttk.Label(f, text="KDV dahil toplam: – ₺",
                                    font=("Segoe UI", 11, "bold"))
        self.toplam_lbl.grid(row=1, column=0, columnspan=3, pady=20)

        return f

    def kdv_hesapla(self):
        try:
            tutar = float(self.ucret_var.get())
            toplam = self.cm.kdv_haric_to_dahil(tutar)
            self.toplam_lbl.config(text=f"KDV dahil toplam: {toplam:.2f} ₺")
        except ValueError:
            alert("Hata", "Geçerli bir tutar girin.", "error")

    # ------------------------ TAB – Hastaları Listele --------------------------
    def hasta_liste_tab(self):
        f = ttk.Frame(self)

        ttk.Button(f, text="Yenile", command=self.hasta_listele)\
            .pack(anchor="ne", padx=5, pady=5)

        cols = ("TC", "Ad", "Soyad", "Doğum", "Telefon", "E-posta", "Not")
        self.ht_tree = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.ht_tree.heading(c, text=c)
            self.ht_tree.column(c, anchor="center", width=90)
        self.ht_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.hasta_listele()  # ilk yükleme
        return f

    def hasta_listele(self):
        for i in self.ht_tree.get_children():
            self.ht_tree.delete(i)

        for p in self.cm.patients.values():
            self.ht_tree.insert("", "end", values=(
                p.tc, p.ad, p.soyad, p.dogum_tarihi,
                p.telefon, p.e_posta, p.not_
            ))


# -------------------------------- Main ----------------------------------------
if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()
