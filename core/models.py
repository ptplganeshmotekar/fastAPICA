# from datetime import datetime
# from tkinter.tix import COLUMN
# from numpy import integer
from sqlalchemy import NVARCHAR, Column, Integer, String, Text
from core.database import Base
from sqlalchemy.types import Date

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

    class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True, index=True)
        email = Column(String)
        username = Column(String)
        password = Column(String)
        # status = Column(String)
        # isFirstLogin = Column(bool)
        # user_wrong_password_count = Column(int)
        # mobile_number = Column(String)
        # name = Column(String)
        # isExclusive = Column(bool)
    
    class files(Base):
        __tablename__ = 'Files'

        id= Column(Integer, primary_key=True, index=True)
        # Name= Column(String)
        # FilePath= Column(String)
        # CreatedByID= Column(String)
        # ModifiedByID= Column(String)
        # CreatedAt= Column(Date)
        UpdatedAt= Column(Date)
        # type= Column(String)
        # format= Column(String)
        # size= Column(String)
        # uploadID= Column(String)
        # bucketID= Column(String)
        # isTrained= Column(String)
        # isTrainingFile= Column(String)
        # ocrStatusID= Column(String)
        trainingStatusID=Column(String)
        # approvalStatusID=Column(String)
        # searchableFileId=Column(String)
        # isSearchable=Column(String)
        # folderName=Column(String)
        # ocrText=Column(String)
        trainingFieldsPercentage= Column(String)
        #identifiedIdentities= Column(String)
        isNlpTrained= Column(Integer)
        nlpTrainingError= Column(String)
        # isAbstracted= Column(String)
        # isTable= Column(String)


    class ContractFilesTrainingData(Base):
        __tablename__ = 'Contract_Files_TrainedData'

        id = Column(String, primary_key=True, index=True)
        value = Column(NVARCHAR)
        contractID = Column(String)
        fileID = Column(String)
        modelName = Column(String)
        CreatedByID = Column(String)
        ModifiedByID = Column(String)
        CreatedAt= Column(Date)
        UpdatedAt= Column(Date)
        missingIdentities = Column(NVARCHAR)
        identifiedIdentities = Column(NVARCHAR)


    class TrainingStatus(Base):
        __tablename__ = 'Training_Status'

        id = Column(Integer, primary_key=True, index=True)
        value = Column(String)

    class contracts(Base):
        __tablename__ = 'Contracts'
        
        id = Column(Integer, primary_key=True, index=True)
        trainingFieldsPercentage = Column(String)
        nlpTrainingStartTime = Column(Date)
        nlpTrainingEndTime = Column(Date)
        trainedByID = Column(String)
        highestFieldsTrainedCount = Column(Integer)
        project_id = Column(String)
        displayModelName = Column(String)

    class fieldMappings(Base):
        __tablename__ = 'FieldMappings'

        id =Column(Integer, primary_key=True, index=True)
        training_model_name =Column(String)
        is_trained = Column(Integer)
        trainedByID = Column(String)
        trainedOn = Column(Date)

    class Contract_FieldMapping(Base):
        __tablename__ = 'Contract_FieldMapping'

        id =Column(Integer, primary_key=True, index=True)
        contract_id = Column(String)
        field_mapping_id = Column(String)
        CreatedByID = Column(String)
        ModifiedByID = Column(String)
        CreatedAt= Column(Date)
        UpdatedAt= Column(Date)

    class Contract_TrainingFiles(Base):
        __tablename__ = 'Contract_TrainingFiles'

        id =Column(Integer, primary_key=True, index=True)
        contract_id = Column(String)
        file_id = Column(String)
        CreatedByID = Column(String)
        ModifiedByID = Column(String)
        CreatedAt= Column(Date)
        UpdatedAt= Column(Date)

    class NLPAppLogs(Base):
        __tablename__ = 'NLPAppLogs'

        id =Column(Integer, primary_key=True, index=True)
        contractID = Column(String)
        modelName = Column(String)
        Logtype = Column(String)
        Logmessage = Column(Text)
        Logginuser = Column(String)
        ModifiedbyID = Column(String)
        CreatedByID = Column(String)
        Logdatetime = Column(Date)
        CreatedAt = Column(Date)
        UpdatedAt = Column(Date)

except Exception as ex:
    AppAzureExtractionDBLogs(ex)
    print(ex)


