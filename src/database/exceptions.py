class DatabaseError(Exception):
    pass


class RepositoryError(DatabaseError):
    pass


class EntityNotFoundError(RepositoryError):
    pass


class EntityNotCreatedError(RepositoryError):
    pass


class EntityAlreadyExistsError(RepositoryError):
    pass


class CommitError(DatabaseError):
    pass


class RollbackError(DatabaseError):
    pass


class InvalidParamsError(RepositoryError):
    pass
