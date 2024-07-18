# RENT & RETURN
#### Video Demo: [Click Here](https://youtu.be/DvRq9gnoUcQ)
#### Description:
This is my final project for CS50x using Python and Flask
Rent & Return is a simple website that allows you to rent and return rented products. It consists of two types of users, the business owner and the client. New customers must register to access system options.
The business owner can add and edit products as well as have access to the product list. You can also edit the insurance amount for the loan of the products, which in this case is a fixed figure for all products. You have access to the actual list of currently rented products and can return products requested by customers by accessing the list. You can also access the history of all operations carried out. All listings are sortable, paginated and searchable.
The client can rent products by accessing the list of products, see the list of products they have rented at the moment as well as consult the history of operations they have carried out.


## Explaining the project and the database


All information about users, products and rent are stored in business.db.


I used sqlite3 to manager the database.

### Sqlite3:
I needed six tables for my database:

- Table real: the products rented at the moment are found.

- Table history: traces of all system operations.

- Table seguro: product income tax.

- Table products: list of products.

- Table operation: possible actions in the system.

- Table users: user list.

## How to use:

As a customer, after logging in you will see the list of the products you have rented at the moment. If you want to see the complete list of products you must click on the navigation bar where it says Products.
- When viewing the list of products, if you want to rent one, you must select the product you want to rent in the select box and enter the quantity you want and select the date range you want to rent the product. Then you must click on rent. Then you will see the list of the products that you have rented.
- If you want to see the history of your actions in the system, you must click on History in the navigation bar.
- If you want to see the list of your rented products, you must click on Real in the navigation bar.

As the business owner, after logging in you will see the list of products rented at the moment.
- If you want to change the tax that is charged to clients for the income of products, you must click on the navigation bar where it says Insurance. Then you must click on the table that is shown where it says edit and enter the new amount and then click on the Edit button.
- If you want to see the list of products you must click on the navigation bar where it says Products. Then you will see the list and if you want to add a new product you must click on New. Then you will see a form where you must add the data of the new product and then click on the Save button. You will then see the list of products.
- If you want to edit a product, you must click on the table in the row where the desired product is located where it says Edit. Then you must modify the data of the product you want and click on the Save button.
- If you want to see the list of actions you have done on the system, you must click on History in the navigation bar.
- If you want to rent a product you must click on Rent in the navigation bar. You will then be able to see all the products and their availability. You must select the product you want to rent in the select box and enter the amount you want and select the date range you want to rent the product. Then you must click on rent.
- If you want to return a rented product, you must click on the navigation bar where it says Return. Then you must click on the Return text in the table row where the product you want to return is located.

The tables are paginated and it is possible to sort the columns and search within them.
You can watch the [Video Demo](https://youtu.be/DvRq9gnoUcQ) for a more visual presentation.

## How I made this:
This web application was built using a Python framework called [Flask](https://flask.palletsprojects.com/en/3.0.x/). Use a part of the design from [C$50 Finance](https://finance.cs50.net/login).


In the root directory are the following files:
- `app.py` contains the code to run almost the entire application. Manage routes and store data in the database.
- `business.db` is the database where all the information is stored.
- `helpers.py` contains helper functions.
- `requirements.txt` contains the names of the external packages required to compile and run this project.

The "static" folder is where CSS and JavaScript files are stored. Inside this folder is `app.js` which is a JavaScript file and `styles.css` which is the CSS file that contains some styles. I have also used Bootstrap for the look and feel of my web application.

The `templates` folder contains the html files.
- `edit_product.html` is the web page that's that allows you to edit products.
- `index.html` is the web page that displays the homepage.
- `layout.html` is the jinja template that the other html pages use.
- `login.html` is the login page.
- `register.html` is the page that is shown when someone's registering a new account.
- `history.html` is the web page that shows the history of user actions.
- `insurance.html` shows and allows you to edit the amount that customers are charged for insurance.
- `new_product.html` allows adding a new product.
- `products.html` shows the list of products.
- `rent.html` allows you to rent a product.
- `return.html` allows you to return a rented product.

