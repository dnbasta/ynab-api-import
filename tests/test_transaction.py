from datetime import datetime
from unittest.mock import patch

import pytest

from ynabapiimport.models.transaction import Transaction


@patch('ynabapiimport.models.transaction.datetime', wraps=datetime)
@pytest.mark.parametrize('test_input', [{'valueDate': '2024-01-01'},
										{'bookingDate': '2024-01-01'},
										{'valueDateTime': '2024-01-01T00:00:'},
										{'bookingDateTime': '2024-01-01T00:00:00'},
										{}])
def test_from_dict_datetimes(mock_datetime, test_input):
	mock_datetime.now.return_value = datetime(2024, 1,1)
	transaction_dict = {'internalTransactionId': 'id',
						'creditorName': 'payee',
						'transactionAmount': {'amount': '100'}}
	transaction_dict = {**transaction_dict, **test_input}
	t = Transaction.from_dict(transaction_dict)
	assert t.transaction_date == '2024-01-01'
