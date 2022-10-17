"""
Test Wait for DB
"""
from app.core.management.commands import wait_for_db

from psycopg2 import OperationalError as Psycog2Error

from django.core.management import call_command
from django.db.utils import OperationalError


def test_wait_for_db_handle_func(mocker):
    mock_check_func = mocker.patch(
        "app.core.management.commands.wait_for_db.Command.check",
        return_value=True)

    call_command(wait_for_db.Command())

    mock_check_func.assert_called_with(databases=["default"])


def test_wait_for_db_delay(mocker):
    mocker.patch("time.sleep")

    mock_check_func = mocker.patch(
        "app.core.management.commands.wait_for_db.Command.check",
        return_value=True)
    mock_check_func.side_effect = [Psycog2Error] * 2 + \
        [OperationalError] * 3 + [True]

    call_command(wait_for_db.Command())

    assert mock_check_func.call_count == 6

    mock_check_func.assert_called_with(databases=["default"])
