# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Header, HTTPException, Request, status

from .schemas import PolicyCreate, PolicyOut, PolicyPublish, PolicyRollback, PublicationOut, EffectivePolicy
from .service import (
    create_policy, list_policies, get_policy_version, publish_policy, rollback_policy, effective_policy,
    ConflictError, NotFoundError
)
from .validation import ValidationError


router = APIRouter()


def _actor_from(req: Request) -> Optional[str]:
    return req.headers.get("x-actor")


def _trace_from(req: Request) -> Optional[str]:
    return req.headers.get("x-trace-id")


def _to_out(p) -> PolicyOut:
    return PolicyOut(
        policy_id=p.policy_id,
        version=p.version,
        status=p.status.value,
        scope=p.scope,
        constraints=p.constraints,
        metadata=p.metadata,
        created_at=p.created_at,
    )


def _pub_out(pub) -> PublicationOut:
    return PublicationOut(
        policy_id=pub.policy_id,
        active_version=pub.active_version,
        scope=pub.scope,
        published_at=pub.published_at,
        note=pub.note,
    )


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/v1/policies", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy_ep(req: Request, body: PolicyCreate):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            p = create_policy(
                session=session,
                policy_id=body.policy_id,
                version=body.version,
                status=body.status,
                scope=body.scope.model_dump(),
                constraints=body.constraints.model_dump(),
                metadata=body.metadata,
                actor=actor,
                trace_id=trace_id,
            )
            return _to_out(p)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))


@router.get("/v1/policies", response_model=List[PolicyOut])
def list_policies_ep(status: Optional[str] = None, policy_id: Optional[str] = None):
    from .app import get_session
    with get_session() as session:
        return [_to_out(p) for p in list_policies(session=session, status=status, policy_id=policy_id)]


@router.get("/v1/policies/{policy_id}/versions/{version}", response_model=PolicyOut)
def get_policy_ep(policy_id: str, version: int):
    from .app import get_session
    with get_session() as session:
        try:
            return _to_out(get_policy_version(session=session, policy_id=policy_id, version=version))
        except NotFoundError:
            raise HTTPException(status_code=404, detail="policy_not_found")


@router.post("/v1/policies/{policy_id}/publish", response_model=PublicationOut)
def publish_policy_ep(req: Request, policy_id: str, body: PolicyPublish, if_match: int = Header(..., alias="If-Match")):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            pub = publish_policy(
                session=session,
                policy_id=policy_id,
                if_match_version=if_match,
                scope=body.scope.model_dump(),
                reason=body.reason,
                actor=actor,
                trace_id=trace_id,
            )
            return _pub_out(pub)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=409, detail=str(e))


@router.post("/v1/policies/{policy_id}/rollback", response_model=PublicationOut)
def rollback_policy_ep(req: Request, policy_id: str, body: PolicyRollback):
    from .app import get_session
    actor = _actor_from(req)
    trace_id = _trace_from(req)
    with get_session() as session:
        try:
            pub = rollback_policy(
                session=session,
                policy_id=policy_id,
                scope=body.scope.model_dump(),
                reason=body.reason,
                actor=actor,
                trace_id=trace_id,
            )
            return _pub_out(pub)
        except NotFoundError:
            raise HTTPException(status_code=404, detail="no_previous_version")


@router.get("/v1/effective-policy", response_model=EffectivePolicy)
def effective_policy_ep(agent_id: str, agent_class: str, channel_id: str, topic: str):
    from .app import get_session
    with get_session() as session:
        try:
            ep = effective_policy(
                session=session,
                agent_id=agent_id,
                agent_class=agent_class,
                channel_id=channel_id,
                topic=topic,
            )
            return EffectivePolicy(**ep)
        except NotFoundError:
            raise HTTPException(status_code=404, detail="effective_policy_not_found")
