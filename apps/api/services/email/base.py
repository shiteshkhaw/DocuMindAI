from abc import ABC, abstractmethod
from pydantic import BaseModel


class EmailResult(BaseModel):
    message_id: str
    recipient: str
    success: bool
    error: str | None = None


class BaseEmailProvider(ABC):
    """
    Abstract email provider interface to support provider-agnostic delivery.
    """

    @abstractmethod
    async def send(
        self, to: str, subject: str, html: str, text: str | None = None
    ) -> EmailResult:
        """Deliver an email message asynchronously."""
        pass
