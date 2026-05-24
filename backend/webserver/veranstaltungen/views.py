from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from webserver.api import serializers
from webserver.models import Veranstaltung, Veranstaltung_Ticket_Umfang
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status


@extend_schema_view(
    get=extend_schema(
        operation_id='veranstaltung_list_filtered',
        summary='Veranstaltungen auflisten und filtern',
        responses=serializers.VeranstaltungListSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Veranstaltungen nach dem Namen',
            ),
            OpenApiParameter(
                name='veranstaltung_kategorie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Veranstaltungen nach der Kategorie_ID',
            ),
            OpenApiParameter(
                name='veranstalter_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Veranstaltungen nach der Veranstalter_ID',
            ),
        ],
    ),
    post=extend_schema(
        operation_id='veranstaltung_create',
        summary='Veranstaltung anlegen',
        request=serializers.VeranstaltungCreateSerializer(),
        responses=serializers.VeranstaltungDetailSerializer(),
    ),
)
class VeranstaltungListCreateView(GenericAPIView):
    queryset = Veranstaltung.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.VeranstaltungCreateSerializer
        return serializers.VeranstaltungListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        veranstaltung_name = self.request.query_params.get('veranstaltung_name')
        if veranstaltung_name:
            queryset = queryset.filter(Veranstaltung_Name__icontains=veranstaltung_name)

        veranstaltung_kategorie_id = self.request.query_params.get('veranstaltung_kategorie_id')
        if veranstaltung_kategorie_id:
            queryset = queryset.filter(Veranstaltung_Kategorie_ID=veranstaltung_kategorie_id)

        veranstalter_id = self.request.query_params.get('veranstalter_id')
        if veranstalter_id:
            queryset = queryset.filter(Veranstalter_ID=veranstalter_id)

        return queryset

    def get(self, request, *args, **kwargs):
        serializer = serializers.VeranstaltungListSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        veranstaltung = serializer.save()
        response_serializer = serializers.VeranstaltungDetailSerializer(veranstaltung)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        operation_id='veranstaltung_ticket_create',
        summary='Ticket-Umfang für Veranstaltung anlegen',
        request=serializers.Veranstaltung_Ticket_UmfangCreateNestedSerializer(),
        responses=serializers.Veranstaltung_Ticket_UmfangSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Veranstaltung, zu der der Ticket-Umfang gehört',
            ),
        ],
    ),
)
class VeranstaltungTicketCreateView(GenericAPIView):
    queryset = Veranstaltung_Ticket_Umfang.objects.all()
    serializer_class = serializers.Veranstaltung_Ticket_UmfangCreateNestedSerializer

    def post(self, request, veranstaltung_id, *args, **kwargs):
        veranstaltung = get_object_or_404(Veranstaltung, Veranstaltung_ID=veranstaltung_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket_umfang = serializer.save(Veranstaltung_ID=veranstaltung)
        response_serializer = serializers.Veranstaltung_Ticket_UmfangSerializer(ticket_umfang)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    patch=extend_schema(
        operation_id='veranstaltung_ticket_partial_update',
        summary='Ticket-Umfang anpassen',
        request=serializers.Veranstaltung_Ticket_UmfangUpdateSerializer(),
        responses=serializers.Veranstaltung_Ticket_UmfangSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Veranstaltung, zu der der Ticket-Umfang gehört',
            ),
            OpenApiParameter(
                name='ticket_typ',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description='Ticket-Typ des zu ändernden Ticket-Umfangs',
            ),
        ],
    ),
)
class VeranstaltungTicketDetailView(GenericAPIView):
    queryset = Veranstaltung_Ticket_Umfang.objects.all()
    lookup_field = 'Ticket_Typ'
    lookup_url_kwarg = 'ticket_typ'

    def patch(self, request, veranstaltung_id, ticket_typ, *args, **kwargs):
        ticket_umfang = get_object_or_404(
            Veranstaltung_Ticket_Umfang,
            Veranstaltung_ID=veranstaltung_id,
            Ticket_Typ=ticket_typ,
        )
        serializer = serializers.Veranstaltung_Ticket_UmfangUpdateSerializer(
            ticket_umfang,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        ticket_umfang = serializer.save()
        response_serializer = serializers.Veranstaltung_Ticket_UmfangSerializer(ticket_umfang)
        return Response(response_serializer.data)


@extend_schema_view(
    get=extend_schema(
        operation_id='veranstaltung_detail',
        summary='Veranstaltung anzeigen',
        responses=serializers.VeranstaltungDetailSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Veranstaltung',
            ),
        ],
    ),
    patch=extend_schema(
        operation_id='veranstaltung_partial_update',
        summary='Veranstaltung anpassen',
        request=serializers.VeranstaltungUpdateSerializer(),
        responses=serializers.VeranstaltungDetailSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Veranstaltung',
            ),
        ],
    ),
)
class VeranstaltungDetailView(GenericAPIView):
    queryset = Veranstaltung.objects.all()
    lookup_field = 'Veranstaltung_ID'
    lookup_url_kwarg = 'veranstaltung_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.VeranstaltungUpdateSerializer
        return serializers.VeranstaltungDetailSerializer

    def get(self, request, veranstaltung_id, *args, **kwargs):
        veranstaltung = self.get_object()
        serializer = serializers.VeranstaltungDetailSerializer(veranstaltung)
        return Response(serializer.data)

    def patch(self, request, veranstaltung_id, *args, **kwargs):
        veranstaltung = self.get_object()
        serializer = self.get_serializer(veranstaltung, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        veranstaltung = serializer.save()
        response_serializer = serializers.VeranstaltungDetailSerializer(veranstaltung)
        return Response(response_serializer.data)
