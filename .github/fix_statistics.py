from pathlib import Path

backend = Path("backend/app.py")
stats = Path("website/statistics.html")
b = backend.read_text(encoding="utf-8")
s = stats.read_text(encoding="utf-8")

route = b.index('@app.route("/statistics")')
start = b.index(
    '    # =====================================================\n'
    '    # BOT SNAPSHOT\n'
    '    # =====================================================\n\n'
    '    bot_snapshot = {}',
    route,
)
end = b.index(
    '    # =====================================================\n'
    '    # HEARTBEAT\n'
    '    # =====================================================',
    start,
)

replacement = '''    # =====================================================
    # BOT SNAPSHOT — POSTGRESQL
    # =====================================================

    bot_snapshot = {}

    try:
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        servers, users, channels, latency, commands,
                        tickets, moderation_actions, announcements,
                        verifications, bot_status, uptime, version,
                        last_seen, admin_servers, updated_at
                    FROM bot_statistics
                    WHERE id = 1
                """)
                result = cursor.fetchone()
                if result:
                    bot_snapshot = {
                        "servers": result[0], "users": result[1],
                        "channels": result[2], "latency": result[3],
                        "commands": result[4], "tickets": result[5],
                        "moderation_actions": result[6],
                        "announcements": result[7],
                        "verifications": result[8],
                        "bot_status": result[9], "uptime": result[10],
                        "version": result[11], "last_seen": result[12],
                        "admin_servers": result[13] or [],
                        "updated_at": result[14],
                    }
                    for key in (
                        "servers", "users", "channels", "latency",
                        "commands", "tickets", "moderation_actions",
                        "announcements", "verifications", "bot_status",
                        "uptime", "updated_at"
                    ):
                        if key in bot_snapshot:
                            statistics_data[key] = bot_snapshot[key]
                    statistics_data["version"] = os.getenv(
                        "MISUKI_VERSION", "1.0.0"
                    )
    except Exception as error:
        print(f"⚠️ Could not load live bot statistics: {error}")

'''
b = b[:start] + replacement + b[end:]

api_route = b.index('@app.route("/api/statistics")')
response_marker = (
    '    # =====================================================\n'
    '    # RESPONSE\n'
    '    # =====================================================\n'
)
response_pos = b.index(response_marker, api_route)
activity = '''    # =====================================================
    # ACTIVITY COUNTERS — POSTGRESQL
    # =====================================================

    try:
        with database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tickets, moderation_actions, announcements
                    FROM bot_statistics
                    WHERE id = 1
                """)
                row = cursor.fetchone()
                if row:
                    statistics_data["tickets"] = int(row[0] or 0)
                    statistics_data["moderation_actions"] = int(row[1] or 0)
                    statistics_data["announcements"] = int(row[2] or 0)
    except Exception as error:
        print(f"⚠️ Could not load activity counters: {error}")

'''
api_section = b[api_route:response_pos]
if "# ACTIVITY COUNTERS — POSTGRESQL" not in api_section:
    b = b[:response_pos] + activity + b[response_pos:]

api_start = b.index('@app.route("/api/statistics")')
init_start = b.index('    statistics_data = {', api_start)
init_end = b.index('    }', init_start) + len('    }')
init = b[init_start:init_end]
if '"moderation_actions": 0' not in init:
    init = init.replace(
        '        "verifications": 0,',
        '        "verifications": 0,\n\n'
        '        "moderation_actions": 0,\n\n'
        '        "announcements": 0,',
        1,
    )
    b = b[:init_start] + init + b[init_end:]

old = '''        return new Date(\n            numericValue * 1000\n        ).toLocaleString();'''
new = '''        const formatted = new Intl.DateTimeFormat(
            "pt-PT",
            {
                timeZone: "Europe/Lisbon",
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                hour12: false
            }
        ).format(new Date(numericValue * 1000));

        return formatted.replace(", ", " ");'''
if old not in s:
    raise SystemExit("Expected statistics date formatter was not found")
s = s.replace(old, new, 1)

backend.write_text(b, encoding="utf-8")
stats.write_text(s, encoding="utf-8")
