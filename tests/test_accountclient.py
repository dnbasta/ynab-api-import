from datetime import date
from unittest.mock import MagicMock, patch
import os
import pytest

from ynabapiimport import YnabApiImport
from ynabapiimport.accountclient import AccountClient
from ynabapiimport.models.transaction import Transaction


@pytest.mark.parametrize('test_input, empty', [(None, True), ('resource_id', False)])
@patch('ynabapiimport.accountclient.AccountFetcher.fetch', return_value='account_id')
def test_init(mock_account_fetch, test_input, empty):
	# Arrange
	client = MagicMock()
	mock_account_api = MagicMock()
	client.account_api.return_value = mock_account_api

	# Act
	gc = AccountClient.from_api_client(client=client, reference='x', resource_id=test_input)

	# Assert
	if empty:
		mock_account_fetch.assert_called_once_with()
	else:
		mock_account_fetch.assert_called_once_with(resource_id='resource_id')

	client.account_api.assert_called_once_with(id='account_id')
	assert gc.account_api == mock_account_api


def test_fetch_balance():
	# Arrange
	mock_account_api = MagicMock()
	mock_account_api.get_balances.return_value = dict(balances=[dict(balanceType='closingBooked', balanceAmount=dict(amount=1.00))])
	ac = AccountClient(account_api=mock_account_api)
	ac.pending = 100

	# Act
	balances, pending = ac.fetch_balances()

	# Assert
	assert balances == {'closingBooked': 1000}
	assert pending == 100


def test_fetch_transactions():
	# Arrange
	mock_account_api = MagicMock()
	mock_account_api.get_transactions.return_value = dict(transactions=dict(booked=[MagicMock()], pending=MagicMock()))
	ac = AccountClient(account_api=mock_account_api)

	# Act
	transactions = ac.fetch_transactions(startdate=date(2024, 1, 1))

	# Assert
	assert len(transactions) == 1
	assert isinstance(transactions[0], Transaction)
	mock_account_api.get_transactions.assert_called_once_with(date_from='2024-01-01')
