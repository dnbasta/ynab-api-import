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
			return next(a for a in req['accounts']
					if self._client.account_api(id=a).get_details()['account']['name'] == 'Main Account')
		except (HTTPError, StopIteration):
			raise NoRequisitionError()
