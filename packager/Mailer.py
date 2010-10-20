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
from copy               import copy
from Exscript.util.mail import send

class Mailer(object):
    def __init__(self, server, mail):
        self.server = server
        self.mail   = mail

    def describe(self):
        return 'Mail package to %s' % ', '.join(self.mail.get_to())

    def send(self, filename):
        mail = copy(self.mail)
        mail.add_attachment(filename)
        send(mail, server = self.server)
