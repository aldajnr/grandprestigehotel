# Guest model
from datetime import datetime, date
from models import db as D


def _nights(ci, co):
    try:
        return max(0, (date.fromisoformat(str(co)[:10]) - date.fromisoformat(str(ci)[:10])).days)
    except Exception:
        return None


def create_guest(data: dict, created_by: int) -> int:
    cur = D.execute(
        """INSERT INTO guests(full_name, national_id, phone, room, checkin_date, checkout_date,
             payment_method, notes, status, created_by, created_at)
           VALUES (?,?,?,?,?,?,?,?,'active',?,?)""",
        (data["full_name"], data["national_id"], data["phone"], data["room"],
         data["checkin_date"], data["checkout_date"],
         data.get("payment_method",""), data.get("notes",""),
         created_by, datetime.utcnow().isoformat())
    )
    D.commit()
    return cur.lastrowid


def list_guests(include_cancelled=True):
    sql = """SELECT g.*, u.username AS created_by_username
               FROM guests g JOIN users u ON u.id = g.created_by
               ORDER BY g.id DESC"""
    rows = D.fetchall(sql)
    for r in rows:
        r["nights"] = _nights(r.get("checkin_date",""), r.get("checkout_date",""))
    return rows


def list_current_guests():
    today = date.today().isoformat()
    rows = D.fetchall(
        """SELECT g.*, u.username AS created_by_username
               FROM guests g JOIN users u ON u.id = g.created_by
              WHERE g.status = 'active' AND g.checkout_date >= ?
              ORDER BY g.checkin_date ASC""",
        (today,)
    )
    for r in rows:
        r["nights"] = _nights(r.get("checkin_date",""), r.get("checkout_date",""))
    return rows


def list_past_guests():
    today = date.today().isoformat()
    rows = D.fetchall(
        """SELECT g.*, u.username AS created_by_username
               FROM guests g JOIN users u ON u.id = g.created_by
              WHERE g.checkout_date < ? OR g.status = 'cancelled'
              ORDER BY g.id DESC""",
        (today,)
    )
    for r in rows:
        r["nights"] = _nights(r.get("checkin_date",""), r.get("checkout_date",""))
    return rows


def get_guest_by_id(guest_id: int):
    row = D.fetchone(
        """SELECT g.*, u.username AS created_by_username
               FROM guests g JOIN users u ON u.id = g.created_by
              WHERE g.id = ?""",
        (guest_id,)
    )
    if row:
        row["nights"] = _nights(row.get("checkin_date",""), row.get("checkout_date",""))
    return row


def search_guests(query: str):
    q = "%" + query.strip() + "%"
    rows = D.fetchall(
        """SELECT g.*, u.username AS created_by_username
               FROM guests g JOIN users u ON u.id = g.created_by
              WHERE g.full_name LIKE ? OR g.national_id LIKE ?
                 OR g.phone LIKE ? OR g.room LIKE ?
              ORDER BY g.id DESC""",
        (q, q, q, q)
    )
    for r in rows:
        r["nights"] = _nights(r.get("checkin_date",""), r.get("checkout_date",""))
    return rows


def cancel_guest(guest_id: int, cancelled_by: int, reason: str):
    D.execute(
        "UPDATE guests SET status='cancelled', cancelled_by=?, cancel_reason=? WHERE id=?",
        (cancelled_by, reason, guest_id)
    )
    D.commit()


def reschedule_guest(guest_id: int, new_checkin: str, new_checkout: str):
    D.execute(
        "UPDATE guests SET checkin_date=?, checkout_date=?, status='active' WHERE id=?",
        (new_checkin, new_checkout, guest_id)
    )
    D.commit()


def occupied_rooms():
    today = date.today().isoformat()
    rows = D.fetchall(
        """SELECT room, full_name, checkin_date, checkout_date, status
               FROM guests
              WHERE status = 'active' AND checkin_date <= ? AND checkout_date >= ?
              ORDER BY room ASC""",
        (today, today)
    )
    return rows
