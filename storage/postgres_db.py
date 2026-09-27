import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

databasename = os.getenv("DB_NAME")
databaseuser = os.getenv("DB_USER")
databasepassword = os.getenv("DB_PASSWORD")
databasehost = os.getenv("DB_HOST")
databaseport = os.getenv("DB_PORT")


class PostgreSQLDB:

    def __init__(self):
        self.connection = psycopg2.connect(
            database=databasename,
            user=databaseuser,
            password=databasepassword,
            host=databasehost,
            port=databaseport,
        )
        self.cursor = self.connection.cursor()

    def get_total_log_count(self):
        query = """
            SELECT COUNT(*)
            FROM valid_logs
        """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return int(row[0])

    def get_error_log_count(self):
        query = """
            SELECT COUNT(*)
            FROM valid_logs
            WHERE level = 'ERROR'
        """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return int(row[0])

    def insert_valid_logs(self, batch):
        batch_data = []

        for log in batch:
            row = (
                log.timestamp,
                log.level,
                log.service,
                log.user_id,
                log.action,
                log.status,
                log.ip,
                log.route,
                log.method,
                log.duration_ms,
                log.request_id,
                log.deployment,
            )
            batch_data.append(row)

        query = """
            INSERT INTO valid_logs (
                timestamp,
                level,
                service,
                user_id,
                action,
                status,
                ip,
                route,
                method,
                duration_ms,
                request_id,
                deployment
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        self.cursor.executemany(query, batch_data)
        self.connection.commit()

    def get_failed_login_counts_per_user(self):
        query = """
            SELECT
                user_id,
                COUNT(*) AS failure_count
            FROM valid_logs
            WHERE action = 'login'
              AND status IN (401, 500, 503)
            GROUP BY user_id
            ORDER BY failure_count DESC
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def insert_failed_logs(self, batch):
        data = []

        for log in batch:
            row = (
                log.raw_log,
                str(log.error_details),
            )
            data.append(row)

        query = """
            INSERT INTO failed_logs (
                raw_log,
                error_details
            )
            VALUES (%s, %s)
        """

        self.cursor.executemany(query, data)
        self.connection.commit()

    def fetch_logs(self, startTime, endTime, level):
        query = """
            SELECT *
            FROM valid_logs
            WHERE timestamp >= %s
              AND timestamp <= %s
              AND level = %s
        """

        self.cursor.execute(
            query,
            (startTime, endTime, level),
        )

        return self.cursor.fetchall()

    def get_counts_grouped_by_user(
        self,
        action,
        hours,
        service,
        status,
        last_user_count,
        last_user_id,
        limit,
    ):
        query = """
            SELECT
                user_id,
                COUNT(*) AS user_count
            FROM valid_logs
            WHERE action = %s
              AND timestamp >= NOW() - (%s)::INTERVAL
        """

        params = [
            action,
            hours,
        ]

        if service is not None:
            query += " AND service = %s"
            params.append(service)

        if status is not None:
            query += " AND status = %s"
            params.append(status)

        query += """
            GROUP BY user_id
        """

        if (
            last_user_count is not None
            and last_user_id is not None
        ):
            query += """
                HAVING
                    COUNT(*) < %s
                    OR (
                        COUNT(*) = %s
                        AND user_id > %s
                    )
            """

            params.extend([
                last_user_count,
                last_user_count,
                last_user_id,
            ])

        query += """
            ORDER BY user_count DESC, user_id ASC
            LIMIT %s
        """

        params.append(limit)

        self.cursor.execute(
            query,
            tuple(params),
        )

        return self.cursor.fetchall()

    # ---------------------------------------------------------
    # SafeStep observability
    # ---------------------------------------------------------

    def get_latency_percentiles(
        self,
        service,
        action,
        hours,
    ):
        query = """
            SELECT
                COUNT(*) AS samples,
                percentile_cont(0.50)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p50_ms,
                percentile_cont(0.95)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p95_ms,
                percentile_cont(0.99)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p99_ms
            FROM valid_logs
            WHERE service = %s
              AND action = %s
              AND duration_ms IS NOT NULL
              AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
        """

        self.cursor.execute(
            query,
            (service, action, hours),
        )

        row = self.cursor.fetchone()

        if row is None or row[0] == 0:
            return None

        return {
            "samples": int(row[0]),
            "p50_ms": round(float(row[1]), 2),
            "p95_ms": round(float(row[2]), 2),
            "p99_ms": round(float(row[3]), 2),
        }

    def get_endpoint_latency(
        self,
        service,
        hours,
    ):
        query = """
            SELECT
                route,
                COUNT(*) AS requests,
                percentile_cont(0.50)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p50_ms,
                percentile_cont(0.95)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p95_ms,
                percentile_cont(0.99)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p99_ms
            FROM valid_logs
            WHERE service = %s
              AND action = 'request_completed'
              AND method <> 'OPTIONS'
              AND duration_ms IS NOT NULL
              AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
            GROUP BY route
            ORDER BY p95_ms DESC
        """

        self.cursor.execute(
            query,
            (service, hours),
        )

        rows = self.cursor.fetchall()

        return [
            {
                "route": row[0],
                "requests": int(row[1]),
                "p50_ms": round(float(row[2]), 2),
                "p95_ms": round(float(row[3]), 2),
                "p99_ms": round(float(row[4]), 2),
            }
            for row in rows
        ]

    def get_request_error_rate(
        self,
        service: str,
        hours: int,
    ):
        query = """
            SELECT
                COUNT(*) AS total_requests,
                COUNT(*) FILTER (
                    WHERE status >= 500
                ) AS server_errors,
                COUNT(*) FILTER (
                    WHERE status >= 400
                    AND status < 500
                ) AS client_errors
            FROM valid_logs
            WHERE service = %s
            AND action IN ('request_completed', 'request_failed')
            AND (method IS NULL OR method <> 'OPTIONS')
            AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
        """

        self.cursor.execute(
            query,
            (service, hours),
        )

        row = self.cursor.fetchone()

        total_requests = int(row[0] or 0)
        server_errors = int(row[1] or 0)
        client_errors = int(row[2] or 0)

        server_error_rate = (
            (server_errors / total_requests) * 100
            if total_requests
            else 0.0
        )

        client_error_rate = (
            (client_errors / total_requests) * 100
            if total_requests
            else 0.0
        )

        return {
            "total_requests": total_requests,
            "server_errors": server_errors,
            "client_errors": client_errors,
            "server_error_rate_percent": round(
                server_error_rate,
                2,
            ),
            "client_error_rate_percent": round(
                client_error_rate,
                2,
            ),
        }

    
    def get_analysis_success_rate(
        self,
        service,
        hours,
    ):
        query = """
            SELECT
                COUNT(*) FILTER (
                    WHERE action = 'analysis_completed'
                ) AS successful,
                COUNT(*) FILTER (
                    WHERE action = 'analysis_failed'
                ) AS failed
            FROM valid_logs
            WHERE service = %s
              AND action IN (
                  'analysis_completed',
                  'analysis_failed'
              )
              AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
        """

        self.cursor.execute(
            query,
            (service, hours),
        )

        row = self.cursor.fetchone()

        successful = int(row[0])
        failed = int(row[1])
        total = successful + failed

        if total == 0:
            return None

        return {
            "successful": successful,
            "failed": failed,
            "total": total,
            "success_rate_percent": round(
                (successful / total) * 100,
                2,
            ),
            "failure_rate_percent": round(
                (failed / total) * 100,
                2,
            ),
        }

    def get_ai_provider_stats(
        self,
        service,
        hours,
    ):
        query = """
            SELECT
                action,
                COUNT(*) AS samples,
                AVG(duration_ms) AS average_ms,
                percentile_cont(0.50)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p50_ms,
                percentile_cont(0.95)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p95_ms,
                percentile_cont(0.99)
                    WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p99_ms
            FROM valid_logs
            WHERE service = %s
              AND action IN (
                  'ai_openai_completed',
                  'ai_openai_failed',
                  'ai_nvidia_completed',
                  'ai_nvidia_failed'
              )
              AND duration_ms IS NOT NULL
              AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
            GROUP BY action
            ORDER BY action
        """

        self.cursor.execute(
            query,
            (service, hours),
        )

        rows = self.cursor.fetchall()

        return [
            {
                "action": row[0],
                "samples": int(row[1]),
                "average_ms": round(float(row[2]), 2),
                "p50_ms": round(float(row[3]), 2),
                "p95_ms": round(float(row[4]), 2),
                "p99_ms": round(float(row[5]), 2),
            }
            for row in rows
        ]

    def get_ai_fallback_rate(
        self,
        service,
        hours,
    ):
        query = """
            SELECT
                COUNT(*) FILTER (
                    WHERE action = 'ai_analysis_completed'
                ) AS analyses,
                COUNT(*) FILTER (
                    WHERE action = 'ai_nvidia_completed'
                ) AS fallbacks
            FROM valid_logs
            WHERE service = %s
              AND timestamp >= NOW()
                    - (%s * INTERVAL '1 hour')
        """

        self.cursor.execute(
            query,
            (service, hours),
        )

        row = self.cursor.fetchone()

        analyses = int(row[0])
        fallbacks = int(row[1])

        if analyses == 0:
            return {
                "analyses": 0,
                "fallbacks": fallbacks,
                "fallback_rate_percent": None,
            }

        return {
            "analyses": analyses,
            "fallbacks": fallbacks,
            "fallback_rate_percent": round(
                (fallbacks / analyses) * 100,
                2,
            ),
        }