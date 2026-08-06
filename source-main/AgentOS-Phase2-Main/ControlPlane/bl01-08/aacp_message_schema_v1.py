# aacp_message_schema_v1.py
# -*- coding: utf-8 -*-
"""
AACP Message Schema (Revised for BL-01)
Audit Envelope is mandatory.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel

from aacp_audit_envelope_v1 import AACPAuditEnvelopeV1


class Metadata(BaseModel):
    schema_version: str
    source: str


class Routing(BaseModel):
    channel_id: str
    topic: str
    flow_id: str


class Security(BaseModel):
    signature: str
    signature_alg: str
    key_id: str


class Payload(BaseModel):
    data: dict


class Processing(BaseModel):
    notes: Optional[str] = None


class AACPMessage(BaseModel):
    metadata: Metadata
    routing: Routing
    security: Security
    payload: Payload
    audit: AACPAuditEnvelopeV1
    processing: Optional[Processing] = None
