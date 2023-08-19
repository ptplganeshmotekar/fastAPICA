connection_string = 'DefaultEndpointsProtocol=https;AccountName=pwccontractanalyzer1;AccountKey=p30YV+MnDhEv0iXP6mKXfIkSyOWusm9UmJ83BEH0cMAjM2FLc14ruCN+YTAk95scCBPr/TNFDx00+AStJyCUYQ==;EndpointSuffix=core.windows.net'
azureShareName = "pwccentral"
sasKey = "?sv=2020-08-04&ss=bfqt&srt=s&sp=rwdlacupitfx&se=2050-03-11T14:50:08Z&st=2022-03-11T06:50:08Z&spr=https,http&sig=qEwKWuNP6SWlcklDVSriKi%2BXXsYDiZ2QBMxrZfJKulY%3D"
azureMonitorkey="InstrumentationKey=d1aa4fd9-aa6e-4788-a587-f8b630148a18;IngestionEndpoint=https://southindia-0.in.applicationinsights.azure.com/;LiveEndpoint=https://southindia.livediagnostics.monitor.azure.com/"
userEmailId = ""
nodeAPIURL = "https://ipzvcqbnadwa003.azurewebsites.net/metadata/notifyTrainModel" #"http://localhost:3000/api/data"
spacyCharLimit = 980000 #14999 


# from pyexpat import model
# from fastapi import Depends, status, HTTPException
# from sqlalchemy.orm import Session
# import sqlalchemy
# from core import database, models
# from core.database import Base, engine

# # // Create database session when request 
# Base.metadata.create_all(engine)

# def getUserDetails(userId):
#     try:
#         # Create the database
#         session = Session(bind=engine, expire_on_commit=False)
#         user = session.query(models.User).filter(models.User.id == userId).first()
#         session.close()
#         if not user:
#             return "Error", "Invalid userId"
#         return "Success", user
#     except Exception as ex:
#         print(f"{ex}")
#         return "Error", f"{ex}"

# def getStatusDetails(value):
#     try:
#         session = Session(bind=engine, expire_on_commit=False)
#         statusDetails = session.query(models.TrainingStatus).filter(models.TrainingStatus.value== value).first()
#         session.close()
#         if not statusDetails:
#             return "Error", "Invalid status values"
#         return "Success", statusDetails
#     except Exception as ex:
#         print(f"{ex}")
#         return "Error", f"{ex}"                
            
# def getContractFieldMapping(contractId):
#     try:
#         session = Session(bind=engine, expire_on_commit=False)
#         contractcount = session.query(models.Contract_FieldMapping).filter(models.Contract_FieldMapping.contract_id == contractId).count()
#         session.close()
#         if not contractcount:
#             return "Error", "Invalid contract Id"
#         return "Success", contractcount
#     except sqlalchemy.exc.OperationalError:  # may need more exceptions here (or trap all)
#         session = Session(bind=engine, expire_on_commit=False)
#         contractcount = session.query(models.Contract_FieldMapping).filter(models.Contract_FieldMapping.contract_id == contractId).count()
#         session.close()
#         return "Success", contractcount
#     except Exception as ex:
#         print(f"{ex}")
#         return "Error", f"{ex}" 
    
# def AppDBLogs(ContractId, ModelName, LogType, LogMessage, LoginUser):
#     try:
#         from sqlalchemy.sql.expression import insert
#         from datetime import datetime

#         db = Session(bind=engine, expire_on_commit=False)
#         stmt = (
#         insert(models.NLPAppLogs).values(contractID=ContractId, modelName=ModelName, Logtype=LogType, Logmessage= LogMessage, Logginuser= LoginUser, ModifiedbyID=LoginUser,
#         CreatedByID=LoginUser, Logdatetime= datetime.now(), CreatedAt= datetime.now(), UpdatedAt= datetime.now()))
#         db.execute(stmt)
#         db.commit()
#         db.close()
#         return "Success", LogMessage
#     except sqlalchemy.exc.OperationalError:  # may need more exceptions here (or trap all)
#         db = Session(bind=engine, expire_on_commit=False)
#         stmt = (
#         insert(models.NLPAppLogs).values(contractID=ContractId, modelName=ModelName, Logtype=LogType, Logmessage= LogMessage, Logginuser= LoginUser, ModifiedbyID=LoginUser,
#         CreatedByID=LoginUser, Logdatetime= datetime.now(), CreatedAt= datetime.now(), UpdatedAt= datetime.now()))
#         db.execute(stmt)
#         db.commit()
#         db.close()
#         return "Success", LogMessage
#     except Exception as ex:
#         print("db log error")
#         print(f"{ex}")
#     return "Error", f"error occured" 

# def getContractFilesCount(contractId):
#     try:
#         # Create the database
#         from sqlalchemy import or_, and_
#         session = Session(bind=engine, expire_on_commit=False)
#         # contractcount = session.query(models.files).join(models.Contrct_TrainingFiles)filter(models.Contract_FieldMapping.contract_id == contractId and_ models.files.isNlpTrained==1).count()
#         filesCount = session.query(models.files).join(models.Contract_TrainingFiles,
#                     and_(models.files.id == models.Contract_TrainingFiles.file_id, 
#                     models.files.isNlpTrained ==1, models.Contract_TrainingFiles.contract_id == contractId)
#         ).count()

#         session.close()
#         print('filesCount', filesCount)
#         if not filesCount:
#             return "Error", filesCount
#         return "Success", filesCount
#     except Exception as ex:
#         print(f"{ex}")
#         return "Error", f"{ex}"

  