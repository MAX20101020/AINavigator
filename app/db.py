import json
import sqlite3
from datetime import datetime

DB_NAME = "navigator.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_point TEXT NOT NULL,
            finish_point TEXT NOT NULL,
            route TEXT NOT NULL,
            distance REAL NOT NULL,
            time REAL,
            traffic INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            actual_time REAL,
            actual_distance REAL
        )
    """)

    columns = [row[1] for row in cursor.execute("PRAGMA table_info(routes)")]
    if "actual_time" not in columns:
        cursor.execute("ALTER TABLE routes ADD COLUMN actual_time REAL")
    if "actual_distance" not in columns:
        cursor.execute("ALTER TABLE routes ADD COLUMN actual_distance REAL")

    conn.commit()
    conn.close()


def save_route(start_point: str, finish_point: str, route: list, distance: float, time: float, traffic: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    route_json = json.dumps(route, ensure_ascii=False)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO routes (start_point, finish_point, route, distance, time, traffic, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?) """, (start_point, finish_point, route_json, distance, time, traffic, created_at))

    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()

    print(f"Маршрут №{inserted_id} успішно збережено в БД.")
    return inserted_id


def save_actual(route_id, actual_time, actual_distance):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE routes SET actual_time = ?, actual_distance = ? WHERE id = ?",
        (actual_time, actual_distance, route_id),
    )
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed:
        print(f"Запис №{route_id} оновлено.")
    else:
        print("Такого запису немає.")
    return changed


def get_route(start_point: str, finish_point: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
                SELECT id, start_point, finish_point, route, distance, time, traffic, created_at,
                       actual_time, actual_distance
                FROM routes
                WHERE (start_point = ? AND finish_point = ?)
                   OR (start_point = ? AND finish_point = ?)
                ORDER BY id DESC
                LIMIT 1""", (start_point, finish_point, finish_point, start_point))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return row_to_dict(row)


def get_all_routes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, start_point, finish_point, route, distance, time, traffic, created_at,
               actual_time, actual_distance
        FROM routes
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [row_to_dict(row) for row in rows]


def row_to_dict(row):
    return {
        "id": row[0],
        "start_point": row[1],
        "finish_point": row[2],
        "route": json.loads(row[3]),
        "distance": row[4],
        "time": row[5],
        "traffic": row[6],
        "created_at": row[7],
        "actual_time": row[8],
        "actual_distance": row[9],
    }