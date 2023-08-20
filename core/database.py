from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
connection_string = 'DefaultEndpointsProtocol=https;AccountName=pwccontractanalyzer1;AccountKey=p30YV+MnDhEv0iXP6mKXfIkSyOWusm9UmJ83BEH0cMAjM2FLc14ruCN+YTAk95scCBPr/TNFDx00+AStJyCUYQ==;EndpointSuffix=core.windows.net'
azureShareName = "pwccentral"

def AppAzureExtractionDBLogs(logMessages: str):
    try:
        from azure.storage.fileshare import ShareClient, ShareFileClient, ShareDirectoryClient
        from datetime import datetime
        import os, shutil, re
        from azure.core.exceptions import ResourceExistsError
        import ssl

        dt = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        
        # from sqlalchemy import select
        # db = Session(bind=engine, expire_on_commit=False)
        # model_name = db.query(models.contracts).filter(models.contracts.id==contractID).first()
        # print("modelname- ", model_name.displayModelName)        
        # db.close()
        model_name = "databaselogs"
        my_modelname = re.sub('[^a-zA-Z0-9 \n\.]', '', model_name)
        modelname = my_modelname.replace(" ", "_").lower()  
        filename = dt

        with open(filename, mode='w') as log_file:
            content = f"{logMessages}"
            log_file.write('\n')
            log_file.write(content) 

            current_directory = os.getcwd()
            rm_dirPath = os.path.join(current_directory)
            share = ShareClient.from_connection_string(connection_string, share_name=azureShareName)
            filesdir = []
            filesdir.append(os.path.join(filename))
            
            try:
                NLPModel = share.get_directory_client("nlp-database")
                NLPModel.create_directory()
            except ResourceExistsError:
                pass
            except ssl.CertificateError:
                pass
            try:
                NLPModel_ProjectName = share.get_directory_client("nlp-database/"+modelname)
                NLPModel_ProjectName.create_directory()
            except ResourceExistsError:
                pass
            except ssl.CertificateError:
                pass 
            properties = share.get_share_properties()
            
            file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-database/"+modelname,file_path=filename)
            
            filepath = current_directory +"/"+filename

            with open(filepath, "rb") as source_file:
                file.upload_file(source_file)            
            print("uploaded")  

    except Exception as ex:
        print(f"Azure log file upload error -- {ex}")
        return "Error", ex



try:
        
    server = 'contract-analyzer-server.database.windows.net'
    database = 'centraldb_Copy'
    username = 'c_admin'
    password = 'sPPBSx7hKU5QDfKc'   
    driver= '{ODBC Driver 17 for SQL Server}' 
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
  



