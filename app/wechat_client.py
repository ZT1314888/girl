from __future__ import annotations

from dataclasses import dataclass

import requests


class WechatApiError(RuntimeError):
    """Raised when WeChat API returns an error."""


@dataclass(frozen=True)
class SendResult:
    ok: bool
    errcode: int
    errmsg: str
    msgid: int | None


class WechatClient:
    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds

    def get_access_token(self, app_id: str, app_secret: str) -> str:
        url = "https://hk.api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret,
        }
        response = requests.get(url, params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()

        if "access_token" not in payload:
            errcode = payload.get("errcode", -1)
            errmsg = payload.get("errmsg", "unknown error")
            raise WechatApiError(f"Failed to get access_token: {errcode} {errmsg}")
        return payload["access_token"]

    def send_template_message(self, access_token: str, payload: dict) -> SendResult:
        url = "https://hk.api.weixin.qq.com/cgi-bin/message/template/send"
        response = requests.post(
            url,
            params={"access_token": access_token},
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()

        errcode = int(body.get("errcode", -1))
        errmsg = str(body.get("errmsg", "unknown error"))
        msgid = body.get("msgid")
        ok = errcode == 0
        return SendResult(ok=ok, errcode=errcode, errmsg=errmsg, msgid=msgid)
