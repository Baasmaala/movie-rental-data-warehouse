import pandas as pd
from sqlalchemy import create_engine

# =====================================================
# DATABASE CONNECTIONS
# =====================================================

username = "root"
password = "root123"
host = "localhost"

# Source Database (Sakila)
sakila_engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}/sakila_prof"
)

# Data Warehouse Database
dw_engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}/movie_dw"
)

print("Connections successful!")

# =====================================================
# LOAD DIMCUSTOMER
# =====================================================

customer_query = """
SELECT
    customer.customer_id,
    CONCAT(customer.first_name, ' ', customer.last_name) AS full_name,
    customer.email,
    city.city,
    country.country,
    customer.active
FROM customer
JOIN address ON customer.address_id = address.address_id
JOIN city    ON address.city_id    = city.city_id
JOIN country ON city.country_id    = country.country_id
"""

dim_customer = pd.read_sql(customer_query, sakila_engine)

dim_customer.columns = [
    "Customer_ID",
    "Full_Name",
    "Email",
    "City",
    "Country",
    "Active_Status"
]

# Data quality: drop nulls in business key, strip whitespace
dim_customer = dim_customer.dropna(subset=["Customer_ID"])
dim_customer["City"] = dim_customer["City"].str.strip().str.title()
dim_customer["Country"] = dim_customer["Country"].str.strip().str.title()

# Surrogate key
dim_customer.insert(0, "Customer_Key", range(1, len(dim_customer) + 1))

dim_customer.to_sql("dimcustomer", dw_engine, if_exists="append", index=False)
print(f"dimcustomer loaded: {len(dim_customer)} rows")

# =====================================================
# LOAD DIMFILM
# =====================================================
# Note: film_category is many-to-many but Sakila assigns exactly one category
# per film in practice. We pick MIN(category_id) for safety to enforce 1:1.

film_query = """
SELECT
    film.film_id,
    film.title,
    category.name     AS category,
    language.name     AS language,
    film.rental_rate,
    film.rental_duration,
    film.length,
    film.release_year,
    CASE
        WHEN COUNT(inventory.inventory_id) > 0 THEN 'Available'
        ELSE 'Not Available'
    END AS inventory_status
FROM film
JOIN language ON film.language_id = language.language_id
JOIN film_category ON film.film_id = film_category.film_id
JOIN category ON film_category.category_id = category.category_id
LEFT JOIN inventory ON film.film_id = inventory.film_id
GROUP BY
    film.film_id, film.title, category.name, language.name,
    film.rental_rate, film.rental_duration, film.length, film.release_year
"""

dim_film = pd.read_sql(film_query, sakila_engine)

dim_film.columns = [
    "Film_ID",
    "Film_Title",
    "Category",
    "Language",
    "Rental_Rate",
    "Rental_Duration",  # expected duration, used for late-return detection
    "Film_Length",
    "Release_Year",
    "Inventory_Status"
]

# Deduplicate on Film_ID (defense against m:n category)
dim_film = dim_film.drop_duplicates(subset=["Film_ID"], keep="first")

dim_film.insert(0, "Film_Key", range(1, len(dim_film) + 1))

dim_film.to_sql("dimfilm", dw_engine, if_exists="append", index=False)
print(f"dimfilm loaded: {len(dim_film)} rows")

# =====================================================
# LOAD DIMSTORE
# =====================================================

store_query = """
SELECT
    store.store_id,
    CONCAT(staff.first_name, ' ', staff.last_name) AS manager_name,
    city.city,
    country.country
FROM store
JOIN staff   ON store.manager_staff_id = staff.staff_id
JOIN address ON store.address_id       = address.address_id
JOIN city    ON address.city_id        = city.city_id
JOIN country ON city.country_id        = country.country_id
"""

dim_store = pd.read_sql(store_query, sakila_engine)
dim_store.columns = ["Store_ID", "Store_Manager", "City", "Country"]
dim_store.insert(0, "Store_Key", range(1, len(dim_store) + 1))

