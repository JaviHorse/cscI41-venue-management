
from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Building,
    Agent,
    Venue,
    VenueAssignment,
    Renovation,
    AmenityType,
    VenueAmenity,
    Customer,
    Reservation,
)


class Command(BaseCommand):
    # Populates our database with sample records
    # We can run it using: python manage.py seed_data
    help = "Populate the SQLite database with sample venue management data."

    @transaction.atomic
    def handle(self, *args, **options):

        # Using get_or_create instead of create so we won't keep adding
        # duplicate records every time we run the seed script
        
        # If the ID already exists, Django will just retrieve that record
        # If it doesn't exist, Django will create it using the provided fields
        def seed(model, pk, **fields):
            obj, created = model.objects.get_or_create(
                pk=pk,
                defaults=fields
            )
            return obj, created
        
        # Keep track of how many new records are added per table
        counts = {}

        # 1. BUILDING

        # Start with BUILDING since AGENT and VENUE both reference it
        # Each building has its own ID, name, location, and acquisition date
        # Using 1001-1005 as fixed sample IDs for easier referencing later
        buildings = [
            (1001, "Ateneo Events Center", "Katipunan Avenue",
             "Loyola Heights", "Quezon City", date(2015, 6, 1)),
            (1002, "Rizal Convention Hall", "Ortigas Avenue",
             "San Antonio", "Pasig City", date(2018, 3, 15)),
            (1003, "Makati Corporate Center", "Ayala Avenue",
             "Bel-Air", "Makati City", date(2020, 8, 10)),
            (1004, "Manila Cultural Center", "Roxas Boulevard",
             "Malate", "Manila", date(2012, 11, 20)),
            (1005, "BGC Conference Tower", "5th Avenue",
             "Bonifacio Global City", "Taguig City", date(2022, 1, 5)),
        ]

        counts["BUILDING"] = 0

        # Loop through the sample buildings and insert them
        for pk, name, street, district, city, acquired in buildings:
            _, created = seed(
                Building, pk,
                building_name=name,
                street=street,
                district=district,
                city=city,
                acquisition_date=acquired
            )
            counts["BUILDING"] += created

        # 2. AGENT

        # Each agent is assigned to a building through Building_ID
        # The buildings must already exist before inserting agents kasi we'll run into foreign key issues
        agents = [
            (1001, "Maria", "Santos", 1001),
            (1002, "Juan", "Dela Cruz", 1002),
            (1003, "Angela", "Reyes", 1003),
            (1004, "Carlos", "Mendoza", 1004),
            (1005, "Patricia", "Garcia", 1005),
        ]

        counts["AGENT"] = 0

        for pk, first, last, building_id in agents:
            _, created = seed(
                Agent, pk,
                first_name=first,
                last_name=last,
                building_id=building_id
            )
            counts["AGENT"] += created

        # 3. VENUE

        # VENUES ARE LOCATED INSIDE THE BUILDINGS
        # Each venue contains its type, floor, area, and capacity
        # Building_ID tells us which building the venue belongs to
    
        # We'll also use these capacities later when testing
        venues = [
            (1001, "Blue Eagle Gym", "Gym", 1, 450.0, 300, 1001),
            (1002, "Rizal Ballroom", "Ballroom", 2, 300.0, 200, 1002),
            (1003, "Executive Meeting Room", "Meeting Room", 5, 80.0, 30, 1003),
            (1004, "Cultural Exhibition Hall", "Exhibition Hall", 1, 600.0, 400, 1004),
            (1005, "BGC Function Room", "Function Room", 10, 150.0, 100, 1005),
        ]

        counts["VENUE"] = 0

        for pk, name, venue_type, floor, area, capacity, building_id in venues:
            _, created = seed(
                Venue, pk,
                venue_name=name,
                venue_type=venue_type,
                floor=floor,
                floor_area_sqm=area,
                capacity=capacity,
                building_id=building_id
            )
            counts["VENUE"] += created



        # 4. VENUE_ASSIGNMENT

        # This table connects an agent to a  venue
        # It also keeps track of the assignment's start and end dates
        # Since this references both AGENT and VENUE, those two tables need to be populated first
        assignments = [
            (1001, date(2026, 9, 1), date(2027, 8, 31), 1001, 1001),
            (1002, date(2026, 9, 1), date(2027, 8, 31), 1002, 1002),
            (1003, date(2026, 9, 1), date(2027, 8, 31), 1003, 1003),
            (1004, date(2026, 9, 1), date(2027, 8, 31), 1004, 1004),
            (1005, date(2026, 9, 1), date(2027, 8, 31), 1005, 1005),
        ]

        counts["VENUE_ASSIGNMENT"] = 0

        for pk, start, end, agent_id, venue_id in assignments:
            _, created = seed(
                VenueAssignment, pk,
                start_date=start,
                end_date=end,
                agent_id=agent_id,
                venue_id=venue_id
            )
            counts["VENUE_ASSIGNMENT"] += created

        # 5. RENOVATION

        # Stores the renovation history
        # Has start, end date, and short description
        # The last record has None as its completion date to signify that its an ongoing renovation
        renovations = [
            (1001, date(2025, 1, 10), date(2025, 2, 10),
             "Sound system upgrade", 1001),
            (1002, date(2025, 3, 5), date(2025, 4, 1),
             "Flooring replacement", 1002),
            (1003, date(2025, 5, 12), date(2025, 5, 30),
             "Lighting improvement", 1003),
            (1004, date(2025, 7, 1), date(2025, 8, 15),
             "Air conditioning upgrade", 1004),
            (1005, date(2026, 10, 1), None,
             "Interior repainting in progress", 1005),
        ]

        counts["RENOVATION"] = 0

        for pk, start, completed, remarks, venue_id in renovations:
            _, created = seed(
                Renovation, pk,
                date_started=start,
                date_completed=completed,
                remarks=remarks,
                venue_id=venue_id
            )
            counts["RENOVATION"] += created


        # 6. AMENITY_TYPE

        # Lists down the amenities that a venue has
        # Separate table so we don't have to repeatedly store the amenity names for every venue
        amenities = [
            (1001, "Projector"),
            (1002, "Sound System"),
            (1003, "Air Conditioning"),
            (1004, "Wi-Fi Router"),
            (1005, "Conference Tables"),
        ]

        counts["AMENITY_TYPE"] = 0

        for pk, name in amenities:
            _, created = seed(
                AmenityType, pk,
                amenity_name=name
            )
            counts["AMENITY_TYPE"] += created




        # 7. VENUE_AMENITY

        # Connect the amenities to the venues that have them
        # Records quantity, description, and installation date
        # Venue_ID references VENUE while Amenity_ID references AMENITY_TYPE
        venue_amenities = [
            (1001, "HD projector", 2, date(2025, 2, 15), 1001, 1001),
            (1002, "Surround sound speakers", 4, date(2025, 4, 5), 1002, 1002),
            (1003, "Ceiling-mounted AC units", 3, date(2025, 6, 1), 1003, 1003),
            (1004, "High-speed wireless router", 5, date(2025, 8, 20), 1004, 1004),
            (1005, "Modular conference tables", 10, date(2026, 1, 15), 1005, 1005),
        ]

        counts["VENUE_AMENITY"] = 0

        for pk, description, quantity, installed, venue_id, amenity_id in venue_amenities:
            _, created = seed(
                VenueAmenity, pk,
                description=description,
                quantity=quantity,
                installation_date=installed,
                venue_id=venue_id,
                amenity_id=amenity_id
            )
            counts["VENUE_AMENITY"] += created


        # 8. CUSTOMER
        
        # Sample customers who will be making venue reservations
        # Each customer has their own ID and personal information
        # These records will be referenced later in RESERVATION
        customers = [
            (1001, "Javier", "Macasaet", "M", date(2000, 3, 12), "Quezon City"),
            (1002, "Gabe", "Labariento", "R", date(1998, 7, 25), "Pasig City"),
            (1003, "Erin", "Maranan", "A", date(2001, 1, 8), "Makati City"),
            (1004, "CJ", "Landicho", "J", date(1997, 11, 19), "Manila"),
            (1005, "Carl", "Basco", "C", date(1999, 5, 30), "Taguig City"),
        ]

        counts["CUSTOMER"] = 0

        for pk, first, last, middle, birth, location in customers:
            _, created = seed(
                Customer, pk,
                first_name=first,
                last_name=last,
                middle_initial=middle,
                birth_date=birth,
                customer_location=location
            )
            counts["CUSTOMER"] += created

 
        # 9. RESERVATION

        # Insert the sample reservations
        # This is last because each reservation needs a customer and venue thats already in the db

        # Helper function for creating timezone-aware dates
        # Django uses timezone-aware datetimes when USE_TZ is enabled
        def local_dt(year, month, day, hour, minute=0):
            return timezone.make_aware(
                datetime(year, month, day, hour, minute)
            )

        reservations = [
            (1001, local_dt(2027, 1, 10, 9),
             local_dt(2027, 1, 10, 12), 150, 1001, 1001),
            (1002, local_dt(2027, 1, 12, 13),
             local_dt(2027, 1, 12, 17), 120, 1002, 1002),
            (1003, local_dt(2027, 1, 15, 10),
             local_dt(2027, 1, 15, 12), 20, 1003, 1003),
            (1004, local_dt(2027, 1, 18, 8),
             local_dt(2027, 1, 18, 16), 250, 1004, 1004),
            (1005, local_dt(2027, 1, 20, 14),
             local_dt(2027, 1, 20, 18), 80, 1005, 1005),
        ]

        counts["RESERVATION"] = 0

        for pk, start, end, participants, venue_id, customer_id in reservations:
            _, created = seed(
                Reservation, pk,
                start_datetime=start,
                end_datetime=end,
                expected_participants=participants,
                venue_id=venue_id,
                customer_id=customer_id
            )
            counts["RESERVATION"] += created


        # SEEDING SUMMARY

        # Display the number of new records inserted into each table
        # This also helps us verify if the script added the expected data
        self.stdout.write(self.style.SUCCESS(
            "\nDatabase seeding completed successfully!"
        ))

        for table, created in counts.items():
            self.stdout.write(
                f"{table}: {created} new record(s)"
            )

        # If we run this script again, the total should be 0
        # since the records already exist in the database
        self.stdout.write(
            f"\nTotal new records: {sum(counts.values())}"
        )
