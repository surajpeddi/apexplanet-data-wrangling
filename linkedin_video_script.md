# LinkedIn Video Walkthrough — Script \& Post Caption

The task asks for a 3–5 min screen recording walking through the data issues and cleaning process.
Here's a script you can read from / adapt in your own words while screen-recording. Swap in your own
name and any personal observations — this is a starting point, not something to read word-for-word.

## Video script (\~4 minutes)

**0:00 – 0:30 | Intro**

> "Hi, I'm PEDDI SURAJ, a Data Analytics Intern at ApexPlanet Software. For Task 1, I was given a
> 1,000-row sales transactions dataset and asked to profile it, clean it, and turn it into an
> analysis-ready dataset. I'll walk through the issues I found and how I handled each one."

**0:30 – 1:30 | Show the raw data + the issues found**

> "Here's the raw dataset — sales orders with customer details, product, and revenue fields.
> When I profiled it, I found a few real issues:
> - Age was missing in 20 rows, and City was missing in 13.
> - Order\_ID is supposed to be a unique order number, but I found one ID — ORD100050 — that's
>   shared by 9 completely different orders.
> - The Order\_Date column was stored as plain text, not an actual date type.
> - And most interestingly — Customer\_ID and Customer\_Name don't line up consistently. 52
>   customer IDs are linked to more than one name, and there are only 425 unique names for
>   947 unique IDs — so Customer\_Name can't be trusted as a unique identifier."

**1:30 – 3:00 | Walk through the cleaning script**

> "Here's my cleaning script. Instead of just dropping rows with missing data, I \[show the script]:
> - Median-imputed the missing ages and flagged exactly which rows were imputed
> - Filled missing cities with an explicit 'Unknown' label rather than guessing
> - Kept the original Order\_ID for traceability but added a guaranteed-unique Row\_UID column,
>   plus a flag marking the affected rows
> - Converted Order\_Date to a real datetime so I could pull out year, month, weekday, etc.
> - Flagged the Customer\_ID/Customer\_Name mismatches instead of arbitrarily picking one as 'correct'
> - I also checked for statistical outliers in Total\_Sales using the IQR method — found 19 — but
>   chose to flag them instead of deleting them, since they're plausible bulk orders, not errors."

**3:00 – 3:45 | Feature engineering + final output**

> "From there I engineered a few features that'll make analysis easier later: order year, month,
> quarter, weekday, a weekend flag, an age-group bucket, how many orders each customer has placed,
> and a high-value-order flag for the top 25% of orders by revenue. The final output is a clean,
> 27-column, fully analysis-ready CSV with zero missing values."

**3:45 – 4:00 | Close**

> "All the code, the data dictionary, and the full data quality report are on my GitHub — link in
> the post. Thanks for watching!"

## Suggested LinkedIn post caption

> 🚀 Task 1 of my Data Analytics Internship at @ApexPlanet Software Pvt Ltd — Data Immersion \& Wrangling!
>
> I took a raw 1,000-row sales dataset and turned it into an analysis-ready one. Along the way I found
> (and fixed/flagged, never silently dropped):
> ✅ Missing values in Age \& City
> ✅ A non-unique Order\_ID shared across 9 different orders
> ✅ Order\_Date stored as plain text instead of a real date
> ✅ Customer\_ID/Customer\_Name inconsistencies that would've thrown off customer-level reporting
> ✅ 19 statistical outliers in revenue — flagged rather than deleted, since they were genuine
>    high-value orders
>
> Then engineered features like order year/month/weekday, age groups, and a high-value-order flag
> to make the dataset analysis-ready.
>
> 🎥 Full walkthrough video above
> 💻 Code + data dictionary + full data quality report on GitHub: \[your repo link]
>
> #DataAnalytics #Internship #Python #Pandas #DataCleaning #ApexPlanet

