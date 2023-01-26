from django.urls import path

from .views import ListingList, AssignmentCreate

urlpatterns = [
    path("", ListingList.as_view()),
    path("assignments/", AssignmentCreate.as_view()),
]
