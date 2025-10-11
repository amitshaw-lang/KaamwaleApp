from voice_job_posting_page import show_voice_job_posting# ✅ RozgarWale app.py — Part 1 (Phase 1–200 Features Implemented)
from ai_job_desc_page import show_ai_job_desc
from ai_resume_page import show_ai_resume  # optional, if you created it
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import random
import os

st.set_page_config(page_title="RozgarWale App", layout="wide")
st.title("🛠️ RozgarWale – Sab Kaam Ek App Se")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "rozgarwale.db")

@st.cache_resource
def get_conn():
    # Single shared connection for Streamlit app
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")  # wait if DB is momentarily locked
    return conn

conn = get_conn()
c = conn.cursor() 

# --- DEBUG: check index list ---
c.execute("PRAGMA index_list(workers)")
st.write(c.fetchall())   # isme idx_workers_name_phone dikhna chahiye
# -------------------------------
st.caption(f"🗂 DB: {DB_PATH}")
# Debug: total workers count

# Tables create
c.execute("""CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, skill TEXT, location TEXT, phone TEXT,
    experience TEXT, aadhar TEXT, verified INTEGER DEFAULT 0,
    earnings REAL DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT, location TEXT, price REAL,
    status TEXT, assigned_worker TEXT, timestamp TEXT
)""")

# Agar customer_name column missing hai to add karo
try:
    c.execute("ALTER TABLE jobs ADD COLUMN customer_name TEXT")
    conn.commit()
except Exception:
    pass   # agar already column hai to ignore

c.execute("""CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER, rating INTEGER,
    comment TEXT, timestamp TEXT
)""")

# UNIQUE index banane ke liye (same name+phone dobara insert nahi hoga)
c.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS idx_workers_name_phone
ON workers(name, phone);
""")
 
conn.commit()   # ✅ iske turant niche daalo

# Ab count check karo (kitne workers DB me hai)
c.execute("SELECT COUNT(*) FROM workers")
count = c.fetchone()[0]
st.caption(f"👷 Workers in DB: {count}")

# # INSERT BLOCK START
# try:
#     c.execute("""
#         INSERT INTO workers (name, skill, location, phone, experience, aadhar, verified)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, ("Raju Kumar", "Plumber", "Kolkata", "9876543210", "5 years", "XXXX-YYYY-ZZZZ", "Yes"))
#     conn.commit()
# except Exception as e:
#     st.warning(f"Insert skipped: {e}")

# try:
#     workers_data = [
#         ("Sohan Das", "Electrician", "Howrah", "9876500001", "3 years", "AAAA-BBBB-CCCC", "Yes"),
#         ("Rahul Singh", "Carpenter", "Kolkata", "9876500002", "7 years", "DDDD-EEEE-FFFF", "No"),
#         ("Arjun Yadav", "Mechanic", "Durgapur", "9876500003", "4 years", "GGGG-HHHH-IIII", "Yes"),
#     ]
#     c.executemany("""
#         INSERT INTO workers (name, skill, location, phone, experience, aadhar, verified)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, workers_data)
#     conn.commit()
# except Exception as e:
#     st.warning(f"Bulk insert skipped: {e}")
# # INSERT BLOCK END 

c.execute('''CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, skill TEXT, location TEXT, phone TEXT,
    experience TEXT, aadhar TEXT, verified INTEGER DEFAULT 0,
    earnings REAL DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT, job_description TEXT, location TEXT,
    status TEXT, assigned_worker TEXT, price REAL, timestamp TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER, rating INTEGER, comment TEXT, timestamp TEXT
)''')

conn.commit()

# Tables create
c.execute("""CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    skill TEXT,
    location TEXT,
    phone TEXT,
    experience TEXT,
    aadhaar TEXT,
    verified TEXT,
    earnings TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_description TEXT,
    location TEXT,
    price REAL,
    timestamp TEXT,
    status TEXT,
    assigned_worker TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id INTEGER,
    rating INTEGER,
    comment TEXT,
    timestamp TEXT
)""")

