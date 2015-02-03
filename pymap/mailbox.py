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

import asyncio
import random

__all__ = ['UserState', 'MailboxState']


class UserState(object):

    _delimiter = '.'
    _folders = ['INBOX', '.Testing', '.Testing.Secrets', '.Stuff']

    def __init__(self, authed):
        super().__init__()
        self.authed = authed
        self.mailboxes = {name: MailboxState(authed, name)
                          for name in self._folders}

    @asyncio.coroutine
    def list(self, ref_name, mbx_name):
        return self._delimiter, self.mailboxes

    @asyncio.coroutine
    def list_subscribed(self, ref_name, mbx_name):
        return self._delimiter, [mbx for mbx, state in self.mailboxes
                                 if state.subscribed]

    @asyncio.coroutine
    def get_mailbox(self, mbx_name):
        return self.mailboxes.get(mbx_name)

    @asyncio.coroutine
    def create_mailbox(self, mbx_name):
        pass

    @asyncio.coroutine
    def delete_mailbox(self, mbx_name):
        pass

class MailboxPersistentState(object):

    def __init__(self, mailbox):
        self.mailbox = mailbox
        self.mapping = {1: "1", 2: "2"}

    @asyncio.coroutine
    def uidnext(self):
        return len(self.mapping) + 1

    @asyncio.coroutine
    def uidvalidity(self):
        return 1

    @asyncio.coroutine
    def new(self, id):
        pass

    @asyncio.coroutine
    def subscribed(self):
        return True

    @asyncio.coroutine
    def __getitem__(self, index):
        return self.mapping[index]

    @asyncio.coroutine
    def __delitem__(self, index):
        del self.mapping[index]

class MailboxState(object):

    def __init__(self, authed, mailbox):
        super().__init__()
        self.authed = authed
        self.mailbox = mailbox
        self.subscribed = True
        self.writable = True
        self.mapping = MailboxPersistentState()

        self.messages = [MessageState() for i in range(random.randint(0, 100))]

    @asyncio.coroutine
    def get_info(self):
        return {'message_count': len(self.messages),
                'recent_count': 0,
                'unseen': next(filter(lambda msg: msg.unseen,
                                      self.messages), False),
                'uid_validity': self.mapping.uidvalidity(),
                'next_uid': self.mapping.uidnext(),
                'writable': self.writable}

    @asyncio.coroutine
    def add_message(self, message, flags):
        pass

    @asyncio.coroutine
    def delete_message(self, message):
        pass

    @asyncio.coroutine
    def fetch_message(self, message):
        pass

    @asyncio.coroutine
    def add_message_flag(self, message, flag):
        pass

    @asyncio.coroutine
    def remove_message_flag(self, message, flag):
        pass

class MessageState(object):

    def __init__(self, uid):
        super().__init__()
        self.uid = uid
        self.unseen = (random.randint(0, 9) >= 8)


    @asyncio.coroutine
    def get_raw(self):
        pass

    @asyncio.coroutine
    def get_flags(self):
        pass

    @asyncio.coroutine
    def get_cachable_fields(self):
        pass

    @asyncio.coroutine
    def get_cached_fields(self):
        pass
