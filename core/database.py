from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
from config import AppAzureExtractionDBLogs


try:
        
    server = 'contract-analyzer-server.database.windows.net'
    database = 'centraldb_Copy'
    username = 'c_admin'
    password = 'sPPBSx7hKU5QDfKc'   
    driver= '{ODBC Driver 18 for SQL Server}' 
    #'{ODBC Driver 13 for SQL Server}'

    params = urllib.parse.quote_plus(
        'Driver=%s;' % driver +
        'Server=tcp:%s,1433;' % server +
        'Database=%s;' % database +
        'Uid=%s;' % username +
        'Pwd={%s};' % password +
        'Encrypt=yes;' +
        'TrustServerCertificate=no;' +
        'Connection Timeout=30;')

    conn_str = 'mssql+pyodbc:///?odbc_connect=' + params
    engine = create_engine(conn_str)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
except Exception as ex:
    print(f"{ex}")
    AppAzureExtractionDBLogs(ex)
  



