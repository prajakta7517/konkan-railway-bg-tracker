from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # MongoDB
    mongodb_uri: str
    db_name: str = "konkan_railway_bg"

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    reset_token_expire_minutes: int = 30
    cookie_secure: bool = True
    cookie_samesite: str = "lax"  # use "none" (with cookie_secure=true) if frontend/backend are on different domains

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Email (Gmail SMTP, or any SMTP provider)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = "noreply@example.com"
    mail_from_name: str = "Konkan Railway Corporation Limited"
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_starttls: bool = True
    mail_ssl_tls: bool = False

    # URLs
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"

    # Helpdesk
    helpdesk_email: str = "helpdesk@konkanrailway.gov.in"
    helpdesk_phone: str = "+91-0000000000"

    # Cron
    cron_secret: str = ""

    # Bootstrap admin (only used by scripts/create_admin.py)
    first_admin_email: str = ""
    first_admin_password: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
