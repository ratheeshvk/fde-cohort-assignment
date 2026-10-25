"""Business rules — sits between the API layer and the repository."""

import repository


def list_employees() -> list[dict]:
    return repository.get_all_employees()
