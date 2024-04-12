import logging
from datetime import date, timedelta
from pathlib import Path
from typing import List

import yaml
from nordigen import NordigenClient

from ynabapiimport.exceptions import BalancesDontMatchError
from ynabapiimport.requisitionhandler import RequisitionHandler
from ynabapiimport.accountclient import AccountClient
from ynabapiimport.memocleaner import MemoCleaner
from ynabapiimport.ynabclient import YnabClient


class YnabApiImport:
	"""
	Class which allows to connect to bank accounts via GoCardless API and import transactions into YNAB
	"""

	def __init__(self, secret_id: str, secret_key: str, token: str,
				 reference: str, budget_id: str, account_id: str, resource_id: str = None) -> None:
		self.logger = self._set_up_logger()
		self._reference = reference
		self._resource_id = resource_id
		self._ynab_client = YnabClient(token=token, account_id=account_id, budget_id=budget_id)
		self._api_client = NordigenClient(secret_id=secret_id, secret_key=secret_key)
		self._api_client.generate_token()
		self._account_client = AccountClient.from_api_client(client=self._api_client, reference=self._reference,
										  resource_id=resource_id)

	@classmethod
	def from_yaml(cls, path: str):
		"""
		Creates instance from provided yaml file
		:param path: path to yaml configuration file
		:return: instance of YnabApiImport
		"""
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
		"""
		Import bank transactions via GoCardless to YNAB. The method will only import booked transactions and ignore pending ones.
		:param startdate: date from which to start importing. Will only work for up to max_history_days available for the bank. If not specified will fetch for last 90 days
		:param memo_regex: regex pattern to parse memos from bank transactions
		:return: count of processed transactions
		"""
		if startdate is None:
			startdate = date.today() - timedelta(days=90)

		transactions = self._account_client.fetch_transactions(startdate=startdate)

		if memo_regex:
			mc = MemoCleaner(memo_regex=memo_regex)
			transactions = [mc.clean(t) for t in transactions]

		i = self._ynab_client.insert(transactions)
		self.logger.info(f"inserted {i} transactions for {self._reference}")
		return i

	def compare_balances(self):
		"""
		Compares balance variants for the account (e.g. expected, closingBooked) from API and from YNAB. The method
		compares the plain balance values as well as the balances minus the sum of still pending transactions.
		:raises BalancesDontMatchError: if none of the API returned balances for the account match with the one in YNAB
		"""
		ab, ap = self._account_client.fetch_balances()
		yb = self._ynab_client.fetch_balance()
		if yb not in ab.values() and yb not in [b - ap for b in ab.values()]:
			raise BalancesDontMatchError({'api': ab, 'ynab': yb, 'pending': ap})
		self.logger.info(f'balances match for {self._reference}')

	def create_auth_link(self, institution_id: str, use_max_historical_days: bool = False,
						 delete_current_auth: bool = False) -> str:
		"""
		Creates a link to authenticate access to specified bank through GoCardless. Link needs to be used in browser
		:param institution_id: Gocardless id for your bank
		:param use_max_historical_days: If set to True will create an auth link for the max_days specified in history for the bank
		:param delete_current_auth: if set to True will delete currently active auth
		:return: Link to authenticate access to bank through Gocardless
		"""
		rh = RequisitionHandler(client=self._api_client, reference=self._reference)
		if delete_current_auth:
			rh.delete_current_requisition()
			self.logger.info(f'deleted auth for reference {self._reference}')
		auth_link = rh.create_requisition_auth_link(institution_id=institution_id,
													use_max_historical_days=use_max_historical_days)
		self.logger.info(f'created auth link for {institution_id} under reference {self._reference}')
		return auth_link

	def fetch_institutions(self, countrycode: str) -> List[dict]:
		"""
		Fetches institutions for specified country from GoCardless
		:param countrycode: ISO2 country code
		:return: List of available institutions in country with as with name, institution_id and max_history_days
		"""
		rh = RequisitionHandler(client=self._api_client, reference=self._reference)
		institutions = rh.get_institutions(countrycode=countrycode)
		self.logger.info(f'fetched list with {len(institutions)} institutions for countrycode {countrycode}')
		return institutions

	def test_memo_regex(self, memo_regex: str) -> List[dict]:
		"""
		Tests cleaning memos in transactions from bank with provided regex. Will test on bank transactions from last 90 days
		:param memo_regex: Regex expression to use for cleaning memos
		:return: list with `dict` which has original memo as key and cleaned memo as value
		"""
		transactions = self._account_client.fetch_transactions(date.today() - timedelta(days=90))
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
