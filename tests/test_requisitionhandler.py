from unittest.mock import MagicMock

import pytest

from ynabapiimport.models.exceptions import NoRequisitionError, ReferenceNotUnique
from ynabapiimport.requisitionhandler import RequisitionHandler


@pytest.mark.parametrize('test_input', [[], [{'reference': 'xxx::xxx', 'status': 'LN'}]])
def test_fetch_requisition_fail(test_input):
	# Arrange
	client = MagicMock()
	client.requisition.get_requisitions.return_value = {'results': test_input}

	# Act & Assert
	rh = RequisitionHandler(client=client, reference='reference')
	with pytest.raises(NoRequisitionError):
		r = rh.fetch_requisition()


def test_fetch_requisition_success():
	# Arrange
	client = MagicMock()
	mock_req = {'reference': 'reference::xxx', 'status': 'LN'}
	client.requisition.get_requisitions.return_value = {'results': [mock_req]}

	# Act
	rh = RequisitionHandler(client=client, reference='reference')
	r = rh.fetch_requisition()

	# Assert
	assert r == mock_req


def test_reference_is_unique_fail():
	# Arrange
	req_list = [{'reference': 'xxx::xxx'}, {'reference': 'ref::xxx'}]

	# Act & Assert
	rh = RequisitionHandler(client=MagicMock(), reference='ref')
	with pytest.raises(ReferenceNotUnique):
		rh.reference_is_unique(req_list)


@pytest.mark.parametrize('test_input', [[], [{'reference': 'xxx:xxx'}]])
def test_reference_is_unique_success(test_input):
	# Act
	rh = RequisitionHandler(client=MagicMock(), reference='ref')
	rh.reference_is_unique(test_input)
