
# SPDX-FileCopyrightText: © 2021 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

# NB: prettyprinter excludes fields with default values
# cf. https://github.com/tommikaikkonen/prettyprinter/issues/74

import os

try:
    import prettyprinter as pp
    pp.install_extras(['dataclasses'])
    if os.isatty(2):
        import io
        def pformat(x, **kws):
            o = io.StringIO()
            pp.cpprint(x, stream=o, **kws)
            return o.getvalue()
    else:
        pformat = pp.pformat
except ImportError:
    from pprint import pformat

