from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os

# ── Postgres ────────────────────────────────────────────
DB_HOST = os.environ.get("DB_HOST", "")
db_conn = None

if DB_HOST:
    import psycopg2
    import psycopg2.extras
    db_conn = psycopg2.connect(
        host=DB_HOST,
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "books"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
    )
    # создаём таблицу если нет
    with db_conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                data JSONB NOT NULL
            )
        """)
    db_conn.commit()
    print(f"Используем Postgres: {DB_HOST}")

# ── Redis ───────────────────────────────────────────────
REDIS_HOST = os.environ.get("REDIS_HOST", "")
redis_db = None

if REDIS_HOST and not db_conn:
    import redis
    redis_db = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    print(f"Используем Redis: {REDIS_HOST}")

# ── JSON fallback ────────────────────────────────────────
DATA_FILE = os.environ.get("DATA_FILE", "/app/data/books.json")

if not db_conn and not redis_db:
    print("Используем JSON-файл")


def load_books():
    if db_conn:
        with db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT data FROM books")
            return [row["data"] for row in cur.fetchall()]
    if redis_db:
        books = redis_db.lrange("books", 0, -1)
        return [json.loads(b) for b in books]
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []


def save_book(book):
    if db_conn:
        with db_conn.cursor() as cur:
            cur.execute("INSERT INTO books (data) VALUES (%s)", [json.dumps(book)])
        db_conn.commit()
        return
    if redis_db:
        redis_db.rpush("books", json.dumps(book))
        return
    books = load_books()
    books.append(book)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(books, f)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

    def do_GET(self):
        books = load_books()
        body = json.dumps(books, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        book = json.loads(self.rfile.read(length))
        save_book(book)
        self.send_response(201)
        self.end_headers()


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", "8080"))
    print(f"BookTracker запущен на порту {PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()