from datetime import datetime
import hmac
import base64
import hashlib
import json
import random
class Utilities:
    def isfloat(num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def celsius_to_fahrenheit(celsius, as_int=True):
        celsius = float(celsius)
        if as_int:
            return int(round((celsius * (9 / 5)) + 32))
        else:
            return round((celsius * (9 / 5)) + 32, 1)

    def fahrenheit_to_celsius(fahrenheit, as_int=True):
        fahrenheit = float(fahrenheit)
        if as_int:
            return int(round((fahrenheit - 32) * 5 / 9))
        else:
            return round((fahrenheit - 32) * 5 / 9, 1)

    def dbm_to_percent(current, perfect=-20, worst=-85):
        nominal = perfect - worst
        percent = (100 * nominal * nominal - (perfect - current) * (15 * nominal + 62 * (perfect - current))) \
                  / (nominal * nominal)  # ipw2200 quqdradic formula
                                         # https://github.com/torvalds/linux/blob/9ff9b0d392ea08090cd1780fb196f36dbb586529/drivers/net/wireless/intel/ipw2x00/ipw2200.c#L4321

        if percent > 100:
            percent = 100
        elif percent < 1:
            percent = 0

        return percent
    def hmac_sign(app_secret, credentials):
        return base64.b64encode(
            hmac.new(app_secret, msg=json.dumps(credentials).encode(), digestmod=hashlib.sha256).digest()
        ).decode()