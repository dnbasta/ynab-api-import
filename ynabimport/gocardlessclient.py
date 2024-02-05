from typing import List
from uuid import uuid4

from nordigen import NordigenClient

from ynabimport.models.transaction import Transaction
from ynabimport.requisitionfetcher import RequisitionFetcher


class GocardlessClient:
	def __init__(self, secret_id: str, secret_key: str, institution_id: str):
		self._institution_id = institution_id
		self._client = NordigenClient(secret_key=secret_key, secret_id=secret_id)
		self._client.generate_token()
		self._account = RequisitionFetcher(client=self._client).fetch()

	def fetch_transactions(self) -> List[Transaction]:
		account = self._client.account_api(id=self._account)
		transaction_dicts = account.get_transactions()['transactions']['booked']
		transactions = [Transaction.from_dict(t) for t in transaction_dicts]
		return transactions

	def create_requisition_auth_link(self) -> str:
		init_session = self._client.initialize_session(institution_id=self._institution_id,
													   redirect_uri='http://localhost:',
													   reference_id=str(uuid4()))
		return init_session.link

	def get_institutions(self, countrycode: str) -> List[dict]:
		institutions = self._client.institution.get_institutions(countrycode)
		return [{'id': i['id'], 'name': i['name']} for i in institutions]
