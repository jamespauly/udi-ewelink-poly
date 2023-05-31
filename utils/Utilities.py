from datetime import datetime


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
