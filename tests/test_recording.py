from core.request_logger import RequestLogger

def test_logger_records_requests():
    logger = RequestLogger("https://example.com")
    dummy_request = type('obj', (object,), {'url': 'https://example.com/api', 'method': 'GET', 'headers': {}, 'post_data': None})
    logger.log_request(dummy_request)
    assert len(logger.recorded_requests) == 1
