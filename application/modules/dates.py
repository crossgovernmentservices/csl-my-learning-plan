import re
from dateutil.parser import *

def convert_duration(duration):
    match = re.search('(-)?P(?:([\.,\d]+)Y)?(?:([\.,\d]+)M)?(?:([\.,\d]+)W)?(?:([\.,\d]+)D)?(?:T)?(?:([\.,\d]+)H)?(?:([\.,\d]+)M)?(?:([\.,\d]+)S)?', duration)
    return (match.group(2) + ' Years' if match.group(2) is not None else '') + \
        (__formatdurationunit(match.group(3), 'Month') if match.group(3) is not None else '') + \
        (__formatdurationunit(match.group(4), 'Week') if match.group(4) is not None else '') + \
        (__formatdurationunit(match.group(5), 'Day') if match.group(5) is not None else '') + \
        (__formatdurationunit(match.group(6), 'Hour') if match.group(6) is not None else '') + \
        (__formatdurationunit(match.group(7), 'Minute') if match.group(7) is not None else '') + \
        (__formatdurationunit(match.group(8), 'Second') if match.group(8) is not None else '')

def __formatdurationunit(item, unitlabel):
    item = int(item)
    if item == 0:
        return ''
    if item > 1:
        unitlabel = unitlabel + 's'
    return str(item) + ' ' + unitlabel + ' '



def format_date(date, format=None):
    date = parse(date)
    native = date.replace(tzinfo=None)
    if format is None:
        format = '%d %b %Y %H:%M'

    return native.strftime(format)
