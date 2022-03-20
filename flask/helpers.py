from functools import wraps
from typing import List
import logging

import os
import re
import hmac
import base64
import json
import hashlib
from flask import request, abort
import pandas as pd
import re
from shopify_client import ShopifyStoreClient

from dotenv import load_dotenv

load_dotenv()
SHOPIFY_SECRET = os.environ.get('SHOPIFY_SECRET')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
INSTALL_REDIRECT_URL = os.environ.get('INSTALL_REDIRECT_URL')
DASHBOARD_REDIRECT_URL = os.environ.get('DASHBOARD_REDIRECT_URL')
APP_NAME = os.environ.get('APP_NAME')

def generate_install_redirect_url(shop: str, scopes: List, nonce: str, access_mode: List):
    scopes_string = ','.join(scopes)
    access_mode_string = ','.join(access_mode)
    redirect_url = f"https://{shop}/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope={scopes_string}&redirect_uri={INSTALL_REDIRECT_URL}&state={nonce}&grant_options[]={access_mode_string}"
    return redirect_url

def generate_dash_redirect_url(shop: str, nonce: str):
    redirect_url = f"{DASHBOARD_REDIRECT_URL}/?shop={shop}&state={nonce}"
    return redirect_url

def generate_post_install_redirect_url(shop: str):
    redirect_url = f"https://{shop}/admin/apps/{APP_NAME}"
    return redirect_url


def verify_web_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs) -> bool:
        get_args = request.args
        hmac = get_args.get('hmac')
        sorted(get_args)
        data = '&'.join([f"{key}={value}" for key, value in get_args.items() if key != 'hmac']).encode('utf-8')
        if not verify_hmac(data, hmac):
            logging.error(f"HMAC could not be verified: \n\thmac {hmac}\n\tdata {data}")
            abort(400)

        shop = get_args.get('shop')
        if shop and not is_valid_shop(shop):
            logging.error(f"Shop name received is invalid: \n\tshop {shop}")
            abort(401)
        return f(*args, **kwargs)
    return wrapper


def verify_webhook_call(f):
    @wraps(f)
    def wrapper(*args, **kwargs) -> bool:
        encoded_hmac = request.headers.get('X-Shopify-Hmac-Sha256')
        hmac = base64.b64decode(encoded_hmac).hex()

        data = request.get_data()
        if not verify_hmac(data, hmac):
            logging.error(f"HMAC could not be verified: \n\thmac {hmac}\n\tdata {data}")
            abort(401)
        return f(*args, **kwargs)
    return wrapper


def verify_hmac(data: bytes, orig_hmac: str):
    new_hmac = hmac.new(
        SHOPIFY_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    )
    return new_hmac.hexdigest() == orig_hmac


def is_valid_shop(shop: str) -> bool:
    # Shopify docs give regex with protocol required, but shop never includes protocol
    shopname_regex = r'[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com[\/]?'
    return re.match(shopname_regex, shop)


def get_all_orders(store_client: ShopifyStoreClient):
    # motivated by here: https://towardsdatascience.com/how-to-get-all-orders-from-shopify-69db163c7a2d
    last=0
    full_orders_df=pd.DataFrame()
    while True:
        response = store_client.get_orders(last)
        tmp_df=pd.DataFrame(response['orders'])
        full_orders_df=pd.concat([full_orders_df,tmp_df])
        last=tmp_df['id'].iloc[-1]
        if len(tmp_df)<250:
            break
    for col in full_orders_df.columns:
        if isinstance(full_orders_df[col].iloc[0], dict):
            full_orders_df[col] = full_orders_df[col].apply(json.dumps) # grabbed from here: https://stackoverflow.com/questions/56808425/sqlalchemy-psycopg2-programmingerror-cant-adapt-type-dict
    return full_orders_df