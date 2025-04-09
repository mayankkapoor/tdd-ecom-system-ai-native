Notes:
- admin user: admin/password


Phased Development Plan (TDD & AI-Native Focus)

Phase 0: Setup & Foundation (The "Scaffolding")

Environment Setup:
Install Python, Pip, Git.
Set up a virtual environment (venv or conda).
Install Cursor IDE.
Initialize Git repository.
Create basic project structure (app/, tests/, requirements.txt, .gitignore).
AI Assist (Cursor): Ask Cursor to generate a standard Python project structure for a Flask/SQLAlchemy application. Ask for a basic .gitignore file for Python.
Install Core Dependencies: Add Flask, SQLAlchemy, pytest, pytest-cov, pytest-flask (and database driver if needed, e.g., psycopg2-binary for PostgreSQL later) to requirements.txt and install.
AI Assist (Cursor): Paste your initial requirements; ask Cursor to generate the requirements.txt file with common versions.
Basic Flask App: Create a minimal Flask app (app/__init__.py, app/routes.py) with a simple health check route (/ping returning pong).
Setup Testing: Configure pytest. Write the first test for the health check route (tests/test_routes.py).
TDD Cycle:
Red: Write test_ping() asserting a 200 status and "pong" response. Run pytest - it should fail.
Green: Implement the /ping route in app/routes.py. Run pytest - it should pass.
Refactor: Code is minimal, little to refactor yet.
AI Assist (Cursor): Ask Cursor to generate a basic pytest.ini configuration. Ask for a pytest fixture to set up the Flask test client. Ask to generate the initial test_ping() test structure based on the requirement.
Database Configuration: Configure SQLAlchemy to connect to the SQLite DB. Set up basic Flask-SQLAlchemy integration.
AI Assist (Cursor): "Generate Flask-SQLAlchemy configuration boilerplate for connecting to an SQLite database located at instance/myapp.db."
CI/CD Pipeline (Basic): Set up a simple GitHub Action (or GitLab CI) workflow that runs pytest on every push/pull request.
AI Assist (Cursor): "Generate a basic GitHub Actions workflow YAML file that checks out the code, sets up Python, installs dependencies from requirements.txt, and runs pytest."
Docker Setup (Optional): Create a Dockerfile and docker-compose.yml for building and running the application and potentially the database in containers.
AI Assist (Cursor): "Generate a Dockerfile for a Flask application using Gunicorn." "Generate a docker-compose.yml to run the Flask app service and a PostgreSQL service."
Phase 1: User Authentication & Authorization (Admin Only MVP)

Model: Define a simple User model (e.g., id, username, password_hash, role='admin'). Use SQLAlchemy.
AI Assist (Cursor): "Define a SQLAlchemy model named User with fields: id (primary key, integer), username (unique string), password_hash (string), role (string, default 'admin'). Include a method to hash passwords using Werkzeug and check passwords."
TDD for Model: Write tests for the User model (tests/test_models.py). Test creation, password hashing, password checking.
Red: Write test_user_creation, test_password_hashing, test_password_verification. Fail.
Green: Implement the model and methods. Pass.
Refactor: Improve clarity, add docstrings. Use Cursor to explain the hashing logic or suggest improvements.
Database Migrations: Introduce Alembic (or Flask-Migrate) for managing database schema changes. Create the initial migration for the User table.
AI Assist (Cursor): "Show me how to set up Flask-Migrate with my Flask-SQLAlchemy app."
TDD for Auth Routes: Plan basic routes (/login, /logout, maybe a protected /admin/dashboard placeholder). Use Flask-Login or JWT for session management.
Red: Write tests (tests/test_auth.py) for:
test_login_success (valid credentials, session set)
test_login_failure (invalid credentials)
test_logout (session cleared)
test_access_protected_route_unauthenticated (redirects to login)
test_access_protected_route_authenticated (succeeds)
AI Assist (Cursor): "Generate pytest tests for a Flask login route using Flask-Login. Include tests for success, failure (wrong password, user not found), and correct redirection."
Green: Implement the login/logout routes, session handling, and @login_required decorator logic. Use Cursor to generate boilerplate Flask route code, handle form data, interact with the User model, and integrate Flask-Login.
Refactor: Ensure security best practices (e.g., CSRF protection if using session cookies). Ask Cursor: "Review this Flask login code for potential security vulnerabilities."
Phase 2: Product Management

