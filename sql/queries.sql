-- BrickView - 30 Business SQL Queries
-- Same queries used live by pages/3_SQL_Queries.py (see sql_queries.py for
-- the Python dict that feeds the Streamlit UI). Kept here as a plain .sql
-- file so the queries can be run directly against brickview.db, e.g.:
--   sqlite3 brickview.db < sql/queries.sql

-- ============================================================
-- 1. Property & Pricing Analysis
-- ============================================================

-- 1. Average listing price by city
SELECT City, ROUND(AVG(Price), 0) AS Avg_Price
FROM listings GROUP BY City ORDER BY Avg_Price DESC;

-- 2. Average price per sqft by property type
SELECT Property_Type, ROUND(AVG(Price_per_sqft), 2) AS Avg_Price_Per_Sqft
FROM listings GROUP BY Property_Type ORDER BY Avg_Price_Per_Sqft DESC;

-- 3. Furnishing status impact on price
SELECT a.Furnishing_Status, ROUND(AVG(l.Price), 0) AS Avg_Price, COUNT(*) AS N
FROM listings l JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY a.Furnishing_Status ORDER BY Avg_Price DESC;

-- 4. Metro distance vs price (bucketed)
SELECT CASE
         WHEN a.Metro_Distance_Km < 2 THEN '< 2 km'
         WHEN a.Metro_Distance_Km < 5 THEN '2-5 km'
         WHEN a.Metro_Distance_Km < 10 THEN '5-10 km'
         ELSE '10+ km' END AS Distance_Band,
       ROUND(AVG(l.Price), 0) AS Avg_Price
FROM listings l JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY Distance_Band ORDER BY Avg_Price DESC;

-- 5. Rented vs non-rented pricing
SELECT a.Is_Rented, ROUND(AVG(l.Price), 0) AS Avg_Price, COUNT(*) AS N
FROM listings l JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY a.Is_Rented;

-- 6. Bedrooms/bathrooms impact on price
SELECT a.Bedrooms, a.Bathrooms, ROUND(AVG(l.Price), 0) AS Avg_Price, COUNT(*) AS N
FROM listings l JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY a.Bedrooms, a.Bathrooms ORDER BY a.Bedrooms, a.Bathrooms;

-- 7. Parking & power backup impact on sale price
SELECT a.Parking_Available, a.Power_Backup, ROUND(AVG(s.Sale_Price), 0) AS Avg_Sale_Price
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY a.Parking_Available, a.Power_Backup;

-- 8. Year built vs listing price
SELECT (a.Year_Built / 10) * 10 AS Decade_Built, ROUND(AVG(l.Price), 0) AS Avg_Price
FROM listings l JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY Decade_Built ORDER BY Decade_Built;

-- 9. Highest priced cities
SELECT City, ROUND(AVG(Price), 0) AS Avg_Price
FROM listings GROUP BY City ORDER BY Avg_Price DESC LIMIT 5;

-- 10. Price bucket distribution
SELECT CASE
         WHEN Price < 300000 THEN 'Under 300K'
         WHEN Price < 600000 THEN '300K-600K'
         WHEN Price < 900000 THEN '600K-900K'
         ELSE '900K+' END AS Price_Bucket,
       COUNT(*) AS N
FROM listings GROUP BY Price_Bucket ORDER BY N DESC;

-- ============================================================
-- 2. Sales & Market Performance
-- ============================================================

-- 11. Average days on market by city
SELECT l.City, ROUND(AVG(s.Days_On_Market), 1) AS Avg_Days_On_Market
FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
GROUP BY l.City ORDER BY Avg_Days_On_Market;

-- 12. Fastest selling property types
SELECT l.Property_Type, ROUND(AVG(s.Days_On_Market), 1) AS Avg_Days_On_Market
FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
GROUP BY l.Property_Type ORDER BY Avg_Days_On_Market;

-- 13. % sold above listing price
SELECT ROUND(100.0 * SUM(CASE WHEN s.Sale_Price > l.Price THEN 1 ELSE 0 END) / COUNT(*), 1)
       AS Pct_Sold_Above_List
FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID;

-- 14. Sale-to-list price ratio by city
SELECT l.City, ROUND(AVG(s.Sale_Price * 1.0 / l.Price), 3) AS Avg_Sale_To_List_Ratio
FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
GROUP BY l.City ORDER BY Avg_Sale_To_List_Ratio DESC;

-- 15. Listings that took more than 90 days to sell
SELECT l.Listing_ID, l.City, l.Property_Type, s.Days_On_Market
FROM sales s JOIN listings l ON s.Listing_ID = l.Listing_ID
WHERE s.Days_On_Market > 90 ORDER BY s.Days_On_Market DESC;

