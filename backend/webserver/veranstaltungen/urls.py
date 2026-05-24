from django.urls import path

from .views import (
    VeranstaltungDetailView,
    VeranstaltungListCreateView,
    VeranstaltungTicketCreateView,
    VeranstaltungTicketDetailView,
)


urlpatterns = [
    path('', VeranstaltungListCreateView.as_view()),
    path('<int:veranstaltung_id>/tickets', VeranstaltungTicketCreateView.as_view()),
    path('<int:veranstaltung_id>/tickets/<str:ticket_typ>', VeranstaltungTicketDetailView.as_view()),
    path('<int:veranstaltung_id>/', VeranstaltungDetailView.as_view()),
]
