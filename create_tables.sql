-- Drop in reverse dependency order if re-running
DROP TABLE IF EXISTS FactRental;
DROP TABLE IF EXISTS FactPayment;
DROP TABLE IF EXISTS FactInventory;
DROP TABLE IF EXISTS DimCustomer;
DROP TABLE IF EXISTS DimFilm;
DROP TABLE IF EXISTS DimStore;
DROP TABLE IF EXISTS DimStaff;
DROP TABLE IF EXISTS DimDate;
 
-- =====================================================
-- DIMENSION: DimDate
-- Generated during ETL from all date columns across OLTP.
-- =====================================================
CREATE TABLE DimDate (
    Date_Key      INT PRIMARY KEY,
    Full_Date     DATE NOT NULL,
    Day           INT NOT NULL,
    Month         INT NOT NULL,
    Month_Name    VARCHAR(15),
    Quarter       INT NOT NULL,
    Year          INT NOT NULL,
    Day_Of_Week   VARCHAR(15),
    Is_Weekend    BOOLEAN
);
 
-- =====================================================
-- DIMENSION: DimCustomer
-- Source: customer, address, city, country
-- =====================================================
CREATE TABLE DimCustomer (
    Customer_Key   INT PRIMARY KEY,
    Customer_ID    INT NOT NULL,           -- business key from OLTP
    Full_Name      VARCHAR(255),
    Email          VARCHAR(255),
    City           VARCHAR(100),
    Country        VARCHAR(100),
    Active_Status  TINYINT
);
 
-- =====================================================
-- DIMENSION: DimFilm
-- Source: film, category, film_category, language
-- =====================================================
CREATE TABLE DimFilm (
    Film_Key          INT PRIMARY KEY,
    Film_ID           INT NOT NULL,        -- business key from OLTP
    Film_Title        VARCHAR(255),
    Category          VARCHAR(100),
    Language          VARCHAR(50),
    Rental_Rate       DECIMAL(5,2),
    Rental_Duration   INT,                 -- expected duration from film table
    Film_Length       INT,
    Release_Year      INT,
    Inventory_Status  VARCHAR(20)
);
 
-- =====================================================
-- DIMENSION: DimStore
-- Source: store, staff (manager), address, city, country
-- =====================================================
CREATE TABLE DimStore (
    Store_Key      INT PRIMARY KEY,
    Store_ID       INT NOT NULL,           -- business key from OLTP
    Store_Manager  VARCHAR(255),
    City           VARCHAR(100),
    Country        VARCHAR(100)
);
 
-- =====================================================
-- DIMENSION: DimStaff
-- Source: staff, store
-- =====================================================
CREATE TABLE DimStaff (
    Staff_Key         INT PRIMARY KEY,
    Staff_ID          INT NOT NULL,        -- business key from OLTP
    Staff_Name        VARCHAR(255),
    Store_Assignment  INT,
    Active_Status     TINYINT
);
 
-- =====================================================
-- FACT: FactRental
-- Grain: one row per rental transaction
-- =====================================================
CREATE TABLE FactRental (
    Rental_Key        INT PRIMARY KEY,
    Customer_Key      INT NOT NULL,
    Film_Key          INT NOT NULL,
    Store_Key         INT NOT NULL,
    Staff_Key         INT NOT NULL,
    Rental_Date_Key   INT NOT NULL,
    Return_Date_Key   INT,                 -- nullable: film may not yet be returned
    Rental_Count      INT DEFAULT 1,
    Rental_Duration   INT,                 -- in days
    Late_Return_Flag  BOOLEAN,
    FOREIGN KEY (Customer_Key)    REFERENCES DimCustomer(Customer_Key),
    FOREIGN KEY (Film_Key)        REFERENCES DimFilm(Film_Key),
    FOREIGN KEY (Store_Key)       REFERENCES DimStore(Store_Key),
    FOREIGN KEY (Staff_Key)       REFERENCES DimStaff(Staff_Key),
    FOREIGN KEY (Rental_Date_Key) REFERENCES DimDate(Date_Key),
    FOREIGN KEY (Return_Date_Key) REFERENCES DimDate(Date_Key)
);
 
-- =====================================================
-- FACT: FactPayment
-- Grain: one row per payment transaction
-- =====================================================
CREATE TABLE FactPayment (
    Payment_Key       INT PRIMARY KEY,
    Customer_Key      INT NOT NULL,
    Film_Key          INT NOT NULL,
    Store_Key         INT NOT NULL,
    Staff_Key         INT NOT NULL,
    Payment_Date_Key  INT NOT NULL,
    Payment_Amount    DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (Customer_Key)     REFERENCES DimCustomer(Customer_Key),
    FOREIGN KEY (Film_Key)         REFERENCES DimFilm(Film_Key),
    FOREIGN KEY (Store_Key)        REFERENCES DimStore(Store_Key),
    FOREIGN KEY (Staff_Key)        REFERENCES DimStaff(Staff_Key),
    FOREIGN KEY (Payment_Date_Key) REFERENCES DimDate(Date_Key)
);
 
-- =====================================================
-- FACT: FactInventory
-- Grain: one row per inventory item per store
-- =====================================================
CREATE TABLE FactInventory (
    Inventory_Key    INT PRIMARY KEY,
    Film_Key         INT NOT NULL,
    Store_Key        INT NOT NULL,
    Inventory_Count  INT DEFAULT 1,
    FOREIGN KEY (Film_Key)  REFERENCES DimFilm(Film_Key),
    FOREIGN KEY (Store_Key) REFERENCES DimStore(Store_Key)
);
 
-- =====================================================
-- Indexes for query performance
-- =====================================================
CREATE INDEX idx_factrental_customer  ON FactRental(Customer_Key);
CREATE INDEX idx_factrental_film      ON FactRental(Film_Key);
CREATE INDEX idx_factrental_date      ON FactRental(Rental_Date_Key);
CREATE INDEX idx_factpayment_customer ON FactPayment(Customer_Key);
CREATE INDEX idx_factpayment_film     ON FactPayment(Film_Key);
CREATE INDEX idx_factpayment_date     ON FactPayment(Payment_Date_Key);
 

 