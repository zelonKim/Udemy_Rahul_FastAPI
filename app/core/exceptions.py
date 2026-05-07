from fastapi import FastAPI, HTTPException, Request, Response, status


class FastShipError(Exception):
    """Base exception in fastship api"""

    status = status.HTTP_400_BAD_REQUEST


class EntityNotFound(FastShipError):
    """Entity is not found"""

    status = status.HTTP_404_NOT_FOUND


class InvalidToken(FastShipError):
    """Token is invalid"""

    status = status.HTTP_401_UNAUTHORIZED


class ClientNotAuthorized(FastShipError):
    """Client is not Authorized"""

    status = status.HTTP_401_UNAUTHORIZED


class BadCredentials(FastShipError):
    """Credintial is wrong"""

    status = status.HTTP_401_UNAUTHORIZED


class DeliveryPartnerNotAvailable(FastShipError):
    """DeliveryPartner is not available"""

    status = status.HTTP_406_NOT_ACCEPTABLE




def _get_handler(status: int, detail: str):
    def handler(request: Request, exception: Exception) -> Response:
        from rich import print, panel

        print(panel.Panel(f"Handled: {exception.__class__.__name__}"))

        raise HTTPException(
            status_code=status,
            detail=detail,
        )

    return handler


def add_exception_handlers(app: FastAPI):
    for subclass in FastShipError.__subclasses__():
        app.add_exception_handler(
            subclass,
            _get_handler(
                subclass.status,
                subclass.__doc__,
            ),
        )
