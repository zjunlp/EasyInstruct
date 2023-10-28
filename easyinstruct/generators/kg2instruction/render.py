from collections import namedtuple
import re


# See https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Dates_and_numbers
Format = namedtuple("Format", ["format_string", "include_era", "remove_leading_zeros"])

YEAR_FORMATS_en = [Format("%Y", True, True)]


YEAR_FORMATS_zh = [Format("%Y年", True, True)]


MONTH_FORMATS_en = [
    Format("%B %Y", True, True),
    Format("%b %Y", True, True),
    *YEAR_FORMATS_en,
]

MONTH_FORMATS_zh = [
    Format("%Y年%m月", True, True),
    Format("%Y年%B", True, True),
    *YEAR_FORMATS_zh,
]

DAY_FORMATS_en = [
    Format("%d %B %Y", True, True),
    Format("%d %b %Y", True, True),
    Format("%B %d, %Y", True, True),
    Format("%b %d, %Y", True, True),
    Format("%d %B", False, True),
    Format("%d %b", False, True),
    Format("%B %d", False, True),
    Format("%b %d", False, True),
    Format("%Y-%m-%d", False, False),
    *MONTH_FORMATS_en,
]


DAY_FORMATS_zh = [
    Format("%Y年%m月%d日", True, True),
    Format("%Y年%B%d日", True, True),
    Format("%m月%d日", False, True),
    Format("%B%d日", False, True),
    Format("%Y-%m-%d", False, False),
    *MONTH_FORMATS_zh,
]


RE_LEADING_ZEROS = re.compile(r"((?<=\s)0+|^0+)")
RE_ISO_8601 = re.compile(
    r"(?P<year>[+-][0-9]+)-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})(?=T)"
)


class Date_en(object):
    LONG_MONTHS = [
        None,
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    SHORT_MONTHS = [
        None,
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    def __init__(self, year, month=None, day=None):
        self._year = year
        self._month = month
        self._day = day

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    def strftime(self, format_string):
        out = format_string
        if self._day:
            out = out.replace("%d", "%02d" % self._day)
        if self._month:
            out = out.replace("%b", Date_en.SHORT_MONTHS[self._month])
            out = out.replace("%m", "%02d" % self._month)
            out = out.replace("%B", Date_en.LONG_MONTHS[self._month])
        out = out.replace("%Y", "%d" % abs(self._year))
        return out


class Date_zh(object):
    LONG_MONTHS = [
        None,
        "一月",
        "二月",
        "三月",
        "四月",
        "五月",
        "六月",
        "七月",
        "八月",
        "九月",
        "十月",
        "十一月",
        "十二月",
    ]

    SHORT_MONTHS = [
        None,
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月",
    ]

    def __init__(self, year, month=None, day=None):
        self._year = year
        self._month = month
        self._day = day

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    def strftime(self, format_string):
        out = format_string
        if self._day:
            out = out.replace("%d", "%02d" % self._day)
        if self._month:
            out = out.replace("%b", Date_zh.SHORT_MONTHS[self._month])
            out = out.replace("%m", "%d" % self._month)
            out = out.replace("%B", Date_zh.LONG_MONTHS[self._month])
        out = out.replace("%Y", "%d" % abs(self._year))
        return out


def parse_iso8601_en(iso_string: str):
    match = RE_ISO_8601.match(iso_string)
    if match:
        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))
        return Date_en(year, month, day)


def parse_iso8601_zh(iso_string: str):
    match = RE_ISO_8601.match(iso_string)
    if match:
        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))
        return Date_zh(year, month, day)


def custom_strftime_en(formats, date):
    out = []
    for format in formats:
        date_string = date.strftime(format.format_string)
        if format.remove_leading_zeros:
            date_string = RE_LEADING_ZEROS.sub("", date_string)
        out.append(date_string)
        if format.include_era:
            is_bc = date.year < 0
            era_strings = ["BC", "BCE"] if is_bc else ["AD", "CE"]
            for era_string in era_strings:
                out.append(" ".join((era_string, date_string)))
                out.append(" ".join((date_string, era_string)))
    return out


def custom_strftime_zh(formats, date):
    out = []
    for format in formats:
        date_string = date.strftime(format.format_string)
        if format.remove_leading_zeros:
            date_string = RE_LEADING_ZEROS.sub("", date_string)
        out.append(date_string)
        if format.include_era:
            is_bc = date.year < 0
            era_strings = ["公元前"] if is_bc else ["公元"]
            for era_string in era_strings:
                out.append("".join((era_string, date_string)))
    return out


def render_time_en(posix_string, precision):
    date = parse_iso8601_en(posix_string)
    if precision == 11:  # Day level precision
        return custom_strftime_en(DAY_FORMATS_en, date)
    if precision == 10:  # Month level prevision
        return custom_strftime_en(MONTH_FORMATS_en, date)
    elif precision < 10:  # Year level precision or less
        return []


def render_time_zh(posix_string, precision):
    date = parse_iso8601_zh(posix_string)
    if precision == 11:  # Day level precision
        return custom_strftime_zh(DAY_FORMATS_zh, date)
    if precision == 10:  # Month level prevision
        return custom_strftime_zh(MONTH_FORMATS_zh, date)
    elif precision < 10:  # Year level precision or less
        return custom_strftime_zh(YEAR_FORMATS_zh, date)


def get_unit_label_from_uri(qid, alias_db):
    try:
        labels = alias_db[qid]
    except KeyError:
        return []
    return labels


def format_number_with_commas(number):
    return "{:,}".format(number)


def format_amount(amount):
    if amount.is_integer():
        formatted_quantity = f"{format_number_with_commas(int(amount))}"
    else:
        formatted_quantity = f"{amount:.2f}"
    return formatted_quantity


def render_quantity(qid, amount, alias_db):
    amount = float(amount)
    if qid == "None":
        return []
    else:
        units = get_unit_label_from_uri(qid, alias_db)
        out = []
        for unit in units:
            formatted_quantity = f"{format_amount(amount)}{unit}"
            out.append(formatted_quantity)
        return out


if __name__ == "__main__":
    language = "en"
    if language == "zh":
        # aliases = render_quantity('Q712226', '+103800')
        # print(aliases)
        aliases = render_time_zh("+2001-12-31T00:00:00Z", 11)
        print(aliases)
    else:
        # aliases = render_quantity('Q712226', '+103800')
        # print(aliases)
        aliases = render_time_en("+2001-12-31T00:00:00Z", 11)
        print(aliases)
