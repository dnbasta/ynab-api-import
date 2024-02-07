from nordigen import NordigenClient
from requests import HTTPError

from ynabapiimport.models.exceptions import NoRequisitionError


class RequisitionFetcher:

	def __init__(self, client: NordigenClient) -> None:
		self._client = client

	def fetch(self, reference: str):
		results = self._client.requisition.get_requisitions()['results']
		try:
			req = next(r for r in results if r['status'] == 'LN' and r['reference'].split('::')[0] == reference)
			account_dicts = [{**self._client.account_api(id=a).get_details()['account'],
				**{'id': a}} for a in req['accounts']]
			return next(a['id'] for a in account_dicts
						if a['status'] == 'enabled')
		except (HTTPError, StopIteration):
			raise NoRequisitionError()
