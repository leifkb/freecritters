from freecritters.web.util import http_date as rss_time

def integer(n):
    n = unicode(n)
    groups = []
    if len(n) % 3 != 0:
        groups.append(n[:len(n) % 3])
    for i in xrange(len(n) % 3, len(n), 3):
        groups.append(n[i:i+3])
    return u'\N{NO-BREAK SPACE}'.join(groups)

def datetime(t, sep=u'\N{NO-BREAK SPACE}'):
    t = t.replace(microsecond=0)
    return t.isoformat('T').decode('ascii').replace('T', sep)