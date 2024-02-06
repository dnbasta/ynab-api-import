from dataclasses import dataclass
from datetime import date


@dataclass(eq=True, frozen=True)
class Transaction:
	transaction_date: date
	memo: str
	payee_name: str
	import_id: str
	amount: int

	@classmethod
	def from_dict(cls, t_dict: dict):
		if 'creditorName' in t_dict:
			payee = t_dict['creditorName']
		else:
			payee = t_dict['debtorName']
		return cls(import_id=t_dict['transactionId'],
				   memo=t_dict['remittanceInformationUnstructured'],
				   payee_name=payee,
				   amount=int(float(t_dict['transactionAmount']['amount']) * 1000),
				   transaction_date=t_dict['valueDate'])

	def as_dict(self):
		return {'memo': self.memo,
				'import_id': self.import_id,
				'payee_name': self.payee_name,
				'amount': self.amount,
				'date': self.transaction_date}
