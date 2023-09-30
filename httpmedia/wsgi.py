import os
from pathlib import Path

import bottle

from . import httpmedia


httpmedia.ROOT = Path(os.environ["HTTPMEDIA_ROOT"])
httpmedia.ROOT = httpmedia.ROOT.resolve(strict=True)
application = bottle.default_app()
