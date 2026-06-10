"""Shared FastAPI dependencies."""

from fastapi import Query

from app.core.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, PageParams


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)
