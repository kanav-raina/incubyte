"""Pagination primitives shared across endpoints."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageParams:
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
