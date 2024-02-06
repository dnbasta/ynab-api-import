from typing import List
from uuid import uuid4

from nordigen import NordigenClient

from ynabapiimport.models.transaction import Transaction
from ynabapiimport.requisitionfetcher import RequisitionFetcher


class GocardlessClient:
	def __init__(self, secret_id: str, secret_key: str):
		self._client = NordigenClient(secret_key=secret_key, secret_id=secret_id)
		self._client.generate_token()

	def fetch_transactions(self, reference: str) -> List[Transaction]:
		account_id = RequisitionFetcher(client=self._client).fetch(reference=reference)
		account = self._client.account_api(id=account_id)
		transaction_dicts = account.get_transactions()['transactions']['booked']
		transactions = [Transaction.from_dict(t) for t in transaction_dicts]
		return transactions

	def create_requisition_auth_link(self, institution_id: str, reference: str) -> str:
		init_session = self._client.initialize_session(institution_id=institution_id,
													   redirect_uri='http://localhost:',
													   reference_id=f"{reference}::{uuid4()}")
		return init_session.link

	def get_institutions(self, countrycode: str) -> List[dict]:
		institutions = self._client.institution.get_institutions(countrycode)
		return [{'institution_id': i['id'], 'name': i['name']} for i in institutions]
