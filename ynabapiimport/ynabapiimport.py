import json
import logging
from datetime import date
from pathlib import Path
from typing import List

import yaml

from ynabapiimport.gocardlessclient import GocardlessClient
from ynabapiimport.memocleaner import MemoCleaner
from ynabapiimport.ynabclient import YnabClient


class YnabApiImport:

	def __init__(self, secret_id: str, secret_key: str, token: str,
				 reference: str, budget_id: str, account_id: str, resource_id: str = None) -> None:
		self.logger = self._set_up_logger()
		self._gocardless_client = GocardlessClient(secret_id=secret_id,
												   secret_key=secret_key,
												   reference=reference,
												   resource_id=resource_id)
		self._ynab_client = YnabClient(token=token, account_id=account_id, budget_id=budget_id)

	@classmethod
	def from_yaml(cls, path: str):
		with Path(path).open('r') as f:
			config_dict = yaml.safe_load(f)

			resource_id = None
			if 'resource_id' in config_dict.keys():
				resource_id = config_dict['resource_id']

			return cls(secret_id=config_dict['secret_id'],
					   secret_key=config_dict['secret_key'],
					   token=config_dict['token'],
					   reference=config_dict['reference'],
					   budget_id=config_dict['budget_id'],
					   account_id=config_dict['account_id'],
					   resource_id=resource_id)

	def import_transactions(self, startdate: date = None, memo_regex: str = None) -> int:
		transactions = self._gocardless_client.fetch_transactions(startdate=startdate)

		if memo_regex:
			mc = MemoCleaner(memo_regex=memo_regex)
			transactions = [mc.clean(t) for t in transactions]

		i = self._ynab_client.insert(transactions)
		self.logger.info(f"inserted {i} transactions for {self._gocardless_client.reference}")
		return i

	def create_auth_link(self, institution_id: str) -> str:
		auth_link = self._gocardless_client.create_requisition_auth_link(institution_id=institution_id)
		self.logger.info(f'created auth link for {institution_id} under reference {self._gocardless_client.reference}')
		return auth_link

	def fetch_institutions(self, countrycode: str) -> List[dict]:
		institutions = self._gocardless_client.get_institutions(countrycode=countrycode)
		self.logger.info(f'fetched list with {len(institutions)} institutions for countrycode {countrycode}')
		return institutions

	def test_memo_regex(self, memo_regex: str) -> List[dict]:
		transactions = self._gocardless_client.fetch_transactions()
		mc = MemoCleaner(memo_regex=memo_regex)
		r = [{t.memo: mc.clean(t).memo} for t in transactions]
		self.logger.info(f'tested memo regex on {len(r)} transactions from {self._gocardless_client.reference}')
		return r

	@staticmethod
	def _set_up_logger() -> logging.Logger:
		parent_name = '.'.join(__name__.split('.')[:-1])
		logger = logging.getLogger(parent_name)
		logger.setLevel(20)
		return logger
