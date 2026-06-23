"""
Database connection helper for AI College Enquiry Chatbot.
Provides a simple connection/cursor wrapper around mysql-connector-python.
"""

import mysql.connector
from mysql.connector import pooling, Error
from config import Config


class Database:
    """Lightweight MySQL connection pool wrapper."""

    _pool = None

    @classmethod
    def init_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="chatbot_pool",
                    pool_size=5,
                    **Config.DB_CONFIG
                )
            except Error as e:
                print(f"[DB ERROR] Could not create connection pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch=False, fetch_one=False, commit=False):
        """
        Execute a query and optionally fetch results or commit.
        Returns: list/dict of rows if fetch is requested, else last row id (for inserts), else True.
        """
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        result = None
        try:
            cursor.execute(query, params or ())
            if fetch_one:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            if commit:
                conn.commit()
                result = cursor.lastrowid
        except Error as e:
            conn.rollback()
            print(f"[DB ERROR] {e}")
            raise
        finally:
            cursor.close()
            conn.close()
        return result
