import asyncio
from datetime import date, datetime
from typing import Annotated

import typer

from config import (
    DEFAULT_CONCURRENCY,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE, DEFAULT_RETRIES, DEFAULT_LOG_LEVEL,
)
from src.database import create_tables

app = typer.Typer(help="Spimex ETL CLI")


def parse_date(value: str) -> date:
    """Преобразует строку в дату"""
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.command()
def run(
        start_date: Annotated[date, typer.Option(parser=parse_date)] = DEFAULT_START_DATE,
        end_date: Annotated[date, typer.Option(parser=parse_date)] = DEFAULT_END_DATE,
        concurrency: int = typer.Option(DEFAULT_CONCURRENCY, min=1),
        retries: int = typer.Option(DEFAULT_RETRIES, min=0),
        log_level: str = typer.Option(DEFAULT_LOG_LEVEL, case_sensitive=False),
):
    """Запуск ETL с ретраями"""

    async def runner():
        from src.logger_config import setup_logging
        setup_logging(level=log_level)
        from src.main import run_etl_async

        await create_tables()

        failed_files = await run_etl_async(
            concurrency=concurrency,
            start_date=start_date,
            end_date=end_date,
        )

        retry_count = retries

        while failed_files and retry_count > 0:
            typer.echo(
                f"Повтор {len(failed_files)} пропущенных файлов... "
                f"({retries - retry_count + 1}/{retries})"
            )

            failed_files = await run_etl_async(
                concurrency=max(DEFAULT_CONCURRENCY, concurrency - 2),
                start_date=start_date,
                end_date=end_date,
                files_to_process=failed_files,
            )

            retry_count -= 1

        if failed_files:
            typer.echo(f"Осталось не обработанных файлов: {len(failed_files)}")

    asyncio.run(runner())


@app.command("init-db")
def init_db():
    """Создать таблицы"""

    async def runner():
        await create_tables()

    asyncio.run(runner())


if __name__ == "__main__":
    app()
