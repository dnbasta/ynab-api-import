from datetime import date
from typing import List

from nordigen import NordigenClient

from ynabapiimport.accountfetcher import AccountFetcher
from ynabapiimport.models.transaction import Transaction


class TransactionFetcher:
	def __init__(self, client: NordigenClient, reference: str, resource_id: str):
		self._client = client
		self._reference = reference
		self.resource_id = resource_id

	def fetch(self, startdate: date) -> List[Transaction]:
		af = AccountFetcher(client=self._client, reference=self._reference)

		if self.resource_id:
			account_id = af.fetch(resource_id=self.resource_id)
		else:
			account_id = af.fetch()

		account = self._client.account_api(id=account_id)

		transaction_dicts = account.get_transactions(date_from=date.strftime(startdate, '%Y-%m-%d'))
		transactions = [Transaction.from_dict(t) for t in transaction_dicts['transactions']['booked']]
		return transactions
