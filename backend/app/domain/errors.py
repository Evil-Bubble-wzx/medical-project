class PipelineError(Exception):
    """Safe public error code; provider details must never reach the API."""

    def __init__(self, code: str, retryable: bool = False):
        super().__init__(code)
        self.code = code
        self.retryable = retryable
