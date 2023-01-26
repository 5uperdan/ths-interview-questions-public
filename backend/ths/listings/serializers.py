from rest_framework import serializers
from datetime import date
from .models import Listing, Assignment
from django.db.models import Q


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ["first_name", "last_name", "pets", "assignments"]


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = ["id", "start_date", "end_date", "listing"]

    def validate(self, data: dict):
        """overwrites existing validate method

        Args:
            data (dict): serialized data

        Returns:
            Any: the result of super().validate(data)
        """
        self.end_date_not_before_start_date(
            data["start_date"], data["end_date"])
        self.earliest_start_date_is_tomorrow(data["start_date"])
        self.no_overlapping_assignments(
            data["start_date"], data["end_date"], data["listing"])
        return super().validate(data)

    def end_date_not_before_start_date(
        self, start_date: date, end_date: date
    ) -> None:
        """checks that the end date is the same as the start date or later

        Args:
            start_date (date):
            end_date (date):

        Raises:
            serializers.ValidationError: if start/ end dates are invalid
        """
        if end_date < start_date:
            raise serializers.ValidationError(
                detail="end date cannot be before start date")

    def earliest_start_date_is_tomorrow(self, start_date: date) -> None:
        """checks that the start date is tomorrow or later

        Args:
            start_date (date):

        Raises:
            serializers.ValidationError: if start date is not valid
        """
        if start_date <= date.today():
            raise serializers.ValidationError(
                detail="earliest start date is tomorrow")

    def no_overlapping_assignments(
            self,
            na_start_date: date,
            na_end_date: date,
            listing_pk: int,) -> None:
        """checks that a new assignment date doesn't overlap with existing assignment

        an assignment may start on the same day as another ends.

        Args:
            na_start_date (date): new assignment's start date
            na_end_date (date): new assignment's end date
            listing_pk (int): the primary key of the listing

        Raises:
            serializers.ValidationError: if an existing assignment conflicts with
            the proposed new assignment dates.
        """
        assignments = Assignment.objects.filter(
            # listing = listing AND
            Q(listing=listing_pk) &
            # existing start date <= na start date
            Q(start_date__lte=na_start_date) &
            # existing end date > na start date
            Q(end_date__gt=na_start_date)
            |  # OR
            # listing = listing AND
            Q(listing=listing_pk) &
            # existing start date < na end date
            Q(start_date__lt=na_end_date) &
            # existing end date >= na end date
            Q(end_date__gte=na_end_date)
        )
        if len(assignments) > 0:
            raise serializers.ValidationError(
                "assignment dates cannot overlap"
            )
