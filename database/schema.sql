CREATE TABLE "BUILDING" ("Building_Name" varchar(100) NOT NULL, "Street" varchar(100) NOT NULL, "District" varchar(50) NOT NULL, "City" varchar(50) NOT NULL, "Acquisition_Date" date NOT NULL, "Building_ID" varchar(8) NOT NULL PRIMARY KEY);

CREATE TABLE "AGENT" ("Agent_ID" varchar(8) NOT NULL PRIMARY KEY, "First_Name" varchar(50) NOT NULL, "Last_Name" varchar(50) NOT NULL, "Building_ID" varchar(8) NOT NULL REFERENCES "BUILDING" ("Building_ID") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "VENUE" ("Venue_Name" varchar(100) NOT NULL, "Venue_Type" varchar(100) NOT NULL, "Floor" varchar(5) NOT NULL, "Floor_Area_Sqm" real NOT NULL, "Capacity" integer unsigned NOT NULL CHECK ("Capacity" >= 0), "Building_ID" varchar(8) NOT NULL REFERENCES "BUILDING" ("Building_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" varchar(8) NOT NULL PRIMARY KEY, CONSTRAINT "venue_positive_floor_area" CHECK ("Floor_Area_Sqm" > 0.0), CONSTRAINT "venue_positive_capacity" CHECK ("Capacity" > 0));

CREATE TABLE "VENUE_ASSIGNMENT" ("Start_Date" date NOT NULL, "End_Date" date NULL, "Agent_ID" varchar(8) NOT NULL REFERENCES "AGENT" ("Agent_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" varchar(8) NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, "Assignment_ID" varchar(8) NOT NULL PRIMARY KEY, CONSTRAINT "assignment_valid_dates" CHECK ("End_Date" >= ("Start_Date")));

CREATE TABLE "RENOVATION" ("Renovation_ID" varchar(8) NOT NULL PRIMARY KEY, "Date_Started" date NOT NULL, "Date_Completed" date NULL, "Remarks" varchar(200) NULL, "Venue_ID" varchar(8) NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "renovation_valid_dates" CHECK (("Date_Completed" IS NULL OR "Date_Completed" >= ("Date_Started"))));

CREATE TABLE "AMENITY_TYPE" ("Amenity_Name" varchar(50) NOT NULL, "Amenity_ID" varchar(8) NOT NULL PRIMARY KEY);

CREATE TABLE "VENUE_AMENITY" ("Description" varchar(150) NOT NULL, "Quantity" integer unsigned NOT NULL CHECK ("Quantity" >= 0), "Installation_Date" date NOT NULL, "Amenity_ID" varchar(8) NOT NULL REFERENCES "AMENITY_TYPE" ("Amenity_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" varchar(8) NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_Amenity_ID" varchar(8) NOT NULL PRIMARY KEY, CONSTRAINT "venue_amenity_positive_quantity" CHECK ("Quantity" > 0));

CREATE TABLE "CUSTOMER" ("First_Name" varchar(50) NOT NULL, "Last_Name" varchar(50) NOT NULL, "Middle_Initial" varchar(2) NULL, "Birth_Date" date NOT NULL, "Customer_Location" varchar(100) NOT NULL, "Customer_ID" varchar(8) NOT NULL PRIMARY KEY);

CREATE TABLE "RESERVATION" ("Reservation_ID" varchar(8) NOT NULL PRIMARY KEY, "Start_DateTime" datetime NOT NULL, "End_DateTime" datetime NOT NULL, "Expected_Participants" integer unsigned NOT NULL CHECK ("Expected_Participants" >= 0), "Customer_ID" varchar(8) NOT NULL REFERENCES "CUSTOMER" ("Customer_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" varchar(8) NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "reservation_valid_dates" CHECK ("End_DateTime" > ("Start_DateTime")), CONSTRAINT "reservation_positive_participants" CHECK ("Expected_Participants" > 0));
