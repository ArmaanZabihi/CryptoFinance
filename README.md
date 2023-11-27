# CryptoFinance
Project ReadMe: Bitcoin Trading Platform

Overview

This project is a comprehensive Bitcoin trading website designed to offer users a seamless experience in buying, selling, and monitoring Bitcoin prices. Developed using SQL Alchemy, the platform features a robust backend with custom databases for Transaction and User data, ensuring secure and efficient data management.

Key Features

User Authentication: The site includes features for user registration, login, and logout, ensuring secure access to personal accounts.
Bitcoin Transactions: Users can buy and sell Bitcoin, with all transactions securely recorded in the custom-built Transaction database.
Live Bitcoin Pricing: Leveraging the CoinGecko API, the platform provides real-time Bitcoin price quotes.
Account Management: Users can manage their accounts, including the functionality to add cash for transactions.
Transaction History: Each user has access to their transaction history, allowing them to keep track of their Bitcoin investments.
Technical Details

Backend Development: The backend is powered by main.py, which houses all the routes for the application's functionality.
Databases:
User Database: Manages user information, including credentials and account details.
Transaction Database: Records all user transactions, such as buying and selling Bitcoin.
API Integration: The CoinGecko API is integrated for fetching live Bitcoin prices.
SQLAlchemy: Used for database handling, providing a powerful ORM layer for efficient data manipulation.
Routes

/buy: Allows users to purchase Bitcoin.
/sell: Enables users to sell their Bitcoin holdings.
/quote: Provides live Bitcoin price quotes.
/add_cash: Functionality for users to add funds to their account for transactions.
/login: Handles user login.
/register: For new users to create an account.
/logout: Logs users out of their accounts.
Getting Started

To get started with this project:

Clone the Repository: Clone the project to your local machine.
Install Dependencies: Ensure that all required libraries and frameworks, including SQLAlchemy, are installed.
Database Setup: Initialize the User and Transaction databases using SQLAlchemy.
API Key: Obtain an API key from CoinGecko and configure it within the application.
Run the Application: Start the server and navigate to the website to begin trading.
Security and Performance

Secure Authentication: Passwords are hashed and stored securely.
Efficient Data Handling: SQL Alchemy ensures efficient querying and data manipulation.
API Rate Limiting: The integration with CoinGecko API is designed to handle rate limiting and ensure uninterrupted service.
Future Enhancements and issues faced
A few complications faced in the building of this project was the creation of databases. Often it is better practice to use an external DB.
The color of the site was not shown though a CSS file was made.
The terminal provided quite a few errors that needed to be ironed out. 
Extended Cryptocurrency Support: Plans to include additional cryptocurrencies beyond Bitcoin suchh as ETH,etc.
Advanced Transaction Features: Implementation of features like limit orders and transaction notifications.
User Interface Improvements: Continuous improvement of the user interface for enhanced user experience.
Conclusion

This Bitcoin trading platform is a full-featured, secure, and user-friendly website for cryptocurrency enthusiasts. It simplifies the process of trading Bitcoin, tracking prices, and managing cryptocurrency investments, making it an ideal choice for both beginners and experienced traders.
