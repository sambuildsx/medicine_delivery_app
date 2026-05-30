# Medicine Delivery App

A full-stack medicine delivery platform built as part of the SDE Intern Coding Assignment.

The application allows users to browse medicines, manage their cart, verify delivery serviceability, place orders, and track order history. The project is built using React, FastAPI, PostgreSQL, and Docker Compose, with additional features such as JWT authentication, coupon support, AI-powered prescription scanning, and transaction-safe order processing.

---

## Live Demo

**Demo Video:** [Watch Demo](https://youtu.be/NuHZa3jy2os)

The demo covers:

* User authentication
* Medicine catalogue and search
* Cart management
* Serviceability validation
* Coupon application
* Dynamic fee calculation
* Order placement
* Order history
* AI prescription scanning
* API documentation

---

## Screenshots

### Medicine Catalogue

![Medicine Catalogue](https://github.com/user-attachments/assets/daf9dffc-2210-4d40-8060-8347b725e3d9)

### Cart

![Cart](https://github.com/user-attachments/assets/1262ed31-ba34-4862-94e4-7521319a1036)

![Cart Summary](https://github.com/user-attachments/assets/18952a46-75fb-476e-906d-7a7528261e0b)

### Checkout

![Checkout](https://github.com/user-attachments/assets/ddb2bef2-403e-4837-af6e-990726d4d90d)

### Order History

![Order History](https://github.com/user-attachments/assets/8bece731-d2db-4964-bfba-ba6b44ef3668)

### Prescription Scanner

![Prescription Scanner](https://github.com/user-attachments/assets/4c121e85-53e5-4f73-b7c9-6a87da8b5c96)

---

## Features

### Medicine Catalogue

* Browse medicines with name, salt composition, pricing, stock availability, and prescription requirements
* Search medicines by name or salt composition
* Prevent adding out-of-stock medicines to cart

### Cart Management

* Add medicines to cart
* Update quantities
* Remove medicines from cart
* Real-time stock validation
* Automatic cart total calculation

### Serviceability Check

* Delivery validation based on distance
* Serviceable for distances up to 5000 meters
* Estimated delivery time calculation

### Dynamic Fee Engine

* Small Cart Fee for orders below ₹199
* Delivery Fee for distances above 2 km
* Late Night Fee between 10 PM and 6 AM

### Order Management

* Secure order placement
* Automatic stock deduction
* Cart reset after successful checkout
* Order history and order details

### Authentication

* User registration
* User login
* JWT-based authentication and authorization

### Coupon Support

* Apply discount coupons during checkout
* Dynamic payable amount calculation

### AI Prescription Scanning

* Upload prescription images
* Google Gemini-powered OCR processing
* Extract medicine information from prescriptions

---

## Key Engineering Decisions

### Transaction-Safe Checkout

Order placement uses PostgreSQL row-level locking (`SELECT FOR UPDATE`) to prevent race conditions and ensure stock consistency during concurrent purchases.

### Server-Side Validation

Critical validations such as stock availability, serviceability checks, coupon validation, and order processing are performed on the server to ensure data integrity and prevent client-side manipulation.

### Containerized Development

Docker Compose provides a reproducible development environment with minimal setup, allowing the entire application stack to be started with a single command.

## Tech Stack

### Frontend

* React.js (Vite)
* React Router DOM
* CSS
* Lucide React Icons

### Backend

* FastAPI
* PostgreSQL
* Pydantic
* JWT Authentication

### Testing

* Pytest

### DevOps

* Docker
* Docker Compose

### AI Integration

* Google Gemini API

---

## API Overview

| Method | Endpoint              |
| ------ | --------------------- |
| GET    | /medicines            |
| GET    | /medicines/search     |
| GET    | /medicines/{id}       |
| POST   | /cart/items           |
| GET    | /cart                 |
| PATCH  | /cart/items/{id}      |
| DELETE | /cart/items/{id}      |
| POST   | /serviceability/check |
| POST   | /orders               |
| GET    | /orders               |
| GET    | /orders/{id}          |

Interactive API documentation is available through Swagger UI at:

http://localhost:8000/docs

---

## Getting Started

### Prerequisites

* Docker Desktop

### Clone Repository

```bash
git clone <repository-url>
cd medicine-delivery-app
```

### Run Application

```bash
docker compose up --build
```

### Application URLs

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

## Demo Credentials

User Account

```text
Email: sam11@gmail.com
Password: 123456
```

You may also create a new account using the registration page and log in with your own credentials.

---

## Environment Variables

Example:

```env
JWT_SECRET=your_secret_key

GEMINI_API_KEY=your_gemini_api_key
```
> GEMINI_API_KEY is only required for the AI prescription scanning feature.
---

## Running Tests

```bash
cd backend

pytest -v
```

---

## Seed Data

The application automatically seeds:

* Sample users
* Medicines
* Coupons

during startup.

---

## Bonus Features Implemented

* JWT Authentication
* Coupon Support
* Google Gemini Prescription Scanner
* Docker Compose Setup
* Concurrent Stock Handling using PostgreSQL Row Locking

---

