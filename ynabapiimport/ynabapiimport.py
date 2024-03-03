import logging
from datetime import date, timedelta
from pathlib import Path
from typing import List

import yaml
from nordigen import NordigenClient

from ynabapiimport.requisitionhandler import RequisitionHandler
from ynabapiimport.transactionfetcher import TransactionFetcher
from ynabapiimport.memocleaner import MemoCleaner
from ynabapiimport.ynabclient import YnabClient


class YnabApiImport:

	def __init__(self, secret_id: str, secret_key: str, token: str,
				 reference: str, budget_id: str, account_id: str, resource_id: str = None) -> None:
		self.logger = self._set_up_logger()
		self._reference = reference
		self._resource_id = resource_id
		self._ynab_client = YnabClient(token=token, account_id=account_id, budget_id=budget_id)
		self._gocardless_client = NordigenClient(secret_id=secret_id, secret_key=secret_key)
		self._gocardless_client.generate_token()

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
		if startdate is None:
			startdate = date.today() - timedelta(days=90)

		tf = TransactionFetcher(client=self._gocardless_client, reference=self._reference,
								resource_id=self._resource_id)
		transactions = tf.fetch(startdate=startdate)

		if memo_regex:
			mc = MemoCleaner(memo_regex=memo_regex)
			transactions = [mc.clean(t) for t in transactions]

		i = self._ynab_client.insert(transactions)
		self.logger.info(f"inserted {i} transactions for {self._reference}")
		return i

	def create_auth_link(self, institution_id: str) -> str:
		rh = RequisitionHandler(client=self._gocardless_client, reference=self._reference)
		auth_link = rh.create_requisition_auth_link(institution_id=institution_id)
		self.logger.info(f'created auth link for {institution_id} under reference {self._reference}')
		return auth_link

	def delete_current_auth(self):
		rh = RequisitionHandler(client=self._gocardless_client, reference=self._reference)
		rh.delete_current_requisition()
		self.logger.info(f'deleted auth for reference {self._reference}')

	def fetch_institutions(self, countrycode: str) -> List[dict]:
		rh = RequisitionHandler(client=self._gocardless_client, reference=self._reference)
		institutions = rh.get_institutions(countrycode=countrycode)
		self.logger.info(f'fetched list with {len(institutions)} institutions for countrycode {countrycode}')
		return institutions

	def test_memo_regex(self, memo_regex: str) -> List[dict]:
		tf = TransactionFetcher(client=self._gocardless_client, reference=self._reference, resource_id=self._resource_id)
		transactions = tf.fetch(date.today() - timedelta(days=90))
		mc = MemoCleaner(memo_regex=memo_regex)
		r = [{t.memo: mc.clean(t).memo} for t in transactions]
		self.logger.info(f'tested memo regex on {len(r)} transactions from {self._reference}')
		return r

	@staticmethod
	def _set_up_logger() -> logging.Logger:
		parent_name = '.'.join(__name__.split('.')[:-1])
		logger = logging.getLogger(parent_name)
		logger.setLevel(20)
		return logger
