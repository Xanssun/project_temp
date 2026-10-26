from typing import Any, Callable

from src.api.common.events.base import Event


class NatsEvent(Event):
    subject: str = ""
    _reply: str = ""
    _headers: dict[str, Any] | None = None


class NatsJetStreamEvent(Event):
    subject: str = ""
    _stream: str | None = None
    _timeout: float | None = None
    _headers: dict[str, Any] | None = None


def rebuild_nats_event[T: NatsEvent](
    subject: str = "",
    subject_namespace: str | None = None,
    separator: str = ".",
    reply: str = "",
    headers: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]:
    def _wrapper(cls: type[T]) -> type[T]:
        updated_subject = subject

        class UpdatedEvent(cls):  # type: ignore
            model_config = {"populate_by_name": True}
            subject: str = updated_subject
            _reply: str = reply
            if headers is not None:
                _headers: dict[str, Any] = headers

            def model_post_init(self, *args: Any, **kwargs: Any) -> None:
                super().model_post_init(*args, **kwargs)
                if subject_namespace:
                    if self.subject:
                        self.subject = f"{subject_namespace}{separator}{self.subject}"
                    else:
                        self.subject = subject_namespace
                elif not self.subject and subject:
                    self.subject = subject

        UpdatedEvent.__name__ = cls.__name__
        UpdatedEvent.__qualname__ = cls.__qualname__
        UpdatedEvent.__module__ = cls.__module__
        return UpdatedEvent  # type: ignore

    return _wrapper


def rebuild_jetstream_event[T: NatsJetStreamEvent](
    subject: str = "",
    subject_namespace: str | None = None,
    separator: str = ".",
    stream: str | None = None,
    timeout: float | None = None,
    headers: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]:
    def _wrapper(cls: type[T]) -> type[T]:
        updated_subject = subject

        class UpdatedEvent(cls):  # type: ignore
            model_config = {"populate_by_name": True}
            subject: str = updated_subject
            if stream is not None:
                _stream: str = stream
            if timeout is not None:
                _timeout: float = timeout
            if headers is not None:
                _headers: dict[str, Any] = headers

            def model_post_init(self, *args: Any, **kwargs: Any) -> None:
                super().model_post_init(*args, **kwargs)
                if subject_namespace:
                    if self.subject:
                        self.subject = f"{subject_namespace}{separator}{self.subject}"
                    else:
                        self.subject = subject_namespace
                elif not self.subject and subject:
                    self.subject = subject

                self.subject = self.subject.format(**self.__dict__)

                if self._stream is not None:
                    self._stream = self._stream.format(**self.__dict__)

        UpdatedEvent.__name__ = cls.__name__
        UpdatedEvent.__qualname__ = cls.__qualname__
        UpdatedEvent.__module__ = cls.__module__
        return UpdatedEvent  # type: ignore

    return _wrapper
