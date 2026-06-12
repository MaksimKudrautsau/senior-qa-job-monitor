import sqlite3

DB_NAME = "jobs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT UNIQUE,
            title TEXT,
            company TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def job_exists(job_url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM jobs WHERE job_url = ?",
        (job_url,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def save_job(job_url, title, company):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs
        (job_url, title, company)
        VALUES (?, ?, ?)
    """, (job_url, title, company))

    conn.commit()
    conn.close()