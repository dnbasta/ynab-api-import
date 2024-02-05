from pathlib import Path

from ynabimport.gocardlessclient import GocardlessClient
from ynabimport.models.config import Config
from ynabimport.ynabclient import YnabClient


class YnabImport:

	def __init__(self, config_path: str):
		config = Config.from_path(Path(config_path))
		self._gocardless_client = GocardlessClient(secret_id=config.secret_id,
												   secret_key=config.secret_key,
												   institution_id=config.institution_id)
		self._ynab_client = YnabClient(token=config.token, budget_id=config.budget_id, account_id=config.account_id)

	def run(self):
		transactions = self._gocardless_client.fetch_transactions()
		i = self._ynab_client.insert(transactions)
		print(f"inserted {i} transactions")

	def fetch_requisition_auth_link(self):
		auth_link = self._gocardless_client.create_requisition_auth_link()
		return auth_link
