from datetime import datetime
from tkinter.tix import COLUMN
from numpy import integer
from sqlalchemy import NVARCHAR, Column, Integer, String, Text
from core.database import Base
from sqlalchemy.types import Date

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