import socket
import sys
from enum import IntEnum, auto
from collections import namedtuple


def _repeat_until_succeeded(fun, max_repeats, *args):
    for i in range(max_repeats):
        try:
            r = fun(*args)
        except socket.timeout:
            pass
        else:
            return r
    raise RuntimeError('Exceeded max repeat count.')


class Energenie:
    def __init__(self, host, port, password, status, max_repeat):
        Switch = namedtuple('switch', ['on', 'off', 'nop'])
        self._host = host
        self._port = port
        self._key = password.ljust(8).encode()
        self.switch = Switch(on=0x01, off=0x02, nop=0x04)
        self.status = status
        self._max_repeat = max_repeat

    @staticmethod
    def _encrypt(request, key, sc):
        return bytes(((((((c ^ sc[2]) + sc[3]) % 256) ^ key[0]) + key[1]) % 256 for c in request))[::-1]

    @staticmethod
    def _decrypt(status, key, sc):
        return bytes(((((((e - key[1] + 256) % 256) ^ key[0]) - sc[3] + 256) % 256) ^ sc[2] for e in status))[::-1]

    def status(self):
        raw = _repeat_until_succeeded(self._talk, self._max_repeat)
        return [self.status[s] for s in raw]

    @staticmethod
    def _solve_challenge(ch, key):
        lo = (((ch[0] ^ key[2]) * key[0]) ^ (key[6] | (key[4] << 8)) ^ ch[2]).to_bytes(2, sys.byteorder)
        hi = (((ch[1] ^ key[3]) * key[1]) ^ (key[7] | (key[5] << 8)) ^ ch[3]).to_bytes(2, sys.byteorder)
        return lo + hi

    def set(self, status):
        available = [a.name for a in self.status]
        assert all((s in available for s in status)), "Available commands: " + str(available)
        raw = _repeat_until_succeeded(self._talk, self._max_repeat, bytes((self.status[s] for s in status)))
        return [self.status(s).name for s in raw]

    def _talk(self, change=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((self._host, self._port))
            encrypted, sc = self._auth(s)
            current = self._decrypt(encrypted, self._key, sc)
            if change:
                request = self._gen_request(change, current)
                s.sendall(self._encrypt(request, self._key, sc))
                encrypted = s.recv(4)
                current = self._decrypt(encrypted, self._key, sc)
            return current

    def _auth(self, s):
        s.sendall(b'\x11')
        sc = s.recv(4)
        response = self._solve_challenge(sc, self._key)
        s.sendall(response)
        encrypted = s.recv(4)
        return encrypted, sc

    def _gen_request(self, desired, current):
        req = []
        for d, c in zip(desired, current):
            if d == self.status.left or d == c:
                req.append(self.switch.nop)
            elif d == self.status.on:
                req.append(self.switch.on)
            elif d == self.status.off:
                req.append(self.switch.off)
            else:  # TOGGLE
                req.append({self.status.on: self.switch.off, self.status.off: self.switch.on}[c])
        return bytes(req)


class EGV21(Energenie):
    class Status(IntEnum):
        on = 0x41
        off = 0x82
        toggle = auto()
        left = auto()

    def __init__(self, host, port, password, max_repeat=10):
        super().__init__(host, port, password, self.Status, max_repeat)


class EGWLAN(Energenie):
    ...


class EGV20(Energenie):
    ...
