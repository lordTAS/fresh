# Copyright (C) 2007-2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import os, paramiko, socket

class SCPPush(object):
    def __init__(self, address, path, filename, user, password="", keyfile=None, pw_only=False):
        self.address  = address
        self.path     = path
        self.filename = filename
        self.user     = user
        self.password = password
        self.keyfile  = keyfile
        self.pw_only  = self.pw_only

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address, 22))

    def describe(self):
        return 'Push package to scp://%s/%s' % (self.address, self.path)

    def send(self, filename):
        t = paramiko.Transport(sock)
        t.start_client()
        if self.pw_only:
            t.auth_password(self.user, self.password)
        else:
            try:
                kf = paramiko.RSAKey.from_private_key_file(self.keyfile)
            except Exception, e:
                pass
            agent = paramiko.Agent()
            agent_keys = agent.get_keys() + (kf,)
            for key in agent_keys:
                try:
                    transport.auth_publickey(self.user, key)
                except paramiko.SSHException, e:
                    pass
            if not t.is_authenticated():
                t.auth_password(self.user, self.password)
        if not t.is_authenticated():
            return

        scp_channel = t.open_session()
        file = open(filename)
        scp_channel.exec_command('scp -v -t %s\n'\
                                 % '/'.join(self.path))
        scp_channel.send('C%s %d %s\n' \
                         %(oct(os.stat(filename).st_mode)[-4:], \
                           os.stat(filename)[6], \
                           self.filename))
        scp_channel.sendall(file.read())

        f.close()
        scp_channel.close()
        t.close()
        sock.close()
