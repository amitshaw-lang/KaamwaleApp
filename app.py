from ai_job_desc_page import show_ai_job_desc
from ai_resume_page import show_ai_resume  # optional, if you created it
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import os
import re
from pathlib import Path
import importlib.util
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet  # Added import for getSampleStyleSheet
import json
import pydeck as pdk


def show_voice_job_post_page():
    """APK build placeholder - desktop-only feature."""
    st.info("Voice features are disabled in APK mode.")


def show_audio_test_page():
    """APK build placeholder - desktop-only feature."""
    st.info("Audio test is disabled in APK mode.")

def is_mobile_build() -> bool:
    """Return True when running inside the ROZGARWALE mobile container."""
    return os.getenv("ROZGARWALE_MOBILE", "0") == "1"


# ==== Aadhaar upload: globally disable (one-shot fix) ====
DISABLE_AADHAAR_UPLOAD = False

if DISABLE_AADHAAR_UPLOAD:
    _orig_file_uploader = st.file_uploader

    def _aadhaar_guard(label: str, *args, **kwargs):
        text = (label or "").lower()
        # sirf Aadhaar/Aadhar wale upload ko roko; baki uploads normal rahen
        if any(
            k in text
            for k in [
                "aadhaar",
                "aadhar",
                "aadhaar card",
                "aadhar card",
                "aadhaar document",
            ]
        ):
            st.info("Aadhaar upload is temporarily disabled.")
            return None
        # other uploads jaise resume/photo normal chalenge
        return _orig_file_uploader(label, *args, **kwargs)

    st.file_uploader = _aadhaar_guard
# =========================================================

st.set_page_config(page_title="RozgarWale App", layout="wide")
st.title("🛠️ RozgarWale – Sab Kaam Ek App Se")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rozgarwale.db")
DISPUTE_EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence_uploads")
os.makedirs(DISPUTE_EVIDENCE_DIR, exist_ok=True)


@st.cache_resource
def get_conn():
    # Single shared connection for Streamlit app
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")  # wait if DB is momentarily locked
    return conn


conn = get_conn()
c = conn.cursor()
# --- TEMP DB MIGRATION (controlled by flag) ---
RUN_MIGRATION = False  # future me True karke ON kar sakte ho

if RUN_MIGRATION:
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN timestamp TEXT;")
        conn.commit()
        st.success("✅ Column 'timestamp' added successfully!")
    except Exception as e:
        st.info(f"ℹ Timestamp column may already exist or failed to add: {e}")
# --- END OF TEMP DB MIGRATION ---

# --- DEBUG TOGGLE (optional clean mode) ---
show_debug = st.sidebar.toggle("Show debug", value=False)
if show_debug:
    st.write(c.execute("PRAGMA index_list(workers)").fetchall())
    st.caption(f"📁 DB: {DB_PATH}")
    st.caption(f"👷 Workers in DB: {c.execute('SELECT count(*) FROM workers').fetchone()[0]}")


def ensure_jobs_description_column(connection, debug=False):
    """Rename legacy jobs.job_description column to description so queries work."""
    cursor = connection.cursor()
    column_names = {row[1] for row in cursor.execute("PRAGMA table_info(jobs)")}
    if "description" in column_names:
        return
    if "job_description" not in column_names:
        return
    try:
        cursor.execute("ALTER TABLE jobs RENAME COLUMN job_description TO description")
        connection.commit()
        if debug:
            st.info("jobs table column renamed to 'description'")
    except sqlite3.OperationalError as exc:
        st.warning(
            "jobs table still uses 'job_description'; manual migration required: "
            f"{exc}"
        )

# --- TABLES CREATE ---
c.execute("""
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    skill TEXT,
    location TEXT,
    phone TEXT,
    experience TEXT,
    aadhar TEXT,
    verified INTEGER DEFAULT 0,
    earnings REAL DEFAULT 0
)
""")

c.execute(
    """CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT, description TEXT, location TEXT,
    status TEXT, assigned_worker TEXT, price REAL, timestamp TEXT
)"""
)
 
c.execute(
    """CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    worker_id TEXT,
    status TEXT DEFAULT 'pending',
    scheduled_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
)"""
)
ensure_jobs_description_column(conn, debug=show_debug)

c.execute(
    """CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER, rating INTEGER, comment TEXT, timestamp TEXT
)"""
)

# UNIQUE index banane ke liye (same name+phone dobara insert nahi hoga)
c.execute(
    """
CREATE UNIQUE INDEX IF NOT EXISTS idx_workers_name_phone
ON workers(name, phone);
"""
)

conn.commit()

_DISPUTE_TABLES_READY = False


def ensure_dispute_tables():
    """Create dispute tables lazily so we don't open extra SQLite connections."""
    global _DISPUTE_TABLES_READY
    if _DISPUTE_TABLES_READY:
        return
    cur = conn.cursor()
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS disputes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    raised_by TEXT,
    user_name TEXT,
    category TEXT,
    title TEXT,
    description TEXT,
    amount REAL,
    priority TEXT,
    status TEXT,
    owner TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
)
"""
    )
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS dispute_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispute_id INTEGER,
    author TEXT,
    role TEXT,
    msg TEXT,
    file_paths TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
    )
    conn.commit()
    _DISPUTE_TABLES_READY = True


def _dispute_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dispute_save_uploads(uploaded_files):
    saved = []
    for uploaded in uploaded_files or []:
        safe_name = uploaded.name.replace(" ", "")
        fname = f"{int(datetime.now().timestamp() * 1000)}_{safe_name}"
        dest = os.path.join(DISPUTE_EVIDENCE_DIR, fname)
        with open(dest, "wb") as out:
            out.write(uploaded.getbuffer())
        saved.append(dest)
    return saved


def dispute_create(job_id, raised_by, user_name, category, title, description, amount, priority):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO disputes (job_id, raised_by, user_name, category, title, description, amount, priority, status, owner, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', '', ?)
        """,
        (job_id, raised_by, user_name, category, title, description, amount, priority, _dispute_now()),
    )
    conn.commit()
    return cur.lastrowid


def dispute_add_message(dispute_id, author, role, msg, file_paths):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dispute_messages (dispute_id, author, role, msg, file_paths)
        VALUES (?, ?, ?, ?, ?)
        """,
        (dispute_id, author, role, msg, json.dumps(file_paths or [])),
    )
    cur.execute("UPDATE disputes SET updated_at=? WHERE id=?", (_dispute_now(), dispute_id))
    conn.commit()


def dispute_update_status(dispute_id, new_status):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute(
        "UPDATE disputes SET status=?, updated_at=? WHERE id=?",
        (new_status, _dispute_now(), dispute_id),
    )
    conn.commit()


def dispute_assign_owner(dispute_id, owner_name):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute(
        "UPDATE disputes SET owner=?, updated_at=? WHERE id=?",
        (owner_name, _dispute_now(), dispute_id),
    )
    conn.commit()


def dispute_fetch(status_filter="all", role_filter="all", search=""):
    ensure_dispute_tables()
    cur = conn.cursor()
    q = "SELECT * FROM disputes WHERE 1=1"
    params = []
    if status_filter != "all":
        q += " AND status=?"
        params.append(status_filter)
    if role_filter != "all":
        q += " AND raised_by=?"
        params.append(role_filter)
    if search.strip():
        q += " AND (job_id LIKE ? OR user_name LIKE ? OR title LIKE ?)"
        like = f"%{search.strip()}%"
        params.extend([like, like, like])
    q += " ORDER BY updated_at DESC, id DESC"
    cur.execute(q, params)
    return cur.fetchall()


def dispute_fetch_messages(dispute_id):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, author, role, msg, file_paths, created_at
        FROM dispute_messages
        WHERE dispute_id=? ORDER BY id ASC
        """,
        (dispute_id,),
    )
    return cur.fetchall()


def dispute_delete(dispute_id):
    ensure_dispute_tables()
    cur = conn.cursor()
    cur.execute("DELETE FROM dispute_messages WHERE dispute_id=?", (dispute_id,))
    cur.execute("DELETE FROM disputes WHERE id=?", (dispute_id,))
    conn.commit()

# Ab count check karo (kitne workers DB me hai)
c.execute("SELECT COUNT(*) FROM workers")
count = c.fetchone()[0]
st.caption(f"👷 Workers in DB: {count}")

# ====================================================
# 📢 NOTIFICATIONS CENTER (Helper Functions)
# ====================================================

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# ---------- Database Setup (Notifications) ----------
conn_notif = sqlite3.connect(DB_PATH, check_same_thread=False)
conn_notif.execute("PRAGMA journal_mode=WAL;")
conn_notif.execute("PRAGMA busy_timeout=5000;")
c_notif = conn_notif.cursor()

