from datetime import date
from typing import List
from uuid import uuid4

from nordigen import NordigenClient

from ynabapiimport.accountfetcher import AccountFetcher
from ynabapiimport.models.exceptions import ReferenceNotUnique, ReferenceNotValid
from ynabapiimport.models.transaction import Transaction


class GocardlessClient:
	def __init__(self, secret_id: str, secret_key: str, reference: str):
		self._client = NordigenClient(secret_key=secret_key, secret_id=secret_id)
		self._client.generate_token()
		self.reference = reference

	def fetch_transactions(self, resource_id: str = None, startdate: date = None) -> List[Transaction]:
		af = AccountFetcher(client=self._client, reference=self.reference)

		if resource_id:
			account_id = af.fetch(resource_id=resource_id)
		else:
			account_id = af.fetch()

		account = self._client.account_api(id=account_id)
		transaction_dicts = account.get_transactions()['transactions']['booked']
		transactions = [Transaction.from_dict(t) for t in transaction_dicts]

		if startdate:
			transactions = [t for t in transactions if t.transaction_date >= date.strftime(startdate, '%Y-%m-%d')]

		return transactions

	def create_requisition_auth_link(self, institution_id: str) -> str:
		req_list = self._client.requisition.get_requisitions()['results']

		self.delete_inactive_requisitions(req_list=req_list)
		self.reference_is_unique(req_list=req_list)
		self.reference_is_valid()

		init_session = self._client.initialize_session(institution_id=institution_id,
													   redirect_uri='http://localhost:',
													   reference_id=f"{self.reference}::{uuid4()}")
		return init_session.link

	def get_institutions(self, countrycode: str) -> List[dict]:
		institutions = self._client.institution.get_institutions(countrycode)
		return [{'institution_id': i['id'], 'name': i['name']} for i in institutions]

	def delete_inactive_requisitions(self, req_list: List[dict]):
		inactive_requisitions = [r['id'] for r in req_list
								 if r['status'] != 'LN' and r['reference'].split('::')[0] == self.reference]
		[self._client.requisition.delete_requisition(ir) for ir in inactive_requisitions]

	def reference_is_unique(self, req_list: List[dict]):
		try:
			existing_reference = next(r for r in req_list if r['reference'].split('::')[0] == self.reference)
			raise ReferenceNotUnique(f"{self.reference} already used for: {existing_reference}")
		except StopIteration:
			pass

	def reference_is_valid(self):
		if '::' in self.reference:
			raise ReferenceNotValid(f"'{self.reference}' is not valid: '::' is not allowed")
