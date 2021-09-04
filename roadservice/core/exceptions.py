class AccessDeniedError(Exception):
    pass


class OccupiedUserError(Exception):
    pass


class DuplicatedInfoError(Exception):
    pass


class BusyResourceError(Exception):
    pass


class ResourceNotFoundError(Exception):
    pass


class IllegalOperationInStateError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass
