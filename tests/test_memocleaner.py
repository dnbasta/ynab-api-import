from unittest.mock import MagicMock

from ynabapiimport.memocleaner import MemoCleaner


def test_clean_pass():
	mc = MemoCleaner(memo_regex=r'search:(.*)')
	r = mc.clean(MagicMock(memo='search:test'))
	assert r.memo == 'test'


def test_clean_fail():
	mc = MemoCleaner(memo_regex=r'search:(.*)')
	r = mc.clean(MagicMock(memo='bearch:test'))
	assert r.memo == 'bearch:test'

def test_trim():
	v = 'mandatereference:,creditorid:,remittanceinformation:NR XXXX 6013 BERLIN                                   KAUFUMSATZ'.strip()
	assert True
