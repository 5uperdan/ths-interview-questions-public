from rest_framework import generics

from .models import Listing
from .serializers import ListingSerializer, AssignmentSerializer


class ListingList(generics.ListAPIView):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()


class AssignmentCreate(generics.CreateAPIView):
    """Enables assignment creation"""
    serializer_class = AssignmentSerializer
