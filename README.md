# MedVibe | Premium Medicine Delivery Web App

A production-ready, highly polished Medicine Delivery Web App built using a modern decoupled architecture. The backend is powered by **Python FastAPI** and **SQLAlchemy** (supporting native SQLite shared-memory in local development and production-grade **PostgreSQL**). The frontend is a beautiful, fluid React single-page application built on **Vite**, featuring a premium custom-curated **Vanilla CSS Dark-Theme Glassmorphism UI**.

---

## 🌟 Key Features
1. **Premium Responsive UI**: Curated medical-emerald and deep carbon colors with frosted glass backdrops, micro-interactions, responsive catalog grids, and glowing feedback.
2. **Robust Authentication**: Secure registration and login utilizing custom cryptographically secure PBKDF2-HMAC password hashing with JWT token protection.
3. **Flexible SQL Engine**: Native PostgreSQL DDL support with an intelligent local SQLite automatic fallback for zero-friction evaluation.
4. **Dynamic Cart Fee Matrix**: Evaluates all rules simultaneously:
   - **Small Cart Fee**: +₹29 if discounted item total < ₹199.
   - **Delivery Fee**: +₹40 if store distance > 2000m (serviceable limit <= 5000m).
   - **Late Night Surcharge**: +₹25 based on server timezone evaluated in Indian Standard Time (IST) (10 PM to 6 AM).
5. **Voucher Validation**: Supports seed flat-discount (`FLAT50`) and percentage-discount (`PCT20`) coupons with minimum order values, active flags, and expiry checks.
6. **Thread-Safe Concurrency**: Employs row-level transaction blocking (`with_for_update`) during order checkout to prevent stock double-spending or overselling.

---

## 📁 Repository Structure
```
medicine-delivery-app/
├── backend/
│   ├── app/
│   │   ├── config.py           # Pydantic settings schema
│   │   ├── database.py         # DB connection & SQLite fallback logic
│   │   ├── models.py           # SQLAlchemy declarative entities
│   │   ├── schemas.py          # Pydantic validation schemas
│   │   ├── auth.py             # Secure PBKDF2 & JWT utilities
│   │   ├── seed.py             # Seed data logic
│   │   ├── main.py             # FastAPI entry coordinate
│   │   └── routers/            # Auth, Medicines, Cart, Orders, Coupons, Serviceability
│   ├── tests/                  # Pytest verification suites
│   ├── pytest.ini
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # ProtectedRoute layouts & Navbar
│   │   ├── pages/              # Cart, Checkout, LoginRegister, MedicineListing, OrderHistory, OrderSuccess
│   │   ├── context/            # Centralized AuthContext with fetch wrappers
│   │   ├── App.jsx             # React Router routing setup
│   │   ├── index.css           # Curated CSS custom design variables & glassmorphism
│   │   └── main.jsx
│   ├── tests/                  # Vitest UI rendering and button state tests
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js          # API proxy routing definition
│   └── vitest.config.js        # Vitest parameters
├── database.sql                # Production PostgreSQL schema
├── docker-compose.yml          # Optional container orchestration
└── README.md                   # This instruction manual
```

---

## 🛠️ Prerequisites
- **Python 3.10+** (Python 3.13.5 fully supported)
- **Node.js v18+** (Node v24.13.1 fully supported)
- **npm** (npm 11.8.0 fully supported)

---

## 🚀 Native Local Setup (No Docker Required)

### 1. Database Setup
The application is pre-configured to automatically attempt connecting to a PostgreSQL server running locally. If a local PostgreSQL service is not detected, it will **automatically and seamlessly fall back to a local SQLite database file** (`medicine_delivery.db` generated inside the `backend/` directory) with all tables created and populated with seed data on first boot! No manual SQL commands or database setups are required.

### 2. Run Backend (FastAPI)
1. Open a new terminal in the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the development server using uvicorn:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The backend will boot up, create database tables automatically, and seed them. It will be accessible at `http://localhost:8000`.*

### 3. Run Frontend (Vite + React)
1. Open a new terminal in the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Boot up the Vite local server:
   ```bash
   npm run dev
   ```
   *The frontend is proxied to redirect API queries to the backend automatically. Open `http://localhost:5173` in your browser to experience the beautiful dark-themed MedVibe dashboard.*

---

## 🧪 Running Test Suites

### 1. Backend Tests (pytest)
Our backend test suite performs 28 unit and integration validations isolating database operations using an in-memory SQLite shared database, including testing all cart fees, serviceability ranges, OOS add errors, stock locks, and active coupon structures.
To execute backend tests:
```bash
cd backend
pytest
```

### 2. Frontend Tests (Vitest)
Our frontend tests verify correct reactive total billing displays, out-of-stock cart button disabling states, and serviceability checks.
To execute frontend tests:
```bash
cd frontend
npm run test
```

---

## 🗃️ Seeding Overview
On startup, the seeder validates if records exist and will automatically seed:
- **5 Users**:
  - `john.doe@example.com` (password: `password123`)
  - `jane.smith@example.com` (password: `password123`)
  - `sam.jones@example.com` (password: `password123`)
  - `alice.williams@example.com` (password: `password123`)
  - `bob.brown@example.com` (password: `password123`)
- **21 Medicines**: Curated mix of OTC and prescription items, with diverse stock counts including one out-of-stock item (`Ranitidine 150mg (OOS)`) to test cart validation edge cases.
- **2 Coupons**:
  - `FLAT50`: Flat ₹50 off (minimum order value ₹299).
  - `PCT20`: 20% off (minimum order value ₹199).

---

## 📡 API Usage Examples (cURL)

### 1. Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "customer@example.com", "password": "password123", "full_name": "Jane Customer"}'
```

### 2. User Login (returns JWT Token)
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "customer@example.com", "password": "password123"}'
```

### 3. List Medicines Catalogue
```bash
curl -X GET "http://localhost:8000/medicines"
```

### 4. Search Medicines (by Name or Salt)
```bash
curl -X GET "http://localhost:8000/medicines/search?q=Paracetamol"
```

### 5. Check Serviceability (Serviceable limit <= 5000m)
```bash
curl -X POST "http://localhost:8000/serviceability/check" \
     -H "Content-Type: application/json" \
     -d '{"pincode": "560001", "distance": 1500}'
```