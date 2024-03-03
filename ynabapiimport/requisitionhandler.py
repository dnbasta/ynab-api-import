from typing import List
from urllib.error import HTTPError
from uuid import uuid4

from nordigen import NordigenClient

from ynabapiimport.models.exceptions import NoRequisitionError, ReferenceNotUnique, ReferenceNotValid


class RequisitionHandler:

	def __init__(self, client: NordigenClient, reference: str):
		self._client = client
		self._reference = reference

	def fetch_requisition(self) -> dict:
		try:
			results = self._client.requisition.get_requisitions()['results']
			return next(r for r in results if r['status'] == 'LN' and r['reference'].split('::')[0] == self._reference)
		except (HTTPError, StopIteration):
			raise NoRequisitionError()

	def create_requisition_auth_link(self, institution_id: str) -> str:
		req_list = self._client.requisition.get_requisitions()['results']

		self.delete_inactive_requisitions(req_list=req_list)
		self.reference_is_unique(req_list=req_list)
		self.reference_is_valid()

		init_session = self._client.initialize_session(institution_id=institution_id,
													   redirect_uri='http://localhost:',
													   reference_id=f"{self._reference}::{uuid4()}",
													   max_historical_days=730)
		return init_session.link

	def delete_inactive_requisitions(self, req_list: List[dict]):
		inactive_requisitions = [r['id'] for r in req_list
								 if r['status'] != 'LN' and r['reference'].split('::')[0] == self._reference]
		[self._client.requisition.delete_requisition(ir) for ir in inactive_requisitions]

	def delete_current_requisition(self):
		req = self.fetch_requisition()
		self._client.requisition.delete_requisition(requisition_id=req['id'])

	def reference_is_unique(self, req_list: List[dict]):
		try:
			existing_reference = next(r for r in req_list if r['reference'].split('::')[0] == self._reference)
			raise ReferenceNotUnique(f"{self._reference} already used for: {existing_reference}")
		except StopIteration:
			pass

	def reference_is_valid(self):
		if '::' in self._reference:
			raise ReferenceNotValid(f"'{self._reference}' is not valid: '::' is not allowed")

	def get_institutions(self, countrycode: str) -> List[dict]:
		institutions = self._client.institution.get_institutions(countrycode)
		return [{'institution_id': i['id'], 'name': i['name']} for i in institutions]
