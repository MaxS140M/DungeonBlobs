"""Big-number helpers. Python whole numbers (ints) never overflow but floats stop
at about 1.8e308, so exponential costs are worked out with exact integer maths,
and big values are shown short, idle-game style: 1.23K, 45.6M, 7.8B, 1T, 2.5aa..."""
from fractions import Fraction
from functools import lru_cache

SHORT_SUFFIXES = ["", "K", "M", "B", "T"]  # after T come two-letter suffixes: aa, ab ... zz


# base * growth ** level, rounded, using exact whole-number maths so huge levels can't overflow.
# Cached because the lobby recalculates every cost each frame.
@lru_cache(maxsize=4096)
def grow(base, growth, level):
    ratio = Fraction(growth).limit_denominator(1000)  # e.g. 1.6 -> 8/5
    numerator = base * ratio.numerator ** level
    denominator = ratio.denominator ** level
    return (numerator + denominator // 2) // denominator


# Multiplies a whole number by a decimal multiplier (e.g. 1.48) without converting the
# whole number to a float, so very large amounts still work. Rounds down.
def scale(amount, multiplier):
    return amount * round(multiplier * 10_000) // 10_000


# Short display of a number: 999 -> "999", 1234 -> "1.23K", 45_600_000 -> "45.6M".
# Small decimals keep their decimals (e.g. attack 17.8). Truncates rather than rounds,
# so a price never looks cheaper than it is.
def format_number(value):
    if isinstance(value, float) and value < 1000:
        return f"{value:g}"
    value = int(value)
    if value < 0:
        return "-" + format_number(-value)
    digits = str(value)
    if len(digits) <= 3:
        return digits
    group = (len(digits) - 1) // 3  # how many groups of three digits to drop
    whole = len(digits) - group * 3  # 1-3 digits before the decimal point
    shown = digits[:whole]
    if whole < 3:
        decimals = digits[whole:3].rstrip("0")
        if decimals:
            shown += "." + decimals
    return shown + suffix(group)


# The suffix for 1000 ** group: K, M, B, T, then aa, ab ... zz, then scientific notation.
def suffix(group):
    if group < len(SHORT_SUFFIXES):
        return SHORT_SUFFIXES[group]
    index = group - len(SHORT_SUFFIXES)
    if index < 26 * 26:
        return chr(ord("a") + index // 26) + chr(ord("a") + index % 26)
    return f"e{group * 3}"