-- 16. Metro distance vs time on market
SELECT CASE
         WHEN a.Metro_Distance_Km < 2 THEN '< 2 km'
         WHEN a.Metro_Distance_Km < 5 THEN '2-5 km'
         WHEN a.Metro_Distance_Km < 10 THEN '5-10 km'
         ELSE '10+ km' END AS Distance_Band,
       ROUND(AVG(s.Days_On_Market), 1) AS Avg_Days_On_Market
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN property_attributes a ON l.Listing_ID = a.Listing_ID
GROUP BY Distance_Band ORDER BY Avg_Days_On_Market;

-- 17. Monthly sales trend
SELECT strftime('%Y-%m', Sale_Date) AS Month, COUNT(*) AS Sales_Count,
       ROUND(SUM(Sale_Price), 0) AS Total_Revenue
FROM sales GROUP BY Month ORDER BY Month;

-- 18. Currently unsold listings
SELECT l.Listing_ID, l.City, l.Property_Type, l.Price, l.Listed_Date
FROM listings l
LEFT JOIN sales s ON l.Listing_ID = s.Listing_ID
WHERE s.Sale_ID IS NULL;

-- ============================================================
-- 3. Agent Performance
-- ============================================================

-- 19. Agents with the most closed sales
SELECT ag.Name, COUNT(s.Sale_ID) AS Sales_Closed
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN agents ag ON l.Agent_ID = ag.Agent_ID
GROUP BY ag.Name ORDER BY Sales_Closed DESC LIMIT 10;

-- 20. Top agents by total sales revenue
SELECT ag.Name, ROUND(SUM(s.Sale_Price), 0) AS Total_Revenue
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN agents ag ON l.Agent_ID = ag.Agent_ID
GROUP BY ag.Name ORDER BY Total_Revenue DESC LIMIT 10;

-- 21. Agents who close deals fastest
SELECT ag.Name, ROUND(AVG(s.Days_On_Market), 1) AS Avg_Closing_Days
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN agents ag ON l.Agent_ID = ag.Agent_ID
GROUP BY ag.Name ORDER BY Avg_Closing_Days ASC LIMIT 10;

-- 22. Experience vs deals closed
SELECT Experience_Years, ROUND(AVG(Deals_Closed), 1) AS Avg_Deals_Closed
FROM agents GROUP BY Experience_Years ORDER BY Experience_Years;

-- 23. Ratings vs closing speed
SELECT ROUND(Rating) AS Rating_Band, ROUND(AVG(Avg_Closing_Days), 1) AS Avg_Closing_Days
FROM agents GROUP BY Rating_Band ORDER BY Rating_Band DESC;

-- 24. Average commission earned by agent
SELECT ag.Name, ROUND(SUM(s.Sale_Price * ag.Commission_Rate / 100.0), 0) AS Est_Commission_Earned
FROM sales s
JOIN listings l ON s.Listing_ID = l.Listing_ID
JOIN agents ag ON l.Agent_ID = ag.Agent_ID
GROUP BY ag.Name ORDER BY Est_Commission_Earned DESC LIMIT 10;

-- 25. Agents with most active (unsold) listings
SELECT ag.Name, COUNT(l.Listing_ID) AS Active_Listings
FROM listings l
JOIN agents ag ON l.Agent_ID = ag.Agent_ID
LEFT JOIN sales s ON l.Listing_ID = s.Listing_ID
WHERE s.Sale_ID IS NULL
GROUP BY ag.Name ORDER BY Active_Listings DESC LIMIT 10;

-- ============================================================
-- 4. Buyer & Financing Behavior
-- ============================================================

-- 26. Investor vs end user split
SELECT Buyer_Type, COUNT(*) AS N,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM buyers), 1) AS Pct
FROM buyers GROUP BY Buyer_Type;

-- 27. Cities with highest loan uptake rate
SELECT l.City,
       ROUND(100.0 * SUM(CASE WHEN b.Loan_Taken THEN 1 ELSE 0 END) / COUNT(*), 1) AS Loan_Uptake_Pct
FROM buyers b
JOIN sales s ON b.Sale_ID = s.Sale_ID
JOIN listings l ON s.Listing_ID = l.Listing_ID
GROUP BY l.City ORDER BY Loan_Uptake_Pct DESC;

-- 28. Average loan amount by buyer type
SELECT Buyer_Type, ROUND(AVG(Loan_Amount), 0) AS Avg_Loan_Amount
FROM buyers WHERE Loan_Taken = 1 GROUP BY Buyer_Type;

-- 29. Most common payment mode
SELECT Payment_Mode, COUNT(*) AS N
FROM buyers GROUP BY Payment_Mode ORDER BY N DESC;

-- 30. Loan-backed purchases vs closing time
SELECT b.Loan_Taken, ROUND(AVG(s.Days_On_Market), 1) AS Avg_Days_On_Market
FROM buyers b JOIN sales s ON b.Sale_ID = s.Sale_ID
GROUP BY b.Loan_Taken;
