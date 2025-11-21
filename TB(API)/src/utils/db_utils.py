# db_utils.py
import os
from sqlalchemy import MetaData, Table, select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus

from src.commons.config_manager import cfg
from src.constants.constants import Constants
from src.constants.global_data import GlobalData
from src.exceptions.db_exception import DBException
from src.utils.encryption_utils import decrypt
from src.utils.logger import Logger

logger = Logger.get_logger()
Base = declarative_base()


class AsyncDBConnect:
    """
    Async DB connection and operations for FastAPI.
    Supports reflection of multiple tables and concurrent access.
    """

    def __init__(self):
        try:
            self.__db_param = cfg.get_env_config(Constants.DATABASE)

            user = decrypt(cfg.get_value_config(self.__db_param, Constants.DB_USER)).strip()
            password = decrypt(cfg.get_value_config(self.__db_param, Constants.DB_PASSWORD))
            password_encoded = quote_plus(password)
            host = decrypt(cfg.get_value_config(self.__db_param, Constants.DB_HOST))
            db_name = decrypt(cfg.get_value_config(self.__db_param, Constants.DATABASE_NAME))
            port = int(decrypt(cfg.get_value_config(self.__db_param, Constants.DB_PORT)))
            self.__pool_recycle = int(decrypt(cfg.get_value_config(self.__db_param, Constants.POOL_RECYCLE)))

            self.database_url = f"mysql+aiomysql://{user}:{password_encoded}@{host}:{port}/{db_name}"

            logger.info(f"Initializing DB engine: user={user}, host={host}, port={port}, db={db_name}")

            self.engine = create_async_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=self.__pool_recycle,
                echo=False,
            )

            self.AsyncSessionLocal = sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )

            self.meta_data = MetaData()
            self.tables = {}
            self.models = {}

        except Exception as e:
            logger.error(f"DB Initialization Failed: {e}")
            raise

    # -------------------------------------------------------------------------
    async def set_up_table(self, table_name: str):
        """Reflect and cache table structure."""
        try:
            if table_name in self.models:
                return self.models[table_name]

            async with self.engine.begin() as conn:
                def reflect(sync_conn):
                    return Table(table_name, self.meta_data, autoload_with=sync_conn)

                table_obj = await conn.run_sync(reflect)

            self.tables[table_name] = table_obj
            model = type(table_name.capitalize(), (Base,), {"__table__": table_obj})
            self.models[table_name] = model

            logger.info(f"Loaded table: {table_name}")
            return model

        except Exception as e:
            logger.error(f"Error reflecting table '{table_name}': {e}")
            raise DBException(f"Table reflection failed for {table_name}")

    # -------------------------------------------------------------------------
    async def get_data(self, table_name: str, **filters):
        """Retrieve data based on filters or return all."""
        try:
            model = await self.set_up_table(table_name)

            async with self.AsyncSessionLocal() as session:
                query = select(model)
                if filters:
                    query = query.filter_by(**filters)

                result = await session.execute(query)
                rows = result.scalars().all()

                data = [
                    {col.name: getattr(row, col.name) for col in row.__table__.columns}
                    for row in rows
                ]

                if filters:
                    if not data:  
                        return None
                    return data[0]



        except Exception as e:
            logger.error(f"DB Get Data Error ({table_name}): Filters={filters}, Error={e}")
            GlobalData.STATUS_CODE = Constants.DB_RETRIEVAL_ERROR
            raise DBException(f"Database retrieval error: {e}")

    # -------------------------------------------------------------------------
    async def insert_data(self, table_name: str, **values):
        try:
            model = await self.set_up_table(table_name)

            async with self.AsyncSessionLocal() as session:
                async with session.begin():
                    obj = model(**values)
                    session.add(obj)

            logger.info(f"Inserted into {table_name}: {values}")

        except Exception as e:
            logger.error(f"DB Insert Error ({table_name}): {values}, Error={e}")
            raise DBException(f"Database insertion error: {e}")

    # -------------------------------------------------------------------------
    async def update_data(self, table_name: str, filter_field: str, filter_value, **values):
        try:
            model = await self.set_up_table(table_name)

            async with self.AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(model)
                        .where(getattr(model, filter_field) == filter_value)
                        .values(**values)
                    )
                    await session.execute(stmt)

            logger.info(f"Updated {table_name} where {filter_field}={filter_value}: {values}")

        except Exception as e:
            logger.error(f"DB Update Error ({table_name}): {values}, Error={e}")
            raise DBException(f"Database update error: {e}")
    # -------------------------------------------------------------------------
    async def delete_data(self, table_name: str, **filters):
        """Delete rows matching filter conditions."""
        try:
            model = await self.set_up_table(table_name)

            async with self.AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = model.__table__.delete()

                    if filters:
                        for field, value in filters.items():
                            stmt = stmt.where(getattr(model, field) == value)

                    await session.execute(stmt)

            logger.info(f"Deleted from {table_name}: Filters={filters}")

        except Exception as e:
            logger.error(f"DB Delete Error ({table_name}): Filters={filters}, Error={e}")
            raise DBException(f"Database deletion error: {e}")
        
    # -------------------------------------------------------------------------
    async def get_all_user_data(self, exclude_email: str = None):
        try:
            model = await self.set_up_table(Constants.USER_TABLE)

            async with self.AsyncSessionLocal() as session:
                query = select(model.email, model.first_name, model.last_name)

                if exclude_email:
                    query = query.where(model.email != exclude_email)

                rows = (await session.execute(query)).all()

            return {
                email: {"first_name": fname, "last_name": lname}
                for email, fname, lname in rows
            }

        except Exception as e:
            logger.error(f"DB Error in get_all_user_data: {e}")
            raise DBException(f"User fetch failed: {e}")
        
    # -------------------------------------------------------------------------
    async def get_user_data(self, current_user_email: str):
        try:
            users = await self.set_up_table(Constants.USER_TABLE)
            conv = await self.set_up_table(Constants.CONVERSATION_TABLE)
            conv_part = await self.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

            async with self.AsyncSessionLocal() as session:

                uid_row = await session.execute(
                    select(users.uid).where(users.email == current_user_email)
                )
                current_uid = uid_row.scalar_one_or_none()

                if not current_uid:
                    logger.warning(f"User not found: {current_user_email}")
                    return {}

                direct_conv_ids = (
                    await session.execute(
                        select(conv.conversation_id)
                        .join(conv_part, conv.conversation_id == conv_part.conversation_id)
                        .where(conv.conversation_type == "private")
                        .where(conv_part.uid == current_uid)
                    )
                ).scalars().all()

                partners = set()
                if direct_conv_ids:
                    partners = set(
                        (await session.execute(
                            select(conv_part.uid)
                            .where(conv_part.conversation_id.in_(direct_conv_ids))
                            .where(conv_part.uid != current_uid)
                        )).scalars().all()
                    )

                query = select(users.email, users.first_name, users.last_name).where(users.uid != current_uid)
                if partners:
                    query = query.where(users.uid.notin_(partners))

                rows = (await session.execute(query)).all()

                return {email: {"first_name": fn, "last_name": ln} for email, fn, ln in rows}

        except Exception as e:
            logger.error(f"DB Error in get_user_data: {e}")
            raise DBException(f"User data retrieval failed: {e}")

db_connect = AsyncDBConnect()
    