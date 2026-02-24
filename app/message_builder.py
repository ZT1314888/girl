from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .config import Settings


WEEKDAY_MAP = {
    0: "星期一",
    1: "星期二",
    2: "星期三",
    3: "星期四",
    4: "星期五",
    5: "星期六",
    6: "星期日",
}


@dataclass(frozen=True)
class TemplatePayload:
    touser: str
    template_id: str
    data: dict

    def to_dict(self) -> dict:
        return {
            "touser": self.touser,
            "template_id": self.template_id,
            "data": self.data,
        }


def _format_anniversary(settings: Settings, now: datetime) -> str:
    if not settings.anniversary_date:
        return "未设置纪念日"

    start = datetime.strptime(settings.anniversary_date, "%Y-%m-%d").date()
    today = now.date()
    delta_days = (today - start).days
    if delta_days >= 0:
        return f"{settings.anniversary_name}已过 {delta_days} 天"
    return f"距离{settings.anniversary_name}还有 {abs(delta_days)} 天"


def build_template_payload(
    settings: Settings,
    now: datetime,
    weather_text: str | None = None,
) -> TemplatePayload:
    weather_value = weather_text or "天气信息暂不可用"
    anniversary_value = _format_anniversary(settings, now)

    data = {
        settings.field_first: {"value": settings.fixed_title, "color": "#173177"},
        settings.field_date: {"value": now.strftime("%Y-%m-%d"), "color": "#173177"},
        settings.field_weekday: {"value": WEEKDAY_MAP[now.weekday()], "color": "#173177"},
        settings.field_weather: {"value": weather_value, "color": "#173177"},
        settings.field_anniversary: {"value": anniversary_value, "color": "#173177"},
        settings.field_remark: {"value": settings.fixed_remark, "color": "#173177"},
    }

    return TemplatePayload(
        touser=settings.wechat_to_user_openid,
        template_id=settings.wechat_template_id,
        data=data,
    )