c_notif.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    body TEXT,
    audience TEXT,
    channels TEXT,         -- JSON string e.g. ["inapp","sms"]
    status TEXT,           -- queued|scheduled|sent|resent|failed
    priority TEXT,         -- low|normal|high
    job_id TEXT,
    tags TEXT,
    scheduled_at TEXT,     -- "YYYY-MM-DD HH:MM"
    sent_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn_notif.commit()

# ---------- Helpers ----------

def insert_notification(
    title, body, audience, channels, priority,
    job_id, tags, scheduled_at, status="queued"
):
    c_notif.execute(
        """
        INSERT INTO notifications
            (title, body, audience, channels, priority, job_id, tags, scheduled_at, status)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, body, audience, json.dumps(channels), priority, job_id, tags, scheduled_at, status),
    )
    conn_notif.commit()

def fetch_notifications(status_filter=None, audience_filter=None):
    q = "SELECT * FROM notifications"
    clauses = []
    params = []
    if status_filter and status_filter != "all":
        clauses.append("status = ?")
        params.append(status_filter)
    if audience_filter and audience_filter != "all":
        clauses.append("audience = ?")
        params.append(audience_filter)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY id DESC"
    c_notif.execute(q, params)
    return c_notif.fetchall()

def update_status(n_id, new_status):
    c_notif.execute(
        "UPDATE notifications SET status=?, sent_at=? WHERE id=?",
        (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), n_id),
    )
    conn_notif.commit()

def delete_notification(n_id):
    c_notif.execute("DELETE FROM notifications WHERE id=?", (n_id,))
    conn_notif.commit()

def clear_all_notifications():
    c_notif.execute("DELETE FROM notifications")
    conn_notif.commit()

# ✅ Sidebar Menu
menu = st.sidebar.selectbox(
    "Main Menu",
    [
        "Worker Profile",
        "Customer Signup",
        "Job Post",
        "CSV Manager",
        "AI Assistant",
        "Notifications",
        "Bookings",
        "Review System",
        "Referral Program",
        "PDF Invoice",
        "Wallet",
        "Emergency Mode",
        "Heatmap",
        "Subscription",
        "Resume Generator",
        "Corporate Module",
        "CRM",
        "Support Chat",
        "Search Workers",
        "Booking Status",
        "Calendar",
        "Live Chat",
        "Feedback",
        "GPS",
        "Skill Test",
        "Availability",
        "AI Job Description",
        "AI Resume",
        "Search Jobs",
    ],
)
st.write("DEBUG menu ->", repr(menu))

# ✅ Worker Profile Section
if menu == "Worker Profile":
    st.header("👷 Worker Profile")
    with st.form("worker_form"):
        name = st.text_input("Name")
        skill = st.selectbox(
            "Skill", ["Plumber", "Electrician", "Carpenter", "Mechanic"]
        )
        location = st.text_input("Location")
        phone = st.text_input("Phone")
        experience = st.text_input("Experience")
        # aadhar = st.file_uploader("Upload Aadhaar")
        aadhar = None

        submit = st.form_submit_button("Submit")
    if submit:
        # --- 1) inputs clean/normalize ---
        nm = (name or "").strip()
        sk = (skill or "").strip()
        loc = (location or "").strip()
        ph = (phone or "").strip().replace(" ", "").replace("-", "")
        exp = (experience or "").strip()

        if not nm or not ph:
            st.warning("⚠ Name aur Phone required hai.")
        else:
            try:
                # --- 2) duplicate check: same name (case-insensitive) + phone ---
                c.execute(
                    "SELECT id FROM workers WHERE name = ? COLLATE NOCASE AND phone = ?",
                    (nm, ph),
                )
                already = c.fetchone()

                if already:
                    st.warning(
                        "⚠ Duplicate: same name + phone already exists. Not added."
                    )
                else:
                    # --- 3) safe insert ---
                    conn.execute("BEGIN IMMEDIATE")
                    c.execute(
                        """
                        INSERT INTO workers
                            (name, skill, location, phone, experience, aadhar)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (nm, sk, loc, ph, exp, aadhar),
                    )
                    conn.commit()
                    st.success("✅ Worker saved!")
            except Exception as e:
                st.error(f"DB error: {e}")
elif menu == "AI Job Description":
    show_ai_job_desc()

elif menu == "AI Resume":
    show_ai_resume()  # Ensure proper indentation for the block

# ✅ Customer Signup Section
elif menu == "Customer Signup":
    st.header("🧍 Customer Signup")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    if st.button("Signup"):
        st.success(f"Customer {name} signed up successfully! (Demo)")

# ====================================================
# 📢 NOTIFICATIONS CENTER (Testing Version)
# ====================================================
elif menu == "Notifications":
    st.title("📢 Notifications Center (Testing Mode)")
    st.caption("Create, preview, and send notifications inside the app (no real SMS/Email).")

    col1, col2 = st.columns([1, 2])

    # ---------- Compose Section ----------
    with col1:
        st.subheader("📝 Compose Notification")

        title = st.text_input("Title", "Job Assigned")
        body = st.text_area("Message", "Your job #15 is assigned to a verified worker.")
        audience = st.selectbox("Audience", ["all", "customer", "worker"])
        channels = st.multiselect("Channels", ["inapp", "email", "sms", "whatsapp", "push"], default=["inapp"])
        priority = st.radio("Priority", ["low", "normal", "high"], index=1)
        job_id = st.text_input("Related Job ID (optional)", "")
        tags = st.text_input("Tags (comma separated)", "job,alert,info")
        schedule = st.text_input("Schedule Time (YYYY-MM-DD HH:MM, optional)", "")

        if st.button("📩 Preview"):
            st.info(
                f"*Preview:*\n\n"
                f"*To:* {audience}  |  *Priority:* {priority}\n\n"
                f"{title}\n{body}\n\n"
                f"Channels: {', '.join(channels)}\n"
                f"Tags: {tags}\n"
                f"Schedule: {schedule or '—'}"
            )

        send_now = st.button("🚀 Send Now")
        schedule_btn = st.button("💾 Schedule")

        if send_now:
            insert_notification(title, body, audience, channels, priority, job_id, tags, schedule, "sent")
            st.success("✅ Notification sent successfully (Test Mode)")
            st.toast(f"📢 {title} - {body}", icon="💬")

        if schedule_btn:
            insert_notification(title, body, audience, channels, priority, job_id, tags, schedule, "scheduled")
            st.success("🕒 Notification scheduled successfully!")

        st.markdown("---")
        if st.button("🧪 Quick Test Notifications"):
            insert_notification("Welcome to RozgarWale", "Your registration was successful.", "customer", ["inapp"], "normal", "", "welcome", "", "sent")
            insert_notification("Job Assigned", "Job #101 assigned successfully.", "worker", ["inapp"], "high", "101", "job", "", "sent")
            insert_notification("Payment Received", "₹500 credited to your wallet.", "worker", ["inapp"], "normal", "", "payment", "", "sent")
            st.success("✅ 3 demo notifications created successfully!")

        with st.expander("Danger Zone (Testing)"):
            if st.button("🗑 Clear All Notifications"):
                clear_all_notifications()
                st.warning("All notifications cleared (testing only).")
                safe_rerun()

    # ---------- Logs Section ----------
    with col2:
        st.subheader("📜 Notification Log")

        # Quick filters for viewing
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            status_filter = st.selectbox("Filter by Status", ["all", "queued", "scheduled", "sent", "resent", "failed"], index=2)
        with fcol2:
            audience_filter = st.selectbox("Filter by Audience", ["all", "customer", "worker"])

        logs = fetch_notifications(status_filter=status_filter, audience_filter=audience_filter)

        if not logs:
            st.warning("No notifications found yet.")
        else:
            for n in logs:
                (
                    n_id, title, body, audience, channels_raw, status,
                    priority, job_id, tags, sched, sent_at, created_at
                ) = n

                # Try decoding channel list nicely
                try:
                    ch_list = json.loads(channels_raw) if channels_raw else []
                    ch_view = ", ".join(ch_list) if isinstance(ch_list, list) else str(channels_raw)
                except Exception:
                    ch_view = str(channels_raw)

                st.markdown(f"🆔 ID: {n_id} | Title: {title} | Status: {status}")
                st.caption(
                    f"To: {audience}  |  Priority: {priority}  |  Channels: {ch_view}  |  "
                    f"Job: {job_id or '—'}  |  Tags: {tags or '—'}  |  "
                    f"Scheduled: {sched or '—'}  |  Sent: {sent_at or '—'}"
                )

