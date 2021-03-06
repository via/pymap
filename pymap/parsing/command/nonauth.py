# Copyright (c) 2014 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pysasl import ServerMechanism

from .. import NotParseable, Parseable, Space, EndLine
from ..primitives import Atom
from ..specials import AString
from . import CommandNonAuth, CommandNoArgs

__all__ = ['AuthenticateCommand', 'LoginCommand', 'StartTLSCommand']


class AuthenticateCommand(CommandNonAuth):
    command = b'AUTHENTICATE'

    def __init__(self, tag, mech):
        super().__init__(tag)
        self.mech = mech()

    @classmethod
    def _parse(cls, tag, buf, **kwargs):
        _, buf = Space.parse(buf)
        atom, after = Atom.parse(buf)
        _, after = EndLine.parse(after)
        available = ServerMechanism.get_available(True)
        mech_name = str(atom.value.upper(), 'ascii')
        mech = available.get(mech_name)
        if not mech:
            raise NotParseable(buf)
        return cls(tag, mech), after

CommandNonAuth.register_command(AuthenticateCommand)


class LoginCommand(CommandNonAuth):
    command = b'LOGIN'

    def __init__(self, tag, userid, password):
        super().__init__(tag)
        self.userid = userid
        self.password = password

    @classmethod
    def _parse(cls, tag, buf, **kwargs):
        _, buf = Space.parse(buf)
        userid, buf = AString.parse(buf, **kwargs)
        _, buf = Space.parse(buf)
        password, buf = AString.parse(buf, **kwargs)
        _, buf = EndLine.parse(buf)
        return cls(tag, userid.value, password.value), buf

CommandNonAuth.register_command(LoginCommand)


class StartTLSCommand(CommandNonAuth, CommandNoArgs):
    command = b'STARTTLS'

CommandNonAuth.register_command(StartTLSCommand)
