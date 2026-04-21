# glbData.py

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from threading import Lock
import logging
import time
from typing import Dict, List, Any, Optional

# ------------------------------------------------------------------
# Logging configuration
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [glbData] %(levelname)s: %(message)s"
)
logger = logging.getLogger("glbData")


class GlbData:
    """
    Production replacement of VB glbData.vb

    Responsibilities:
    - Single DB entry point
    - SQLAlchemy engine & pooling
    - VB-compatible API surface
    - In-memory table cache (glbTableDic)
    - Retry & logging
    """

    def __init__(self):
        self._engine = None
        self._lock = Lock()

        # Application state
        self.glbUserLoginCod: int = 0

        self.glbStr: Dict[str, str] = {}
        self.glbInt: Dict[str, int] = {}
        self.glbDec: Dict[str, float] = {}
        self.glbBol: Dict[str, bool] = {}
        self.glbClr: Dict[str, Any] = {}

        # In-memory tables
        self.glbTableDic: Dict[str, List[Dict[str, Any]]] = {}
        self.glbTableDic_InRam: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Engine initialization
    # ------------------------------------------------------------------
    def set_connection_string(self, conn_str: str):
        """
        Initialize SQLAlchemy engine. Call once at startup.
        """
        with self._lock:
            if self._engine is not None:
                logger.info("DB engine already initialized")
                return

            logger.info("Initializing SQLAlchemy engine")
            self._engine = create_engine(
                conn_str,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_pre_ping=True,
                fast_executemany=True,
                future=True
            )

    # ------------------------------------------------------------------
    # Internal retry helper
    # ------------------------------------------------------------------
    def _run_with_retry(self, fn, retries: int = 3, delay: float = 0.5):
        for i in range(retries):
            try:
                return fn()
            except OperationalError as ex:
                logger.warning(
                    "DB operation failed (attempt %s/%s): %s", i + 1, retries, ex
                )
                if i == retries - 1:
                    raise
                time.sleep(delay * (i + 1))

    # ------------------------------------------------------------------
    # VB-compatible API
    # ------------------------------------------------------------------
    def pfExecSql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute INSERT / UPDATE / DELETE. Returns affected rows.
        """
        if not sql or not sql.strip():
            return 0

        logger.info("pfExecSql: %s", sql)

        def run():
            with self._engine.begin() as conn:
                result = conn.execute(text(sql), params or {})
                return result.rowcount or 0

        return self._run_with_retry(run)

    def select_scalar(self, sql: str, params: Optional[Dict[str, Any]] = None):
        """
        Replacement of ExecuteScalar.
        """
        logger.info("select_scalar: %s", sql)

        def run():
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                row = result.fetchone()
                return row[0] if row else None

        return self._run_with_retry(run)

    def pfLoadTableWithReader(
        self,
        table_name: str,
        sql: str,
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Loads data into glbTableDic[table_name].
        VB-style: False=OK, True=ERROR
        """
        logger.info("Loading table %s", table_name)

        def run():
            with self._engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                cols = result.keys()
                rows = [dict(zip(cols, row)) for row in result.fetchall()]
                self.glbTableDic[table_name] = rows
                return False

        try:
            return self._run_with_retry(run)
        except SQLAlchemyError as ex:
            logger.error("LoadTable ERROR %s: %s", table_name, ex)
            return True

    def glbTableDic_Reload(self, table_name: str, select_sql: Optional[str] = None) -> bool:
        if not select_sql:
            select_sql = f"SELECT * FROM {table_name}"
        return self.pfLoadTableWithReader(table_name, select_sql)

    # ------------------------------------------------------------------
    # In-RAM tables
    # ------------------------------------------------------------------
    def mark_table_in_ram(self, table_name: str, select_sql: str):
        self.glbTableDic_InRam[table_name] = select_sql

    def refresh_in_ram_tables(self):
        for table, sql in self.glbTableDic_InRam.items():
            self.pfLoadTableWithReader(table, sql)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def get_table(self, table_name: str) -> List[Dict[str, Any]]:
        return self.glbTableDic.get(table_name, [])

    def table_loaded(self, table_name: str) -> bool:
        return table_name in self.glbTableDic

    # ------------------------------------------------------------------
    # 11-step initialization
    # ------------------------------------------------------------------
    def DoTableDicIn11Steps_Init(self):
        logger.info("Starting DoTableDicIn11Steps_Init")

        tables = [
            "SysFrm",
            "SysFrmGrd",
            "SysFrmGrdCol",
            "SysFrmGrdBtn",
            "SysBtnMain",
            "SysFrmGrdColUser",
        ]

        for t in tables:
            self.glbTableDic_Reload(t)

        self.refresh_in_ram_tables()

        logger.info("DoTableDicIn11Steps_Init finished")

    # ------------------------------------------------------------------
    # Diagnostics / shutdown
    # ------------------------------------------------------------------
    def health_check(self) -> bool:
        try:
            self.select_scalar("SELECT 1")
            return True
        except Exception:
            return False

    def shutdown(self):
        if self._engine:
            self._engine.dispose()
            logger.info("DB engine disposed")
