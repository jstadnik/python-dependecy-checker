import pytest
import check


@pytest.mark.parametrize(
    "line, expected", [("boto3==1.2.4", ["boto3", "1.2.4"]), ("# I am a comment", None)]
)
def test_process_line(line, expected):
    assert check.process_line(line) == expected


def test_process_file():
    pass
