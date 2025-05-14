# -*- coding: utf-8 -*-
"""Veri kalıcılığı ve iş mantığı."""
import json
import os
from datetime import datetime

from patient import Patient
from appointment import Appointment


class ClinicManager:
    def __init__(self, veri_dosyasi="veriler.json"):
        self.veri_dosyasi = veri_dosyasi
        self.patients = {}         # {tc: Patient}
        self.appointments = []     # [Appointment]
        self.load()

    # ---------- Dosya İşlemleri ----------
    def load(self):
        if not os.path.exists(self.veri_dosyasi):
            return
        with open(self.veri_dosyasi, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.patients = {
            tc: Patient.from_dict(p) for tc, p in data.get("patients", {}).items()
        }
        self.appointments = [
            Appointment.from_dict(a) for a in data.get("appointments", [])
        ]

    def save(self):
        data = {
            "patients": {tc: p.to_dict() for tc, p in self.patients.items()},
            "appointments": [a.to_dict() for a in self.appointments],
        }
        with open(self.veri_dosyasi, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def backup(self):
        if os.path.exists(self.veri_dosyasi):
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.system(f'copy /y "{self.veri_dosyasi}" "{stamp}_backup.json" > nul')

    # ---------- CRUD ----------
    def add_patient(self, patient: Patient):
        if patient.tc in self.patients:
            raise ValueError("Bu TC ile kayıtlı hasta zaten var!")
        self.patients[patient.tc] = patient
        self.save()

    def add_appointment(self, appointment: Appointment):
        if appointment.hasta_tc not in self.patients:
            raise ValueError("Hasta bulunamadı – önce hasta kaydı ekleyin.")
        # aynı hekim-aynı tarih/saat çakışma kontrolü
        new_dt = datetime.fromisoformat(appointment.tarih_saat)
        for a in self.appointments:
            if a.dis_hekim_adi == appointment.dis_hekim_adi:
                if new_dt == datetime.fromisoformat(a.tarih_saat):
                    raise ValueError("Bu hekim için bu saatte randevu var!")
        self.appointments.append(appointment)
        self.save()

    def list_appointments(self, start=None, end=None):
        s = datetime.fromisoformat(start) if start else None
        e = datetime.fromisoformat(end) if end else None
        lst = []
        for a in self.appointments:
            t = datetime.fromisoformat(a.tarih_saat)
            if (s is None or t >= s) and (e is None or t <= e):
                lst.append(a)
        return sorted(lst, key=lambda x: x.tarih_saat)

    # ---------- Finans ----------
    @staticmethod
    def kdv_haric_to_dahil(ucret, oran=0.20):
        return round(ucret * (1 + oran), 2)

