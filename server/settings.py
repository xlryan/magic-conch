"""
应用配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置"""

    # 安全配置
    SECRET_KEY: str = "please-change-me-to-a-random-string"
    ADMIN_TOKEN: str = "your-admin-token-here"

    # CORS 配置
    ALLOWED_ORIGINS: str = "*"

    # 数据库配置
    DB_PATH: str = "/app/storage/app.db"

    # 可选：hCaptcha 配置
    HCAPTCHA_SECRET: str = ""
    HCAPTCHA_SITEKEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins(self) -> list:
        """解析 CORS 允许的源"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def hcaptcha_enabled(self) -> bool:
        """检查 hCaptcha 是否启用"""
        return bool(self.HCAPTCHA_SECRET and self.HCAPTCHA_SITEKEY)


# 全局配置实例
settings = Settings()
