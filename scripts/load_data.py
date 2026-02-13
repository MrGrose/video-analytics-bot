import asyncio
import json
import sys
import os
import logging

from pathlib import Path
from dateutil import parser

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.core.config import settings
from src.db.models import Video, VideoSnapshot, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_data_sqlalchemy():
    engine = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы созданы")

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    json_paths = []
    if Path("/app/data").exists():
        json_paths.extend(Path("/app/data").glob("*.json"))
    json_paths.extend(Path(".").glob("**/videos.json"))

    if not json_paths:
        logger.error("JSON файл не найден!")
        return False

    json_path = json_paths[0]
    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    if isinstance(raw_data, dict) and "videos" in raw_data:
        videos_data = raw_data["videos"]
    elif isinstance(raw_data, list):
        videos_data = raw_data
    else:
        videos_data = [raw_data] if raw_data else []

    async with async_session() as session:
        video_count = 0
        snapshot_count = 0

        for i, video_data in enumerate(videos_data):
            try:
                video = Video(
                    id=video_data["id"],
                    creator_id=str(video_data["creator_id"]),
                    video_created_at=parser.parse(video_data["video_created_at"]),
                    views_count=video_data.get("views_count", 0),
                    likes_count=video_data.get("likes_count", 0),
                    comments_count=video_data.get("comments_count", 0),
                    reports_count=video_data.get("reports_count", 0),
                    created_at=parser.parse(video_data["created_at"]),
                    updated_at=parser.parse(video_data["updated_at"]),
                )
                session.add(video)
                video_count += 1

                for snapshot_data in video_data.get("snapshots", []):
                    snapshot = VideoSnapshot(
                        id=snapshot_data["id"],
                        video_id=snapshot_data["video_id"],
                        views_count=snapshot_data.get("views_count", 0),
                        likes_count=snapshot_data.get("likes_count", 0),
                        comments_count=snapshot_data.get("comments_count", 0),
                        reports_count=snapshot_data.get("reports_count", 0),
                        delta_views_count=snapshot_data.get("delta_views_count", 0),
                        delta_likes_count=snapshot_data.get("delta_likes_count", 0),
                        delta_comments_count=snapshot_data.get(
                            "delta_comments_count", 0
                        ),
                        delta_reports_count=snapshot_data.get("delta_reports_count", 0),
                        created_at=parser.parse(snapshot_data["created_at"]),
                        updated_at=parser.parse(snapshot_data["updated_at"]),
                    )
                    session.add(snapshot)
                    snapshot_count += 1

                if (i + 1) % 100 == 0:
                    await session.commit()
                    logger.info(
                        f"Прогресс: {i + 1}/{len(videos_data)} видео, {snapshot_count} снапшотов"
                    )

            except Exception as e:
                logger.error(f"Ошибка в видео {video_data.get('id', 'unknown')}: {e}")
                await session.rollback()
                continue

        await session.commit()
        logger.info(f"Загружено: {video_count} видео, {snapshot_count} снапшотов")

    await engine.dispose()
    return True


async def main():
    try:
        success = await load_data_sqlalchemy()
        if success:
            logger.info("Все операции завершены успешно!")
        else:
            logger.error("Загрузка данных не удалась!")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
