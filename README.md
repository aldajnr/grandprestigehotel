# Grand Prestige Hotel — Secure Staff Portal
Zetech University

## Quick Start
```
pip install flask werkzeug python-dotenv
python app.py
```
Open: http://localhost:5000

## Admin Account
| Email | Password | Role |
|---|---|---|
| kaharukakelvin@zetech.ac.ke | kaharuka | Admin |

All other staff accounts (Manager, Receptionist) are created through the Admin panel.

## Features
- **Two-factor login** — OTP sent to each staff member's registered email
- **Password reset** — staff can request a reset OTP from the login page
- **Admin: view passwords** — admin can reveal the password hash for any account
- **Admin: reset any password** — admin can set a new password for any account
- **Role-based access** — Admin / Manager / Receptionist
- **Full audit trail** — every action logged

## OTP Email Setup (Gmail)
1. Go to myaccount.google.com/apppasswords
2. Create an App Password → copy the 16-char code
3. Edit `.env`:
   ```
   MAIL_USERNAME=you@gmail.com
   MAIL_PASSWORD=your16charcode
   MAIL_FROM=you@gmail.com
   ```
4. Run `python app.py`

Leave `MAIL_USERNAME` blank to run in **demo mode** — OTP shown on screen.

## Roles
| Role | Access |
|---|---|
| Admin | Full access + staff management + audit trail |
| Manager | View and register guest bookings + cancel/reschedule bookings |
| Receptionist | Register guests + view room status (ID/phone masked) |
