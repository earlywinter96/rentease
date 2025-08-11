RentEase – Rental Management Web App
Team Name: Hemant Solanki
Team ID: 230
Developer: Solo Developer – Hemant Solanki

📌 Project Overview
RentEase is a comprehensive rental management platform designed for seamless booking, listing, and managing of sports facilities and rental spaces. Built for efficiency and scalability, the platform supports role-based access (Admin, Owner, User) and integrates OTP verification for secure logins (with admin OTP bypass).

The goal is to simplify the rental experience for both owners and customers while giving admins complete control over approvals and listings.

🚀 Features
For Users
Search and filter facilities by location, sport, and price range
View facility details, images, and available courts
Book courts with a preferred date and time
OTP-based secure login and verification

For Owners
Add, edit, and manage their facilities
Upload facility images and set hourly prices
Manage court availability

For Admins
Approve or reject new facility listings
Manage all user accounts and bookings
Direct admin login without OTP
Access dedicated admin dashboards

🛠 Tech Stack
Backend: Python, Flask, SQLAlchemy
Frontend: HTML5, CSS3, Bootstrap 5, Jinja2
Database: SQLite / PostgreSQL
Authentication: Flask-Login, OTP verification via Email (SMTP)
Deployment Ready For: WSGI servers (Gunicorn, uWSGI)

rentease/
│── app/
│   ├── routes/         # All Flask Blueprints
│   ├── models.py       # Database Models
│   ├── forms.py        # WTForms
│   ├── utils.py        # Helper Functions (OTP, Email)
│   ├── templates/      # Jinja2 HTML Templates
│   ├── static/         # Images, CSS, JS
│── venv/               # Virtual Environment (ignored in Git)
│── README.md
│── requirements.txt
│── config.py
│── run.py


⚡ How to Run Locally
Clone the repository
git clone https://github.com/earlywinter96/rentease.git
cd rentease
Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
Install dependencies
pip install -r requirements.txt
Run the server
flask run
Access in browser
http://127.0.0.1:5000

🎯 Hackathon Relevance
Fully meets the problem statement for rental management
Focused on secure authentication, role-based access control, and admin approvals
Built to be extended with payment gateways, analytics, and reporting

📧 Contact
Hemant Solanki
GitHub: earlywinter96
Email: hemantsolanki333@gmail.com




