# Environment Setup

This document describes how to set up the local development environment for testing the application.

---

## Prerequisites

- **Node.js** (v18+)
- **MySQL** (v8+)
- **Redis** (v7+)
- **Python** (v3.10+) — for automation scripts
- **npm** — included with Node.js

---

## Application Setup

### Backend

1. Navigate to the backend directory:
   ```
   cd back_end/
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file in `back_end/` with the following variables:
   ```
   DB_HOST=localhost
   DB_USER=<your_mysql_user>
   DB_PASSWORD=<your_mysql_password>
   DB_DATABASE=<your_database_name>
   ACCESS_TOKEN_SECRET=<your_jwt_secret>
   PORT=3036
   ```

4. Run database migrations (if applicable) or seed the database.

5. Start the backend server:
   ```
   npm run dev
   ```

6. Start the BullMQ worker (requires Redis running):
   ```
   node workers/moduleWorker.js
   ```

The backend API will be available at `http://localhost:3036/api`.

### Frontend

1. Navigate to the frontend directory:
   ```
   cd front_end/my-app-vite/
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Ensure `VITE_API_URL` is set (defaults to `http://localhost:3036/api`).

4. Start the development server:
   ```
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`.

---

## Test Accounts

The following account types are needed for test execution:

- **Admin user** — `user_type = 'admin'`, `is_admin = true`
- **Regular user** — `user_type = 'user'`, `is_admin = false`
- **Fresh registration data** — Unused email and username for registration tests

Accounts can be created through the registration flow or seeded directly in the database.

---

## Automation Setup

### API Tests (Python + requests)

```
pip install requests
```

Scripts are located in `automation/api/`. Each script targets a specific feature area and can be run independently.

### UI Tests (Playwright)

```
pip install playwright
playwright install
```

Specs are located in `automation/playwright/`. Tests require the frontend and backend to be running.

---

## Verification

Confirm the environment is ready:

1. Backend health check: `curl http://localhost:3036/health`
2. Frontend loads at `http://localhost:5173`
3. Login with a test account succeeds
4. Redis is running (`redis-cli ping` returns `PONG`)

---

## Tools Used During Testing

- **Browser DevTools** — Network tab, console, localStorage inspection
- **curl** — Direct API endpoint testing
- **PM2 logs** — Server-side log inspection (when running backend via PM2)
- **MySQL client** — Direct database verification
- **Playwright** — UI automation
- **Python `requests`** — API automation
