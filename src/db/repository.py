import logging
from sqlalchemy import func, select, text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Video

logger = logging.getLogger(__name__)


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def execute_sql_query(self, sql_query: str) -> int | str:
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        result: Result = await self.session.execute(text(sql_query))
        rows = result.fetchall()

        if len(rows) == 1 and len(rows[0]) == 1:
            value = rows[0][0]
            return int(value) if value is not None else 0

        formatted: list[str] = []
        for i, row in enumerate(rows, 1):
            if len(row) == 2:
                formatted.append(f"{i}. {row[1]}")
            else:
                formatted.append(str(row[0]))

        return "\n".join(formatted)

    async def count_videos(self) -> int:
        result: Result = await self.session.execute(
            select(func.count()).select_from(Video)
        )
        count: int = result.scalar_one()
        return count
