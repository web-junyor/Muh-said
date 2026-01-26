import hashlib
from fastapi import FastAPI, Request, HTTPException
from config import CLICK_SECRET_KEY
from backend.database import register_sale
from bot.notifier import notify_admin

app = FastAPI()

def verify_click_signature(data: dict) -> bool:
    """
    Click sign_string tekshiruv
    """
    sign_string = (
        str(data["click_trans_id"]) +
        str(data["service_id"]) +
        CLICK_SECRET_KEY +
        str(data["merchant_trans_id"]) +
        str(data["amount"]) +
        str(data["action"]) +
        str(data["sign_time"])
    )

    calculated_sign = hashlib.md5(sign_string.encode()).hexdigest()
    return calculated_sign == data["sign_string"]


@app.post("/click/webhook")
async def click_handler(request: Request):
    payload = await request.json()

    if not verify_click_signature(payload):
        raise HTTPException(status_code=403, detail="Invalid Click signature")

    product = payload["merchant_trans_id"]   # masalan: Mocha
    amount = int(payload["amount"])
    quantity = int(payload.get("quantity", 1))

    register_sale(product, quantity, amount)
    await notify_admin(product, quantity, amount, payload)

    return {"error": 0, "error_note": "Success"}
