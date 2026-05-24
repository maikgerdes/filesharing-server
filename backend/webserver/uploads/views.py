import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from webserver.api import serializers
from webserver.infrastructure.azure import upload_blob
from webserver.infrastructure.json_model_compatibility import validate_payload_against_models_with_mapping
from webserver.infrastructure.word_reader import read_doc
from webserver.models import Datei

logger = logging.getLogger(__name__)


@extend_schema_view(
    post=extend_schema(
        operation_id="docx_document",
        request=serializers.DateiUploadSerializer,
        responses=serializers.DateiSerializer,
    )
)
class PostDocxDocument(GenericAPIView):
    serializer_class = serializers.DateiUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        logger.info(" request.data: %s", request.data)
        upload_serializer = self.get_serializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)

        uploaded_file = upload_serializer.validated_data["file"]
        dateipfad = upload_blob(uploaded_file, uploaded_file.name)
        logger.info(" uploaded_file: %s", uploaded_file)
        intake_dictionary = read_doc(path=uploaded_file) or {}
        logger.info(intake_dictionary.items())

        datei = Datei.objects.create(
            Datei_Name=uploaded_file.name,
            Datei_Pfad=dateipfad,
            Datei_Typ=uploaded_file.content_type,
            Datei_Inhalt=intake_dictionary,
            Uploader=upload_serializer.validated_data["Uploader"],
            Datei_Inhalt_Benoetigt=True,
        )

        return Response(serializers.DateiSerializer(datei).data)


@extend_schema_view(
    post=extend_schema(
        operation_id="validate_datei_json_against_model",
        request=serializers.DateiModelValidationSerializer,
    )
)
class PostValidateDateiJson(GenericAPIView):
    serializer_class = serializers.DateiModelValidationSerializer

    def post(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        datei = request_serializer.validated_data["Datei_ID"]
        zielmodelle = request_serializer.validated_data.get("Zielmodelle") or []
        zielmodell = request_serializer.validated_data.get("Zielmodell")
        if zielmodell:
            zielmodelle = [zielmodell]
        should_create = request_serializer.validated_data["Anlegen_Bei_Kompatibilitaet"]

        report = validate_payload_against_models_with_mapping(
            payload=datei.Datei_Inhalt,
            target_models=zielmodelle,
            context={"uploader_id": datei.Uploader_id},
            create_objects=should_create,
        )

        if should_create and report["kompatibel"]:
            datei.Datei_Inhalt_Benoetigt = False
            datei.save(update_fields=["Datei_Inhalt_Benoetigt"])

        if len(zielmodelle) == 1:
            single_report = report["model_reports"][zielmodelle[0]]
            response_payload = {
                "datei": serializers.DateiSerializer(datei).data,
                "validierungsreport": single_report,
                "angelegter_eintrag": single_report.get("created_entry"),
            }
        else:
            response_payload = {
                "datei": serializers.DateiSerializer(datei).data,
                "validierungsreport": report,
                "angelegter_eintrag": None,
            }

        return Response(response_payload, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        operation_id="update_datei_json",
        request=serializers.DateiJsonUpdateSerializer,
        responses=serializers.DateiSerializer,
    )
)
class PostUpdateDateiJson(GenericAPIView):
    serializer_class = serializers.DateiJsonUpdateSerializer

    def post(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        datei = request_serializer.validated_data["Datei_ID"]
        datei_inhalt = request_serializer.validated_data["Datei_Inhalt"]

        Datei.objects.filter(Datei_ID=datei.Datei_ID).update(
            Datei_Inhalt=datei_inhalt,
            Datei_Inhalt_Benoetigt=True,
        )
        datei.refresh_from_db()

        return Response(
            {
                "datei": serializers.DateiSerializer(datei).data,
                "hinweis": "JSON aktualisiert. Bitte validierungs Endpoint erneut ausfuehren.",
            },
            status=status.HTTP_200_OK,
        )
