from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from webserver.api import serializers
from webserver.models import Veranstaltung_Einladung, Einladung_Kommentar, Einladung_Entscheidung
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status


@extend_schema_view(
    get=extend_schema(
        operation_id='einladungen_list_filtered',
        summary='Einladungen auflisten und filtern',
        responses=serializers.Veranstaltung_EinladungSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID der Veranstaltung, zu welcher eingeladen wurde',
            ),
            OpenApiParameter(
                name='anfragesteller_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID des Anfragestellers',
            ),
            OpenApiParameter(
                name='personengruppe_anfragesteller_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID der jeweiligen Personengruppe des Anfragestellers',
            ),
            OpenApiParameter(
                name='datum',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert nach dem Einladungsdatum. Formate: exact:YYYY-MM-DD, lt:YYYY-MM-DD, gt:YYYY-MM-DD',
            ),
        ],
    ),
    post=extend_schema(
        operation_id='einladung_create',
        summary='Einladung anlegen',
        request=serializers.Veranstaltung_EinladungCreateSerializer(),
        responses=serializers.Veranstaltung_EinladungSerializer(),
    ),
)
class EinladungListCreateView(GenericAPIView):
    queryset = Veranstaltung_Einladung.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.Veranstaltung_EinladungCreateSerializer
        return serializers.Veranstaltung_EinladungSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        veranstaltung_id = self.request.query_params.get('veranstaltung_id')
        if veranstaltung_id:
            queryset = queryset.filter(Veranstaltung_ID=veranstaltung_id)

        anfragesteller_id = self.request.query_params.get('anfragesteller_id')
        if anfragesteller_id:
            queryset = queryset.filter(Anfragesteller_ID=anfragesteller_id)

        personengruppe_anfragesteller_id = self.request.query_params.get('personengruppe_anfragesteller_id')
        if personengruppe_anfragesteller_id:
            queryset = queryset.filter(Repraesentiert=personengruppe_anfragesteller_id)

        datum = self.request.query_params.get('datum')
        if datum:
            operator = 'exact'
            datum_wert = datum

            if ':' in datum:
                operator, datum_wert = datum.split(':', 1)
                operator = operator.strip().lower()
                datum_wert = datum_wert.strip()

            datum_lookup_map = {
                'exact': 'Einladung_Datum__date',
                'lt': 'Einladung_Datum__date__lt',
                'gt': 'Einladung_Datum__date__gt',
            }

            lookup = datum_lookup_map.get(operator)
            if lookup:
                queryset = queryset.filter(**{lookup: datum_wert})

        return queryset

    def get(self, request, *args, **kwargs):
        serializer = serializers.Veranstaltung_EinladungSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        einladung = serializer.save()
        response_serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        operation_id='einladung_kommentar_create',
        summary='Kommentar zu Einladung anlegen',
        request=serializers.Einladung_KommentarCreateNestedSerializer(),
        responses=serializers.Einladung_KommentarSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Einladung, zu der der Kommentar gehört',
            ),
        ],
        examples=[
            OpenApiExample(
                'Root-Kommentar',
                value={
                    'Parent_ID': None,
                    'Absender_ID': 2,
                    'Kommentar_Inhalt': 'Ich habe die Einladung geprüft und lasse hier Feedback da.',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Antwort auf Kommentar',
                value={
                    'Parent_ID': 5,
                    'Absender_ID': 2,
                    'Kommentar_Inhalt': 'Danke, ich habe es angepasst.',
                },
                request_only=True,
            ),
        ],
    ),
)
class EinladungKommentarCreateView(GenericAPIView):
    queryset = Einladung_Kommentar.objects.all()
    serializer_class = serializers.Einladung_KommentarCreateNestedSerializer

    def post(self, request, einladung_id, *args, **kwargs):
        einladung = get_object_or_404(Veranstaltung_Einladung, Veranstaltung_Einladung_ID=einladung_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kommentar = serializer.save(Veranstaltung_Einladung_ID=einladung)
        response_serializer = serializers.Einladung_KommentarSerializer(kommentar)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        operation_id='einladung_entscheidung_create',
        summary='Entscheidung zu Einladung anlegen',
        request=serializers.Einladung_EntscheidungCreateNestedSerializer(),
        responses=serializers.Einladung_EntscheidungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Einladung, zu der die Entscheidung gehört',
            ),
        ],
    ),
)
class EinladungEntscheidungCreateView(GenericAPIView):
    queryset = Einladung_Entscheidung.objects.all()
    serializer_class = serializers.Einladung_EntscheidungCreateNestedSerializer

    def post(self, request, einladung_id, *args, **kwargs):
        einladung = get_object_or_404(Veranstaltung_Einladung, Veranstaltung_Einladung_ID=einladung_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entscheidung = serializer.save(Veranstaltung_Einladung_ID=einladung)
        response_serializer = serializers.Einladung_EntscheidungSerializer(entscheidung)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        operation_id='einladung_detail',
        summary='Einladung anzeigen',
        responses=serializers.Veranstaltung_EinladungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Einladung',
            ),
        ],
    ),
    patch=extend_schema(
        operation_id='einladung_partial_update',
        summary='Einladung anpassen',
        request=serializers.Veranstaltung_EinladungCreateSerializer(),
        responses=serializers.Veranstaltung_EinladungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Einladung',
            ),
        ],
    ),
)
class EinladungDetailView(GenericAPIView):
    queryset = Veranstaltung_Einladung.objects.all()
    lookup_field = 'Veranstaltung_Einladung_ID'
    lookup_url_kwarg = 'einladung_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.Veranstaltung_EinladungCreateSerializer
        return serializers.Veranstaltung_EinladungSerializer

    def get(self, request, einladung_id, *args, **kwargs):
        einladung = self.get_object()
        serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(serializer.data)

    def patch(self, request, einladung_id, *args, **kwargs):
        einladung = self.get_object()
        serializer = self.get_serializer(einladung, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        einladung = serializer.save()
        response_serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(response_serializer.data)
