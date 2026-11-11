"""DatasetStore interface: where uploaded user data lives."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class DatasetMeta:
    id: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime
    sha256: str


@runtime_checkable
class DatasetStore(Protocol):
    """Blob-style storage for datasets (local disk, S3, GCS, ...).

    Reads and writes are streamed so large files never need to fit in memory.
    """

    async def put(
        self,
        filename: str,
        content_type: str,
        data: AsyncIterator[bytes],
    ) -> DatasetMeta:
        ...

    async def get_meta(self, dataset_id: str) -> DatasetMeta | None:
        ...

    def open(self, dataset_id: str) -> AsyncIterator[bytes]:
        """Stream a dataset's bytes."""
        ...

    async def delete(self, dataset_id: str) -> None:
        ...
