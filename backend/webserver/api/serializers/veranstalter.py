from rest_framework import serializers

from webserver.models import Veranstalter

from .common import InformationenGeprueftMixin
from .veranstaltungen import VeranstaltungListSerializer


class VeranstalterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstalter
        fields = [
            "Veranstalter_ID",
            "Veranstalter_Name",
            "Veranstalter_Email",
            "Veranstalter_Telefonnummer",
            "Veranstalter_Hauptsitz",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class VeranstalterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstalter
        fields = [
            "Veranstalter_Name",
            "Veranstalter_Email",
            "Veranstalter_Telefonnummer",
            "Veranstalter_Hauptsitz",
        ]


class VeranstalterUpdateSerializer(InformationenGeprueftMixin, serializers.ModelSerializer):
    class Meta:
        model = Veranstalter
        fields = [
            "Veranstalter_Name",
            "Veranstalter_Email",
            "Veranstalter_Telefonnummer",
            "Veranstalter_Hauptsitz",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class VeranstalterDetailSerializer(serializers.ModelSerializer):
    Veranstaltungen = VeranstaltungListSerializer(many=True, read_only=True)

    class Meta:
        model = Veranstalter
        fields = [
            "Veranstalter_ID",
            "Veranstalter_Name",
            "Veranstalter_Email",
            "Veranstalter_Telefonnummer",
            "Veranstalter_Hauptsitz",
            "Informationen_Geprueft",
            "Geprueft_Von",
            "Veranstaltungen",
        ]
