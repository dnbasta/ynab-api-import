from typing import List

from nordigen import NordigenClient
from requests import HTTPError

from ynabapiimport.models.exceptions import NoActiveAccountError, MultipleActiveAccountsError, NoRequisitionError


class AccountFetcher:

	def __init__(self, client: NordigenClient, reference: str):
		self._client = client
		self._reference = reference

	@staticmethod
	def fetch_by_resource_id(resource_id: str, active_accounts: List[dict]) -> str:
		try:
			return next(a['id'] for a in active_accounts if a['resourceId'] == resource_id)
		except StopIteration:
			raise NoActiveAccountError(f"No active account with resource_id. Available accounts: {active_accounts}")

	def fetch(self, resource_id: str = None) -> str:
		req = self.fetch_requisition()

		account_dicts = [{**self._client.account_api(id=a).get_details()['account'],
						  **{'id': a}} for a in req['accounts']]
		active_accounts = [a for a in account_dicts if a['status'] == 'enabled']

		if len(active_accounts) == 0:
			raise NoActiveAccountError('No active accounts available in active requisition')
		if resource_id:
			return self.fetch_by_resource_id(resource_id=resource_id, active_accounts=active_accounts)
		if len(active_accounts) > 1:
			raise MultipleActiveAccountsError(f"There are multiple active accounts available in active requisition. "
											  f"Please provide resourceId in import_transaction() call. Available accounts: {active_accounts}")
		return next(a['id'] for a in active_accounts)

	def fetch_requisition(self) -> dict:
		try:
			results = self._client.requisition.get_requisitions()['results']
			return next(r for r in results if r['status'] == 'LN' and r['reference'].split('::')[0] == self._reference)
		except (HTTPError, StopIteration):
			raise NoRequisitionError()