dim_store.to_sql("dimstore", dw_engine, if_exists="append", index=False)
print(f"dimstore loaded: {len(dim_store)} rows")

# =====================================================
# LOAD DIMSTAFF
# =====================================================

staff_query = """
SELECT
    staff.staff_id,
    CONCAT(staff.first_name, ' ', staff.last_name) AS staff_name,
    staff.store_id,
    staff.active
FROM staff
"""

dim_staff = pd.read_sql(staff_query, sakila_engine)
dim_staff.columns = [
    "Staff_ID", "Staff_Name", "Store_Assignment", "Active_Status"
]
dim_staff.insert(0, "Staff_Key", range(1, len(dim_staff) + 1))

dim_staff.to_sql("dimstaff", dw_engine, if_exists="append", index=False)
print(f"dimstaff loaded: {len(dim_staff)} rows")

# =====================================================
# LOAD DIMDATE
# =====================================================
# Collect ALL distinct dates across the source so every fact date has a key.

date_query = """
SELECT DATE(rental_date)  AS d FROM rental
UNION
SELECT DATE(return_date)  AS d FROM rental WHERE return_date IS NOT NULL
UNION
SELECT DATE(payment_date) AS d FROM payment
"""

dim_date = pd.read_sql(date_query, sakila_engine)
dim_date.columns = ["Full_Date"]
dim_date = dim_date.dropna().drop_duplicates()
dim_date["Full_Date"] = pd.to_datetime(dim_date["Full_Date"])
dim_date = dim_date.sort_values("Full_Date").reset_index(drop=True)

# Date attributes
dim_date["Day"]         = dim_date["Full_Date"].dt.day
dim_date["Month"]       = dim_date["Full_Date"].dt.month
dim_date["Month_Name"]  = dim_date["Full_Date"].dt.strftime("%B")
dim_date["Quarter"]     = dim_date["Full_Date"].dt.quarter
dim_date["Year"]        = dim_date["Full_Date"].dt.year
dim_date["Day_Of_Week"] = dim_date["Full_Date"].dt.strftime("%A")
dim_date["Is_Weekend"]  = dim_date["Full_Date"].dt.dayofweek >= 5

# Surrogate key as YYYYMMDD (human-readable and deterministic)
dim_date.insert(
    0,
    "Date_Key",
    dim_date["Full_Date"].dt.strftime("%Y%m%d").astype(int)
)

dim_date.to_sql("dimdate", dw_engine, if_exists="append", index=False)
print(f"dimdate loaded: {len(dim_date)} rows")

# =====================================================
# BUILD LOOKUP MAPS (business key -> surrogate key)
# These let the fact-table ETL translate OLTP IDs into warehouse keys.
# =====================================================

customer_map = dict(zip(dim_customer["Customer_ID"], dim_customer["Customer_Key"]))
film_map     = dict(zip(dim_film["Film_ID"],         dim_film["Film_Key"]))
store_map    = dict(zip(dim_store["Store_ID"],       dim_store["Store_Key"]))
staff_map    = dict(zip(dim_staff["Staff_ID"],       dim_staff["Staff_Key"]))

print("Lookup maps built.")

# =====================================================
# LOAD FACTRENTAL
# =====================================================
# We pull expected rental_duration from film so late return can be
# computed correctly per film instead of using a flat 7 days.

rental_query = """
SELECT
    rental.rental_id,
    rental.customer_id,
    inventory.film_id,
    inventory.store_id,
    rental.staff_id,
    rental.rental_date,
    rental.return_date,
    DATEDIFF(rental.return_date, rental.rental_date) AS rental_duration_actual,
    film.rental_duration AS rental_duration_expected
FROM rental
JOIN inventory ON rental.inventory_id = inventory.inventory_id
JOIN film      ON inventory.film_id    = film.film_id
"""

rental_df = pd.read_sql(rental_query, sakila_engine)

