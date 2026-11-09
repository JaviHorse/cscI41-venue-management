from django.db import models

# 1. BUILDING
class Building(models.Model):
    building_id = models.AutoField(
        primary_key=True,
        db_column='Building_ID'
    )
    building_name = models.CharField(max_length=100, db_column='Building_Name')
    street = models.CharField(max_length=100, db_column='Street')
    district = models.CharField(max_length=50, db_column='District')
    city = models.CharField(max_length=50, db_column='City')
    acquisition_date = models.DateField(db_column='Acquisition_Date')

    class Meta:
        db_table = 'BUILDING'

    def __str__(self):
        return self.building_name


# 2. AGENT
class Agent(models.Model):
    agent_id = models.AutoField(
        primary_key=True,
        db_column='Agent_ID'
    )
    first_name = models.CharField(max_length=50, db_column='First_Name')
    last_name = models.CharField(max_length=50, db_column='Last_Name')
    building = models.ForeignKey(
        Building,
        on_delete=models.PROTECT,
        related_name='agents',
        db_column='Building_ID'
    )

    class Meta:
        db_table = 'AGENT'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# 3. VENUE
class Venue(models.Model):
    venue_id = models.AutoField(
        primary_key=True,
        db_column='Venue_ID'
    )
    venue_name = models.CharField(max_length=100, db_column='Venue_Name')
    venue_type = models.CharField(max_length=100, db_column='Venue_Type')
    floor = models.CharField(max_length=5, db_column='Floor')
    floor_area_sqm = models.FloatField(db_column='Floor_Area_Sqm')
    capacity = models.PositiveIntegerField(db_column='Capacity')
    building = models.ForeignKey(
        Building,
        on_delete=models.PROTECT,
        related_name='venues',
        db_column='Building_ID'
    )

    class Meta:
        db_table = 'VENUE'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(floor_area_sqm__gt=0),
                name='venue_positive_floor_area'
            ),
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name='venue_positive_capacity'
            ),
        ]

    def __str__(self):
        return self.venue_name
    
# 4. VENUE_ASSIGNMENT
class VenueAssignment(models.Model):
    assignment_id = models.AutoField(
        primary_key=True,
        db_column='Assignment_ID'
    )
    start_date = models.DateField(db_column='Start_Date')
    end_date = models.DateField(
        null=True,
        blank=True,
        db_column='End_Date'
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        related_name='venue_assignments',
        db_column='Agent_ID'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='assignments',
        db_column='Venue_ID'
    )

    class Meta:
        db_table = 'VENUE_ASSIGNMENT'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F('start_date')),
                name='assignment_valid_dates'
            )
        ]

    def __str__(self):
        return f"{self.agent} - {self.venue}"


# 5. RENOVATION
class Renovation(models.Model):
    renovation_id = models.AutoField(
        primary_key=True,
        db_column='Renovation_ID'
    )
    date_started = models.DateField(db_column='Date_Started')
    date_completed = models.DateField(
        null=True,
        blank=True,
        db_column='Date_Completed'
    )
    remarks = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='Remarks'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='renovations',
        db_column='Venue_ID'
    )

    class Meta:
        db_table = 'RENOVATION'
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(date_completed__isnull=True) |
                    models.Q(date_completed__gte=models.F('date_started'))
                ),
                name='renovation_valid_dates'
            )
        ]

    def __str__(self):
        return f"Renovation {self.renovation_id} - {self.venue}"


# 6. AMENITY_TYPE
class AmenityType(models.Model):
    amenity_id = models.AutoField(
        primary_key=True,
        db_column='Amenity_ID'
    )
    amenity_name = models.CharField(
        max_length=50,
        db_column='Amenity_Name'
    )

    class Meta:
        db_table = 'AMENITY_TYPE'

    def __str__(self):
        return self.amenity_name


# 7. VENUE_AMENITY
class VenueAmenity(models.Model):
    venue_amenity_id = models.AutoField(
        primary_key=True,
        db_column='Venue_Amenity_ID'
    )
    description = models.CharField(max_length=150, db_column='Description')
    quantity = models.PositiveIntegerField(db_column='Quantity')
    installation_date = models.DateField(db_column='Installation_Date')
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='venue_amenities',
        db_column='Venue_ID'
    )
    amenity = models.ForeignKey(
        AmenityType,
        on_delete=models.PROTECT,
        related_name='venue_amenities',
        db_column='Amenity_ID'
    )

    class Meta:
        db_table = 'VENUE_AMENITY'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='venue_amenity_positive_quantity'
            )
        ]

    def __str__(self):
        return f"{self.venue} - {self.amenity}"


# 8. CUSTOMER
class Customer(models.Model):
    customer_id = models.AutoField(
        primary_key=True,
        db_column='Customer_ID'
    )
    first_name = models.CharField(max_length=50, db_column='First_Name')
    last_name = models.CharField(max_length=50, db_column='Last_Name')
    middle_initial = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        default=None,
        db_column='Middle_Initial'
    )
    birth_date = models.DateField(db_column='Birth_Date')
    customer_location = models.CharField(
        max_length=100,
        db_column='Customer_Location'
    )

    class Meta:
        db_table = 'CUSTOMER'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# 9. RESERVATION
class Reservation(models.Model):
    reservation_id = models.AutoField(
        primary_key=True,
        db_column='Reservation_ID'
    )
    start_datetime = models.DateTimeField(db_column='Start_DateTime')
    end_datetime = models.DateTimeField(db_column='End_DateTime')
    expected_participants = models.PositiveIntegerField(
        db_column='Expected_Participants'
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='reservations',
        db_column='Venue_ID'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='reservations',
        db_column='Customer_ID'
    )

    class Meta:
        db_table = 'RESERVATION'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    end_datetime__gt=models.F('start_datetime')
                ),
                name='reservation_valid_dates'
            ),
            models.CheckConstraint(
                condition=models.Q(expected_participants__gt=0),
                name='reservation_positive_participants'
            )
        ]

    def __str__(self):
        return f"Reservation {self.reservation_id}"
