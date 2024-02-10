import re

from ynabapiimport.models.transaction import Transaction


class MemoCleaner:

	def __init__(self, memo_regex: str):
		self._memo_regex = memo_regex

	def clean(self, transaction: Transaction) -> Transaction:

		r = re.search(self._memo_regex, transaction.memo)
		if r:
			transaction.memo = r.groups()[0]
		return transaction


