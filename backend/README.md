Installation
============

This project uses Django 3.2, so requires Python >=3.6 and <3.11.

You can create a virtual environment as follows:

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up DB
=========

The following commands create the required database tables in a
local sqlite db, and load in some sample data.

```
source venv/bin/activate
cd ths
# run migrations
./manage.py migrate
# Load sample data
./manage.py loaddata sampledata.json
````

Run project
===========

```
source venv/bin/activate
cd ths
./manage.py runserver
````

This runs the Django devserver on port 8000.

You can now access the API using curl, e.g.

```
curl http://localhost:8000/listings/
```

or go to http://localhost:8000/listings/ in your browser


Run test suite
==============

```
source venv/bin/activate
cd ths
./manage.py test
````

Improving the performance of the Listing endpoint
=================================================

Some thoughts about improving the performance of of the listing endpoint, in no particular order:

- Not sure if pagination is currently enabled, that would reduce the amount of data collected from the database at once, and reduce the amount of data potentially sent to the client.

- The only endpoint doesn't offer any filtering or search functionality. You could add additional end points that allowed filtering based on pet type/ number or whether they have assignments within a certain date range.

- The captured sql queries for a single request to the listings endpoint were:

1. SELECT "listings_listing"."id", "listings_listing"."first_name", "listings_listing"."last_name" FROM "listings_listing"
2. SELECT "pets_pet"."id", "pets_pet"."name", "pets_pet"."animal_type", "pets_pet"."description", "pets_pet"."listing_id" FROM "pets_pet" WHERE "pets_pet"."listing_id" = 1
3. SELECT "listings_assignment"."id", "listings_assignment"."start_date", "listings_assignment"."end_date", "listings_assignment"."listing_id" FROM "listings_assignment" WHERE "listings_assignment"."listing_id" = 1
4. SELECT "pets_pet"."id", "pets_pet"."name", "pets_pet"."animal_type", "pets_pet"."description", "pets_pet"."listing_id" FROM "pets_pet" WHERE "pets_pet"."listing_id" = 2
5. SELECT "listings_assignment"."id", "listings_assignment"."start_date", "listings_assignment"."end_date", "listings_assignment"."listing_id" FROM "listings_assignment" WHERE "listings_assignment"."listing_id" = 2

5 queries is pretty bad for the scale of the data there is in the test database. Every new listing generates 2 more queries. I think 100 listings would generated 1 + 100 + 100 db queries.

We can make a quick optimisation by changing the queryset used in the listings view to use the "prefetch_related" method. This makes django a little smarter by making it work out what data it needs from the 3 tables and joining it itself later. This should always result in a maximum of 3 queries, eg.:

1. SELECT "listings_listing"."id", "listings_listing"."first_name", "listings_listing"."last_name" FROM "listings_listing"
2. SELECT "listings_assignment"."id", "listings_assignment"."start_date", "listings_assignment"."end_date", "listings_assignment"."listing_id" FROM "listings_assignment" WHERE "listings_assignment"."listing_id" IN (1, 2)
3. SELECT "pets_pet"."id", "pets_pet"."name", "pets_pet"."animal_type", "pets_pet"."description", "pets_pet"."listing_id" FROM "pets_pet" WHERE "pets_pet"."listing_id" IN (1, 2)

Ideally we'd like to get it down to a single query which should be possible if we could make django use inner joins with the "select_related" method, but that would require some database restructuring.
 