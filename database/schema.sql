-- CSCI 41: Venue Management Database
-- Final SQLite table definitions and integrity constraints
-- Generated from the migrated database schema

PRAGMA foreign_keys = ON;

-- BUILDING
CREATE TABLE "BUILDING" ("Building_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Building_Name" varchar(150) NOT NULL, "Street" varchar(150) NOT NULL, "District" varchar(100) NOT NULL, "City" varchar(100) NOT NULL, "Acquisition_Date" date NOT NULL);

-- AGENT
CREATE TABLE "AGENT" ("Agent_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "First_Name" varchar(100) NOT NULL, "Last_Name" varchar(100) NOT NULL, "Building_ID" integer NOT NULL REFERENCES "BUILDING" ("Building_ID") DEFERRABLE INITIALLY DEFERRED);

-- VENUE
CREATE TABLE "VENUE" ("Venue_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Venue_Name" varchar(150) NOT NULL, "Venue_Type" varchar(100) NOT NULL, "Floor" integer NOT NULL, "Floor_Area_Sqm" real NOT NULL, "Capacity" integer unsigned NOT NULL CHECK ("Capacity" >= 0), "Building_ID" integer NOT NULL REFERENCES "BUILDING" ("Building_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "venue_positive_floor_area" CHECK ("Floor_Area_Sqm" > 0.0), CONSTRAINT "venue_positive_capacity" CHECK ("Capacity" > 0));

-- VENUE_ASSIGNMENT
CREATE TABLE "VENUE_ASSIGNMENT" ("Assignment_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Start_Date" date NOT NULL, "End_Date" date NOT NULL, "Agent_ID" integer NOT NULL REFERENCES "AGENT" ("Agent_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" integer NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "assignment_valid_dates" CHECK ("End_Date" >= ("Start_Date")));

-- RENOVATION
CREATE TABLE "RENOVATION" ("Renovation_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Date_Started" date NOT NULL, "Date_Completed" date NULL, "Remarks" text NOT NULL, "Venue_ID" integer NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "renovation_valid_dates" CHECK (("Date_Completed" IS NULL OR "Date_Completed" >= ("Date_Started"))));

-- AMENITY_TYPE
CREATE TABLE "AMENITY_TYPE" ("Amenity_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Amenity_Name" varchar(100) NOT NULL);

-- VENUE_AMENITY
CREATE TABLE "VENUE_AMENITY" ("Venue_Amenity_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Description" text NOT NULL, "Quantity" integer unsigned NOT NULL CHECK ("Quantity" >= 0), "Installation_Date" date NOT NULL, "Amenity_ID" integer NOT NULL REFERENCES "AMENITY_TYPE" ("Amenity_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" integer NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "venue_amenity_positive_quantity" CHECK ("Quantity" > 0));

-- CUSTOMER
CREATE TABLE "CUSTOMER" ("Customer_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "First_Name" varchar(100) NOT NULL, "Last_Name" varchar(100) NOT NULL, "Middle_Initial" varchar(1) NOT NULL, "Birth_Date" date NOT NULL, "Customer_Location" varchar(200) NOT NULL);

-- RESERVATION
CREATE TABLE "RESERVATION" ("Reservation_ID" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "Start_DateTime" datetime NOT NULL, "End_DateTime" datetime NOT NULL, "Expected_Participants" integer unsigned NOT NULL CHECK ("Expected_Participants" >= 0), "Customer_ID" integer NOT NULL REFERENCES "CUSTOMER" ("Customer_ID") DEFERRABLE INITIALLY DEFERRED, "Venue_ID" integer NOT NULL REFERENCES "VENUE" ("Venue_ID") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "reservation_valid_dates" CHECK ("End_DateTime" > ("Start_DateTime")), CONSTRAINT "reservation_positive_participants" CHECK ("Expected_Participants" > 0));
