
USE movie_dw;

-- =====================================================
-- 1. Most rented films
-- =====================================================
SELECT
    f.Film_Title,
    f.Category,
    COUNT(*) AS Total_Rentals
FROM FactRental r
JOIN DimFilm f ON r.Film_Key = f.Film_Key
GROUP BY f.Film_Key, f.Film_Title, f.Category
ORDER BY Total_Rentals DESC
LIMIT 20;

-- =====================================================
-- 2. Highest revenue films
-- =====================================================
SELECT
    f.Film_Title,
    f.Category,
    SUM(p.Payment_Amount) AS Revenue,
    COUNT(*) AS Payment_Count
FROM FactPayment p
JOIN DimFilm f ON p.Film_Key = f.Film_Key
GROUP BY f.Film_Key, f.Film_Title, f.Category
ORDER BY Revenue DESC
LIMIT 20;



-- =====================================================
-- 4. Customers with most rentals
-- =====================================================
SELECT
    c.Full_Name,
    c.City,
    c.Country,
    COUNT(*) AS Rental_Count
FROM FactRental r
JOIN DimCustomer c ON r.Customer_Key = c.Customer_Key
GROUP BY c.Customer_Key, c.Full_Name, c.City, c.Country
ORDER BY Rental_Count DESC
LIMIT 20;

-- =====================================================
-- 5. Customers generating the highest revenue
-- =====================================================
SELECT
    c.Full_Name,
    c.City,
    c.Country,
    SUM(p.Payment_Amount) AS Total_Spent
FROM FactPayment p
JOIN DimCustomer c ON p.Customer_Key = c.Customer_Key
GROUP BY c.Customer_Key, c.Full_Name, c.City, c.Country
ORDER BY Total_Spent DESC
LIMIT 20;

-- =====================================================
-- 6. Rental activity by month (trend analysis)
-- =====================================================
SELECT
    d.Year,
    d.Month,
    d.Month_Name,
    COUNT(*) AS Rentals
FROM FactRental r
JOIN DimDate d ON r.Rental_Date_Key = d.Date_Key
GROUP BY d.Year, d.Month, d.Month_Name
ORDER BY d.Year, d.Month;

-- =====================================================
-- 7. Revenue by month / quarter / year
-- =====================================================
SELECT
    d.Year,
    d.Quarter,
    d.Month_Name,
    SUM(p.Payment_Amount) AS Revenue,
    COUNT(*) AS Transactions
FROM FactPayment p
JOIN DimDate d ON p.Payment_Date_Key = d.Date_Key
GROUP BY d.Year, d.Quarter, d.Month, d.Month_Name
ORDER BY d.Year, d.Month;




-- =====================================================
-- 13. Store inventory levels (by store and category)
-- =====================================================
SELECT
    s.Store_ID,
    s.City,
    f.Category,
    COUNT(*) AS Inventory_Count
FROM FactInventory i
JOIN DimStore s ON i.Store_Key = s.Store_Key
JOIN DimFilm  f ON i.Film_Key  = f.Film_Key
GROUP BY s.Store_Key, s.Store_ID, s.City, f.Category
ORDER BY s.Store_ID, Inventory_Count DESC;

