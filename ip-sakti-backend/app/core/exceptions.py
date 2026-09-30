class IPSaktiException(Exception):
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class SessionNotFoundError(IPSaktiException):
    def __init__(self, session_id: str):
        super().__init__(f"Session with id '{session_id}' not found", "SESSION_NOT_FOUND", 404)

class InvalidJurisdictionError(IPSaktiException):
    def __init__(self, msg: str = "Invalid jurisdiction specified"):
        super().__init__(msg, "INVALID_JURISDICTION", 400)

class ClassificationFlowError(IPSaktiException):
    def __init__(self, msg: str = "Error in classification flow state"):
        super().__init__(msg, "CLASSIFICATION_FLOW_ERROR", 400)
