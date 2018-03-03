# -*- coding: utf-8 -*-

from datetime import datetime
import requests
import lxml.html
from geopy.distance import great_circle
import geocoder
from geojson import Feature, Point, FeatureCollection
import urllib.parse
from urllib.parse import urlencode

mapquest_key = ""

class FederFarma(object):
    """docstring for FederFarma."""

    city = "Genoa"
    base_url = "http://www.federfarmagenova.it"
    url_path = "website/farmacie/cerca_aperta.asp"
    base_vars = {
        # ?data=12%2F12%2F2016&ora=8&minuti=11&zonaturni=&textfield4=Cerca
        'data': "",
        'ora': "",
        'minuti': "",
        'zonaturni': "",
        'textfield4': "Cerca"
    }

    def __init__(self, gc):
        """
        gc @geocoder : Geocoder
        """
        super(FederFarma, self).__init__()
        # TODO: Better check
        assert gc.city==self.city
        self.source = gc
        self()

    def __call__(self):
        dom = self.fetch()
        infos = self.parse(dom)
        self.result = self.sort(infos)

    def first(self):
        return self.result[0]

    def sort(self, nfos):
        gres = geocoder.mapquest([n["indirizzo"] for n in nfos],
            method = 'batch',
            key = mapquest_key
        )
        for i, c in enumerate(gres):
            nfos[i]["latlng"] = c.latlng
            nfos[i]["osm_url"] = "http://www.openstreetmap.org/directions?" + urlencode({
            "route": ";".join(map(lambda c: ','.join(map(str, c)), (self.source.latlng, c.latlng))),
            "engine": "graphhopper_foot"
        })

        return sorted(nfos, key=lambda nfo: great_circle(nfo["latlng"], self.source.latlng,).m)

    def geocollection(self):
        """ Build-up a geojson-like object """
        feature_collection = FeatureCollection([Feature(
            geometry = Point(nfo["latlng"]
        )) for nfo in self.sort(self.result)])
        return feature_collection

    def dumps(self, nfos, *args, **kwargs):
        """ json encode """
        return geojson.dumps(self.geocollection(), *args, **kwargs)

    def fetch(self):
        """ Fetch informations from the source """
        now = datetime.now()
        url = urllib.parse.urljoin(self.base_url, self.url_path)
        payload = vars = dict(self.base_vars,
            data=now.strftime("%d/%m/%Y"),
            ora=now.strftime("%H"),
            minuti=now.strftime("%M")
        )

        res = requests.get(url, params=payload)
        res.raise_for_status()
        return res.text

    @staticmethod
    def parse(_dom):
        """ Extract information from the source service response """
        page = lxml.html.fromstring(_dom)
        _div = page.find_class("testo")[0]
        _nfos = sum([[[x.text_content() for x in j if not callable(x.tag)] \
            for j in i if len(j)>1] for i in _div[5]], [])
        nfos = []
        for _nfo in _nfos:
            nfo = {"nome": _nfo[0]}
            for k,x in zip(["indirizzo", "tel"], _nfo[1].split("\r\n    ")):
                nfo[k] = (' '.join(x.split())).strip()
            if len(_nfo)>2:
                nfo["note"] = _nfo[-1]
            nfos.append(nfo)
        return nfos

if __name__=="__main__":
    # Usage example
    here = geocoder.ip("me")
    ff = FederFarma(here)
    ff()
