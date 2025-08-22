from typing import Any, Coroutine, Self, List, Type

import zmq
import zmq.asyncio
from abc import ABC, abstractmethod
from typing import Optional

from .parameters import AbstractSocketParameters, TCPSocketParameters
 
from ..cuuid cimport randstr_16


class ZMQSocket(object):
    def __init__(
        self,
        socket_type: zmq.SocketType,
        socket_parameters: AbstractSocketParameters,
        id=None,
    ):
        self._id: bytes = id or randstr_16()
        self._socket_type: zmq.SocketType = socket_type
        self._socket_parameters: AbstractSocketParameters = socket_parameters

        self._context: zmq.asyncio.Context = None
        self._socket: zmq.asyncio.Socket = None

    def initialize_socket(self):
        self._context: zmq.asyncio.Context = zmq.asyncio.Context.instance()
        self._socket = self._context.socket(self._socket_type)
        self._socket.identity = self._id

    async def __aenter__(self) -> Self:
        raise NotImplementedError

    async def __aexit__(self, *args: any, **kwargs: any) -> None:
        self._socket.close()
        self._context.term()

    def send_multipart(self, message: List[bytes]) -> Coroutine[Any, Any, None]:
        return self._socket.send_multipart(message)

    def recv_multipart(self) -> Coroutine[Any, Any, bytes]:
        return self._socket.recv_multipart()


class ZMQPublisher(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.PUB, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.bind(self._socket_parameters.url)
        return self


class ZMQSubscriber(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.SUB, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.connect(self._socket_parameters.url)
        return self

    def subscribe(self, topic: bytes=b""):
        self._socket.setsockopt(zmq.SUBSCRIBE, topic)
        return self


class ZMQRouter(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.ROUTER, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.bind(self._socket_parameters.url)
        return self


class ZMQDealer(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.DEALER, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.connect(self._socket_parameters.url)
        return self


class ZMQPush(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.PUSH, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.connect(self._socket_parameters.url)
        return self


class ZMQPull(ZMQSocket):
    def __init__(self, socket_parameters: AbstractSocketParameters):
        super().__init__(zmq.PULL, socket_parameters)

    async def __aenter__(self) -> Self:
        self.initialize_socket()
        self._socket.bind(self._socket_parameters.url)
        return self