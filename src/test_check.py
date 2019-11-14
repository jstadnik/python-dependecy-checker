import check

def test_process_line():
    line = "boto3==1.2.4"
    assert check.process_line(line) == ['boto3', "1.2.4"]
    line = "# I am a comment"
    assert check.process_line(line) is None
    
