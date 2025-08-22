import unittest

from sdk.cnet.parameters import AbstractSocketParameters, TCPSocketParameters

class TestSocketParameters(unittest.TestCase):
    def test_tcp_socket_parameters_url(self):
        tcp = TCPSocketParameters("127.0.0.1", 5555)
        self.assertEqual(tcp.url, "tcp://127.0.0.1:5555")

    def test_tcp_socket_parameters_url_cache(self):
        tcp = TCPSocketParameters("localhost", 1234)
        url1 = tcp.url
        url2 = tcp.url
        self.assertEqual(url1, url2)

    def test_abstract_socket_parameters_url_not_implemented(self):
        abs_param = AbstractSocketParameters()
        with self.assertRaises(NotImplementedError):
            _ = abs_param.url

if __name__ == "__main__":
    unittest.main()