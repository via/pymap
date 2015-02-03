# Copyright (c) 2015 Matthew Via
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
import asyncio_redis
import aiohttpmail

class UserPersistence(object):

    def __init__(self, user, config):
        self.user = user
        self.client = yield from asyncio_redis.Connection.create(
            host=config['redis_host'], port=config['redis_port'])

    def get_mailbox(self, mailbox):
        return MailboxPersistence(self.user, mailbox, client)

class MailboxPersistence(object):
    def __init__(self, user, mailbox, client):
        self.user = user
        self.client = client
        self.mailbox = mailbox
    
    def uidvalidity(self):
        validity = yield from self.client.get('{0}/mailboxes/{1}/uidvalidity'.format(self.user, self.mailbox))
        return validity

    def uidnext(self):
        validity = yield from self.client.get('{0}/mailboxes/{1}/uidnext'.format(self.user, self.mailbox))
        return validity

    def new(self, id):
        newuid = yield from self.client.incr('{0}/mailboxes/{1}/uidnext'.format(self.user, self.mailbox))
        yield from self.client.hset('{0}/mailboxes/{1}/uids'.format(self.user, self.mailbox), newuid, id)
        return newuid

    def __getitem__(self, index):
        id = yield from self.client.hget('{0}/mailboxes{1}/uids'.format(self.user, self.mailbox), index)
        return id

    def __delitem__(self, index):
        yield from self.client.hdelete('{0}/mailboxes{1}/uids'.format(self.user, self.mailbox), index)

class UserState(object):
    _delimiter = '.'

    def __init__(self, user, config):
        self.client = aiohttpmail.AIOHTTPMail(config['api_uri'])
        self.user = user
        self.persistence = UserPersistence(user)

    @asyncio.coroutine
    def list(self, ref_name, mbx_name):
        tags = yield from self.client.get_mailbox_tags(self.user)
        return [t['tag'] for t in tags]

    @asyncio.coroutine
    def list_subscribed(self, ref_name, mbx_name):
        return (yield from self.list(ref_name, mbx_name))

    @asyncio.coroutine
    def get_mailbox(self, mbx_name):
        return MailboxState(self, mbx_name)

    @asyncio.coroutine
    def create_mailbox(self, mbx_name):
        return (yield from self.client.create_mailbox_tag(self.user, mbx_name))

    @asyncio.coroutine
    def delete_mailbox(self, mbx_name):
        return (yield from self.client.delete_mailbox_tag(self.user, mbx_name))

    @asyncio.coroutine
    def subscribed(self):
        return True

class MailboxState(object):

    def __init__(self, user, mbx_name):
        self.user = user.user
        self.client = user.client
        self.pdata = user.persistance.get_mailbox(mbx_name)
        self.mailbox = mbx_name
        self.writable = True

    @asyncio.coroutine
    def get_info(self):
        mbx_info = yield from self.client.get_mailbox_tag(self.user, self.mailbox)
        return {'message_count': mbx_info['message-count'],
                'recent_count': 0,
                'unseen': mbx_info['unread-count'],
                'uid_validity': self.pdata.uidvalidity(),
                'next_uid': self.pdata.uidnext(),
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

    def __init__(self, uid, user):
        self.client = user.client
        self.user = user.user
        self.uid = uid


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
