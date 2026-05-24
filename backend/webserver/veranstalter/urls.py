from django.urls import path

from .views import VeranstalterDetailView, VeranstalterListCreateView


urlpatterns = [
    path('', VeranstalterListCreateView.as_view()),
    path('<int:veranstalter_id>/', VeranstalterDetailView.as_view()),
]
