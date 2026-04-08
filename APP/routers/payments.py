# import ipaddress
import os
from pathlib import Path
import hashlib
import json
# from datetime import datetime, timezone
# from typing import Any, Dict
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from APP.db_depends import get_async_db
from APP.models.accounts import Account as AccountModel
from APP.models.users import User as UserModel
from APP.models.transactions import Transaction as TransactionModel

from APP.schemas.payments import Payment

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

SECRET_KEY = os.getenv("PAYM_SECRET_KEY")

# Список разрешенных сетей/адресов для проверки источника запроса
# SYSTEMS_IP_LIST: tuple[str, ...] = (
# )


# def is_ip_allowed(ip: str | None) -> bool:
#     if ip is None:
#         return False
#     try:
#         address = ipaddress.ip_address(ip)
#     except ValueError:
#         return False
#
#     for mask in SYSTEM_IP_LIST:
#         if "/" in mask:
#             if address in ipaddress.ip_network(mask, strict=False):
#                 return True
#         else:
#             if address == ipaddress.ip_address(mask):
#                 return True
#     return False


# def _extract_client_ip(request: Request) -> str | None:
#     forwarded_for = request.headers.get("x-forwarded-for")
#     if forwarded_for:
#         return forwarded_for.split(",")[0].strip()
#     return request.client.host if request.client else None

def signature_check(data: dict) -> bool:

    json_signature = data.pop('signature')

    sorted_keys = sorted(data.keys())

    concatenated = ""
    for key in sorted_keys:
        concatenated += str(data[key])

    concatenated += SECRET_KEY

    signature = hashlib.sha256(concatenated.encode('utf-8')).hexdigest()

    if signature == json_signature:
        return True

    return False


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def payment_webhook(
        request: Request,
        db: AsyncSession = Depends(get_async_db),
):
    # Проверка на ip отправляющий запрос, может быть полезно
    # client_ip = _extract_client_ip(request)
    # if not is_ip_allowed(client_ip):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP not allowed")

    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {exc}")

    if signature_check(payload):
        try:
            payment_data = Payment(**payload)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

        user_q = select(UserModel).where(UserModel.id == payload.get('user_id'))

        db_user = (await db.scalars(user_q)).first()

        if not db_user:
            raise HTTPException(status_code=400, detail='User with this id not found')

        account_q = select(AccountModel).where(AccountModel.user_id == payload.get('user_id'),
                                               AccountModel.id == payload.get('account_id'))

        db_acc = (await db.scalars(account_q)).first()

        if not db_acc:
            db_acc = AccountModel(user_id=payload.get('user_id'), amount=payload.get('amount'))
            db.add(db_acc)
        else:
            db_acc.amount += payload.get('amount')

        await db.flush()

        new_transact = TransactionModel(user_id=payload.get('user_id'), amount=payload.get('amount'),
                                        account_id=db_acc.id, transaction_id=payload.get('transaction_id'))
        db.add(new_transact)
        await db.commit()

    else:
        raise HTTPException(status_code=403, detail='Invalid signature')

    return {"status": "ok"}
