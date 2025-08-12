#  RentEase – Sports Facility & Court Booking Platform

RentEase is a **Flask-based sports facility booking platform** built for the Hackathon.  
It allows users to search, book, and pay for sports courts and facilities online, with an **admin approval system** for facility listings.

Demo Video : https://www.loom.com/share/7ea9b199c86348b9ba1373acddcacf0b?sid=69f1ea9c-d58c-4e32-9fc9-55f09e31050a
---

🏆 Authors
Hemant Solanki – Backend & Flask Development
Hackathon Team RentEase
Team no 230 

## 🚀 Features

### 🔹 User Features
- Browse and search sports facilities with filters (location, sport type, price range)
- View facility details and available courts
- Book courts with a specified date and time
- Pay online using **Stripe INR** (supports card & UPI)
- Download **professional PDF invoices** for confirmed bookings

### 🔹 Admin Features
- Admin approval panel for new facility listings
- Approve or reject facilities
- Manage user accounts

### 🔹 Extras
- OTP-based authentication for secure login/registration
- Responsive and clean UI
- Invoice generation with RentEase logo and unique invoice numbers
- Hackathon mode – payment can be skipped, and an invoice generated instantly

---

## 🛠️ Tech Stack

| Layer        | Technology |
|--------------|------------|
| **Backend**  | Python 3, Flask, SQLAlchemy |
| **Frontend** | HTML, CSS (Bootstrap), Jinja2 Templates |
| **Database** | SQLite (default), can be switched to PostgreSQL/MySQL |
| **Payments** | Stripe API (INR support) |
| **PDF**      | ReportLab |
| **Auth**     | Flask-Login, OTP Email Verification |

---

## 📂 Project Structure

rentease/
├── app/
│ ├── routes/ # Flask Blueprints (auth, booking, facility, etc.)
│ ├── templates/ # Jinja2 HTML templates
│ ├── static/ # CSS, JS, Images
│ ├── models.py # Database models
│ ├── forms.py # WTForms definitions
│ ├── init.py # App factory
│ └── ...
├── requirements.txt
├── README.md
└── run.py


---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/rentease.git
cd rentease
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
Create a .env file in the root directory:
FLASK_APP=run.py
FLASK_ENV=development
STRIPE_SECRET_KEY=sk_test_yourkey
STRIPE_PUBLISHABLE_KEY=pk_test_yourkey
SECRET_KEY=supersecret
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password

flask db upgrade
flask run
Visit: http://127.0.0.1:5000

💳 Hackathon Mode (Skip Payments)
For demo purposes, you can skip Stripe payments:

Book a court → Checkout → Instant PDF Invoice Download.

📜 License
This project is for educational/hackathon purposes.
Feel free to fork and modify for personal or commercial use.





