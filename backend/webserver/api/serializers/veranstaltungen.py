from rest_framework import serializers

from webserver.models import Veranstaltung

from .common import InformationenGeprueftMixin, Veranstaltung_Ticket_UmfangSerializer
from .einladungen import Veranstaltung_EinladungSerializer


class VeranstaltungListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung
        fields = [
            "Veranstaltung_ID",
            "Veranstalter_ID",
            "Veranstaltung_Name",
            "Veranstaltung_Beschreibung",
            "Veranstaltung_Webseite",
            "Veranstaltung_Sprache",
            "Veranstaltung_Subevent",
            "Veranstaltung_Kategorie_ID",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class VeranstaltungCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung
        fields = [
            "Veranstalter_ID",
            "Veranstaltung_Name",
            "Veranstaltung_Beschreibung",
            "Veranstaltung_Webseite",
            "Veranstaltung_Sprache",
            "Veranstaltung_Subevent",
            "Veranstaltung_Kategorie_ID",
        ]


class VeranstaltungUpdateSerializer(InformationenGeprueftMixin, serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung
        fields = [
            "Veranstalter_ID",
            "Veranstaltung_Name",
            "Veranstaltung_Beschreibung",
            "Veranstaltung_Webseite",
            "Veranstaltung_Sprache",
            "Veranstaltung_Subevent",
            "Veranstaltung_Kategorie_ID",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class VeranstaltungDetailSerializer(serializers.ModelSerializer):
    Ticket_Arten = Veranstaltung_Ticket_UmfangSerializer(read_only=True, many=True)
    Einladungen = Veranstaltung_EinladungSerializer(read_only=True, many=True)

    class Meta:
        model = Veranstaltung
        fields = [
            "Veranstaltung_ID",
            "Veranstalter_ID",
            "Veranstaltung_Name",
            "Veranstaltung_Beschreibung",
            "Veranstaltung_Webseite",
            "Veranstaltung_Sprache",
            "Veranstaltung_Subevent",
            "Veranstaltung_Kategorie_ID",
            "Informationen_Geprueft",
            "Geprueft_Von",
            "Ticket_Arten",
            "Einladungen",
        ]
