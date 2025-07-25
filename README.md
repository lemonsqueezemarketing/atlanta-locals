
# 🏙️ Atlanta Locals — Community Search Engine for ATL

**Atlanta Locals** is a custom-built, community-first local search app designed to help Atlanta residents discover the best small businesses, services, events, and real estate across the city — all in one place. This project is built using Flask and inspired by platforms like Yelp, Thumbtack, HubSpot, Eventbrite, and Zillow — but purpose-built for Atlanta.

---

## 🔧 Tech Stack

- **Backend:** Python Flask (App Factory pattern)
- **Frontend:** HTML, CSS, JavaScript (modular static files per route)
- **Database:** SQLite (expandable)
- **Web Server:** Gunicorn
- **Deployment:** AWS EC2 (Ubuntu)
- **Reverse Proxy (Production):** Nginx
- **Domain Management:** GoDaddy

---

## 📁 Project Structure

```
atlanta-locals/
├── app/
│   ├── __init__.py         # Initializes Flask app and database
│   ├── models.py           # SQLAlchemy models (e.g., Property)
│   ├── routes.py           # All route definitions
│   ├── templates/          # HTML views (organized by section)
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
├── main.py                 # Gunicorn entrypoint
├── requirements.txt        # Python dependencies
├── config.py               # Flask config file
├── run.py                  # Optional script runner
└── README.md
```

---

## 🌐 Features

### ✅ Views
- `/` — Home: Local weather, news, spotlight
- `/directory` — Business discovery (Yelp-style)
- `/book` — Book ATL professionals (Thumbtack-style)
- `/shop` — Local e-commerce (Amazon-style)
- `/blog` — Atlanta Local EDU Hub (SEO & Business Blog)
- `/events` — Atlanta Events (Eventbrite-style)
- `/real-estate` — Real estate listings (Zillow-style)
- `/about` — Mission + Founder story

---

## 🛠️ Setup Instructions (Local)

### 1. Clone the Repo

```bash
git clone https://github.com/lemonsqueezemarketing/atlanta-locals.git
cd atlanta-locals
```

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the Flask App with Gunicorn

```bash
gunicorn main:app
```

Open `http://127.0.0.1:8000` in your browser to view the app.

---

## 🚀 Deployment Guide

### Hosting on AWS EC2 (Ubuntu)

1. Launch EC2 Instance (Ubuntu)
2. SSH into instance
3. Add user data to:
   - Update server
   - Install packages
   - Clone project
   - Set up virtualenv
4. Use Gunicorn + Nginx for production
5. Connect your GoDaddy domain to EC2 static IP

> A full deployment walkthrough is included in the `docs/deployment.md` (optional).

---

## 🧪 Test Database Connection

Database: SQLite  
Test Model: `Property`  
Defined in `models.py`.  
Routes to test: `/real-estate` will query all properties and print them to the terminal to confirm DB connection.

---

## 🤝 Contributors

- **Mike W.** — Founder, Strategy & Vision
- **Lemon Squeeze Marketing** — Development & Design Team

---

## 📢 Mission

> "Our goal is to empower Atlanta small business owners with a true SEO advantage — built for locals, by locals."

This app connects real Atlanta residents with the gems in their own city — whether that’s a hidden tea lounge, a local moving service, or a rising artist.

---

## 🛡️ License

MIT License (or specify your preferred license)
