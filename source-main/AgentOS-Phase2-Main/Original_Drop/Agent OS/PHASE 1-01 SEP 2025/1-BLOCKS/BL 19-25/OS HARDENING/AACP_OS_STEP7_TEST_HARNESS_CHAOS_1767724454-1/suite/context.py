from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
import json

from lib.http_clients import HttpClient

@dataclass
class Ctx:
    cfg: Dict[str, Any]
    audit: HttpClient
    trust: HttpClient
    policy: HttpClient
    permit: HttpClient
    registry: HttpClient

def make_ctx(cfg: Dict[str, Any]) -> Ctx:
    eps = cfg["endpoints"]
    return Ctx(
        cfg=cfg,
        audit=HttpClient(eps["audit_sink"]),
        trust=HttpClient(eps["trust"]),
        policy=HttpClient(eps["policy"]),
        permit=HttpClient(eps["permit"]),
        registry=HttpClient(eps.get("registry", eps["audit_sink"])),
    )
