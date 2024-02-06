from pathlib import Path
from typing import List

import yaml

from ynabapiimport.gocardlessclient import GocardlessClient
from ynabapiimport.ynabclient import YnabClient


class YnabApiImport:

	def __init__(self, secret_id: str, secret_key: str, budget_id: str, token: str):
		self._gocardless_client = GocardlessClient(secret_id=secret_id,
												   secret_key=secret_key)
		self._ynab_client = YnabClient(token=token, budget_id=budget_id)

	@classmethod
	def from_yaml(cls, path: str):
		with Path(path).open('r') as f:
			config_dict = yaml.safe_load(f)
			return cls(secret_id=config_dict['secret_id'],
					   secret_key=config_dict['secret_key'],
					   budget_id=config_dict['budget_id'],
					   token=config_dict['token'])

	def import_transactions(self, reference: str, account_id: str):
		transactions = self._gocardless_client.fetch_transactions(reference=reference)
		i = self._ynab_client.insert(transactions, account_id=account_id)
		print(f"inserted {i} transactions for {reference} into account {account_id}")

	def create_auth_link(self, institution_id: str, reference: str) -> str:
		auth_link = self._gocardless_client.create_requisition_auth_link(institution_id=institution_id,
																		 reference=reference)
		return auth_link

	def fetch_institutions(self, countrycode: str) -> List[dict]:
		return self._gocardless_client.get_institutions(countrycode=countrycode)