# Translate OLTP IDs to warehouse surrogate keys
fact_rental = pd.DataFrame({
    "Rental_Key":      rental_df["rental_id"],
    "Customer_Key":    rental_df["customer_id"].map(customer_map),
    "Film_Key":        rental_df["film_id"].map(film_map),
    "Store_Key":       rental_df["store_id"].map(store_map),
    "Staff_Key":       rental_df["staff_id"].map(staff_map),
    "Rental_Date_Key": pd.to_datetime(rental_df["rental_date"]).dt.strftime("%Y%m%d").astype(int),
    "Return_Date_Key": pd.to_datetime(rental_df["return_date"]).dt.strftime("%Y%m%d"),
    "Rental_Count":    1,
    "Rental_Duration": rental_df["rental_duration_actual"],
})

# Return_Date_Key: keep as nullable Int64 (some rentals not yet returned)
fact_rental["Return_Date_Key"] = pd.to_numeric(
    fact_rental["Return_Date_Key"], errors="coerce"
).astype("Int64")

# Proper late return: actual > expected (per film), False if not yet returned
fact_rental["Late_Return_Flag"] = (
    rental_df["rental_duration_actual"] > rental_df["rental_duration_expected"]
).fillna(False)

# Data quality: drop rows where any FK didn't resolve
before = len(fact_rental)
fact_rental = fact_rental.dropna(
    subset=["Customer_Key", "Film_Key", "Store_Key", "Staff_Key"]
)
if before != len(fact_rental):
    print(f"  warning: dropped {before - len(fact_rental)} rental rows with unresolved keys")

fact_rental.to_sql("factrental", dw_engine, if_exists="append", index=False)
print(f"factrental loaded: {len(fact_rental)} rows")

# =====================================================
# LOAD FACTPAYMENT
# =====================================================
# Include Film_Key and Store_Key so revenue-by-film / revenue-by-store
# queries actually work.

payment_query = """
SELECT
    payment.payment_id,
    payment.customer_id,
    inventory.film_id,
    inventory.store_id,
    payment.staff_id,
    payment.payment_date,
    payment.amount
FROM payment
JOIN rental    ON payment.rental_id   = rental.rental_id
JOIN inventory ON rental.inventory_id = inventory.inventory_id
"""

payment_df = pd.read_sql(payment_query, sakila_engine)

fact_payment = pd.DataFrame({
    "Payment_Key":      payment_df["payment_id"],
    "Customer_Key":     payment_df["customer_id"].map(customer_map),
    "Film_Key":         payment_df["film_id"].map(film_map),
    "Store_Key":        payment_df["store_id"].map(store_map),
    "Staff_Key":        payment_df["staff_id"].map(staff_map),
    "Payment_Date_Key": pd.to_datetime(payment_df["payment_date"]).dt.strftime("%Y%m%d").astype(int),
    "Payment_Amount":   payment_df["amount"],
})

# Data quality: positive payment amounts only, no unresolved FKs
fact_payment = fact_payment[fact_payment["Payment_Amount"] > 0]
fact_payment = fact_payment.dropna(
    subset=["Customer_Key", "Film_Key", "Store_Key", "Staff_Key"]
)

fact_payment.to_sql("factpayment", dw_engine, if_exists="append", index=False)
print(f"factpayment loaded: {len(fact_payment)} rows")

# =====================================================
# LOAD FACTINVENTORY
# =====================================================

inventory_query = """
SELECT
    inventory.inventory_id,
    inventory.film_id,
    inventory.store_id
FROM inventory
"""

inventory_df = pd.read_sql(inventory_query, sakila_engine)

fact_inventory = pd.DataFrame({
    "Inventory_Key":   inventory_df["inventory_id"],
    "Film_Key":        inventory_df["film_id"].map(film_map),
    "Store_Key":       inventory_df["store_id"].map(store_map),
    "Inventory_Count": 1,
})

fact_inventory = fact_inventory.dropna(subset=["Film_Key", "Store_Key"])

fact_inventory.to_sql("factinventory", dw_engine, if_exists="append", index=False)
print(f"factinventory loaded: {len(fact_inventory)} rows")

# =====================================================
# ETL COMPLETED
# =====================================================

print("\nETL process completed successfully!")