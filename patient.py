# -*- coding: utf-8 -*-
"""Hasta modelini tanımlar."""
import uuid


class Patient:
    """Hasta verilerini tutar."""

    def __init__(self, ad, soyad, tc, dogum_tarihi, telefon, e_posta, not_=""):
        self.id = str(uuid.uuid4())
        self.ad = ad.title().strip()
        self.soyad = soyad.title().strip()
        self.tc = str(tc)
        self.dogum_tarihi = dogum_tarihi          # YYYY-MM-DD
        self.telefon = telefon
        self.e_posta = e_posta
        self.not_ = not_

    def to_dict(self):
        return vars(self)

    @staticmethod
    def from_dict(d):
        p = Patient(
            d["ad"], d["soyad"], d["tc"], d["dogum_tarihi"],
            d["telefon"], d["e_posta"], d.get("not_", "")
        )
        p.id = d.get("id", p.id)
        return p

    def __str__(self):
        return f"{self.ad} {self.soyad} (TC: {self.tc})"

