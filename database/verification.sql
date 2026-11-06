-- CSCI 41: Venue Management Database
-- Database verification queries
-- Run these queries after migrating and seeding the database.

-- Checks if 9 tables exists
SELECT name AS Table_Name
FROM sqlite_master
WHERE type = 'table'
  AND name IN (
    'BUILDING',
    'AGENT',
    'VENUE',
    'VENUE_ASSIGNMENT',
    'RENOVATION',
    'AMENITY_TYPE',
    'VENUE_AMENITY',
    'CUSTOMER',
    'RESERVATION'
  )
ORDER BY name;


-- 2Checks the no. of records in each table
SELECT 'BUILDING' AS Table_Name, COUNT(*) AS Record_Count FROM BUILDING
UNION ALL
SELECT 'AGENT', COUNT(*) FROM AGENT
UNION ALL
SELECT 'VENUE', COUNT(*) FROM VENUE
UNION ALL
SELECT 'VENUE_ASSIGNMENT', COUNT(*) FROM VENUE_ASSIGNMENT
UNION ALL
SELECT 'RENOVATION', COUNT(*) FROM RENOVATION
UNION ALL
SELECT 'AMENITY_TYPE', COUNT(*) FROM AMENITY_TYPE
UNION ALL
SELECT 'VENUE_AMENITY', COUNT(*) FROM VENUE_AMENITY
UNION ALL
SELECT 'CUSTOMER', COUNT(*) FROM CUSTOMER
UNION ALL
SELECT 'RESERVATION', COUNT(*) FROM RESERVATION;


-- Foreign key checks
PRAGMA foreign_key_check;

PRAGMA foreign_key_list('AGENT');
PRAGMA foreign_key_list('VENUE');
PRAGMA foreign_key_list('VENUE_ASSIGNMENT');
PRAGMA foreign_key_list('RENOVATION');
PRAGMA foreign_key_list('VENUE_AMENITY');
PRAGMA foreign_key_list('RESERVATION');


-- Checks the final CREATE TABLE description
SELECT name AS Table_Name, sql AS Create_Statement
FROM sqlite_master
WHERE type = 'table'
  AND name IN (
    'BUILDING',
    'AGENT',
    'VENUE',
    'VENUE_ASSIGNMENT',
    'RENOVATION',
    'AMENITY_TYPE',
    'VENUE_AMENITY',
    'CUSTOMER',
    'RESERVATION'
  )
ORDER BY name;
