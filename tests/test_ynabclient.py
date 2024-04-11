from unittest.mock import patch, MagicMock

from ynabapiimport.models.transaction import Transaction
from ynabapiimport.ynabclient import YnabClient


@patch('ynabapiimport.ynabclient.requests.get')
def test_fetch_balance(mock_request):
	# Arrange
	response = MagicMock()
	response.json.return_value = dict(data=dict(account=dict(cleared_balance=1000)))
	mock_request.return_value = response
	yc = YnabClient(token='token', budget_id='budget_id', account_id='account_id')
	# Act
	b = yc.fetch_balance()
	# Assert
	assert b == 1000


@patch('ynabapiimport.ynabclient.requests.post')
def test_insert(mock_request):
	# Arrange
	response = MagicMock()
	response.json.return_value = dict(data=dict(transaction_ids=['xxx']))
	mock_request.return_value = response
	mock_transaction = Transaction.from_dict(MagicMock())
	yc = YnabClient(token='token', budget_id='budget_id', account_id='account_id')

	# Act
	c = yc.insert([mock_transaction])

	j = mock_request.call_args.kwargs['json']
	assert isinstance(j, dict)
	assert all(k in ('account_id', 'date', 'cleared', 'amount', 'import_id') for k in j['transactions'][0].keys())
	assert c == 1
