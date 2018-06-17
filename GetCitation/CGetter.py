import re, time, datetime
import habanero
import json
from common import *


class Validator:
    @staticmethod
    def email(s):
        return re.match(r'[^@]+@[^\.]+\.\w+', s) is not None


def mapget(el, *argv):
    return map(el.find, argv)


def mapget_text(el, *argv):
    return [got is not None and got.text or "" for got in mapget(el, *argv)]


class CGetter:
    getter_list = []

    USE_TEST_DATA = False

    entry_identifier = None
    ls_required_pref_key = []

    def does_understand(self, s):
        raise Exception("You should not call me directly")

    def __init__(self):
        dlog(self.__class__)

    def resolve(self, identifier):
        raise Exception("You should not call me directly")

    @classmethod
    def add(selfclass, getterclass):
        selfclass.getter_list.append(getterclass())


def process_pubdate(el_pubdate, *timekey):
    if len(el_pubdate):
        _year, _month, _day = mapget_text(el_pubdate[0], *timekey)
        month = day = 1
        if _year:
            if _month:
                if _month.isdigit():
                    month = int(_month)
                elif len(_month) is 3:
                    month = time.strptime(_month, "%b").tm_mon
                if _day:
                    day = int(_day)
            return datetime.datetime(int(_year), month, day)


@CGetter.add
class CrossRefGetter(CGetter):

    entry_identifier = "doi"
    ls_required_pref_key = [(Const.CROSSREF_API_KEY, Validator.email)]

    CROSSREF_TEMPLATE = "http://www.crossref.org/openurl/?id=doi:%s&noredirect=true&pid=%s&format=unixref"

    def does_understand(self, s):
        # ref: http://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
        return re.match(r'\s*(10[.][0-9]{3,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b', s)

    def resolve(self, identifier):
        paper_meta = json.loads(
            habanero.content_negotiation(ids=identifier,
                                         format='citeproc-json'))
        dc = {
            "title": paper_meta['title'],
            "pubdate": paper_meta['published-print']['date-parts'],
            "author_sort": '',
            "publisher": paper_meta['publisher'],
            "issue": '',
            "abstract": paper_meta['container-title'],
            "keywords": '',
            "volume": '',
            "pages": '',
            "authors": ['{} {}'.format(author['given'], author['family'])
                        for author in paper_meta['author']],
        }
        return dc
