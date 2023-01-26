from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Listing, Assignment


class AssignmentCreate(APITestCase):
    def setUp(self):
        self.listing_1 = Listing.objects.create(
            first_name="Ross", last_name="Geller")
        self.listing_2 = Listing.objects.create(
            first_name="Phoebe", last_name="Buffay")
        self.assignment_1 = Assignment.objects.create(
            start_date=date(2023, 2, 7),
            end_date=date(2023, 2, 15),
            listing=self.listing_1,
        )
        self.assignment_2 = Assignment.objects.create(
            start_date=date(2023, 4, 1),
            end_date=date(2023, 4, 4),
            listing=self.listing_2,
        )

    def test_create_assignment_returns_201(self):
        response = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": date.today() + timedelta(days=5),
                "end_date": date.today() + timedelta(days=7),
                "listing": self.listing_1.pk,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_created_assignment_is_stored_correctly(self):
        start_date = date.today() + timedelta(days=5)
        post_data = {
            "start_date": start_date,
            "end_date": start_date + timedelta(days=5),
            "listing": self.listing_2.pk,
        }

        response = self.client.post("/listings/assignments/", post_data)

        new_assignment = Assignment.objects.get(
            id=response.data["id"],
        )

        created_data = {
            "start_date": new_assignment.start_date,
            "end_date": new_assignment.end_date,
            "listing": new_assignment.listing_id,
        }
        self.assertDictEqual(created_data, post_data)

    def test_do_not_create_assignment_if_end_before_start(self):
        start_date = date.today()

        response = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date,
                "end_date": start_date - timedelta(days=5),
                "listing": self.listing_2.pk,
            },)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_do_not_create_assignment_starting_today(self):
        start_date = date.today()

        response = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date,
                "end_date": start_date + timedelta(days=5),
                "listing": self.listing_2.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_do_not_create_assignment_in_the_past(self):
        start_date = date.today() - timedelta(days=1)

        response = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date,
                "end_date": start_date + timedelta(days=5),
                "listing": self.listing_2.pk,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_overlapping_assignments_for_different_listings(self):
        start_date_1 = date.today() + timedelta(days=10)
        end_date_1 = start_date_1 + timedelta(days=4)

        # an assignment that overlaps with the first
        start_date_2 = start_date_1 - timedelta(days=2)
        end_date_2 = start_date_1 + timedelta(days=2)

        # create first assignment
        self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_1,
                "end_date": end_date_1,
                "listing": self.listing_1.pk,
            },
        )

        # create second assignment
        response_2 = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_2,
                "end_date": end_date_2,
                "listing": self.listing_2.pk,
            },
        )

        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

    def test_do_not_create_overlapping_assignments_for_same_listings(self):
        listing = self.listing_1.pk
        start_date_1 = date.today() + timedelta(days=30)
        end_date_1 = start_date_1 + timedelta(days=4)

        # an assignment that overlaps with the first
        start_date_2 = start_date_1 - timedelta(days=2)
        end_date_2 = start_date_1 + timedelta(days=2)

        # create first assignment
        self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_1,
                "end_date": end_date_1,
                "listing": listing,
            },
        )

        # try to create overlapping assignment
        response_2 = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_2,
                "end_date": end_date_2,
                "listing": listing,
            },
        )

        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_assignment_start_same_day_as_another_ends(self):
        listing = self.listing_1.pk
        start_date_1 = date.today() + timedelta(days=68)
        end_date_1 = start_date_1 + timedelta(days=4)

        start_date_2 = end_date_1
        end_date_2 = start_date_2 + timedelta(days=2)

        # create first assignment
        self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_1,
                "end_date": end_date_1,
                "listing": listing,
            },
        )

        # create second assignment
        response_2 = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_2,
                "end_date": end_date_2,
                "listing": listing,
            },
        )

        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

    def test_create_assignment_end_on_same_day_as_another_starts(self):
        listing = self.listing_1.pk
        start_date_1 = date.today() + timedelta(days=28)
        end_date_1 = start_date_1 + timedelta(days=4)

        end_date_2 = start_date_1
        start_date_2 = end_date_2 - timedelta(days=4)

        # create first assignment
        self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_1,
                "end_date": end_date_1,
                "listing": listing,
            },
        )

        # create second assignment
        response_2 = self.client.post(
            path="/listings/assignments/",
            data={
                "start_date": start_date_2,
                "end_date": end_date_2,
                "listing": listing,
            },
        )

        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
