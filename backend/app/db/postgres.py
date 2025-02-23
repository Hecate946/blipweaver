import asyncpg
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Initialize the connection pool and execute schema.sql"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
            await self.run_schema()  # Apply schema on startup

    async def disconnect(self):
        """Close the database pool"""
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        """Execute a query that modifies the database"""
        logger.info(f"Executing query: {query} | Params: {args}")
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows from the database"""
        logger.info(f"Fetching multiple rows: {query} | Params: {args}")
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row from the database"""
        logger.info(f"Fetching single row: {query} | Params: {args}")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
        
    async def fetchval(self, query: str, *args):
        """Fetch a single value from the database"""
        logger.info(f"Fetching single value: {query} | Params: {args}")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def run_schema(self):
        """Read and execute schema.sql file on startup"""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            logger.warning(f"Schema file not found: {schema_path}")
            return

        try:
            async with self.pool.acquire() as conn:
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                await conn.execute(schema_sql)
                logger.info("Database schema applied successfully.")
        except Exception as e:
            logger.error(f"Error applying schema: {e}")

db = Database()
