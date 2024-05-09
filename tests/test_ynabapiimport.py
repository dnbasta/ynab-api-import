from unittest.mock import patch, MagicMock

import pytest

from ynabapiimport import YnabApiImport
from ynabapiimport.models.exceptions import BalancesDontMatchError


@patch('ynabapiimport.ynabapiimport.YnabApiImport._account_client')
@patch('ynabapiimport.ynabapiimport.NordigenClient')
@patch('ynabapiimport.ynabapiimport.YnabClient')
def test_compare_balances(mock_ynab_client, mock_nordigen_client, mock_account):
	# Arrange
	yi = YnabApiImport(secret_id='', secret_key='', token='', resource_id='', reference='reference',
					   budget_id='', account_id='')
	mock_account.fetch_balances.return_value = (dict(closingBooked=1000), 500)
	yi._ynab_client = MagicMock(**{'fetch_balance.return_value': 1000})
	# Act
	yi.compare_balances()


@patch('ynabapiimport.ynabapiimport.YnabApiImport._account_client')
@patch('ynabapiimport.ynabapiimport.NordigenClient')
@patch('ynabapiimport.ynabapiimport.YnabClient')
def test_compare_balances_fail(mock_ynab_client, mock_nordigen_client, mock_account):
	# Arrange
	yi = YnabApiImport(secret_id='', secret_key='', token='', resource_id='', reference='reference',
					   budget_id='', account_id='')
	mock_account.fetch_balances.return_value = (dict(closingBooked=2000), 500)
	yi._ynab_client = MagicMock(**{'fetch_balance.return_value': 1000})
	# Act
	with pytest.raises(BalancesDontMatchError) as e:
		yi.compare_balances()

