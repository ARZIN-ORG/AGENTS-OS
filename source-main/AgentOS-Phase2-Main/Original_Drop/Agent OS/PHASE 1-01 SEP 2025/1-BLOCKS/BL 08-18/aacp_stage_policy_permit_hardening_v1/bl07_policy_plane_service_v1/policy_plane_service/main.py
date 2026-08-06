# -*- coding: utf-8 -*-
from __future__ import annotations

import uvicorn

from .settings import Settings
from .app import app


def run() -> None:
    s = Settings()
    uvicorn.run(app, host=s.bind_host, port=s.bind_port, log_level="info")


if __name__ == "__main__":
    run()
