from typing import List

import requests

from ynabapiimport.models.transaction import Transaction

YNAB_BASE_URL = "https://api.ynab.com/v1"


class YnabClient:

	def __init__(self, token: str, budget_id: str) -> None:
		self._token = token
		self._budget_id = budget_id
		self._header = {"Authorization": f"Bearer {token}"}

	def insert(self, transactions: List[Transaction], account_id: str) -> int:
		common_attributes = {'account_id': account_id, 'cleared': 'cleared'}
		data = {'transactions': [{**t.as_dict(), **common_attributes} for t in transactions]}
		r = requests.post(f"{YNAB_BASE_URL}/budgets/{self._budget_id}/transactions",
						  json=data,
						  headers=self._header)
		r.raise_for_status()
		return len(r.json()['data']['transaction_ids'])
