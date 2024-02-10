from dataclasses import dataclass
from datetime import date


@dataclass
class Transaction:
	transaction_date: str
	memo: str
	payee_name: str
	import_id: str
	amount: int

	@classmethod
	def from_dict(cls, t_dict: dict):
		payee = None
		if 'creditorName' in t_dict:
			payee = t_dict['creditorName'].strip()
		elif 'debtorName' in t_dict:
			payee = t_dict['debtorName'].strip()

		memo = None
		if 'remittanceInformationUnstructured' in t_dict:
			memo = str(' '.join(t_dict['remittanceInformationUnstructured'].replace('\n', ' ')[:127].strip().split()))

		return cls(import_id=t_dict['internalTransactionId'],
				   memo=memo,
				   payee_name=payee,
				   amount=int(float(t_dict['transactionAmount']['amount']) * 1000),
				   transaction_date=t_dict['valueDate'])

	def as_dict(self):
		raw_dict = {'memo': self.memo,
				'import_id': self.import_id,
				'payee_name': self.payee_name,
				'amount': self.amount,
				'date': self.transaction_date}
		return {k: v for k, v in raw_dict.items() if v is not None}
