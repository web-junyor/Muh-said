import requests


class ApiError(Exception):
    """Sayt API xatosi: status_code va foydalanuvchiga ko'rsatiladigan xabar."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _error_message_from_response(r: requests.Response) -> str:
    """Javobdan xato matnini oladi (DRF validation yoki detail)."""
    try:
        body = r.json()
        if isinstance(body, dict):
            if "detail" in body:
                return str(body["detail"])
            for key in ("title", "body", "image", "owner_telegram_id"):
                if key in body and isinstance(body[key], list):
                    return body[key][0] if body[key] else ""
    except Exception:
        pass
    return r.text[:200] if r.text else ""


class DjangoApi:
    def __init__(self, base_url: str, bot_key: str):
        self.base_url = base_url.rstrip("/")
        self.bot_key = bot_key

    def create_post(
        self,
        title: str,
        body: str,
        owner_telegram_id: int,
        image_path: str | None = None,
        post_type: str = "blog",
    ):
        url = f"{self.base_url}/api/posts/"
        headers = {"X-BOT-KEY": self.bot_key}
        data = {
            "title": title,
            "body": body,
            "owner_telegram_id": owner_telegram_id,
            "post_type": post_type,
        }

        try:
            if image_path:
                with open(image_path, "rb") as f:
                    files = {"image": ("image.jpg", f, "image/jpeg")}
                    r = requests.post(url, data=data, files=files, headers=headers, timeout=25)
            else:
                r = requests.post(url, data=data, headers=headers, timeout=25)
        except requests.RequestException as e:
            raise ApiError(0, "connection") from e

        if r.status_code >= 400:
            msg = _error_message_from_response(r) or f"HTTP {r.status_code}"
            raise ApiError(r.status_code, msg)
        return r.json()

    def list_posts(self, owner_telegram_id: int, last_hours: int | None = None):
        url = f"{self.base_url}/api/posts/"
        headers = {"X-BOT-KEY": self.bot_key}
        params = {"owner_telegram_id": owner_telegram_id}
        if last_hours is not None:
            params["last_hours"] = last_hours
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def delete_post(self, post_id: int, access_token: str):
        url = f"{self.base_url}/api/posts/{post_id}/"
        headers = {"X-BOT-KEY": self.bot_key}
        try:
            r = requests.delete(
                url,
                params={"access_token": access_token},
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as e:
            raise ApiError(0, "connection") from e
        if r.status_code >= 400:
            msg = _error_message_from_response(r) or f"HTTP {r.status_code}"
            raise ApiError(r.status_code, msg)