Model: Define Product model (SKU, Name, Description, Price, Category, Image URL placeholder, Stock Quantity, Is Active). Link stock here for simplicity initially.
AI Assist (Cursor): "Define a SQLAlchemy model Product with fields..." (specify types, constraints like unique SKU).
TDD for Model: Write tests for Product model creation, validations (e.g., price > 0, unique SKU).
Database Migration: Create migration for the Product table.
TDD for CRUD API/Routes: Define routes/API endpoints (e.g., POST /api/products, GET /api/products, GET /api/products/<sku>, PUT /api/products/<sku>, DELETE /api/products/<sku>). Protect these routes (require login).
Red: Write tests (tests/test_products.py) for each endpoint: success cases, error cases (invalid data, SKU not found, unauthorized access).
Example: test_create_product_success, test_create_product_missing_name, test_get_product_found, test_get_product_not_found, test_update_product_success, test_delete_product_unauthorized.
AI Assist (Cursor): "Generate pytest tests for a Flask REST API endpoint POST /api/products which creates a product. Include tests for valid data (201 Created), invalid data (400 Bad Request), and unauthorized access (401 Unauthorized)."
Green: Implement the Flask routes/views. Handle JSON request data, validate input, interact with the Product model using SQLAlchemy sessions, handle database commits/rollbacks, return appropriate JSON responses and status codes.
AI Assist (Cursor): "Generate a Flask route for POST /api/products. It should accept JSON data, validate it against the Product model requirements, create a new Product using SQLAlchemy, and return the created product data with a 201 status code. Ensure it requires login."
Refactor: Organize code (e.g., use Flask Blueprints). Improve error handling. Add input validation logic (perhaps using a library like Marshmallow or Pydantic). Ask Cursor: "Refactor this Flask route to use a Pydantic model for input validation."
AI Feature (Optional): Add a button/function in the management interface (or an API call) that takes product name/category and uses an LLM (via API call like OpenAI's) to generate a draft description. Use Cursor to help write the API call logic and handle the response. Write tests for this helper function.
Phase 3: Inventory Management (Integrated with Product)

Logic: Inventory is currently a field (stock_quantity) on the Product model. The core logic involves updating this field accurately.
TDD for Inventory Updates: Focus on testing the effects of actions on stock. Since orders don't exist yet, write tests for potential inventory adjustment functions/logic (which will be used later by orders).
Red: Write tests (tests/test_inventory.py or within test_products.py if tightly coupled):
test_decrement_stock_success
test_decrement_stock_insufficient_stock (should fail or raise error)
test_increment_stock_success
AI Assist (Cursor): "Generate pytest tests for a function adjust_stock(product_sku, quantity_change) that updates the stock_quantity of a Product in the database. Test positive changes, negative changes, and attempting to go below zero stock."
Green: Implement the adjust_stock function or methods within the Product service/repository layer. Ensure atomic updates if necessary (though less critical with SQLite initially). Use Cursor to help write the database update logic safely.
Refactor: Ensure the stock adjustment logic is robust and reusable.
Phase 4: Order Management

Models: Define Order (Order ID, Customer details, Date, Status, Total Amount) and OrderItem (links Order to Product, stores Quantity and Price at the time of order). Establish relationships (Order has many OrderItems, OrderItem links to one Product).
AI Assist (Cursor): "Define SQLAlchemy models Order and OrderItem with specified fields and a one-to-many relationship between them. OrderItem should also have a many-to-one relationship with Product."
Database Migrations: Create migrations for Order and OrderItem tables.
TDD for Order Creation Logic: This is crucial. Test the service function/logic that creates an order.
Red: Write tests (tests/test_orders.py) covering:
test_create_order_success (stock decreases, order/items created correctly, total calculated)
test_create_order_insufficient_stock (order fails, stock unchanged)
test_create_order_invalid_product_sku
test_calculate_order_total (separate unit test if logic is complex)
AI Assist (Cursor): "Generate pytest tests for an create_order(customer_data, items_list) service function. It should: create Order/OrderItem records, calculate the total based on current product prices, decrement stock for each item, and fail if any item has insufficient stock. Ensure database changes are rolled back on failure."
Green: Implement the order creation service logic. This involves database transactions: fetch products, check stock, create Order record, create OrderItem records, decrement stock for each product, commit. Use Cursor to help structure the transaction logic and error handling.
Refactor: Encapsulate order creation logic cleanly within a service class or functions. Ask Cursor: "Review this order creation logic for potential race conditions or transaction issues."
TDD for Order Viewing/Status Updates: Add API endpoints/routes (e.g., GET /api/orders, GET /api/orders/<id>, PUT /api/orders/<id>/status).
Red: Write tests for retrieving orders, filtering, updating status (e.g., test_update_order_status_valid, test_update_order_status_invalid_transition).
Green: Implement the routes, ensuring appropriate authorization.
Refactor: Improve querying efficiency if needed.
Phase 5: Basic Management Interface & Refinement

Interface Choice: Decide:
Simple HTML Templates: Use Flask's template engine (Jinja2) to render basic HTML pages for viewing/managing products and orders. Less modern but potentially faster for a simple backend tool.
API + Simple Frontend: Keep the Flask app as a pure API and build a separate, minimal frontend using HTML/CSS/JavaScript (maybe a simple framework like Alpine.js or HTMX) that consumes the API. More separation, potentially more work initially.
Use Django Admin: If you switched to Django, leverage its built-in admin interface for rapid CRUD views.
Recommendation: If using Flask, start with simple Jinja2 templates for speed.
Implement Views: Create Flask routes that render templates displaying lists of products/orders and forms for editing/creating. Use the existing service logic and models.
AI Assist (Cursor): "Generate a Flask route /admin/products that queries all products using SQLAlchemy and renders a Jinja2 template products.html, passing the products list." "Generate a basic Jinja2 template products.html to display a list of products in an HTML table with Edit/Delete links."
TDD (for Frontend?): TDD is harder for traditional frontend rendering. Focus TDD on the backend routes that serve the data to the templates. You can write integration tests that check if the correct template is rendered and potentially if key data appears in the HTML response (using libraries like BeautifulSoup in tests), but keep it high-level.
Refinement: Review the usability. Add basic searching/filtering to lists. Improve error messages.
AI Assist (Cursor): Ask for code improvements, alternative ways to structure template logic, or ways to make forms easier to handle in Flask.
Phase 6: Deployment & Monitoring

Choose Deployment Platform: Heroku, AWS (EC2, Elastic Beanstalk, Lambda), Google Cloud (App Engine, Cloud Run), DigitalOcean App Platform, etc.
Prepare for Production:
Switch Database to PostgreSQL (update config, install driver). Run migrations.
Configure a production web server (Gunicorn, uWSGI) behind a reverse proxy (Nginx).
Set environment variables for secrets (DB password, API keys, Flask secret key).
Configure logging.
AI Assist (Cursor): "Generate a Gunicorn configuration file." "Show an example Nginx configuration for proxying requests to a Gunicorn Flask app."
Deploy: Use Docker containers for easier deployment or follow platform-specific guides.
Monitoring: Set up basic health checks, logging aggregation (e.g., Sentry, Datadog), and potentially performance monitoring.