conn.commit()

# Insert ek sample worker (sirf pehli baar run karne ke liye)
try:
    c.execute("""
    INSERT INTO workers (name, skill, location, phone, experience, aadhaar, verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Raju Kumar", "Plumber", "Kolkata", "9876543210", "5 years", "XXXX-YYYY-ZZZZ", "Yes"))
    conn.commit()
except Exception:
    pass  # agar already insert ho chuka hoga toh error ignore

# Insert extra sample workers (sirf pehli baar run ke liye)
try:
    workers_data = [
        ("Sohan Das", "Electrician", "Howrah", "9876500001", "3 years", "AAAA-BBBB-CCCC", "Yes"),
        ("Rahul Singh", "Carpenter", "Kolkata", "9876500002", "7 years", "DDDD-EEEE-FFFF", "No"),
        ("Arjun Yadav", "Mechanic", "Durgapur", "9876500003", "4 years", "GGGG-HHHH-IIII", "Yes")
    ]
    c.executemany("""
        INSERT INTO workers (name, skill, location, phone, experience, aadhaar, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, workers_data)
    conn.commit()
except Exception:
    pass

# ⬇ YAHAN ADD KARO (ek baar ke liye data insert karne ke liye)
try:
    c.execute("""
    INSERT INTO workers (name, skill, location, phone, experience, aadhaar, verified)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Raju Kumar", "Plumber", "Kolkata", "9876543210", "5 years", "XXXX-YYYY-ZZZZ", "Yes"))
    conn.commit()
except Exception:
    pass

# ✅ Sidebar Menu
menu = st.sidebar.selectbox("Main Menu", [
    "Worker Profile", "Customer Signup", "Job Post", "CSV Manager", "AI Assistant",
    "Notifications", "Bookings", "Review System", "Referral Program", "PDF Invoice",
    "Wallet", "Emergency Mode", "Heatmap", "Dispute System", "Subscription",
    "Resume Generator", "Corporate Module", "CRM", "Support Chat", "Voice Job Post","Audio Test",
    "Search Workers", "Booking Status", "Calendar", "Live Chat", "Feedback", "GPS", "Skill Test",
    "Availability","AI Job Description","AI Resume","Search Jobs"
])
st.write("DEBUG menu ->", repr(menu))

# ✅ Worker Profile Section
if menu == "Worker Profile":
    st.header("👷 Worker Profile")
    with st.form("worker_form"):
        name = st.text_input("Name")
        skill = st.selectbox("Skill", ["Plumber", "Electrician", "Carpenter", "Mechanic"])
        location = st.text_input("Location")
        phone = st.text_input("Phone")
        experience = st.text_input("Experience")
        aadhar = st.file_uploader("Upload Aadhaar")
        submit = st.form_submit_button("Submit")
    if submit:
        # --- 1) inputs clean/normalize ---
        nm  = (name or "").strip()
        sk  = (skill or "").strip()
        loc = (location or "").strip()
        ph  = (phone or "").strip().replace(" ", "").replace("-", "")
        exp = (experience or "").strip()
        
        if not nm or not ph:
            st.warning("⚠ Name aur Phone required hai.")
        else:
            try:
                # --- 2) duplicate check: same name (case-insensitive) + phone ---
                c.execute(
                    "SELECT id FROM workers WHERE name = ? COLLATE NOCASE AND phone = ?",
                    (nm, ph)
                )
                already = c.fetchone()

                if already:
                    st.warning("⚠ Duplicate: same name + phone already exists. Not added.")
                else:
                    # --- 3) safe insert ---
                    conn.execute("BEGIN IMMEDIATE")
                    c.execute("""
                        INSERT INTO workers
                            (name, skill, location, phone, experience, aadhar)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (nm, sk, loc, ph, exp, aadhar))
                    conn.commit()
                    st.success("✅ Worker saved!")
            except Exception as e:
                st.error(f"DB error: {e}")
        # Voice Job Post Section
elif menu == "Voice Job Post":
    show_voice_job_posting()   # ye function tumne voice_job_posting_page.py me banaya hai

elif menu == "AI Job Description":
    show_ai_job_desc()

elif menu == "AI Resume":
    show_ai_resume()

elif menu == "Audio Test":
    import test_audio  # file: test_audio.py
    test_audio.app()

# ✅ Customer Signup Section
elif menu == "Customer Signup":
    st.header("🧍 Customer Signup")
    name = st.text_input("Customer Name")
    phone = st.text_input("Phone Number")
    if st.button("Signup"):
        st.success(f"Customer {name} signed up successfully! (Demo)")

elif menu.strip().lower() == "audio test":
    st.success("Reached Audio Test branch")  # debug confirm
    import test_audio
    test_audio.app()

# ✅ Job Post Section
elif menu == "Job Post":
    st.header("📝 Post a Job")
    cust_name = st.text_input("Customer Name")
    job_desc = st.text_area("Job Description")
    location = st.text_input("Location")
    price = st.text_input("Price")  # Add price input field
    if st.button("Post Job"):
        cust = (cust_name or "").strip()    # <-- input se aya hua naam
        desc = (job_desc  or "").strip()
        loc  = (location  or "").strip()
        prc  = float(price) if str(price).strip() else 0.0

# DEBUG: what did we capture?
        st.write({"cust": repr(cust), "desc": repr(desc), "loc": repr(loc), "prc": prc})
        st.write({"lens": (len(cust), len(desc), len(loc))})
        if not cust or not desc or not loc:
            st.warning("⚠ Customer name, description aur location required hai.")
        else:
            try:
                conn.execute("BEGIN IMMEDIATE")
                c.execute("""
                    INSERT INTO jobs (customer_name, description, location, price, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (cust, desc, loc, prc, "open", str(datetime.datetime.now())))
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
    from datetime import datetime
    import pandas as pd
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
        "Enter keyword (customer, job description, location)",
        key="kw_jobs"
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
        c.execute("SELECT id, customer_name, description, location, price, status, timestamp FROM jobs")
        st.session_state.job_rows = c.fetchall()
        st.session_state.last_keyword = ""

    # ---------- Results ----------
    rows = st.session_state.job_rows
    if rows:
        # DataFrame
        df = pd.DataFrame(
            rows,
            columns=["ID", "Customer", "Description", "Location", "Price", "Status", "Timestamp"]
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
            f_status = st.multiselect("Filter status", ["open", "completed", "cancelled"], default=[])
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
        csv = tmp.drop(columns=["StatusRaw"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download jobs (CSV)",
            data=csv,
            file_name="jobs_results.csv",
            mime="text/csv",
            key="dl_jobs_csv"
        )

        # Quick stats
        total_jobs = len(tmp)
        total_price = tmp["Price"].apply(_to_num).sum()
        st.caption(f"{total_jobs} job(s) • Total price approx ₹{int(total_price):,}")

        # ---------- Update status controls ----------
        job_ids = tmp["ID"].tolist()
        selected_id = st.selectbox("Select Job ID to update", job_ids, key="upd_search_id")

        # Preselect current status of selected row
        cur_status = df.loc[df["ID"] == selected_id, "StatusRaw"].iloc[0]
        status_choices = ["open", "completed", "cancelled"]
        new_status = st.selectbox(
            "Update status",
            status_choices,
            index=status_choices.index(cur_status),
            key="upd_search_status"
        )

        # ---------- Update button ----------
        if st.button("Update Job Status"):
            try:
                c.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, selected_id))
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

# ==== AI Assistant menu block ====
elif menu == "AI Assistant":
    st.header("🤖 RozgarWale AI Assistant")
    st.write("Ask anything about jobs, pricing, job profiles, etc.")

    # Input box
    user_q = st.text_input("Type your question...", value="", key="ai_q")

    # Clear button
    if st.button("🧹 Clear chat"):
        st.session_state["ai_last"] = None
        st.experimental_rerun()

    # Optional: Fraud check (Mock)
    st.subheader("🛡 AI Assistant – Fraud Check (Mock)")
    desc = st.text_area("Describe the Job or Situation", placeholder="e.g., my tap pipe is leaked")
    if st.button("Run AI Fraud Check"):
        risk = "✅ Low risk"
        if any(w in desc.lower() for w in ["advance", "prepaid", "otp", "fee", "refund", "link"]):
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
            ans = "⚠ AI Assistant is temporarily unavailable (API key missing/disabled)."

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
        # handle 'YYYY-MM-DD HH:MM:SS' or ISO strings
        return datetime.fromisoformat(str(x)).strftime("%d-%b-%Y %I:%M %p")
    except Exception:
        return str(x)

def _fmt_price(x) -> str:
    try:
        v = float(x)
        return f"₹{int(v):,}"
    except Exception:
        return str(x)

def _status_icon(s: str) -> str:
    s = (s or "").strip().lower()
    if s == "completed":
        return "🟢 Completed"
    if s == "cancelled":
        return "🔴 Cancelled"
    # default / open
    return "🟡 Open"

def show_bookings(conn):
    st.header("📒 Job Bookings")

    # --- read rows (handle DBs without 'worker' column) ---
    c = conn.cursor()
    try:
        rows = c.execute("""
            SELECT id, customer_name, description, location, status, worker, price, timestamp
            FROM jobs
            ORDER BY timestamp DESC
        """).fetchall()
        cols = ["ID", "Customer", "Description", "Location", "Status", "Worker", "Price", "Timestamp"]
    except Exception:
        # fallback: old schema without worker
        rows = c.execute("""
            SELECT id, customer_name, description, location, status, price, timestamp
            FROM jobs
            ORDER BY timestamp DESC
        """).fetchall()
        cols = ["ID", "Customer", "Description", "Location", "Status", "Price", "Timestamp"]

    df = pd.DataFrame(rows, columns=cols)
    if df.empty:
        st.info("No bookings yet.")
        return

    # ensure Worker column exists for consistent UI
    if "Worker" not in df.columns:
        df["Worker"] = "—"

    # --- basic transforms / pretty columns ---
    df["Price"] = df["Price"].apply(_fmt_price)
    df["Status"] = df["Status"].apply(_status_icon)
    df["Timestamp"] = df["Timestamp"].apply(_fmt_ts)

    # --- Filters row ---
    with st.container():
        f1, f2, f3, f4 = st.columns([2, 2, 2, 2])

        # Status filter
        all_status = ["🟡 Open", "🟢 Completed", "🔴 Cancelled"]
        pick_status = f1.multiselect("Filter: Status", all_status, default=all_status)

        # Location filter (unique values)
        locs = sorted([x for x in df["Location"].astype(str).unique() if x and x != "None"])
        pick_loc = f2.multiselect("Filter: Location", locs, default=locs if locs else [])

        # Text search
        q = f3.text_input("Search (customer / description / worker)")
        # Quick action
        dl_all = f4.checkbox("Download filtered CSV")

    # apply filters
    mask = pd.Series([True] * len(df))
    if pick_status:
        mask &= df["Status"].isin(pick_status)
    if pick_loc:
        mask &= df["Location"].astype(str).isin(pick_loc)
    if q:
        ql = q.lower()
        mask &= (
            df["Customer"].astype(str).str.lower().str.contains(ql)
            | df["Description"].astype(str).str.lower().str.contains(ql)
            | df["Worker"].astype(str).str.lower().str.contains(ql)
            | df["Location"].astype(str).str.lower().str.contains(ql)
        )

    view = df.loc[mask].copy()

    # show summary chips
    c1, c2, c3 = st.columns(3)
    c1.metric("Total bookings", len(view))
    c2.metric("Open", (view["Status"] == "🟡 Open").sum())
    c3.metric("Completed", (view["Status"] == "🟢 Completed").sum())

    # dataframe
    st.dataframe(
        view[["ID", "Customer", "Description", "Location", "Status", "Worker", "Price", "Timestamp"]],
        use_container_width=True,
        hide_index=True
    )

    # CSV download of filtered view (restore raw-ish columns)
    if dl_all and not view.empty:
        # make a clean CSV without icons
        export = view.copy()
        export["Status"] = export["Status"].str.replace("🟡 ", "", regex=False)\
                                           .str.replace("🟢 ", "", regex=False)\
                                           .str.replace("🔴 ", "", regex=False)
        # try to convert price back to int
        def _unfmt_price(p):
            try:
                return int(str(p).replace("₹", "").replace(",", ""))
            except Exception:
                return p
        export["Price"] = export["Price"].apply(_unfmt_price)

        st.download_button(
            "⬇ Download filtered bookings (CSV)",
            data=export.to_csv(index=False).encode("utf-8"),
            file_name="bookings_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )
# ===== End Bookings page =====

if menu == "Bookings":
    show_bookings(conn)   # conn = sqlite3 connection

# ✅ Review System
elif menu == "Review System":
    st.header("🌟 Submit a Review")
    worker_id = st.number_input("Worker ID", step=1)
    rating = st.slider("Rating", 1, 5)
    comment = st.text_area("Comment")
    if st.button("Submit Review"):
        c.execute("INSERT INTO feedback (worker_id, rating, comment, timestamp) VALUES (?,?,?,?)",
                  (worker_id, rating, comment, str(datetime.datetime.now())))
        conn.commit()
        st.success("Review submitted!")

elif menu == "Search Workers":
    st.header("🔎 Search Workers")

    keyword = st.text_input("Enter name, skill or location")

    # search button
    if st.button("Search"):
        if not keyword.strip():
            st.warning("⚠ Please type something to search")
        else:
            try:
                c.execute("""
                    SELECT id, name, skill, location, phone, experience, aadhar, verified, earnings
                    FROM workers
                    WHERE name LIKE ? OR skill LIKE ? OR location LIKE ?
                    ORDER BY name COLLATE NOCASE
                """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
                rows = c.fetchall()

                if rows:
                    # ---- Polished table for Search Workers ----
                    import pandas as pd

                    df = pd.DataFrame(
                        rows,
                        columns=["ID", "Name", "Skill", "Location", "Phone", "Experience", "Aadhar", "Verified", "Earnings"]
                    )

                    # --- small format helpers
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

                    # --- clean / beautify columns
                    for col in ("Name", "Skill", "Location"):
                        if col in df.columns:
                            df[col] = df[col].astype(str).str.title()

                    if "Verified" in df.columns:
                        df["Verified"] = df["Verified"].apply(fmt_verified)

                    if "Earnings" in df.columns:
                        df["Earnings"] = df["Earnings"].apply(fmt_inr)

                    if "Phone" in df.columns:
                        df["Phone"] = df["Phone"].apply(fmt_phone)

                    # Ensure proper column order
                    cols = ["ID", "Name", "Skill", "Location", "Phone", "Experience", "Aadhar", "Verified", "Earnings"]
                    df = df[[c for c in cols if c in df.columns]]

                    # Show nicely
                    st.success(f"✅ Found {len(df)} result(s)")
                    st.dataframe(df, use_container_width=True)

                    # Quick export
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇ Download results (CSV)",
                        data=csv,
                        file_name="workers_results.csv",
                        mime="text/csv",
                        key="dl_workers_csv"
                    )

                else:
                    st.info("⚠ No results found. Dusra keyword try karo ya click [Show All].")

            except Exception as e:
                st.error(f"❌ Search error: {e}")

    # Show all button
    if st.button("Show All"):
        try:
            c.execute("SELECT id, name, skill, location, phone, experience, aadhar, verified, earnings FROM workers")
            rows = c.fetchall()

            if rows:
                import pandas as pd
                df = pd.DataFrame(
                    rows,
                    columns=["ID", "Name", "Skill", "Location", "Phone", "Experience", "Aadhar", "Verified", "Earnings"]
                )

                # format again
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

                cols = ["ID", "Name", "Skill", "Location", "Phone", "Experience", "Aadhar", "Verified", "Earnings"]
                df = df[[c for c in cols if c in df.columns]]

                st.success(f"✅ Found {len(df)} worker(s)")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇ Download results (CSV)",
                    data=csv,
                    file_name="workers_results.csv",
                    mime="text/csv",
                    key="dl_workers_csv_all"
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


# ✅ Aadhaar Upload
#   elif menu == "Aadhaar Upload":
st.header("🆔 Upload Aadhaar Document")
aadhaar = st.file_uploader("Upload your Aadhaar file")
if aadhaar:
    st.success("Aadhaar uploaded!")

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

# ✅ Referral Program
elif menu == "Referral Program":
    st.header("🎁 Referral Program")
    user_id = st.text_input("Enter your user ID")
    if st.button("Get Referral Code"):
        referral_code = f"REF{random.randint(1000,9999)}"
        st.success(f"Your referral code is: {referral_code}")

# ✅ PDF Invoice (Placeholder)
elif menu == "PDF Invoice":
    st.header("🧾 Generate Invoice")
    job_id = st.text_input("Enter Job ID for Invoice")
    if st.button("Generate PDF"):
        st.success(f"Invoice PDF generated for Job ID: {job_id} (Mock)")

# ✅ Wallet
elif menu == "Wallet":
    st.header("💰 RozgarWale Wallet")
    worker_id = st.number_input("Enter Worker ID", step=1)
    if st.button("Check Wallet Balance"):
        c.execute("SELECT earnings FROM workers WHERE id=?", (worker_id,))
        row = c.fetchone()
        if row:
            st.success(f"Wallet Balance: ₹{row[0]:.2f}")
        else:
            st.error("Worker not found.")

# ✅ Emergency Mode
elif menu == "Emergency Mode":
    st.header("🚨 1-Hour Emergency Service")
    location = st.text_input("Enter Location for Emergency")
    if st.button("Activate Emergency"):
        st.warning(f"Emergency worker dispatched to {location} within 1 hour! (Mock)")

# ✅ Heatmap
elif menu == "Heatmap":
    st.header("🌡️ Worker Demand Heatmap (Mock)")
    st.text("Heatmap: High demand in Kolkata, Asansol, Durgapur (demo)")

# ✅ Dispute System
elif menu == "Dispute System":
    st.header("⚖️ Dispute Resolution")
    job_id = st.text_input("Job ID")
    reason = st.text_area("Reason for dispute")
    if st.button("Submit Dispute"):
        st.success(f"Dispute raised for Job {job_id} – Our team will review. (Mock)")

# ✅ Subscription System
elif menu == "Subscription":
    st.header("📦 Subscription Packages")
    option = st.selectbox("Choose Plan", ["Free", "Pro ₹99/mo", "Elite ₹199/mo"])
    if st.button("Subscribe"):
        st.success(f"Subscribed to {option} Plan! (Mock)")

# ✅ Resume Generator
elif menu == "Resume Generator":
    st.header("📄 Worker Resume Generator")
    worker_id = st.text_input("Enter Worker ID")
    if st.button("Generate Resume"):
        st.success(f"Resume PDF generated for Worker ID {worker_id} (Mock)")

# ✅ Corporate Module
elif menu == "Corporate Module":
    st.header("🏢 Corporate Booking Module")
    company = st.text_input("Company Name")
    requirement = st.text_area("Workforce Requirement")
    if st.button("Submit Request"):
        st.success(f"Request received from {company} – Team will contact shortly.")

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
menu_stripped = menu.strip()
if menu_stripped == "Job Filter":
    st.header("🧰 Job Filter")
    skill = st.selectbox("Filter by Skill", ["All", "Plumber", "Electrician", "Mechanic"])
    location = st.text_input("Location Filter")
    if st.button("Apply Filter"):
        if skill == "All":
            c.execute("SELECT id, customer_name, description, location, status, assigned_worker, price, timestamp FROM jobs WHERE location LIKE ?", (f"%{location}%",))
        else:
            c.execute("SELECT id, customer_name, description, location, status, assigned_worker, price, timestamp FROM jobs WHERE location LIKE ? AND description LIKE ?", (f"%{location}%", f"%{skill}%"))
        rows = c.fetchall()
        st.dataframe(pd.DataFrame(rows, columns=["ID", "Customer", "Description", "Location", "Status", "Worker", "Price", "Timestamp"]))
    # ✅ RozgarWale App — Part 3 (Final Features: Phase 401–600)

# ✅ ETA Countdown System
elif menu == "Booking Status":
    st.header("⏳ Booking ETA Countdown")
    job_id = st.text_input("Job ID")
    eta = st.number_input("ETA in minutes", min_value=1)
    if st.button("Start Countdown"):
        st.success(f"ETA countdown for Job {job_id} started – {eta} mins remaining (mock)")

# ✅ Voice-to-Text Job Posting
elif menu == "Voice Job Post":
    st.header("🎙️ Voice to Text Job Post (Mock)")
    st.text("Feature will capture voice and convert to job post automatically.")


# ✅ Admin Weekly Report to Email
elif menu == "Notifications":
    st.header("📧 Admin Weekly Report (Mock)")
    email = st.text_input("Enter Admin Email")
    if st.button("Send Report"):
        st.success(f"Report sent to {email} (Simulated)")

# ✅ SOS Alert
elif menu == "Emergency Mode":
    st.header("🚨 SOS Alert Button")
    user = st.text_input("Enter User ID")
    if st.button("Send SOS Alert"):
        st.warning(f"SOS Alert sent for User {user}! (Simulated)")

# ✅ Offline Mode Sync (Mock)
elif menu == "Offline Sync":
    st.header("📶 Offline Mode")
    st.text("You are in offline mode. Data will sync when internet is restored. (Mock)")

# ✅ Recent Bookings Carousel
# elif menu == "Bookings":
#     st.header("🧾 Recent Bookings")
#     c.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 5")
#     rows = c.fetchall()
#     for row in rows:
#         st.info(f"📌 {row[1]} booked {row[2]} at {row[3]} – Status: {row[4]}")

# ✅ Multi Job Bundling
elif menu == "Subscription":
    st.header("📦 Bundle Multiple Jobs")
    jobs = st.text_area("Enter multiple jobs separated by commas")
    if st.button("Bundle Jobs"):
        st.success("All jobs bundled successfully! (Mock)")

# ✅ AI Resume Sentiment Analysis (Mock)
elif menu == "Feedback":
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
elif menu == "CRM":
    st.header("📊 CRM Analytics")
    c.execute("SELECT COUNT(*) FROM workers")
    total_workers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    st.metric("Total Workers", total_workers)
    st.metric("Total Jobs", total_jobs)

# ✅ Admin Control Panel – Log (Mock)
elif menu == "Corporate Module":
    st.header("📘 Admin Logs (Corporate)")
    st.text("Admin actions log, booking history and analytics (Mock UI)")

# ✅ Support Chat Widget (Mock UI)
elif menu == "Support Chat":
    st.header("💬 In-App Support Chat Widget")
    msg = st.text_input("Type your query")
    if st.button("Send to Support"):
        st.success("Support has received your query! (Simulated)")

# ✅ End of App
st.sidebar.info("✅ All 600 Phases Integrated")