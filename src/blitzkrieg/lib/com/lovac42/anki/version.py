# -*- coding: utf-8 -*-
# Copyright (c) 2020 Lovac42
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from anki import version

ANKI20 = version.startswith("2.0.")

CCBC = version.endswith("ccbc")

ANKI21 = not CCBC and version.startswith("2.1.")

VERSION = version.split('_')[0] #rm ccbc
m,n,p = VERSION.split('.')

MAJOR_VERSION = int(m)
MINOR_VERSION = int(n)
PATCH_VERSION = int(p)
POINT_VERSION = 0 if ANKI20 else PATCH_VERSION

