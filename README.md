# Konkan Railway Corporation Limited — Bank Guarantee Tracking System

Internal system for tracking Bank Guarantee (BG) documents submitted by
contractors, with automated expiry email alerts.

## Stack

- **Frontend:** React + Tailwind CSS (Vite)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB Atlas
- **File storage:** Cloudinary
- **Email:** Brevo transactional email API (HTTPS — works on Render's free
  tier, which blocks raw SMTP ports 25/465/587)
- **Auth:** JWT in httpOnly cookies, bcrypt password hashing
- **Hosting:** Render (Web Service + Static Site + Cron Job)

Roles: **Admin** (full CRUD + user management) and **Viewer/Data-Entry**
(can add and view BG records; only Admins can edit, delete, or manage users).
SMS alerts are intentionally not wired up yet — the `mobile_no` field and the
`notifications` collection's `channel` field are already in place so an SMS
provider (MSG91/Twilio) can be added later without a schema change.

---

## 1. Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\activate on cmd/PowerShell
pip install -r requirements.txt
cp .env.example .env            # then fill in MONGODB_URI, JWT_SECRET, etc.
```

Fill in `.env`:
- `MONGODB_URI` — connection string from MongoDB Atlas (see below)
- `JWT_SECRET` — any long random string
- `CLOUDINARY_*` — from your Cloudinary dashboard
- `BREVO_API_KEY` / `MAIL_FROM` — from Brevo (see below); leave `BREVO_API_KEY` blank to disable email sending locally — the app logs a warning instead of failing
- `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` — used once to bootstrap the first Admin

Create the first Admin user, then run the API:

```bash
python -m scripts.create_admin
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

App available at `http://localhost:5173`.

### Manually testing the expiry-check job locally

```bash
cd backend
python -m scripts.expiry_check
```

---

## 2. Setting up external services (all free tier, no credit card required)

### MongoDB Atlas
1. Create a free M0 cluster at https://www.mongodb.com/cloud/atlas.
2. Create a database user (username/password).
3. Under Network Access, allow access from anywhere (`0.0.0.0/0`) — Render's
   outbound IPs are not static on the free plan.
4. Copy the connection string into `MONGODB_URI`.

### Cloudinary
1. Sign up at https://cloudinary.com (free tier: 25GB storage/bandwidth).
2. From the dashboard, copy Cloud Name, API Key, and API Secret into the
   `CLOUDINARY_*` env vars.

### Brevo (email)
1. Sign up free at https://www.brevo.com (300 emails/day, no credit card).
2. Under **Senders, Domains & Dedication > Senders**, add and verify the email
   address you want to send from (a confirmation link is emailed to it) — set
   that same address as `MAIL_FROM`. Only the sender needs verifying; you can
   send to any recipient once it's confirmed, no domain setup required.
3. Under **Settings > SMTP & API > API Keys**, create a new API key and set
   it as `BREVO_API_KEY`.
4. Note: Render's free web services block outbound SMTP entirely (ports
   25/465/587), which is why this app calls Brevo's HTTPS API directly
   instead of using SMTP — it works on the free tier as a result.

---

## 3. Deploying to Render

This repo includes a [`render.yaml`](render.yaml) Blueprint that provisions:
- a **Web Service** for the FastAPI backend
- a **Static Site** for the React frontend
- a **Cron Job** that runs the daily expiry-check independent of the web
  service's sleep state

Steps:
1. Push this repo to GitHub.
2. In Render, choose **New > Blueprint** and point it at the repo — it will
   read `render.yaml` and create all three services.
3. Fill in the env vars marked `sync: false` in the Render dashboard for each
   service (Mongo URI, Cloudinary keys, `BREVO_API_KEY`/`MAIL_FROM`,
   `FRONTEND_URL`, `CORS_ORIGINS`, helpdesk contact info, first-admin
   bootstrap credentials). **Type these values directly rather than pasting**
   — a stray whitespace/tab character from a copy-paste can silently break a
   URL field (Vite bakes `VITE_*` vars into the build at build time, so a
   bad value there requires a rebuild to fix, not just a restart).
   - `CORS_ORIGINS` on the backend must equal the frontend's Render URL
     exactly (no trailing slash) — a mismatch here fails silently as a CORS
     error in the browser console, not a 401.
   - `VITE_API_URL` on the frontend must equal the backend's Render URL.
   - The Cron Job's `JWT_SECRET` should match the Web Service's `JWT_SECRET`
     if you want tokens to remain valid across both (not strictly required —
     the cron job doesn't issue or verify tokens today).
4. Render's **Shell** access requires a paid instance type — it's not
   available on the free web service. To create the first Admin account,
   run this locally instead (against the same `MONGODB_URI` your Render
   backend uses):
   ```bash
   python -m scripts.create_admin
   ```
5. Because the backend and frontend are on Render's free instance type, the
   backend spins down after 15 minutes of inactivity — the first request
   after idle takes ~30-50s. The Cron Job runs as its own scheduled process,
   so daily expiry emails still fire on time regardless of whether the web
   service is awake.
6. Note: Render's `free` instance type isn't available for Cron Jobs (only
   for Web Services and Static Sites), so `render.yaml` sets the cron job's
   `plan` to `starter`. It's billed per second of actual run time — a job
   this small (a few seconds once a day) costs roughly $1/month, not $0.

---

## 4. Security notes

- JWT is stored in an httpOnly, Secure cookie (not localStorage) to reduce
  XSS exposure. `COOKIE_SAMESITE=none` is required when the frontend and
  backend live on different Render domains (the default Blueprint setup);
  `COOKIE_SAMESITE=lax` works if you put them behind the same domain.
- Login and password-reset endpoints are rate-limited per IP.
- All BG record deletes are soft deletes (`is_deleted` flag) — records are
  never physically removed, and every create/update/delete is written to
  `audit_logs` with who/when/what changed.
- Only Admins can create/manage user accounts — there is no public
  self-registration endpoint.
- All secrets are read from environment variables; none are hardcoded.
