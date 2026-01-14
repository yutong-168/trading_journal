# Trading Journal APP functional requirements

## Authentication

**1. Must have a basic authentication functions. (registration, sign in, forget password)**

**2. Make sure the user must sign in before performing any operations**



## Home page

1. after signing in, there should be a home page. **The info displayed on the home page can be flexible (such as date, list of journals created today, calendar, etc.)** 

**2. Important: **

**a. a button to create a new journal.**

**b. a place to view the journals created.**

**c. a place to view the list of all trading journals. The list should support filtering (by name, by date, by tag, etc.)**

**d. clicking on an entry in the list should lead to a detail page** 

**e. A place to view trades and profit & loss**

3. There should be a side panel that contains buttons allow user to **change settings, manage profile, manage account**



## Trading Journals

1. A trading journal shoud have **date, tag (treat this as a searching criteria, for instance, user may want to search find all journals made on the FOMC days, the user then can create a custom tag called FOMC), orders (list of Order item) (optional), notes (optional), images (optional)**

2. **Order Item:** Users can make 0 to many orders in one day. There should be a place to allow user to create orders in the Trading Journal detail page. Each order item should have: **ticker, price, direction (buy or sell), status (pending or filled), note (optional), images (optional)** 
   **Challenge:** usually a complete trade is consisted of multiple (buys and sells). The user could close a postion months after its entry. So, **the system should have a way to link an order with another order in the past. This is also useful to keep track of the profit and loss of the account**

   **Optional challenge: **the order can be Options. An option contract is different from normal stock trades (**strike price, expiration date, implied volatilities, etc.**)

## Profit and loss

1. Once a complete trade is recorded, the system should automatically record the profit and loss of such trade. User can view them in separate page