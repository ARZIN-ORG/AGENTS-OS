# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from .schemas import AgentCreate, AgentUpdate, AgentStatusChange, AgentOut, EffectiveAllowlist
from .models import AgentStatus, AgentClass
from .service import (
    register_agent,
    get_agent,
    list_agents,
    update_agent,
    change_status,
    revoke_agent,
    ConflictError,
    NotFoundError,
)
from .validation import ValidationError


router = APIRouter()


def _actor_from(req: Request) -> Optional[str]:
    # In private cloud, this can be set by a trusted gateway later.
    return req.headers.get("x-actor")


def _trace_from(req: Request) -> Optional[str]:
    return req.headers.get("x-trace-id")


def _to_out(a) -> AgentOut:
    return AgentOut(
        agent_id=a.agent_id,
        agent_class=a.agent_class,
        agent_version=a.agent_version,
        public_key_id=a.public_key_id,
        status=a.status,
        decision_classes=a.decision_classes,
        channels=a.channels,
        metadata=a.agent_metadata,
        version=a.version,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/v1/agents", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
def create_agent(req: Request, body: AgentCreate):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            a = register_agent(
                session=session,
                agent_id=body.agent_id,
                agent_class=body.agent_class,
                agent_version=body.agent_version,
                public_key_id=body.public_key_id,
                status=body.status,
                decision_classes=body.decision_classes,
                channels=[c.model_dump() for c in body.channels],
                metadata=body.metadata,
                actor=actor,
                trace_id=trace_id,
            )
            return _to_out(a)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))


@router.get("/v1/agents", response_model=List[AgentOut])
def list_agents_ep(status: Optional[str] = None, agent_class: Optional[str] = None, channel_id: Optional[str] = None):
    from .app import get_session
    with get_session() as session:
        agents = list_agents(session=session, status=status, agent_class=agent_class, channel_id=channel_id)
        return [_to_out(a) for a in agents]


@router.get("/v1/agents/{agent_id}", response_model=AgentOut)
def get_agent_ep(agent_id: str):
    from .app import get_session
    with get_session() as session:
        try:
            return _to_out(get_agent(session=session, agent_id=agent_id))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="agent_not_found")


@router.put("/v1/agents/{agent_id}", response_model=AgentOut)
def update_agent_ep(req: Request, agent_id: str, body: AgentUpdate, if_match: int = Header(..., alias="If-Match")):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            a = update_agent(
                session=session,
                agent_id=agent_id,
                if_match_version=if_match,
                agent_version=body.agent_version,
                public_key_id=body.public_key_id,
                decision_classes=body.decision_classes,
                channels=[c.model_dump() for c in body.channels],
                metadata=body.metadata,
                actor=actor,
                trace_id=trace_id,
            )
            return _to_out(a)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="agent_not_found")


@router.post("/v1/agents/{agent_id}/status", response_model=AgentOut)
def change_status_ep(req: Request, agent_id: str, body: AgentStatusChange, if_match: int = Header(..., alias="If-Match")):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            a = change_status(
                session=session,
                agent_id=agent_id,
                if_match_version=if_match,
                status=body.status,
                reason=body.reason,
                actor=actor,
                trace_id=trace_id,
            )
            return _to_out(a)
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="agent_not_found")


@router.post("/v1/agents/{agent_id}/revoke", response_model=AgentOut)
def revoke_agent_ep(req: Request, agent_id: str, if_match: int = Header(..., alias="If-Match")):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            a = revoke_agent(
                session=session,
                agent_id=agent_id,
                if_match_version=if_match,
                actor=actor,
                trace_id=trace_id,
            )
            return _to_out(a)
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="agent_not_found")


@router.get("/v1/agents/{agent_id}/effective-allowlist", response_model=EffectiveAllowlist)
def effective_allowlist_ep(agent_id: str):
    from .app import get_session
    with get_session() as session:
        try:
            a = get_agent(session=session, agent_id=agent_id)
            return EffectiveAllowlist(
                agent_id=a.agent_id,
                status=a.status,
                version=a.version,
                decision_classes=a.decision_classes,
                channels=a.channels,
            )
        except NotFoundError:
            raise HTTPException(status_code=404, detail="agent_not_found")
