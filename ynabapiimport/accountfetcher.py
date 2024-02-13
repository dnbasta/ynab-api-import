from typing import List

from nordigen import NordigenClient
from requests import HTTPError

from ynabapiimport.models.exceptions import NoAccountError, MultipleAccountsError, NoRequisitionError


class AccountFetcher:

	def __init__(self, client: NordigenClient, reference: str):
		self._client = client
		self._reference = reference

	@staticmethod
	def fetch_by_resource_id(resource_id: str, account_dicts: List[dict]) -> str:
		try:
			return next(a['account_id'] for a in account_dicts if a['resourceId'] == resource_id)
		except StopIteration:
			raise NoAccountError(f"No active account with resource_id. Available accounts: {account_dicts}")

	def fetch(self, resource_id: str = None) -> str:
		req = self.fetch_requisition()

		account_dicts = [{**self._client.account_api(id=a).get_details()['account'],
						  **{'account_id': a}} for a in req['accounts']]

		if len(account_dicts) == 0:
			raise NoAccountError('No active accounts available in active requisition')
		if resource_id:
			return self.fetch_by_resource_id(resource_id=resource_id, account_dicts=account_dicts)
		if len(account_dicts) > 1:
			raise MultipleAccountsError(f"There are multiple active accounts available in active requisition. "
											  f"Please provide one of the following resourceId when initializing library.", account_dicts)
		return next(a['account_id'] for a in account_dicts)

	def fetch_requisition(self) -> dict:
		try:
			results = self._client.requisition.get_requisitions()['results']
			return next(r for r in results if r['status'] == 'LN' and r['reference'].split('::')[0] == self._reference)
		except (HTTPError, StopIteration):
			raise NoRequisitionError()
