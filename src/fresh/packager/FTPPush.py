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
import os, ftplib
from ftplib import FTP

class FTPPush(object):
    def __init__(self, address, path, filename, user, password):
        self.address  = address
        self.path     = path
        self.filename = filename
        self.user     = user
        self.password = password

    def describe(self):
        return 'Push package to ftp://%s/%s' % (self.address, self.path)

    def send(self, filename):
        file = open(filename)
        path = self.path + '/' + self.filename
        ftp  = FTP(self.address, self.user, self.password)
        try:
            ftp.sendcmd('DELE ' + path)
        except ftplib.error_perm:
            pass # File does not exist.
        ftp.storbinary('STOR ' + path, file)
        ftp.quit()
