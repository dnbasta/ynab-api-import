from datetime import date
from typing import List

from nordigen import NordigenClient
from nordigen.api import AccountApi

from ynabapiimport.accountfetcher import AccountFetcher
from ynabapiimport.models.transaction import Transaction


class AccountClient:

	@classmethod
	def from_api_client(cls, client: NordigenClient, reference: str, resource_id: str) -> "AccountClient":
		af = AccountFetcher(client=client, reference=reference)
		if resource_id:
			account_id = af.fetch(resource_id=resource_id)
		else:
			account_id = af.fetch()
		account = client.account_api(id=account_id)
		return cls(account_api=account)

	def __init__(self, account_api: AccountApi):
		self.account_api = account_api

	def fetch_transactions(self, startdate: date) -> List[Transaction]:
		transaction_dicts = self.account_api.get_transactions(date_from=date.strftime(startdate, '%Y-%m-%d'))
		transactions = [Transaction.from_dict(t) for t in transaction_dicts['transactions']['booked']]
		return transactions

	def fetch_balance(self) -> int:
		balances = self.account_api.get_balances()
		balance = next(b['balanceAmount']['amount'] for b in balances['balances']
					   if b['balanceType'] == 'closingBooked')
		return int(float(balance) * 1000)
