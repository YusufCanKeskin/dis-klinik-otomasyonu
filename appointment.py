# -*- coding: utf-8 -*-
"""Randevu modelini tanımlar."""
import uuid


class Appointment:
    """Randevu verilerini tutar."""

    def __init__(self, hasta_tc, tarih_saat_iso, dis_hekim_adi, islem, ucret):
        self.id = str(uuid.uuid4())
        self.hasta_tc = str(hasta_tc)
        self.tarih_saat = tarih_saat_iso           # YYYY-MM-DD HH:MM
        self.dis_hekim_adi = dis_hekim_adi.title().strip()
        self.islem = islem
        self.ucret = float(ucret)

    def to_dict(self):
        return vars(self)

    @staticmethod
    def from_dict(d):
        a = Appointment(
            d["hasta_tc"], d["tarih_saat"],
            d["dis_hekim_adi"], d["islem"], d["ucret"]
        )
        a.id = d.get("id", a.id)
        return a

    def __str__(self):
        return f"{self.tarih_saat} – {self.dis_hekim_adi} – TC:{self.hasta_tc} – {self.islem}"

