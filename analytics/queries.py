import datetime

from fastapi import HTTPException


class AnalyticsService:

    def __init__(self, db):
        self.db = db

    def get_last_hour_errors(self):
        currentTime = datetime.datetime.now()

        endtime = currentTime.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        starttime = (
            currentTime - datetime.timedelta(hours=1)
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        raw_logs = self.db.fetch_logs(
            starttime,
            endtime,
            "ERROR",
        )

        return raw_logs

    def get_login_counts_per_user(
        self,
        limit,
        hours,
        service,
        status,
        last_user_count,
        last_user_id,
    ):
        char_hours = str(hours) + " hours"

        if (last_user_count is None) != (
            last_user_id is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid cursor",
            )

        return self.db.get_counts_grouped_by_user(
            "login",
            char_hours,
            service,
            status,
            last_user_count,
            last_user_id,
            limit,
        )

    def get_error_rate(self):
        total_logs = self.db.get_total_log_count()

        if total_logs == 0:
            return None

        error_logs = self.db.get_error_log_count()

        return error_logs / total_logs

    def get_failed_login_counts_per_user(self):
        return self.db.get_failed_login_counts_per_user()

    # ---------------------------------------------------------
    # SafeStep observability
    # ---------------------------------------------------------

    def get_safestep_request_latency(
        self,
        hours,
    ):
        return self.db.get_latency_percentiles(
            service="safestep-api",
            action="request_completed",
            hours=hours,
        )

    def get_safestep_analysis_latency(
        self,
        hours,
    ):
        return self.db.get_latency_percentiles(
            service="safestep-api",
            action="analysis_completed",
            hours=hours,
        )

    def get_safestep_ai_latency(
        self,
        hours,
    ):
        return self.db.get_latency_percentiles(
            service="safestep-api",
            action="ai_analysis_completed",
            hours=hours,
        )

    def get_safestep_endpoint_latency(
        self,
        hours,
    ):
        return self.db.get_endpoint_latency(
            service="safestep-api",
            hours=hours,
        )

    def get_safestep_error_rate(
        self,
        hours,
    ):
        return self.db.get_request_error_rate(
            service="safestep-api",
            hours=hours,
        )

    def get_safestep_analysis_success_rate(
        self,
        hours,
    ):
        return self.db.get_analysis_success_rate(
            service="safestep-api",
            hours=hours,
        )

    def get_safestep_ai_provider_stats(
        self,
        hours,
    ):
        return self.db.get_ai_provider_stats(
            service="safestep-api",
            hours=hours,
        )

    def get_safestep_ai_fallback_rate(
        self,
        hours,
    ):
        return self.db.get_ai_fallback_rate(
            service="safestep-api",
            hours=hours,
        )