# ✅ Job Post Section
elif menu == "Job Post":
    st.header("📝 Post a Job")
    cust_name = st.text_input("Customer Name")
    job_desc = st.text_area("Job Description")
    location = st.text_input("Location")
    price = st.text_input("Price")  # Add price input field
    if st.button("Post Job"):
        cust = (cust_name or "").strip()  # <-- input se aya hua naam
        desc = (job_desc or "").strip()
        loc = (location or "").strip()
        prc = float(price) if str(price).strip() else 0.0

        # DEBUG: what did we capture?
        st.write({"cust": repr(cust), "desc": repr(desc), "loc": repr(loc), "prc": prc})
        st.write({"lens": (len(cust), len(desc), len(loc))})
        if not cust or not desc or not loc:
            st.warning("⚠ Customer name, description aur location required hai.")
        else:
            try:
                conn.execute("BEGIN IMMEDIATE")
                c.execute(
                    """
                    INSERT INTO jobs (customer_name, description, location, price, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (cust, desc, loc, prc, "open", str(datetime.datetime.now())),
                )
                conn.commit()
                st.success("✅ Job posted successfully!")
            except Exception as e:
                st.error(f"DB error: {e}")
    # ---- Job Post ka pura code ----

# ================================
# 🔎 SEARCH JOBS  (single clean block)
# ================================
elif menu == "Search Jobs":

    # ---------- session defaults ----------
    if "job_rows" not in st.session_state:
        st.session_state.job_rows = []
    if "last_keyword" not in st.session_state:
        st.session_state.last_keyword = ""

    # ---------- helpers (local to this section) ----------
    import re

    def fmt_time(ts: str) -> str:
        try:
            return datetime.fromisoformat(str(ts)).strftime("%d-%b-%Y %I:%M %p")
        except Exception:
            return str(ts)

    def fmt_price(x):
        try:
            x = float(x)
            return f"₹{x:,.0f}"
        except Exception:
            return x

    def _to_num(s):
        """Extract numeric for range/total calc (handles blanks/₹/comma)."""
        try:
            s = str(s)
            s = re.sub(r"[^\d.]", "", s)
            return float(s) if s else 0.0
        except Exception:
            return 0.0

    def color_status(val: str) -> str:
        v = str(val or "").lower().strip()
        if v == "open":
            return "🟡 open"
        if v == "completed":
            return "🟢 completed"
        if v == "cancelled":
            return "🔴 cancelled"
        return v

    # ---------- UI: header + keyword ----------
    st.header("🔎 Search Jobs")
    keyword = st.text_input(
        "Enter keyword (customer, job description, location)", key="kw_jobs"
    )

    # ---------- Search button ----------
    if st.button("Search Jobs"):
        q = """
            SELECT id, customer_name, description, location, price, status, timestamp
            FROM jobs
            WHERE customer_name LIKE ? OR description LIKE ? OR location LIKE ?
        """
        c.execute(q, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        st.session_state.job_rows = c.fetchall()
        st.session_state.last_keyword = keyword

    # ---------- Show all ----------
    if st.button("Show All Jobs"):
        c.execute(
            "SELECT id, customer_name, description, location, price, status, timestamp FROM jobs"
        )
        st.session_state.job_rows = c.fetchall()
        st.session_state.last_keyword = ""

    # ---------- Results ----------
    rows = st.session_state.job_rows
    if rows:
        # DataFrame
        df = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Customer",
                "Description",
                "Location",
                "Price",
                "Status",
                "Timestamp",
            ],
        )

        # Transform for display
        df["Timestamp"] = df["Timestamp"].apply(fmt_time)
        df["Price"] = df["Price"].apply(fmt_price)

        # Keep raw status separately for preselect/filter
        df["StatusRaw"] = df["Status"]
        df["Status"] = df["Status"].apply(color_status)

        # ---------- Filters (status + price range) ----------
        colA, colB = st.columns([1, 2])
        with colA:
            f_status = st.multiselect(
                "Filter status", ["open", "completed", "cancelled"], default=[]
            )
        with colB:
            max_price = int(df["Price"].apply(_to_num).max() or 0)
            pmin, pmax = st.slider("Price range", 0, max_price, (0, max_price))

        tmp = df.copy()
        if f_status:
            tmp = tmp[tmp["StatusRaw"].isin(f_status)]
        tmp = tmp[tmp["Price"].apply(_to_num).between(pmin, pmax)]

        # Table
        st.dataframe(tmp, use_container_width=True)

        # CSV download (drop helper cols if present)
        csv = (
            tmp.drop(columns=["StatusRaw"], errors="ignore")
            .to_csv(index=False)
            .encode("utf-8")
        )
        st.download_button(
            "⬇ Download jobs (CSV)",
            data=csv,
            file_name="jobs_results.csv",
            mime="text/csv",
            key="dl_jobs_csv",
        )

        # Quick stats
        total_jobs = len(tmp)
        total_price = tmp["Price"].apply(_to_num).sum()
        st.caption(f"{total_jobs} job(s) • Total price approx ₹{int(total_price):,}")

        # ---------- Update status controls ----------
        job_ids = tmp["ID"].tolist()
        selected_id = st.selectbox(
            "Select Job ID to update", job_ids, key="upd_search_id"
        )

        # Preselect current status of selected row
        cur_status = df.loc[df["ID"] == selected_id, "StatusRaw"].iloc[0]
        status_choices = ["open", "completed", "cancelled"]
        new_status = st.selectbox(
            "Update status",
            status_choices,
            index=status_choices.index(cur_status),
            key="upd_search_status",
        )

        # ---------- Update button ----------
        if st.button("Update Job Status"):
            try:
                c.execute(
                    "UPDATE jobs SET status = ? WHERE id = ?", (new_status, selected_id)
                )
                conn.commit()
                st.success(f"✅ Job ID {selected_id} updated to {new_status}")

                # Refresh using last keyword
                refresh_q = """
                    SELECT id, customer_name, description, location, price, status, timestamp
                    FROM jobs
                    WHERE customer_name LIKE ? OR description LIKE ? OR location LIKE ?
                """
                lk = st.session_state.last_keyword
                c.execute(refresh_q, (f"%{lk}%", f"%{lk}%", f"%{lk}%"))
                st.session_state.job_rows = c.fetchall()

                st.rerun()  # instant refresh
            except Exception as e:
                st.error(f"DB error: {e}")

    else:
        st.info("No jobs found. Search karke dekho ya 'Show All Jobs' dabao.")

elif menu == "CSV Manager":
    st.header("📁 Upload CSV File")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        df = pd.read_csv(file)
        st.write(df.head())
    if show_debug:
        st.divider()
        st.info("Debug → CSV Manager → Dispute System")
        render_dispute_system()

# ==== AI Assistant menu block ====
elif menu == "AI Assistant":
    st.header("🤖 RozgarWale AI Assistant")
    st.write("Ask anything about jobs, pricing, job profiles, etc.")

    # Input box
    user_q = st.text_input("Type your question...", value="", key="ai_q")

    # Clear button
    if st.button("🧹 Clear chat"):
        st.session_state["ai_last"] = None
        safe_rerun()

    # Optional: Fraud check (Mock)
    st.subheader("🛡 AI Assistant – Fraud Check (Mock)")
    desc = st.text_area(
        "Describe the Job or Situation", placeholder="e.g., my tap pipe is leaked"
    )
    if st.button("Run AI Fraud Check"):
        risk = "✅ Low risk"
        if any(
            w in desc.lower()
            for w in ["advance", "prepaid", "otp", "fee", "refund", "link"]
        ):
            risk = "⚠ Potential risk △ – avoid sending money/OTP/links."
        st.info(risk)

    # Main Q&A
    if user_q:
        try:
            api_key_present = bool(os.getenv("OPENAI_API_KEY"))
        except Exception:
            api_key_present = False

        # Check if openai package is available
        import importlib.util

        OPENAI_AVAILABLE = importlib.util.find_spec("openai") is not None

        if OPENAI_AVAILABLE and api_key_present:
            # Define a simple call_openai function (mock response)
            def call_openai(prompt):
                # You can replace this with actual OpenAI API call logic
                return f"Mock AI response for: {prompt}"

            ans = call_openai(user_q)
        else:
            ans = (
                "⚠ AI Assistant is temporarily unavailable (API key missing/disabled)."
            )

        st.session_state["ai_last"] = ans
        st.success(ans)

    # Show last answer on reload
    if "ai_last" in st.session_state and not user_q:
        st.caption("Last answer:")
        st.write(st.session_state["ai_last"])
# ===== Bookings page (drop-in) =====
# deps (safe to keep even if already imported)
# (imports moved to top of file)


def _fmt_ts(x) -> str:
    try:
        return datetime.fromisoformat(str(x)).strftime("%d-%b-%Y %I:%M %p")
    except Exception:
        return str(x)


if menu == "Bookings":
    st.header("📅 Bookings Management")
    st.caption("Monitor every pending/approved booking in one place.")

    col_status, col_date, col_worker, col_customer = st.columns([1, 1, 1, 1])
    with col_status:
        status_filter = st.selectbox(
            "Status",
            ["all", "pending", "approved", "rejected", "completed"],
            index=0,
        )
    with col_date:
        use_date_filter = st.checkbox("Filter by date", value=False, key="book_date_toggle")
        date_filter = None
        if use_date_filter:
            date_filter = st.date_input(
                "Scheduled Date",
                value=datetime.now().date(),
                key="book_date_input",
            )
    with col_worker:
        worker_filter = st.text_input("Worker ID", "", key="book_worker_filter")
    with col_customer:
        customer_filter = st.text_input("Customer ID", "", key="book_customer_filter")

    base_q = """
        SELECT id, customer_id, worker_id, status, scheduled_at, created_at, notes
        FROM bookings
    """
    clauses = []
    params = []
    if status_filter != "all":
        clauses.append("status = ?")
        params.append(status_filter)
    if date_filter:
        clauses.append("date(scheduled_at) = ?")
        params.append(date_filter.strftime("%Y-%m-%d"))
    if worker_filter.strip():
        clauses.append("worker_id LIKE ?")
        params.append(f"%{worker_filter.strip()}%")
    if customer_filter.strip():
        clauses.append("customer_id LIKE ?")
        params.append(f"%{customer_filter.strip()}%")

    if clauses:
        base_q += " WHERE " + " AND ".join(clauses)
    base_q += " ORDER BY datetime(scheduled_at) DESC, id DESC"

    try:
        booking_rows = c.execute(base_q, params).fetchall()
    except sqlite3.OperationalError as exc:
        st.error(f"Bookings table unavailable: {exc}")
        booking_rows = []

    if not booking_rows:
        st.warning("No bookings found for the selected filters.")
    else:
        df = pd.DataFrame(
            booking_rows,
            columns=[
                "ID",
                "Customer ID",
                "Worker ID",
                "Status",
                "Scheduled At",
                "Created At",
                "Notes",
            ],
        )
        df["Scheduled At"] = df["Scheduled At"].apply(_fmt_ts)
        df["Created At"] = df["Created At"].apply(_fmt_ts)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Quick Actions")
        for row in booking_rows:
            (
                row_id,
                row_customer,
                row_worker,
                row_status,
                row_scheduled,
                row_created,
                row_notes,
            ) = row
            with st.container():
                st.markdown(
                    f"**Booking #{row_id}** — Status: `{row_status}`  "
                    f"| Worker: `{row_worker or '—'}`  | Customer: `{row_customer or '—'}`"
                )
                meta = (
                    f"Scheduled: { _fmt_ts(row_scheduled) }  | "
                    f"Created: { _fmt_ts(row_created) }"
                )
                st.caption(meta)
                if row_notes:
                    st.write(f"Notes: {row_notes}")

                action_cols = st.columns([1, 1, 6])
                approve_disabled = row_status == "approved"
                reject_disabled = row_status == "rejected"
                with action_cols[0]:
                    if st.button(
                        "Approve",
                        key=f"booking_approve_{row_id}",
                        disabled=approve_disabled,
                    ):
                        try:
                            c.execute(
                                "UPDATE bookings SET status=? WHERE id=?",
                                ("approved", row_id),
                            )
                            conn.commit()
                            st.success(f"Booking #{row_id} approved.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to approve booking: {e}")
                with action_cols[1]:
                    if st.button(
                        "Reject",
                        key=f"booking_reject_{row_id}",
                        disabled=reject_disabled,
                    ):
                        try:
                            c.execute(
                                "UPDATE bookings SET status=? WHERE id=?",
                                ("rejected", row_id),
                            )
                            conn.commit()
                            st.warning(f"Booking #{row_id} rejected.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to reject booking: {e}")


elif menu == "Review System":
    def star_str(n):
        try:
            full = int(round(float(n)))
            return "⭐" * max(full, 0) or "—"
        except Exception:
            return "—"

    # Worker dropdown (name + skill + #id)
    workers = c.execute(
        "SELECT id, name, skill FROM workers ORDER BY id DESC"
    ).fetchall()
    if not workers:
        st.info("No workers in database yet.")
        st.stop()

    options = [f"{w[1]} ({w[2]}) — #{w[0]}" for w in workers]
    sel = st.selectbox("Choose Worker", options, index=0)
    worker_id = int(sel.split("#")[-1])

    # Current average for selected worker
    avg = c.execute(
        "SELECT AVG(rating) FROM feedback WHERE worker_id=?", (worker_id,)
    ).fetchone()[0]
    st.caption(f"Average rating for selected worker: {star_str(avg) if avg else '—'}")

    # Inputs
    rating = st.slider("Rating", 1, 5, 3)
    comment = st.text_area("Comment", placeholder="Write your experience...")

    # Submit with validation
    if st.button("Submit Review"):
        if rating < 1 or rating > 5:
            st.warning("Rating 1–5 ke beech hona chahiye.")
        elif not comment.strip():
            st.warning("Comment required hai.")
        else:
            c.execute(
                "INSERT INTO feedback (worker_id, rating, comment, timestamp) VALUES (?,?,?,?)",
                (
                    worker_id,
                    int(rating),
                    comment.strip(),
                    datetime.datetime.now().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
            st.success("Review submitted!")
            st.rerun()

    # Recent reviews (latest 10) for this worker
    rows = c.execute(
        "SELECT rating, comment, timestamp FROM feedback WHERE worker_id=? ORDER BY id DESC LIMIT 10",
        (worker_id,),
    ).fetchall()

    st.subheader("Recent Reviews (latest 10)")
    if not rows:
        st.info("No reviews yet. Be the first to add one!")
    else:
        import datetime  # ensure this is at top level

        for r, cm, ts in rows:
            when = (
                datetime.datetime.fromisoformat(ts).strftime("%d %b %Y, %I:%M %p")
                if ts
                else ""
            )
            st.markdown(
                f"""
                    <div style='padding:10px 15px; margin-bottom:8px; border-radius:10px; background-color:#1e1e1e;'>
                        <div style='font-size:18px; color:#ffcc00;'>{star_str(r)}</div>
                        <div style='font-size:14px; color:#aaa; margin-top:-3px;'>{when}</div>
                        <div style='margin-top:6px; color:#eee;'>{cm}</div>
                    </div>
                    """,
                unsafe_allow_html=True,
            )

if menu == "Search Workers":
    st.header("🔎 Search Workers")

    keyword = st.text_input("Enter name, skill or location")

    # search button
    if st.button("Search"):
        if not keyword.strip():
            st.warning("⚠ Please type something to search")
        else:
            try:
                c.execute(
                    """
                    SELECT id, name, skill, location, phone, experience, aadhar, verified, earnings
                    FROM workers
                    WHERE name LIKE ? OR skill LIKE ? OR location LIKE ?
                    ORDER BY name COLLATE NOCASE
                """,
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
                )
                rows = c.fetchall()

                if rows:
                    df = pd.DataFrame(
                        rows,
                        columns=[
                            "ID",
                            "Name",
                            "Skill",
                            "Location",
                            "Phone",
                            "Experience",
                            "Aadhar",
                            "Verified",
                            "Earnings",
                        ],
                    )

                    def fmt_inr(x):
                        try:
                            x = float(x)
                            return f"₹{x:,.0f}"
                        except Exception:
                            return x

                    def fmt_verified(x):
                        s = str(x).strip().lower()
                        return "✅ Yes" if s in ("1", "true", "yes", "y") else "❌ No"

                    def fmt_phone(p):
                        p = str(p or "").strip()
                        digits = "".join(ch for ch in p if ch.isdigit())
                        if len(digits) >= 10:
                            d = digits[-10:]
                            return f"+91-{d[:5]}-{d[5:]}"
                        return p

                    for col in ("Name", "Skill", "Location"):
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.title()

                    if "Verified" in df.columns:
                        df["Verified"] = df["Verified"].apply(fmt_verified)

                    if "Earnings" in df.columns:
                        df["Earnings"] = df["Earnings"].apply(fmt_inr)

                    if "Phone" in df.columns:
                        df["Phone"] = df["Phone"].apply(fmt_phone)

                    cols = [
                        "ID",
                        "Name",
                        "Skill",
                        "Location",
                        "Phone",
                        "Experience",
                        "Aadhar",
                        "Verified",
                        "Earnings",
                    ]
                    df = df[[col for col in cols if col in df.columns]]

                    st.success(f"✅ Found {len(df)} result(s)")
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇ Download results (CSV)",
                        data=csv,
                        file_name="workers_results.csv",
                        mime="text/csv",
                        key="dl_workers_csv",
                    )

                else:
                    st.info(
                        "⚠ No results found. Dusra keyword try karo ya click [Show All]."
                    )

            except Exception as e:
                st.error(f"❌ Search error: {e}")

    # Show all button
    if st.button("Show All"):
        try:
            c.execute(
                "SELECT id, name, skill, location, phone, experience, aadhar, verified, earnings FROM workers"
            )
            rows = c.fetchall()

            if rows:
                df = pd.DataFrame(
                    rows,
                    columns=[
                        "ID",
                        "Name",
                        "Skill",
                        "Location",
                        "Phone",
                        "Experience",
                        "Aadhar",
                        "Verified",
                        "Earnings",
                    ],
                )

                def fmt_inr(x):
                    try:
                        x = float(x)
                        return f"₹{x:,.0f}"
                    except Exception:
                        return x

                def fmt_verified(x):
                    s = str(x).strip().lower()
                    return "✅ Yes" if s in ("1", "true", "yes", "y") else "❌ No"

                def fmt_phone(p):
                    p = str(p or "").strip()
                    digits = "".join(ch for ch in p if ch.isdigit())
                    if len(digits) >= 10:
                        d = digits[-10:]
                        return f"+91-{d[:5]}-{d[5:]}"
                    return p

                for col in ("Name", "Skill", "Location"):
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.title()

                if "Verified" in df.columns:
                    df["Verified"] = df["Verified"].apply(fmt_verified)

                if "Earnings" in df.columns:
                    df["Earnings"] = df["Earnings"].apply(fmt_inr)

                if "Phone" in df.columns:
                    df["Phone"] = df["Phone"].apply(fmt_phone)

                cols = [
                    "ID",
                    "Name",
                    "Skill",
                    "Location",
                    "Phone",
                    "Experience",
                    "Aadhar",
                    "Verified",
                    "Earnings",
                ]
                df = df[[col for col in cols if col in df.columns]]

                st.success(f"✅ Found {len(df)} worker(s)")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇ Download results (CSV)",
                    data=csv,
                    file_name="workers_results.csv",
                    mime="text/csv",
                    key="dl_workers_csv_all",
                )

            else:
                st.info("⚠ No workers in database.")

        except Exception as e:
            st.error(f"❌ Show All error: {e}")

elif menu == "Feedback":
    st.header("📣 Send Feedback")
    message = st.text_area("Enter your feedback")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback! (Mock)")

# ✅ GPS Location (Mock)
elif menu == "GPS":
    st.header("📍 GPS Location (Mock)")
    st.success("GPS acquired! Showing mock location: Kolkata, WB")


# ✅ Aadhaar Upload (disabled via DISABLE_AADHAAR_UPLOAD flag at top)
elif menu == "Aadhaar Upload":
    st.header("Upload Aadhaar Document")
    st.info("Aadhaar upload is currently disabled for security purposes.")

# ✅ Booking Status
elif menu == "Booking Status":
    st.header("📊 Booking Status")
    job_id = st.number_input("Enter Job ID", step=1)
    if st.button("Check Status"):
        c.execute("SELECT status FROM jobs WHERE id=?", (job_id,))
        res = c.fetchone()
        if res:
            st.info(f"Current Status: {res[0]}")
        else:
            st.error("Job not found.")


# ✅ RozgarWale App.py — Part 2 (Phase 201–400 Internal Features)
# Make sure Part 1 is already pasted above this code block.

# --- PDF INVOICE SECTION ---
def generate_invoice_pdf(job_id):
    """Generate a mock PDF invoice for the given job ID."""
    try:
        c.execute(
            "SELECT id, customer_name, description, location, price, status, timestamp FROM jobs WHERE id=?",
            (job_id,)
        )
        job = c.fetchone()
        if job:
            st.write(f"Invoice for Job ID {job_id}: {job[1]} - ₹{job[4]}")
    except Exception as e:
        st.error(f"Error fetching job for invoice: {e}")


def fetch_job_record(job_id: str):
    """Try to fetch job row for numeric or text IDs. Returns dict or None."""
    row = None
    # numeric try
    try:
        row = c.execute(
            "SELECT id, customer_name, description, location, price, status, timestamp FROM jobs WHERE id=? LIMIT 1",
            (int(job_id),),
        ).fetchone()
    except Exception:
        pass
    # text fallback
    if not row:
        row = c.execute(
            "SELECT id, customer_name, description, location, price, status, timestamp FROM jobs WHERE id=? LIMIT 1",
            (job_id,),
        ).fetchone()
    if not row:
        return None
    keys = ["id", "customer_name", "description", "location", "price", "status", "timestamp"]
    return dict(zip(keys, row))

def generate_invoice_pdf_with_gst(job: dict, brand: dict, gst: dict) -> str:
    """
    job: {'id','customer_name','description','location','price','status','timestamp'}
    brand: {'company','address','gstin','pan','logo_path'}
    gst: {'rate','split_cgst_sgst'}
    Returns file path (str)
    """
    # Define invoice directory
    INVOICE_DIR = Path(os.path.join(BASE_DIR, "invoices"))
    INVOICE_DIR.mkdir(exist_ok=True)
    invoice_no = f"RW-INV-{datetime.datetime.now():%Y%m%d}-{job['id']}"
    pdf_path = INVOICE_DIR / f"{invoice_no}.pdf"

    # Amounts
    subtotal = float(job.get("price") or 0)
    rate = float(gst.get("rate") or 0)
    tax_total = round(subtotal * rate / 100.0, 2)
    total = round(subtotal + tax_total, 2)

    cgst = sgst = igst = 0.0
    if rate > 0:
        if gst.get("split_cgst_sgst", True):
            cgst = round(tax_total / 2.0, 2)
            sgst = round(tax_total - cgst, 2)
        else:
            igst = tax_total

    # --------- PDF build ----------
    styles = getSampleStyleSheet()
    style_h1 = styles["Heading1"]
    style_h2 = styles["Heading2"]
    style_n = styles["BodyText"]

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm
    )
    story = []

    # Header (logo + company)
    if brand.get("logo_path") and os.path.exists(brand["logo_path"]):
        try:
            story.append(Image(brand["logo_path"], width=38*mm, height=38*mm))
            story.append(Spacer(1, 4*mm))
        except Exception:
            st.warning("⚠️ Could not load company logo")

    story.append(Paragraph(brand.get("company","RozgarWale Pvt. Ltd."), style_h1))
    addr_line = brand.get("address","India") + (
        f"<br/>GSTIN: {brand['gstin']}" if brand.get("gstin") else ""
    ) + (f" &nbsp;&nbsp; PAN: {brand['pan']}" if brand.get("pan") else "")
    story.append(Paragraph(addr_line, style_n))
    story.append(Spacer(1, 6*mm))

    # Invoice meta
    meta_tbl = Table([
        ["Invoice No", invoice_no],
        ["Invoice Date", f"{datetime.datetime.now():%Y-%m-%d %H:%M}"],
        ["Job ID", f"{job['id']}"],
        ["Customer", f"{job['customer_name']}"],
        ["Location", f"{job['location']}"],
        ["Status", f"{job['status']}"],
    ], colWidths=[35*mm, 120*mm])
    meta_tbl.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.25,colors.black),
        ("INNERGRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph("Description", style_h2))
    story.append(Paragraph(job.get("description","-"), style_n))
    story.append(Spacer(1, 4*mm))

    # Amount table
    rows = [
        ["Particulars", "Amount (₹)"],
        ["Service Charge", f"{subtotal:,.2f}"],
    ]
    if rate > 0:
        if gst.get("split_cgst_sgst", True):
            rows.append([f"CGST @ {rate/2:.1f}%", f"{cgst:,.2f}"])
            rows.append([f"SGST @ {rate/2:.1f}%", f"{sgst:,.2f}"])
        else:
            rows.append([f"IGST @ {rate:.1f}%", f"{igst:,.2f}"])
    rows.append(["", ""])
    rows.append(["Grand Total", f"{total:,.2f}"])

    amt_tbl = Table(rows, colWidths=[120*mm, 35*mm])
    amt_tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.whitesmoke),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(-2,-1),(-1,-1),"Helvetica-Bold"),
        ("ALIGN",(-1,0),(-1,-1),"RIGHT"),
    ]))
    story.append(amt_tbl)
    story.append(Spacer(1, 8*mm))

    # Footer note
    note = (
        "This is a system-generated invoice by RozgarWale. "
        "Payments are secured via verified channels. "
        "For queries, contact support@rozgarwale.com"
    )
    story.append(Paragraph(note, style_n))

    doc.build(story)
    return str(pdf_path)


# ========================= UI BLOCK =========================
if menu == "PDF Invoice":
    st.header("🧾 Generate PDF Invoice")

    # ---- Branding / GST inputs (left aligned) ----
    with st.expander("Branding & GST settings", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("Company/Brand Name", value="RozgarWale Pvt. Ltd.")
            address = st.text_area("Company Address", value="Kolkata, India", height=70)
            logo_path = st.text_input("Logo file path (optional)", value="")
        with c2:
            gstin = st.text_input("GSTIN (optional)", value="")
            pan = st.text_input("PAN (optional)", value="")
            gst_rate = st.number_input("GST Rate (%)", min_value=0.0, max_value=28.0, value=18.0, step=0.5)
            split_tax = st.checkbox("Split as CGST + SGST", value=True, help="Untick to use IGST")

    brand_cfg = {"company": company, "address": address, "logo_path": logo_path, "gstin": gstin, "pan": pan}
    gst_cfg = {"rate": gst_rate, "split_cgst_sgst": split_tax}

    # ---- Job ID input (sanitize to UPPER, allow A-Z0-9_- or pure numbers) ----
    raw_job_id = st.text_input("Enter Job ID for Invoice", placeholder="e.g., 15 or JOB12345")
    job_id = (raw_job_id or "").strip().upper().replace(" ", "-")
    if job_id:
        st.caption(f"Job ID: *{job_id}*")

    # ---- Quick: create dummy job OR pick recent ----
    st.divider()
    st.subheader("🔧 Quick Tools")

    colA, colB = st.columns([1, 2])
    with colA:
        if st.button("➕ Create a dummy job for testing"):
            now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                # If your 'id' column is INTEGER PRIMARY KEY AUTOINCREMENT, pass NULL to autoincrement
                c.execute(
                    "INSERT INTO jobs (id, customer_name, description, location, price, status, timestamp) VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                    ("Demo Customer", "Test plumbing job", "Kolkata", 500.00, "Completed", now_ts),
                )
                conn.commit()
                new_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]
                st.success(f"✅ Dummy job created with ID: {new_id}")
                job_id = str(new_id)
            except Exception as e:
                st.error(f"Failed to create dummy job: {e}")

    with colB:
        try:
            rows = c.execute(
                "SELECT id, customer_name, description, location, price, status, timestamp FROM jobs ORDER BY timestamp DESC LIMIT 12"
            ).fetchall()
        except Exception as e:
            rows = []
            st.error(f"DB read error: {e}")

        # Build dropdown of recent IDs
        recent_ids = [str(r[0]) for r in rows if r and r[0] is not None]
        picked = st.selectbox("Or pick an existing Job ID", ["-"] + recent_ids, index=0)
        if picked not in ("-", None, ""):
            job_id = str(picked).strip().upper()
            st.caption(f"Job ID selected: *{job_id}*")

    # ---- Preview (if job exists) ----
    row = fetch_job_record(job_id) if job_id else None
    if row:
        prev = f"• ID: {row['id']} • Customer: {row['customer_name']} • Desc: {row['description']} • Location: {row['location']} • Amount: ₹{float(row['price']):.2f} • Status: {row['status']} • Time: {row['timestamp']}"
        st.info(prev)

    # ---- Validation regex ----
    valid_pattern = re.compile(r"^[A-Z0-9_-]{1,32}$|^\d{1,10}$")

    # ---- Generate button ----
    if st.button("Generate PDF", type="primary"):
        if not job_id:
            st.warning("Please enter a Job ID.")
        elif not valid_pattern.match(job_id):
            st.error("Invalid Job ID format. Use letters/numbers only (A–Z, 0–9, _ or -).")
        else:
            row = fetch_job_record(job_id)
            if not row:
                st.error(f"Job ID {job_id} not found in database.")
            else:
                try:
                    with st.spinner("Generating invoice..."):
                        pdf_path = generate_invoice_pdf_with_gst(row, brand_cfg, gst_cfg)
                    st.success(f"✅ Invoice for Job ID {row['id']}: {row['customer_name']} – ₹{float(row['price']):.2f}")
                except Exception as e:
                    st.error(f"Error generating invoice: {e}")
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "⬇ Download Invoice PDF",
                                data=f,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                            )
                    else:
                        st.info("📄 Your invoice has been generated and saved in the system folder.")
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")

elif menu == "Emergency Mode":
    st.header("🚨 Emergency Mode")
    company = st.text_input("Your Company/Organization Name")
    if st.button("Submit Request"):
        if company.strip():
            st.success(f"Request received from {company} – Team will contact shortly.")
        else:
            st.warning("Please enter your company name.")

    # ============================
# 🔥 HEATMAP (Testing Mode)
# ============================
elif menu == "Heatmap":
    st.header("🔥 Demand / Activity Heatmap (Testing Mode)")
    st.caption("If lat/lng are present in DB, we'll use them. Otherwise we show a Kolkata demo heatmap so you can test UI quickly.")

    import pydeck as pdk
    import random
    import pandas as pd
    import sqlite3

    # ---------- Helpers ----------
    def table_has_columns(cur, table, cols):
        try:
            cur.execute(f"PRAGMA table_info({table})")
            names = [r[1].lower() for r in cur.fetchall()]
            return all(c.lower() in names for c in cols)
        except Exception:
            return False

    def read_points_from_db():
        """Try workers -> (lat, lng), else jobs -> (lat, lng), else None"""
        try:
            conn_local = sqlite3.connect(DB_PATH, check_same_thread=False)
            cur = conn_local.cursor()

            # 1) workers table
            if table_has_columns(cur, "workers", ["lat", "lng"]):
                df = pd.read_sql_query("SELECT lat AS latitude, lng AS longitude FROM workers WHERE lat IS NOT NULL AND lng IS NOT NULL", conn_local)
                if not df.empty:
                    return df.assign(weight=1.0, source="workers")

            # 2) jobs table
            if table_has_columns(cur, "jobs", ["lat", "lng"]):
                df = pd.read_sql_query("SELECT lat AS latitude, lng AS longitude FROM jobs WHERE lat IS NOT NULL AND lng IS NOT NULL", conn_local)
                if not df.empty:
                    return df.assign(weight=1.0, source="jobs")

            # 3) bookings table (optional)
            if table_has_columns(cur, "bookings", ["lat", "lng"]):
                df = pd.read_sql_query("SELECT lat AS latitude, lng AS longitude FROM bookings WHERE lat IS NOT NULL AND lng IS NOT NULL", conn_local)
                if not df.empty:
                    return df.assign(weight=1.0, source="bookings")

            return None
        except Exception:
            return None

    def demo_kolkata_points(n=300):
        """Generate demo points around Kolkata bounds."""
        # Kolkata approx bounds
        lat_c, lng_c = 22.5726, 88.3639
        pts = []
        for _ in range(n):
            lat = lat_c + random.uniform(-0.15, 0.15)
            lng = lng_c + random.uniform(-0.15, 0.15)
            weight = random.uniform(0.5, 3.0)
            pts.append((lat, lng, weight))
        df = pd.DataFrame(pts, columns=["latitude", "longitude", "weight"])
        df["source"] = "demo"
        return df

    # ---------- Load data ----------
    df_points = read_points_from_db()
    using_demo = False
    if df_points is None or df_points.empty:
        df_points = demo_kolkata_points(300)
        using_demo = True

    # ---------- Sidebar / Controls ----------
    with st.sidebar:
        st.subheader("Heatmap Controls")
        default_lat = float(df_points["latitude"].mean())
        default_lng = float(df_points["longitude"].mean())
        zoom = st.slider("Map Zoom", 8, 16, 11)
        radius = st.slider("Point Radius (meters)", 100, 3000, 800, step=100)
        intensity = st.slider("Intensity Multiplier", 1, 10, 5)
        show_scatter = st.checkbox("Show dot layer (for debugging)", value=False)

    # Re-scale weight by intensity
    df = df_points.copy()
    df["weight"] = df["weight"].astype(float) * float(intensity)

    # ---------- Map Layers ----------
    heat_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_weight="weight",
        aggregation='"MEAN"',
        radiusPixels=radius // 10,  # HeatmapLayer uses pixels
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df if show_scatter else df.head(0),
        get_position="[longitude, latitude]",
        get_radius=radius,
        pickable=True,
        opacity=0.35,
    )

    view_state = pdk.ViewState(latitude=default_lat, longitude=default_lng, zoom=zoom, pitch=0)

    r = pdk.Deck(
        layers=[heat_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "Lat: {latitude}\nLng: {longitude}\nWeight: {weight}"}
    )

    st.pydeck_chart(r, use_container_width=True)

    # ---------- Summary ----------
    left, right = st.columns([1,1])
    with left:
        st.metric("Total Points", len(df))
        st.metric("Source", "DEMO (Kolkata)" if using_demo else str(df_points["source"].iloc[0]).upper())
    with right:
        st.write("*Tip:* Zoom in/out and adjust radius to see cluster intensity clearly.")

    # ---------- Quick test buttons ----------
    with st.expander("⚙ Testing Utilities"):
        if st.button("Add 100 random demo points (session only)"):
            extra = demo_kolkata_points(100)
            df_points = pd.concat([df_points, extra], ignore_index=True)
            st.success("Added 100 demo points. Change any slider to refresh map.")
        st.caption("Real DB integration will automatically reflect if your jobs/workers tables store lat/lng columns.")
def render_dispute_system():
    st.subheader("🧾 Dispute System (Testing Mode)")
    st.caption("Raise, review, and resolve disputes. (No real refunds; test flow only.)")

    left, right = st.columns([1, 2])

    with left:
        st.markdown("### ➕ Raise New Dispute")
        job_id = st.text_input("Job ID", "")
        raised_by = st.selectbox("Raised By", ["customer", "worker"])
        user_name = st.text_input("User Name", "")
        category = st.selectbox("Category", ["payment", "quality", "delay", "behavior", "other"])
        title = st.text_input("Title", "Payment not received")
        description = st.text_area("Description", "Please check the payment; it shows pending.")
        amount = st.number_input("Amount in Dispute (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        priority = st.radio("Priority", ["low", "normal", "high"], index=1, horizontal=True)
        uploads = st.file_uploader(
            "Attach evidence (images/PDFs, optional)",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
        )

        if st.button("📨 Submit Dispute"):
            did = dispute_create(job_id, raised_by, user_name, category, title, description, amount, priority)
            paths = dispute_save_uploads(uploads)
            if description or paths:
                dispute_add_message(did, author=user_name or raised_by, role=raised_by, msg=description, file_paths=paths)
            st.success(f"✅ Dispute #{did} created.")
            st.rerun()

        st.markdown("---")
        if st.button("🧪 Quick Test Disputes"):
            d1 = dispute_create("101", "customer", "rahul", "payment", "Payment short", "₹500 missing.", 500.0, "high")
            dispute_add_message(d1, "rahul", "customer", "Attaching invoice copy.", [])
            d2 = dispute_create("102", "worker", "imran", "behavior", "Misbehaviour reported", "Customer used abusive words.", 0.0, "normal")
            dispute_add_message(d2, "imran", "worker", "Please review call log.", [])
            st.success("✅ 2 demo disputes added.")
            st.rerun()

    with right:
        st.markdown("### 📋 Dispute Queue")
        f1, f2, f3 = st.columns(3)
        status_filter = f1.selectbox("Filter by Status", ["all", "open", "in_review", "awaiting_evidence", "resolved", "refunded", "rejected"], index=1)
        role_filter = f2.selectbox("Filter by Raised By", ["all", "customer", "worker"], index=0)
        search = f3.text_input("Search (job/user/title)", "")

        rows = dispute_fetch(status_filter, role_filter, search)
        if not rows:
            st.warning("No disputes found for current filters.")
        else:
            for r in rows:
                (
                    did,
                    job_id,
                    raised_by,
                    user_name,
                    category,
                    title,
                    desc,
                    amount,
                    priority,
                    status,
                    owner,
                    created_at,
                    updated_at,
                ) = r
                with st.expander(
                    f"#{did} | {title}  •  {status.upper()}  •  {category}  •  Job:{job_id}  •  By:{raised_by}",
                    expanded=False,
                ):
                    st.markdown(
                        f"*User:* {user_name}  \n"
                        f"*Priority:* {priority}  \n"
                        f"*Amount:* ₹{amount:.2f}  \n"
                        f"*Owner:* {owner or '—'}  \n"
                        f"*Created:* {created_at}  \n"
                        f"*Updated:* {updated_at}"
                    )
                    st.markdown("> *Initial Description:*\n>\n" + (desc or "(none)"))

                    msgs = dispute_fetch_messages(did)
                    if msgs:
                        st.markdown("*Conversation / Notes:*")
                        for mid, author, role, msg, file_paths, ts in msgs:
                            st.caption(f"{ts} — {author} ({role})")
                            st.write(msg or "")
                            paths = json.loads(file_paths or "[]")
                            if paths:
                                st.write("Attachments:")
                                for p in paths:
                                    st.code(p)

                    st.markdown("---")
                    mcol1, mcol2 = st.columns([3, 2])
                    with mcol1:
                        st.markdown("*Add Admin Note / Reply*")
                        note = st.text_area(f"note_{did}", placeholder="Write a reply or internal note…")
                        note_files = st.file_uploader(
                            f"Attach files for #{did}",
                            key=f"up_{did}",
                            type=["png", "jpg", "jpeg", "pdf"],
                            accept_multiple_files=True,
                        )
                        if st.button("💬 Add Note", key=f"add_{did}"):
                            paths = dispute_save_uploads(note_files)
                            dispute_add_message(did, author="admin", role="admin", msg=note, file_paths=paths)
                            st.success("Note added.")
                            st.rerun()

                    with mcol2:
                        st.markdown("*Actions*")
                        new_owner = st.text_input(f"Assign Owner for #{did}", value=owner or "", key=f"own_{did}")
                        if st.button("👤 Assign", key=f"assign_{did}"):
                            dispute_assign_owner(did, new_owner)
                            st.success("Owner assigned.")
                            st.rerun()

                        status_options = ["open", "in_review", "awaiting_evidence", "resolved", "refunded", "rejected"]
                        new_status = st.selectbox(
                            f"Update Status #{did}",
                            status_options,
                            index=status_options.index(status),
                            key=f"sts_{did}",
                        )
                        if st.button("🔄 Update Status", key=f"sts_btn_{did}"):
                            dispute_update_status(did, new_status)
                            st.success(f"Status changed to {new_status}.")
                            st.rerun()

                        if st.button("🗑 Delete Dispute", key=f"del_{did}"):
                            dispute_delete(did)
                            st.warning("Dispute deleted.")
                            st.rerun()

    st.caption(
        "Tip: ‘Quick Test Disputes’ se example rows create karke full flow test kar lo. "
        "Real refunds/wallet linkage abhi disabled (test mode)."
    )

# ====================================================
# 🪙 WALLET SYSTEM (Testing Version)
# ====================================================

# ✅ Wallet dashboard (testing-only ledger)
if menu == "Wallet":
    st.header("💼 RozgarWale Wallet")

    if "wallet_state" not in st.session_state:
        st.session_state.wallet_state = {
            "available": 1250.0,
            "pending": 280.0,
            "rewards": 420,
            "transactions": [
                {"id": "TXN-1207", "type": "credit", "label": "Job #231 payout", "amount": 650.0, "status": "settled", "timestamp": "2024-05-19 14:10"},
                {"id": "TXN-1184", "type": "debit", "label": "Fast payout fee", "amount": -49.0, "status": "settled", "timestamp": "2024-05-18 19:42"},
                {"id": "TXN-1160", "type": "credit", "label": "Customer tip", "amount": 150.0, "status": "settled", "timestamp": "2024-05-16 11:03"},
                {"id": "TXN-1154", "type": "credit", "label": "Job #226 payout", "amount": 520.0, "status": "pending", "timestamp": "2024-05-16 08:55"},
            ],
        }

    wallet_state = st.session_state.wallet_state

    c1, c2, c3 = st.columns(3)
    c1.metric("Available Balance", f"₹{wallet_state['available']:,.2f}")
    c2.metric("Pending Clearance", f"₹{wallet_state['pending']:,.2f}")
    c3.metric("Reward Credits", f"{wallet_state['rewards']} pts")

    st.subheader("Recent Transactions")
    if wallet_state["transactions"]:
        tx_rows = [
            [
                tx["timestamp"],
                tx["id"],
                tx["label"],
                "Credit" if tx["type"] == "credit" and tx["amount"] >= 0 else "Debit",
                f"₹{tx['amount']:,.2f}",
                tx["status"].title(),
            ]
            for tx in wallet_state["transactions"]
        ]
        tx_df = pd.DataFrame(
            tx_rows,
            columns=["When", "Txn ID", "Description", "Type", "Amount", "Status"],
        )
        st.dataframe(tx_df, use_container_width=True, hide_index=True)
    else:
        st.info("No wallet transactions yet. Complete jobs to see payouts here.")

    st.subheader("Manual Adjustments (demo)")
    col_add, col_withdraw = st.columns(2)

    with col_add:
        topup = st.number_input(
            "Add credit amount (₹)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            key="wallet_topup_amt",
        )
        if st.button("Add Credit", key="wallet_add_btn"):
            if topup <= 0:
                st.warning("Enter an amount greater than zero.")
            else:
                wallet_state["available"] += topup
                wallet_state["transactions"].insert(
                    0,
                    {
                        "id": f"TXN-{random.randint(2000,9999)}",
                        "type": "credit",
                        "label": "Manual wallet top-up",
                        "amount": topup,
                        "status": "settled",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    },
                )
                st.success(f"₹{topup:,.2f} credited to wallet.")
                safe_rerun()

    with col_withdraw:
        withdraw = st.number_input(
            "Withdraw amount (₹)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            key="wallet_withdraw_amt",
        )
        if st.button("Request Withdrawal", key="wallet_withdraw_btn"):
            if withdraw <= 0:
                st.warning("Enter an amount greater than zero.")
            elif withdraw > wallet_state["available"]:
                st.error("Withdrawal exceeds available balance.")
            else:
                wallet_state["available"] -= withdraw
                wallet_state["pending"] += withdraw
                wallet_state["transactions"].insert(
                    0,
                    {
                        "id": f"TXN-{random.randint(3000,9999)}",
                        "type": "debit",
                        "label": "Withdrawal request",
                        "amount": -withdraw,
                        "status": "pending",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    },
                )
                st.success("Withdrawal request submitted. Will be moved from pending once processed.")
                safe_rerun()

    st.caption("Note: Wallet balances here are demo-only and reset when the app restarts.")


# ✅ Subscription Management
elif menu == "Subscription":
    st.header("💳 Subscriptions")

    if not isinstance(st.session_state.get("subscription"), dict):
        st.session_state["subscription"] = None

    plans = [
        {
            "name": "Free",
            "tagline": "Discover RozgarWale basics",
            "price": 0,
            "price_label": "₹0 / month",
            "features": [
                "Browse worker profiles",
                "Create up to 3 job posts / month",
                "Basic support (email)",
            ],
        },
        {
            "name": "Basic",
            "tagline": "Grow with scheduling tools",
            "price": 399,
            "price_label": "₹399 / month",
            "features": [
                "Unlimited job posts",
                "Priority matching engine",
                "SMS + WhatsApp notifications",
                "Basic analytics dashboard",
            ],
        },
        {
            "name": "Pro",
            "tagline": "Full automation + AI insights",
            "price": 899,
            "price_label": "₹899 / month",
            "features": [
                "AI-powered job descriptions",
                "Dedicated account manager",
                "Advanced reports & CSV exports",
                "Dispute handling priority lane",
                "Early access to beta modules",
            ],
        },
    ]

    st.subheader("Plan Comparison")
    table_rows = [
        {
            "Plan": p["name"],
            "Price": p["price_label"],
            "Highlights": " • ".join(p["features"][:3]) + ("…" if len(p["features"]) > 3 else ""),
        }
        for p in plans
    ]
    st.table(pd.DataFrame(table_rows))

    active = st.session_state.get("subscription")
    st.subheader("Your Subscription")
    if active:
        st.success(
            f"Active Subscription: **{active['name']}** "
            f"({active['price_label']}) — since {active['purchased_at']}"
        )
    else:
        st.info("No active subscription yet. Pick a plan below to unlock more features.")

    st.subheader("Choose a Plan")
    cols = st.columns(len(plans))
    for col, plan in zip(cols, plans):
        with col:
            st.markdown(f"### {plan['name']}")
            st.caption(plan["tagline"])
            st.markdown(f"**{plan['price_label']}**")
            for feat in plan["features"]:
                st.write(f"• {feat}")

            already_active = bool(active and active.get("name") == plan["name"])
            button_label = "Current Plan" if already_active else "Purchase"
            if st.button(
                button_label,
                key=f"sub_{plan['name']}",
                disabled=already_active,
            ):
                st.session_state["subscription"] = {
                    "name": plan["name"],
                    "price": plan["price"],
                    "price_label": plan["price_label"],
                    "features": plan["features"],
                    "purchased_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                st.success(f"{plan['name']} plan activated. Enjoy the new benefits!")
                safe_rerun()


# ✅ CRM System
elif menu == "CRM":
    st.header("🧮 CRM Dashboard")
    st.metric("Total Workers", "1024")
    st.metric("Active Customers", "847")
    st.metric("Monthly Bookings", "563")

# ✅ Support Chat
elif menu == "Support Chat":
    st.header("💬 Support Chat (Mock)")
    message = st.text_input("Your message")
    if st.button("Send"):
        st.success("Support team received your message. They will reply soon.")

# ✅ Booking Calendar
elif menu == "Calendar":
    st.header("📅 Booking Calendar")
    st.date_input("Select date to view bookings")
    st.text("Calendar view: Bookings shown here (demo)")

# ✅ Live Chat System
elif menu == "Live Chat":
    st.header("💬 Live Chat with Worker (Mock)")
    msg = st.text_input("Enter message to send to assigned worker")
    if st.button("Send Message"):
        st.success("Message sent! (Simulated)")

# ✅ Worker Availability
elif menu == "Availability":
    st.header("⏰ Worker Availability")
    worker_id = st.number_input("Worker ID", step=1)
    status = st.selectbox("Set Availability", ["Available", "Busy", "On Leave"])
    if st.button("Update Status"):
        st.success(f"Status set to: {status} (Mock)")

# ✅ Skill Test
elif menu == "Skill Test":
    st.header("🧪 Skill Verification Test")
    st.text("Question: How to fix a leaking pipe?")
    answer = st.text_area("Your Answer")
    if st.button("Submit Answer"):
        st.success("Answer submitted for evaluation! (Mock)")

# ✅ PAN & GST Invoice Generator (Mock)
elif menu == "PAN-GST Invoice":
    st.header("🧾 GST + PAN Linked Invoice")
    pan = st.text_input("Enter PAN Number")
    gst = st.text_input("Enter GSTIN")
    if st.button("Generate PAN-GST Invoice"):
        st.success("Invoice generated with PAN & GST (Mock)")

# ✅ RozgarWale Loyalty Credits
elif menu == "Wallet Credits":
    st.header("🏅 RozgarWale Loyalty Points")
    user_id = st.text_input("Enter Your ID")
    if st.button("Check Points"):
        points = random.randint(50, 500)  # Generate random points
        st.success(f"You have {points} RozgarWale credits!")

# ✅ Job Filter System (Phase 397–400)
elif menu == "Job Filter":
    st.header("🧰 Job Filter")
    skill = st.selectbox(
        "Filter by Skill", ["All", "Plumber", "Electrician", "Mechanic"]
    )
    location = st.text_input("Location Filter")
    if st.button("Apply Filter"):
        if skill == "All":
            c.execute(
                "SELECT id, customer_name, description, location, status, assigned_worker, price, timestamp FROM jobs WHERE location LIKE ?",
                (f"%{location}%",),
            )
        st.success("Filter applied! (Mock)")

# ✅ AI Resume Sentiment Analysis (Mock)
elif menu == "Feedback Sentiment":
    st.header("🧠 Feedback Sentiment")
    text = st.text_area("Paste Feedback")
    if st.button("Analyze Sentiment"):
        if "bad" in text.lower():
            st.error("Negative sentiment detected!")
        elif "good" in text.lower():
            st.success("Positive feedback!")
        else:
            st.info("Neutral")

# ✅ Resume PDF Generator (Full)
elif menu == "Resume Generator":
    st.header("📄 Final Resume Generator")
    worker_id = st.text_input("Worker ID")
    if st.button("Create PDF Resume"):
        c.execute("SELECT * FROM workers WHERE id=?", (worker_id,))
        row = c.fetchone()
        if row:
            st.success(f"Resume for {row[1]} with skill {row[2]} generated! (Mock)")
        else:
            st.error("Worker not found.")

# ✅ Auto Smart Routing System (Mock)
elif menu == "GPS":
    st.header("📍 Smart Auto Routing")
    st.text("Auto-assign nearest available worker using GPS + availability (Demo only)")

# ✅ Referral + Loyalty
elif menu == "Referral Program":
    st.header("🎁 Referral + Loyalty")
    user = st.text_input("Your ID")
    if st.button("Generate Referral Code"):
        st.success(f"Code: REF-{user}-{random.randint(1000,9999)}")

# ✅ CRM Dashboard – Final
# ✅ CRM Dashboard – Final

# ✅ Admin Control Panel – Log (Mock)
elif menu == "Corporate Module":
    st.header("📘 Admin Logs (Corporate)")
    st.text("Admin actions log, booking history and analytics (Mock UI)")


# ✅ End of App
st.sidebar.info("✅ All 600 Phases Integrated")
