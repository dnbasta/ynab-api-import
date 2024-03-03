from typing import List

from nordigen import NordigenClient

from ynabapiimport.models.exceptions import NoAccountError, MultipleAccountsError
from ynabapiimport.requisitionhandler import RequisitionHandler


class AccountFetcher:

	def __init__(self, client: NordigenClient, reference: str):
		self._client = client
		self._requisitionhandler = RequisitionHandler(reference=reference, client=client)

	@staticmethod
	def fetch_by_resource_id(resource_id: str, account_dicts: List[dict]) -> str:
		try:
			return next(a['account_id'] for a in account_dicts if a['resourceId'] == resource_id)
		except StopIteration:
			raise NoAccountError(f"No active account with resource_id. Available accounts: {account_dicts}")

	def fetch(self, resource_id: str = None) -> str:
		req = self._requisitionhandler.fetch_requisition()

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
