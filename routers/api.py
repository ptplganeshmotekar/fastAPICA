
from select import select
from typing import Iterator, Union
import os, shutil, re
from numpy import double
import uuid
import subprocess
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from regex import P
from requests import session
from sqlalchemy import null
from core import models
from sqlalchemy.orm import Session
import spacy
from pathlib import Path
from azure.storage.fileshare import ShareClient, ShareFileClient, ShareDirectoryClient
from config import connection_string, azureShareName, getUserDetails, userEmailId, getStatusDetails , getContractFieldMapping, getContractFilesCount, nodeAPIURL, AppDBLogs, spacyCharLimit #,  azureMonitorkey
from azure.core.exceptions import ResourceExistsError
from tqdm import tqdm
from spacy.tokens import DocBin
from sklearn.model_selection import train_test_split
from fastapi import Request
from sqlalchemy.sql.expression import update
import json
from opencensus.ext.azure.log_exporter import AzureLogHandler
import ssl
from core.database import Base, engine
import gc

gc.enable()


router = APIRouter(tags=['NLP Learning'])
TRAIN_DATA = []
TRAINDATA_OriginalTuple = []
# nlp = spacy.load("en_core_web_sm")
# Base.metadata.create_all(engine)


# def UploadModeltoAzure(projectname:str, trainingType: str):        
#     filesdir = []
#     files = []
#     #ssl.CERT_OPTIONAL = 0
#     try:
#         current_directory = os.getcwd()
#         if trainingType == "Train":
#             current_directory = current_directory + "/uploadtrainmodels"
#             rm_dirPath = os.path.join(current_directory, projectname)
#             model_dirPath = rm_dirPath+"/output/model-best"
#             print("Train--", model_dirPath)
#         elif trainingType == "updateTrain":
#             current_directory = current_directory + "/nlp-models"
#             rm_dirPath = os.path.join(current_directory, projectname)
#             model_dirPath = rm_dirPath+"/output/model-best"
#             print("Re-Train--", model_dirPath)
#         filesdir = []
#         files = []
#         share = ShareClient.from_connection_string(connection_string, share_name=azureShareName)

#         for file in os.listdir(model_dirPath):
#             if file.endswith('.json')==True or file.endswith('.cfg')==True or file.startswith('tokenizer')==True:
#                 files.append(os.path.join(file))
#             else:
#                 filesdir.append(os.path.join(file))

#         #Create the share
#         #share.create_share()
        
#         try:
#             NLPModel = share.get_directory_client("nlp-models")
#             NLPModel.create_directory()
#         except ResourceExistsError:
#             pass
#         except ssl.CertificateError:
#             pass
#         try:
#             NLPModel_ProjectName = share.get_directory_client("nlp-models/"+projectname)
#             NLPModel_ProjectName.create_directory()
#         except ResourceExistsError:
#             pass
#         except ssl.CertificateError:
#             pass
            
       
#         for uploadfile in files:
#             properties = share.get_share_properties()
#             # [END get_share_properties]

#             file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-models/"+projectname,file_path=uploadfile)
#             # [END create_file_client]
#             filepath = model_dirPath +"/"+uploadfile
#             # Upload a files
#             with open(filepath, "rb") as source_file:
#                 file.upload_file(source_file)
#                 # print('uploaded file = ' + uploadfile)

#         for fileDirectories in filesdir:
#             for files in os.listdir(model_dirPath+"/"+fileDirectories):
#                 dirFiles= []
#                 dirFiles.append(os.path.join(files))
#                 try:
#                     NLPModel = share.get_directory_client("nlp-models/"+ projectname+"/"+ fileDirectories)
#                     NLPModel.create_directory()
#                     # print('directory folder created = ' + fileDirectories)
#                 except ResourceExistsError:
#                     pass
                
#                 if fileDirectories == 'lemmatizer':
#                     #print('l')
#                     if dirFiles == ['lookups']:
#                         subdirPath = files
#                         for subDirFiles in os.listdir(model_dirPath+"/"+fileDirectories+"/"+subdirPath):
#                             dirFileschild= []
#                             dirFileschild.append(os.path.join(subDirFiles))
#                             try:
#                                 NLPModel_ProjectNameSubDir = share.get_directory_client("nlp-models/"+projectname+"/"+fileDirectories+"/"+subdirPath)
#                                 NLPModel_ProjectNameSubDir.create_directory()
#                             except ResourceExistsError:
#                                 pass
                            
#                             for uploadfile in dirFileschild:
#                                 properties = share.get_share_properties()
#                                 file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-models/"+projectname+"/"+fileDirectories+"/"+subdirPath,file_path=uploadfile)
#                                 filepath = model_dirPath +"/"+fileDirectories+"/"+subdirPath+"/"+uploadfile
#                                 print(filepath)
#                                 with open(filepath, "rb") as source_file:
#                                     file.upload_file(source_file)
#                                     # print('lookup uploaded file = ' + uploadfile)
#                 else:
#                     #print('o')
#                     for uploadfile in dirFiles:
#                         properties = share.get_share_properties()
#                         # [END get_share_properties]
#                         file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-models/"+projectname+"/"+fileDirectories,file_path=uploadfile)
#                         # [END create_file_client]
#                         filepath = model_dirPath +"//"+fileDirectories+"//"+uploadfile
#                         # Upload a files
#                         with open(filepath, "rb") as source_file:
#                             file.upload_file(source_file)
#                             # print('uploaded file = ' + uploadfile)

            
#         if os.path.exists(rm_dirPath):
#             shutil.rmtree(rm_dirPath)
    
#     except Exception as azureEx:
#         print(f"Azure file upload error -- {azureEx}")
#         logMessage = {"ModelName- ":projectname, "LogType":"Error","UserEmail-":userEmailId, "Message-": azureEx ,"MethodName":"UploadModeltoAzure"}
#         return "Error",azureEx        

#     else:
#         return "Success", "File uploading completed"
 
def DumpTRAINDATA(data):
    try:
        print("test dump TRAIN_DATA ")
        TRAIN_DATA_Splited=[]
        FileName_Splited=[]
        fieldMappingIDList=[]

        userID = data["userID"]
        ModelName = data["modelName"]
        contractID = data["contractID"]
        trainingType = data["trainingType"]

        for training_data in data['trainingData']:
            infoDict={}
            infoDict["userID"]=userID
            infoDict["fileID"]=training_data["fileID"]
            infoDict["contractID"]=contractID#training_data["contractID"]
            
            infoDict["modelName"]=ModelName
            infoDict["value"]="null" #training_data["value"]
            
            FileName_Splited.append(infoDict)
            fieldMappingID=[]

            sing_data=[] #store each individual training sample(to be converted to tuple)
            sing_data.append(training_data['text'])
            sing_data_ent=[]
            for entities in training_data['entities']:
                sing_ent=(entities['start'], entities['end'], entities['label'])
                sing_data_ent.append(sing_ent)
                fieldMappingID.append(entities['fieldMappingID'])

            dic_ent = {"entities":sing_data_ent}
            sing_data.append(dic_ent)
            sing_data = tuple(sing_data)
            TRAIN_DATA_Splited.append(sing_data)
            fieldMappingIDList.append(fieldMappingID)

        return "Success DumpTRAINDATA", TRAIN_DATA_Splited, FileName_Splited
    
    except Exception as ex:
        print("error- DumpTRAINDATA", ex)
        return "Error DumpTRAINDATA", TRAIN_DATA_Splited, FileName_Splited
        
def TrainingDatasetfromJSON(data):
    try:
        TRAIN_DATA=[]
        FileName=[]
        fieldMappingIDList=[]
        #print("------",data["userID"])
        userID = data["userID"]
        ModelName = data["modelName"]
        contractID = data["contractID"]
        trainingType = data["trainingType"]
        # print(ModelName)
        for training_data in data['trainingData']:

            infoDict={}
            infoDict["userID"]=userID
            infoDict["fileID"]=training_data["fileID"]
            infoDict["contractID"]=contractID#training_data["contractID"]
            
            infoDict["modelName"]=ModelName
            infoDict["value"]="null" #training_data["value"]
            
            FileName.append(infoDict)
            fieldMappingID=[]
            
            sing_data=[] #store each individual training sample(to be converted to tuple)
            sing_data.append(training_data['text'])
            sing_data_ent=[]
            for entities in training_data['entities']:
                sing_ent=(entities['start'], entities['end'], entities['label'])
                sing_data_ent.append(sing_ent)
                fieldMappingID.append(entities['fieldMappingID'])
            
            dic_ent = {"entities":sing_data_ent}
            sing_data.append(dic_ent)
            sing_data = tuple(sing_data)
            TRAIN_DATA.append(sing_data)
            fieldMappingIDList.append(fieldMappingID)
            
    except Exception as err:
        print(f"Jsonformating Error-- {err}")        
        return "Error",err
    else:
        return ModelName,TRAIN_DATA,FileName,userID,fieldMappingIDList,trainingType,contractID

# def trainingAccPerData(data,filenames,modelPath,fieldMappingIDList,contractID,trainingType,modelname, ActualData):
#     print("Start- trainingAccPerData")
#     # print("filenames:--", filenames)
#     # logMessage = {"UserEmail-":userEmailId, "LogType":"Info","Message:ActualData --- ": ActualData ,"MethodName":"trainingAccPerData"}
#     # AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#     # ActualData = this variable mean - it will save actual json result into it, without split data.

#     logMessage = {"UserEmail-":userEmailId, "LogType":"Info","Message: ActualData ":ActualData ,"MethodName":"trainingAccPerData"}
#     writelogs(logMessage)
#     AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#     logMessage = {"UserEmail-":userEmailId, "LogType":"Info","Message: filenames ":filenames ,"MethodName":"trainingAccPerData"}
#     writelogs(logMessage)
#     AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#     fieldMappingCount = getContractFieldMapping(contractID) # Getting field mapping count from fieldmapping table based on contract Id    
   
#     print('fieldMappingCount', fieldMappingCount[1])

#     logMessage = {"UserEmail-":userEmailId, "LogType":"Debug","Message-mapping count: ":fieldMappingCount[1] ,"MethodName":"trainingAccPerData"}
#     writelogs(logMessage)
#     AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#     print("nlp load A-->", modelPath)
#     nlp = spacy.load(modelPath)
#     print("nlp load B-->", modelPath)
#     output =[] #outermost list
#     modelname='modelname'
#     totalPercentage =0
#     highestFieldCount=[]
#     highestPercentage=[]
#     try:
#         for i in range (len(ActualData)):
#             identifiedEntities=[]
#             allAnnotations =[]
#             eachData={}
#             for text,annotation in [ActualData[i]]:
                
#                 nlp.max_length = len(text)
#                 doc = nlp(text)

#                 identifiedEntities= [(ent.label_) for ent in doc.ents]
#                 for ent in annotation.get("entities"):
#                     allAnnotations.append(ent[2])

#                 eachData["contractID"]=filenames[i]["contractID"]
#                 eachData["fileID"]=filenames[i]["fileID"]
#                 print("FileID--> ", filenames[i]["fileID"])
#                 eachData["modelName"]=filenames[i]["modelName"]
#                 modelname = filenames[i]["modelName"]
#                 eachData["userID"]=filenames[i]["userID"]
#                 eachData["value"]=filenames[i]["value"]
#                 eachData["identifiedIdentities"]=identifiedEntities
#                 eachData["missingIdentities"]=[lbl for lbl in allAnnotations if lbl not in identifiedEntities]
#                 # eachData["percentage"] = f'{((len(allAnnotations)-len((eachData["missingIdentities"])))/len(allAnnotations))*100}'
#                 eachData["percentage"] = f'{(len(allAnnotations)/fieldMappingCount[1])*100}'
#                 totalPercentage+=double(eachData["percentage"])                
#                 output.append(eachData)   
#                 highestFieldCount.append(len(identifiedEntities))
#                 highestPercentage.append(eachData["percentage"])
#         # output.append({'totalPercentage':totalPercentage/len(data)})
#         if trainingType =='updateTrain':
#             print("inside-updatte")
#             from sqlalchemy import or_, and_
#             session = Session(bind=engine, expire_on_commit=False)
#             filesPerList = session.query(models.files.trainingFieldsPercentage).join(models.Contract_TrainingFiles,
#                         and_(models.files.id == models.Contract_TrainingFiles.file_id, 
#                         models.files.isNlpTrained ==1, models.Contract_TrainingFiles.contract_id == contractID)
#             ).all()
#             session.close()
#             for p in filesPerList:
#                 print('inside loop')
#                 highestPercentage.append(p.trainingFieldsPercentage)
                
#         print('highestPercentage-1', highestPercentage)
#         print('highestPercentage-2', max(highestPercentage))
        
#         contracthighestPercentage = max(highestPercentage)
#         contracthighestFieldCount = max(highestFieldCount)
        
#     except Exception as exp:
#         logMessage = {"UserEmail-":userEmailId, "LogType":"Error","Message-":exp ,"MethodName":"trainingAccPerData"}
#         writelogs(logMessage)
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#         print(f"trainingAccPerData Error--{exp}")  ##?? what to send here
#         return "Error",exp
#     else:
#         print("end- trainingAccPerData")
#         jsonResult = {"ModelResult": output, "contracthighestPercentage":contracthighestPercentage, "fieldMappingIDs": fieldMappingIDList, "contracthighestFieldCount":contracthighestFieldCount }
#         return "ModelResult", jsonResult

# # Insert the trained model result to the SQL database
# #@router.post('/ConnectFiletable')
# def UpdateResult(modelResult, modelname):
#     try:
#         #modelResult = """{ "ModelResult": [ { "contractID": "c227fbac-f689-400f-8f2d-000dfe4f38eb", "fileID": "05b5e1c5-d8d4-4c1a-b87c-e14700e0997a", "modelName": "PVA_Format_F2", "userID": "3b25af2b-cc7a-451d-b33c-1b555ea569d5", "value": "Null", "percentage": "95", "identifiedIdentities": [ "LAW", "ORG", "GPE", "ORG", "GPE", "DATE", "ORG" ], "missingIdentities": [ "DOCUMENTTYPE", "EFFECTIVEDATE", "PARTYNAME1", "PARTYNAME2", "TERMENDDATE" ] }, { "contractID": "c227fbac-f689-400f-8f2d-000dfe4f38eb", "fileID": "0d5b981e-b58e-4e2a-880e-5fa04bb128ed", "modelName": "PVA_Format_F2", "userID": "3b25af2b-cc7a-451d-b33c-1b555ea569d5", "value": "Null", "percentage": "65", "identifiedIdentities": [ "LAW", "ORG", "ORG", "GPE", "DATE", "ORG" ], "missingIdentities": [ "DOCUMENTTYPE", "EFFECTIVEDATE", "PARTYNAME1", "PARTYNAME2", "TERMENDDATE" ] } ] }"""
#         jsonResult =json.loads(json.dumps(modelResult))
        
#         logMessage = {"UserEmail-":userEmailId, "LogType":"Info","Message- UpdateResult method is invoked. !--- ":jsonResult ,"MethodName":"UpdateResult"}
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#         Contract_Files_TrainedData= []
#         statusID = getStatusDetails("Completed")
#         if statusID[0] == "Error":
#             print("Error:", statusID[1])
#             with open("DbError.txt", mode="w") as data_file:
#                 content = f"DbError : {statusID[1]}"
#                 data_file.write(content)
                
#             # UpdateStatus(filename, "trainingAccPerData -"+modelResult[1], userEmailId, "error")
#         db = Session(bind=engine, expire_on_commit=False)
        
#         for item in jsonResult["ModelResult"]:
#             modelname = item.get('modelName')
#             contractid = item.get('contractID')
#             userId = item.get('userID')
#             print('fileID',item.get('fileID'))
#             print('FilePercentage',item.get('percentage'))

#             stmt = (update(models.files).where(models.files.id == item.get('fileID'))
#             .values(trainingFieldsPercentage = item.get('percentage'), UpdatedAt = datetime.now(), isNlpTrained= 1, trainingStatusID=statusID[1].id, nlpTrainingError="Training-Completed"))
#             db.execute(stmt)
#             db.commit()
            
#             # below code is written to get identified and missing entities into comma seperated string
#             identifiedEntities = item.get('identifiedIdentities')
#             if identifiedEntities is not None:
#                 identified = ",".join(identifiedEntities)

#             missingEntities = item.get('missingIdentities')
#             if missingEntities is not None:
#                 missing = ",".join(missingEntities)
            
#             c1 = models.ContractFilesTrainingData(id = uuid.uuid1(), value = item.get('value'), contractID = item.get('contractID'), fileID = item.get('fileID'),
#             modelName = item.get('modelName'), missingIdentities = missing, identifiedIdentities = identified, CreatedByID = item.get('userID'), 
#             ModifiedByID = item.get('userID'), CreatedAt = datetime.now(), UpdatedAt= datetime.now())

#             Contract_Files_TrainedData.append(c1)

#         print("files table updated successfully. !")
#         if len(Contract_Files_TrainedData)>0:
#             exists = db.query(models.ContractFilesTrainingData).filter(models.ContractFilesTrainingData.contractID==contractid).first() is not None
#             if exists:
#                 from sqlalchemy import delete
#                 print('existing data found for contract Id', contractid)
#                 delete_existingdata = (delete(models.ContractFilesTrainingData).where(models.ContractFilesTrainingData.contractID == contractid))
#                 db.execute(delete_existingdata)
#                 db.commit()
        
#         db.bulk_save_objects(Contract_Files_TrainedData)
#         db.commit()
#         print("ContractFilesTrainingData inserted successfully for contract Id", contractid)
    
#         # ************************************** below code commented for New code implementation to calculate & update contract level Average
#         # See below code 

#         # print("Contract ", contractid)
#         # contractPercentage_update = (update(models.contracts).where(models.contracts.id == contractid).values(trainingFieldsPercentage = highestPercentage, 
#         # nlpTrainingEndTime = datetime.now(), trainedByID= userId, highestFieldsTrainedCount=highestFieldCount)) 
#         # db.execute(contractPercentage_update)
#         # db.commit()
        
#         # ******************* End here
            

#         # ======================================= Below code is to update field Mapping table as contract Id for given field mapping id's
#         list=[]
#         feildMapping_updateList= []
#         for item in jsonResult['fieldMappingIDs']:
#             fieldMappingIDs= ",".join(item)
#             list.append(fieldMappingIDs)
#         fieldMappingAllIds = ",".join(list)
                
#         for fieldMappingId in fieldMappingAllIds.split(','):
#             # print(fieldMappingId)
#             feildMapping_update = (update(models.fieldMappings).where(models.fieldMappings.id == fieldMappingId).values(training_model_name= contractid, is_trained = 1
#             ,trainedByID = userId, trainedOn = datetime.now()))
#             db.execute(feildMapping_update)
#             db.commit()
#         print("fieldMapping table updated successfully. !") 
#         # ======================================= End here

        

#         # ************************************** New code implememted to calculate & update contract level Average
#         highestPercentage = jsonResult["contracthighestPercentage"]
#         highestFieldCount = jsonResult["contracthighestFieldCount"]
#         print("Percentage -", highestPercentage)
#         print("Contract ", contractid)

#         fieldMappingsList=[] 

#         # session = Session(bind=engine, expire_on_commit=False
#         contractDetails = db.query(models.Contract_FieldMapping).filter(models.Contract_FieldMapping.contract_id == contractid).all()
#         for item in contractDetails:
#             fieldMappingsList.append(item.field_mapping_id)
#         print('FieldMappingCount', len(fieldMappingsList))

#         fieldMapped_ModelNames = db.query(models.fieldMappings).filter(models.fieldMappings.id.in_((fieldMappingsList)),
#         models.fieldMappings.training_model_name.is_not(None), models.fieldMappings.training_model_name != '').all()
#         print('ModelMappedCount' , len(fieldMapped_ModelNames))

#         ContractLevelAverage = len(fieldMapped_ModelNames)/len(fieldMappingsList)*100
#         print('ContractLevelAverage', ContractLevelAverage)

#         contractPercentage_update = (update(models.contracts).where(models.contracts.id == contractid).values(trainingFieldsPercentage = ContractLevelAverage, 
#         nlpTrainingEndTime = datetime.now(), trainedByID= userId, highestFieldsTrainedCount=highestFieldCount)) 
#         db.execute(contractPercentage_update)
#         db.commit()

#         print("contracts table updated successfully. !")   
#         # ======================================= Ends here

#         db.close()
        
#         logMessage = {"ModelName- ":modelname, "LogType":"Info","UserEmail-":userEmailId, "Message-":"Successfully completed database operations.!" ,"MethodName":"UpdateResult"}
#         writelogs(logMessage)
    
#         # release variable memory when value no more required for next process.
#         del jsonResult, statusID, Contract_Files_TrainedData, modelname, contractid, userId,identifiedEntities, missingEntities, c1,highestPercentage,highestFieldCount,contractPercentage_update,fieldMappingAllIds

#     except Exception as dbError:
#         print(f"Update DB Error--{dbError}")
#         logMessage = {"UserEmail-":userEmailId, "LogType":"Error", "Message- dberror ": dbError,"MethodName":"UpdateResult"}
#         writelogs(logMessage)
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#         with open("DbErrorEx.txt", mode="w") as data_file:
#             content = f"DbErrorEx : {dbError}"
#             data_file.write(content)
#         return "Error", dbError

#     else:
#         return "Success", "Db Updated Success"

################################### Train model 2 starts here ###################################################################################

# def toSpacy(currentDir, data, fileName):
    
#     try:
#         db = DocBin()
#         nlp = spacy.load("en_core_web_sm")
#         for text, annot in tqdm(data): # data in previous format
#             doc = nlp.make_doc(text) # create doc object from text
#             ents = []
#             for start, end, label in annot["entities"]: # add character indexes
#                 span = doc.char_span(start, end, label=label, alignment_mode="expand")
#                 if span is None:
#                     print("Skipping entity")
#                 else:
#                     ents.append(span)
#             doc.ents = ents # label the text with the ents
#             db.add(doc)
#         db.to_disk(os.path.join(currentDir,f'{fileName}.spacy'))

#     except Exception as ex:
#         err = str(ex)
#         err1 = err.replace('[', '-')
#         err2 = err1.replace(']', '-')
#         print("error occured in tosapcy method -", err2)
#         return "Error", err2

#     else:
#         return  "Success","Success"

# def UpdateStatus(trainingData, NLPTrainingMessage, userEmailId, StatusType,contractid):
#     try:
#         db = Session(bind=engine, expire_on_commit=False)
#         if StatusType =="error":
#             statusID = getStatusDetails("Failed")
#             contractDateUpdate = (update(models.contracts).where(models.contracts.id == contractid).values(nlpTrainingEndTime = datetime.now())) 
#         if StatusType =="started":
#             statusID = getStatusDetails("In Progress")
#             contractDateUpdate = (update(models.contracts).where(models.contracts.id == contractid).values(nlpTrainingStartTime = datetime.now())) 
#         db.execute(contractDateUpdate)
#         db.commit()        
#         for item in trainingData:
#             #print("fileId", item.get('fileID'))
#             # print("StatusType==", StatusType)
#             stmt = (update(models.files).where(models.files.id == item.get('fileID'))
#             .values(trainingFieldsPercentage = "0.00", UpdatedAt = datetime.now(), isNlpTrained= 0, trainingStatusID=statusID[1].id, nlpTrainingError=NLPTrainingMessage))
#             db.execute(stmt)
#             db.commit()
#             db.close()
#         # log = {"userEmail":userEmailId,"message":"Status successfully updated to the files table column. ","module":"UpdateStatusResult","logType":"Info"}
#         # logger.info(log)

#     except Exception as exError:
#         print("UpdateStatus Error: ", exError)
#         # log = {"userEmail":userEmailId,"message":"Error occured - " + exError, "module":"UpdateExceptionResult","logType":"Info"}
#         # logger.info(log)

# def check_duplicate(data):
#     duplicate,label1,label2,field_ID,x,y,x2,y2=[],[],[],[],[],[],[],[]
#     del_file=[]
#     maxLimit = False
#     try:
#         r=""
#         result=[]
#         for i in range(len(data["trainingData"])):  #Iterate over files
#             print(len(data["trainingData"][i]["text"]))
#             if(len(data["trainingData"][i]["text"]) >= spacyCharLimit):
#                 print("Identified max limit value for file id: ", data["trainingData"][i]["fileID"])
#                 maxLimit = True
#             for j in range(len(data["trainingData"][i]["entities"])): #Iterate over entities
#                 start=data["trainingData"][i]["entities"][j]["start"]
#                 end=data["trainingData"][i]["entities"][j]["end"]
#                 betwn1=set(range(start,end+1))
#                 for check in range(j,(len(data["trainingData"][i]["entities"])-1)):  #Check start and end each one by one
#                     start_2=data["trainingData"][i]["entities"][check+1]["start"]
#                     end_2=data["trainingData"][i]["entities"][check+1]["end"]
#                     betwn_2=set(range(start_2,end_2+1))
#                     if(bool(betwn1.intersection(betwn_2))==True):
#                         #duplicate.append("between")
#                         label1.append(data["trainingData"][i]["entities"][j]["label"])
#                         label2.append(data["trainingData"][i]["entities"][check+1]["label"])
#                         field_ID.append(data["trainingData"][i]["fileID"])
#                         x.append(start)
#                         y.append(end)
#                         x2.append(start_2)
#                         y2.append(end_2)
#                         del_file.append(i)
        
#         statusID = getStatusDetails("Failed")
#         for i in range(len(label1)):
#             r ="\nDuplicates indices identified for "+label1[i]+":("+str(x[i])+":"+str(y[i])+") & "+label2[i]+":("+str(x2[i])+":"+str(y2[i])+") of file id:"+field_ID[i]
#             # r="\nDuplicates "+ duplicate[i]+" indices:("+str(x[i])+","+str(y[i])+")"+" identified for "+ label1[i]+" & "+label2[i]+" of file id:"+field_ID[i]
#             result.append(r)
#             db = Session(bind=engine, expire_on_commit=False)
#             stmt = (update(models.files).where(models.files.id == field_ID[i])
#             .values(trainingFieldsPercentage = "0", UpdatedAt = datetime.now(), isNlpTrained= 0, trainingStatusID=statusID[1].id, nlpTrainingError=r))
#             db.execute(stmt)
#             db.commit()
#             db.close()
#             print("Duplicate Error updated to fileid:", field_ID[i])
        
#         #Delete the Dulpicate file
#         del_file=set(del_file)
#         for val in sorted(del_file, reverse=True):
#             print(val)
#             del data["trainingData"][val]
            
#         if (len(data["trainingData"]) <=1):            
#             if (len(data["trainingData"]) ==0):
#                 return "false", data        
#             db = Session(bind=engine, expire_on_commit=False)
#             stmt = (update(models.files).where(models.files.id == data["trainingData"][0]["fileID"])
#             .values(trainingFieldsPercentage = "0", UpdatedAt = datetime.now(), isNlpTrained= 0, trainingStatusID=statusID[1].id, nlpTrainingError="Identified only one dataset count in the training data"))
#             db.execute(stmt)
#             db.commit()
#             db.close()  
#             print("Found only 1 dataset in training dataset- updated file id: ", data["trainingData"][0]["fileID"])

#         if not result:
#             return "false", data, maxLimit
#         else:
#             print("Duplicate Span error updated to db for fileID", field_ID)
#             return "true", data, maxLimit
            
#     except Exception as error:
#         return "Error", error						  

# def backgroundTrainingProcess2(trainingData, userEmailId, trainingType, TRAIN_DATA_Splited, FileName_Splited):
#     try:
        
#         modelname,TRAIN_DATA,filename,userID,fieldMappingIDList,trainingType,contractID = trainingData
#         TRAINDATA_OriginalTuple = TRAIN_DATA_Splited
#         # major change, test with mulitple files
#         filename = FileName_Splited

#         my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', modelname)
#         modelname = my_new_string.replace(" ", "_").lower()
#         print("Modelname===",modelname)
#         if TRAIN_DATA is not None:
#             apiResult = "Success"
#             # print("Background proc-2----")
#             current_directory = os.getcwd()
#             current_directory = current_directory+"/uploadtrainmodels/"+modelname
            
#             if trainingType =="Train":
#                 print('Train model path ===', current_directory)
#                 if not os.path.exists(current_directory):
#                     os.makedirs(current_directory)
#                 relativePath = "uploadtrainmodels/"+modelname

#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Model directory created successfully.","MethodName":"backgroundTrainingProcess2"}
#                 logText = json.dumps(logMessage)
#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#             elif trainingType == "updateTrain":
#                 model_dirPath = os.path.join('nlp-models', modelname)
#                 files_list = list_files(
#                     dir_path=model_dirPath,
#                     share_name=azureShareName,
#                     connection_string=connection_string,
#                     include_properties=False,
#                     recursive=True
#                 )
#                 for k, f in enumerate(files_list, start=1):
#                     pass            
#                 print("Model downloading completed.")
                
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Model downloading completed.","MethodName":"backgroundTrainingProcess2"}
#                 writelogs(logMessage) 

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)  

#                 relativePath = "nlp-models/"+modelname
#             train, test = train_test_split(TRAIN_DATA, test_size=0.2, random_state = 69)
        
#             # cleaning_TrainData = trim_entity_spans(train) # added new line of code
#             spacyPathTrain = toSpacy(relativePath, train, "train") # reverted line of code

#             if spacyPathTrain[0] == "Error":
#                # log = {"userEmail":userEmailId,"message":"error occured while converting into spacy format.","module":"TrainModel2Api","logType":"Error"}
#                # logger.info(log)
#                 print("duplicate error Train", spacyPathTrain[1])
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message":"duplicate error in spacy Train split-  {spacyPathTrain[1]} file ids are updated.","MethodName":"toSpacy"}
#                 writelogs(logMessage)               
#                 UpdateStatus(filename, spacyPathTrain[1], userEmailId, "error", contractID)                

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'w',True, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID) 

#                 return {"Result" : "Error" , "ErrorMessage - toSpacy: " : spacyPathTrain[1]} 

#             spacyPathTest = toSpacy(relativePath, test, "dev")

#             if spacyPathTest[0] == "Error":
#                # log = {"userEmail":userEmailId,"message":"error occured while converting into spacy format.","module":"TrainModel2Api","logType":"Error"}
#                # logger.info(log)
#                 print("error Test", spacyPathTest[1])
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message":"duplicate error in spacy Test split-  {spacyPathTest[1]} files Id are updated. ","MethodName":"toSpacy"}
#                 writelogs(logMessage)                 
#                 UpdateStatus(filename, spacyPathTest[1], userEmailId, "error", contractID)   

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'w',True, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID)                            
#                 return {"Result" : "Error" , "ErrorMessage - toSpacy: " : spacyPathTest[1]} 

#             print("train_test_split is completed.")
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Splitting data for training and testing is completed. ","MethodName":"toSpacy"}
#             writelogs(logMessage)
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)       

#             # Config file creation
#             # createConfigFile = f"python -m spacy init fill-config base_config.cfg config.cfg"

#             # configSP = subprocess.run(createConfigFile, capture_output=True,shell=True)
#             # if configSP.returncode != 0:
#             #     log = {"userEmail":userEmailId,"message":configSP.stderr,"module":"TrainModel2Api","logType":"Error"}
#             #     logger.info(log)
#             #     print("error config file ", configSP.stderr)
#             #     UpdateStatus(filename, "error occured while creating config spacy file.", userEmailId, "error")                
#             #     return {"Result" : "Error" , "ErrorMessage-configSP:": configSP.stderr}

            
#             # traning Config file creation
#             if trainingType == "Train":
#                 trainModelCli = f"python -m spacy train config.cfg --output {relativePath}/output --paths.train {relativePath}/train.spacy --paths.dev {relativePath}/dev.spacy"
#                 print("Training started....")
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Spacy training started....","MethodName":"Train-py"}
#                 writelogs(logMessage) 

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)     

#             elif trainingType == "updateTrain":
#                 print("updateTraining Initaited....")
#                 create_config(model_dirPath,"ner","updateTrainconfig")
#                 trainModelCli = f"python -m spacy train updateTrainconfig.cfg --output {relativePath}/output --paths.train {relativePath}/train.spacy --paths.dev {relativePath}/dev.spacy"
#                 print("updateTraining started....")
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Spacy update training started....","MethodName":"Train-py"}
#                 writelogs(logMessage)                   
                
#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)     

#             trainSP = subprocess.run(trainModelCli, capture_output=True, shell=True)
#             if trainSP.returncode != 0:
#                 print("Error training model Cli--", trainSP.stderr)               
#                 errroMessage = trainSP.stderr
#                 logMessage = {"UserEmail":userEmailId,"LogType":"Error","Message":"Error training model Cli--","-": errroMessage,"MethodName":"Train-py"}
#                 writelogs(logMessage)   
#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)   
#                 UpdateStatus(filename, errroMessage ,userEmailId, "error", contractID)    
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID)

#                 if "[E024] Could not find an optimal move to supervise the parser." in errroMessage:
#                     errroMessage = "[E024] Make sure that none of your annotated entity spans have leading or trailing whitespace or punctuation"

#                 # Save Logs into DB tables
#                 return {"Result" : "Error" , "ErrorMessage-trainSP:": errroMessage}              

#             print("Successfully completed the training process.")        
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Successfully completed the training process.","MethodName":"Train-py"}
#             writelogs(logMessage)      
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)  
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)
            
#             print("reached-- trainSP end")
#             print("reached-- nlp load")

#             # server
#             modelPath = ""
#             if trainingType == "Train": 
#                 # nlp = spacy.load(os.path.join(current_directory, "output/model-best"))
#                 modelPath = os.path.join(current_directory, "output/model-best")
#             elif trainingType == "updateTrain":
#                 # nlp = spacy.load(os.path.join(model_dirPath, "output/model-best"))
#                 modelPath = os.path.join(model_dirPath, "output/model-best")
#             # local
#             # nlp = spacy.load(os.path.join(model_dirPath, relativePath))
#             print("reached to spacy model path -- ", relativePath)
#             print("Successfully loaded spacy model --", relativePath)
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Successfully loaded spacy model","MethodName":"Train-py"}
#             writelogs(logMessage)
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#             # Code to get model result based nlp result
#             try:
#                 modelResult = trainingAccPerData(TRAIN_DATA,filename,modelPath,fieldMappingIDList,contractID,trainingType,modelname,TRAINDATA_OriginalTuple)
#             except Exception as exp:
#                 logMessage = {"ModelName- ":"modelname", "LogType":"Error","Message":exp,"MethodName":"modelResult"}
#                 writelogs(logMessage)
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID)

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#                 UpdateStatus(filename, "modelResult -"+exp, userEmailId, "error", contractID)
                
#             # release variable memory when value no more required for next process.
#             del TRAIN_DATA            
#             print(modelResult[0])
#             if modelResult[0]== "Error":
#                 print("Error:"+ modelResult[0])
#                 logMessage = {"ModelName- ":modelname, "LogType":"Error","UserEmail-":userEmailId,"Message":modelResult[1],"MethodName":"trainingAccPerData"}
#                 writelogs(logMessage)  

#                 UpdateStatus(filename, "trainingAccPerData -"+modelResult[1], userEmailId, "error", contractID)   
                
#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID) 

#                 return {"Result" : "Error" , "ErrorMessage- trainingAccPerData: " : f"error occured while generating the json result --- {modelResult[1]}"}    

#             print(apiResult+" modelresult passed")

#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Successfully completed the model Result process.! ","MethodName":"trainingAccPerData"}
#             writelogs(logMessage)

#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#             #Uploading saved trained model to Azure file storage account - pwccentral

#             print("reached---upload start", modelname)
#             uploadReult = UploadModeltoAzure(modelname, trainingType)
#             if uploadReult[0]== "Error":
#                 print("Error:"+ uploadReult[0])
#                 # log = {"userEmail":userEmailId,"message":"error occured while uploading spacy model files to Azure.","module":"TrainModel2Api","logType":"Error"}
#                 # logger.info(log)
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message":uploadReult[0],"MethodName":"UploadModeltoAzure"}
#                 writelogs(logMessage)    
#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#                 UpdateStatus(filename, "UploadModeltoAzure -"+uploadReult[0], userEmailId, "error", contractID)  

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID)      

#                 return {"Result" : "Error" , "ErrorMessage- UploadModeltoAzure: " : f"error occured while uploading spacy model files to Azure --- {uploadReult[1]}"}
            
#             print("Successfully uploaded model result to Azure storage account.!")
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message":"Successfully uploaded the spacy model into Azure storage account.! ","MethodName":"UploadModeltoAzure"}
#             writelogs(logMessage)            
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#             #update result to database
#             logMessage = {"UserEmail-":userEmailId, "LogType":"Info","Message: modelResult[1] --- ": modelResult[1] ,"MethodName":"trainingAccPerData"}
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#             dbResult = UpdateResult(modelResult[1], modelname)
#             if dbResult[0]== "Error":
#                 # log = {"userEmail":userEmailId,"message":f"error occured while Insert/Update result to db --- {dbResult[1]}","module":"TrainModel2Api","logType":"Error"}
#                 # logger.info(log)
#                 print("Error:"+ dbResult[0])
#                 logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message":dbResult[0],"MethodName":"dbResult"}
#                 writelogs(logMessage) 
                
#                 UpdateStatus(filename, "UpdateResult -"+dbResult[0], userEmailId, "error", contractID)

#                 AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)

#                 # Save Logs into DB tables
#                 logText = json.dumps(logMessage)
#                 LogMessageResult = AppDBLogs(contractID, modelname, "Error", logText, userID)       

#                 return {"Result" : "Error" , "ErrorMessage- UpdateResult: " : f"error occured while Insert/Update result to db --- {dbResult[1]}"}

#             print(apiResult+" Database operation completed successfully.!")

#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message-":"Successfully completed the database operations .!", "MethodName-":"UpdateResult"}
#             writelogs(logMessage)

#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
            
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#             print("Training completed  - " + modelname, datetime.now())
#             tempMessage = "Successfully completed the model training - ", datetime.now() , "-"
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message-":tempMessage, "MethodName-":"UpdateResult"}
#             writelogs(logMessage)  
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage, indent=4, sort_keys=True, default=str)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)
            
#             # Notify = NotifyTrainModel(trainingType, contractID, userID, userEmailId)
#             # if Notify[0]== "Error":
#             #     print("Error notify:"+ Notify[1])
#             #     logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message":Notify[1],"MethodName":"Notify"}
#             #     writelogs(logMessage) 

#             # print('Notify[0]-', Notify[0])

#             tempMessage= "Notification sent successfully.! ", datetime.now() , "-"
#             logMessage = {"UserEmail-":userEmailId,"LogType":"Info","Message- ":tempMessage,"MethodName-":"UpdateResult"}
#             writelogs(logMessage)  
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname)
#             # Save Logs into DB tables
#             logText = json.dumps(logMessage, indent=4, sort_keys=True, default=str)
#             LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)            
    
#             return {"Result" : "Success" , "ModelResult" : modelResult}

#     except Exception as ex:
#         print("Error Backgroung process method ", ex) 
#         logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message- ":ex,"MethodName-":"SpacyTraining"}   
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',True, False, modelname) 
#         return "Background method Error", ex

# def create_config(model_name: str, component_to_update: str, output_path: Path):
#     nlp = spacy.load(model_name)
#     # create a new config as a copy of the loaded pipeline's config
#     config = nlp.config.copy()

#     # revert most training settings to the current defaults
#     default_config = spacy.blank(nlp.lang).config
#     config["corpora"] = default_config["corpora"]
#     config["training"]["logger"] = default_config["training"]["logger"]

#     # copy tokenizer and vocab settings from the base model, which includes
#     # lookups (lexeme_norm) and vectors, so they don't need to be copied or
#     # initialized separately
#     config["initialize"]["before_init"] = {
#         "@callbacks": "spacy.copy_from_base_model.v1",
#         "tokenizer": model_name,
#         "vocab": model_name,
#     }
#     config["initialize"]["lookups"] = None
#     config["initialize"]["vectors"] = None

#     # source all components from the loaded pipeline and freeze all except the
#     # component to update; replace the listener for the component that is
#     # being updated so that it can be updated independently
#     config["training"]["frozen_components"] = []
#     for pipe_name in nlp.component_names:
#         if pipe_name != component_to_update:
#             config["components"][pipe_name] = {"source": model_name}
#             config["training"]["frozen_components"].append(pipe_name)
#         else:
#             config["components"][pipe_name] = {
#                 "source": model_name,
#                 "replace_listeners": ["model.tok2vec"],
#             }

#     # save the config
#     config.to_disk(f"{output_path}.cfg")

# def NotifyTrainModel(trainingType, contractID, userId, userEmail):
#     try:
#         import requests
#         session = Session(bind=engine, expire_on_commit=False)
#         contractDetails = session.query(models.contracts).filter(models.contracts.id == contractID).first()
#         session.close()
#         url = nodeAPIURL
#         # Create the data to send as a dictionary 
#         isProjectSpecific = False
#         if contractDetails.project_id is not None:
#             isProjectSpecific = True
#             print(isProjectSpecific)
#         data = { 
#             "isProjectSpecific": isProjectSpecific, 
#             "projectID": contractDetails.project_id, 
#             "modelName": contractDetails.displayModelName,
#             "trainingType":trainingType,
#             "userId":userId
#         } 
#         json_Data = json.dumps(data)
#         headers = {'Content-Type': 'application/json','loggedin-useremail':userEmail}
#         response = requests.post(url, data=json_Data, headers=headers)

#     except Exception as ex:
#         return "Error", ex
#     else:
#         return  "Success","Success"

# @router.post("/TrainModel2")
# async def TrainModel2(data: Request, background_tasks: BackgroundTasks):#UploadFile = File(...)#projectname:str, data:str 
#     try:
#         intialMessage = "-- Logs started --"

#         with open("applogs.txt", mode="w") as log_file:
#             content = f"appLogs: {intialMessage}"
#             log_file.write(content)
            
#         try:
#             data = await data.json()
#         except ValueError as e:
#             logMessage = {"LogType":"Error","message":"Train model API identified invalid json format.!","MethodName":"TrainModel2Api"}
#             writelogs(logMessage)
#             return {"Result" : "Error" , "ErrorMessage - TrainingDatasetfromJSON: " : f"Train model API identified invalid json format."}
        
#         dataResult = check_duplicate(data)
#         # print("check_duplicate: ", dataResult[1])
#         data = dataResult[1]
#         if (len(data["trainingData"]) <=1):
#             logMessage = {"LogType":"Error","message":"Cannot process for the training with 1 dataset, atleast 2 datasets are required !","MethodName":"TrainModel2Api"}
#             AppAzureLogs(logMessage,'_applogs.txt', 'w',True, False, "")
#             writelogs(logMessage)
#             print('Cannot process for the training with 1 dataset, atleast 2 datasets are required !')
#             return {"Result" : "Error" , "ErrorMessage - Check-Duplicates: " : f"Cannot process for the training with 1 dataset, atleast 2 datasets are required !"}

#         with open("TrainingData.txt", mode="w") as data_file:
#             content = f"checkduplicates: {data}"
#             data_file.write(content)

#         if dataResult[2] == True:
#             print("inside max limit")
#             orig_len = len(data['trainingData'])
#             TRAINDATA_OriginalTuple =DumpTRAINDATA(data)
#             print('Original Length: ', orig_len)
#             split = spacyCharLimit
#             updated_data = data_split_modified(split,orig_len, data)
#             print("Updated data pass")
            
#             trainingData = TrainingDatasetfromJSON(updated_data)
#             logMessage = {"LogType":"Error","Message trainingData: ":updated_data,"MethodName":"Split Json data method"}
#             writelogs(logMessage)

#             if trainingData[0]== "Error":
#                 logMessage = {"LogType":"Error","Message":"error occured while converting json to spacy format. ","MethodName":"Split Json data method"}
#                 AppAzureLogs(logMessage,'_applogs.txt', 'w',True, False, "modelname")
#                 writelogs(logMessage)             
#                 return {"Result" : "Error" , "ErrorMessage - TrainingDatasetfromJSON: " : f"error occured while converting json to spacy format --- {trainingData[1]}"}
#         else:
#             TRAINDATA_OriginalTuple =DumpTRAINDATA(data)

#             trainingData = TrainingDatasetfromJSON(data)  
#             if trainingData[0]== "Error":
#                 logMessage = {"LogType":"Error","Message":"error occured while converting json to spacy format. ","MethodName":"Data method"}
#                 AppAzureLogs(logMessage,'_applogs.txt', 'w',True, False, "modelname")
#                 writelogs(logMessage)             
#                 return {"Result" : "Error" , "ErrorMessage - TrainingDatasetfromJSON: " : f"error occured while converting json to spacy format --- {trainingData[1]}"}


#         # Preparing a training dataset to the model
#         modelname,TRAIN_DATA,filename,userID,fieldMappingIDList,trainingType,contractID = trainingData
#         TRAIN_DATA_Splited = TRAINDATA_OriginalTuple[1]
#         FileName_Splited = TRAINDATA_OriginalTuple[2]
#         # print("TRAIN DATA:--- ", TRAIN_DATA)
#         # print("TRAIN_DATA_Splited:--- ", TRAIN_DATA_Splited)
#         my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', modelname)
#         modelname = my_new_string.replace(" ", "_").lower()
#         print("Training started - ", datetime.now())

#         userDetails = getUserDetails(userID)
#         if userDetails[0] == "Error":
#             logMessage = {"UserEmail-":"Not found","LogType-":"Error","UserEmail-":userEmailId,"Message-":"error occured while getting user details. ","MethodName":"TrainModel2Api"}
#             writelogs(logMessage)
#             AppAzureLogs(logMessage,modelname+'_applogs.txt', 'w',True, False, modelname)
#             return {"Result" : "Error" , "ErrorMessage - getUserDetails: " : f"error occured while getting user details for {userID}: {userDetails[1]}"} 

#         userEmailId = userDetails[1].email

#         # Save Logs into DB tables
#         logMessage = {"userEmail":userEmailId,"LogType-":"Info","message":"Learning model User details identified.","MethodName":"TrainModel"}
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#         logText = json.dumps(logMessage)
#         LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#         tempMessage = "Training model initiated at -", datetime.now() , "-"
#         logMessage = {"userEmail":userEmailId,"LogType-":"Info","LogType-":"Info","message-": tempMessage,"MethodName-":"TrainModel2Api"}
#         logMessageAzure = {"userEmail":userEmailId,"LogType-":"Info","LogType-":"Info","message-": tempMessage,"MethodName-":"TrainModel2Api","Payload":data}
#         LogMessageResult = AppAzureLogs(logMessageAzure,modelname+'_applogs.txt', 'a',False, False, modelname)
#         writelogs(logMessage)

#         # print('filename = ', filename)
#         UpdateStatus(filename, "Training started", userEmailId, "started",contractID)
#         # Save Logs into DB tables
#         logMessage = {"userEmail":userEmailId,"LogType-":"Info","message":"Respective files status are updated successfully. ","MethodName":"TrainModel"}
#         AppAzureLogs(logMessage,modelname+'_applogs.txt', 'a',False, False, modelname)
#         logText = json.dumps(logMessage)
#         LogMessageResult = AppDBLogs(contractID, modelname, "Info", logText, userID)

#         # # release variable memory when value no more required for next process.
#         del data 
        
#         background_tasks.add_task(backgroundTrainingProcess2, trainingData, userEmailId, trainingType, TRAIN_DATA_Splited, FileName_Splited)
        
#         return {"Result": "Training process started.."}

#     except Exception as ex:
#         print("Train Model API Error--",ex)
#         logMessage = {"UserEmail-":userEmailId,"LogType":"Error","Message- ":ex,"MethodName-":"SpacyTraining"}
#         AppAzureLogs(logMessage,"modelname"+'_applogs.txt', 'w',True, False, "modelname")

################################### Train model 2 end here ###################################################################################


################################### Abstraction starts here ###################################################################################

# def writelogs(logMessage: str):
#     with open("applogs.txt", mode="a") as log_file:
#         content = f"appLogs: {logMessage}"
#         log_file.write('\n')
#         log_file.write(content)

# def list_files(dir_path: str,
#     share_name: str,
#     connection_string: str,
#     include_properties: bool = False,
#     recursive: bool = True)->Iterator[Union[str, dict]]:

#     dir_client = ShareDirectoryClient.from_connection_string(
#         conn_str=connection_string,
#         share_name=share_name,
#         directory_path=dir_path
#     )

#     # Listing files from current directory path:
#     for file in dir_client.list_directories_and_files():
#         name, is_directory = file['name'], file['is_directory']
#         path = os.path.join(dir_path, name)
               
#         if is_directory:
#             os.makedirs(path,exist_ok=True)
#             if recursive:
#                 # Listing files recursively:
#                 childrens = list_files(
#                     dir_path=path,
#                     share_name=share_name,
#                     connection_string=connection_string,
#                     include_properties=include_properties,
#                     recursive=recursive
#                 )
#                 for child in childrens:
#                     #print('sub-dir'+child)
#                     yield child           
            
#         else:
                        
#             file_client = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=path)
            
#             with open(path, "wb") as file_handle:
#                 data = file_client.download_file()
#                 data.readinto(file_handle)
                 
#             if include_properties:
#                 file_client = ShareFileClient.from_connection_string(
#                     conn_str=connection_string,
#                     share_name=share_name,
#                     file_path=path
#                 )
#                 yield file_client.get_file_properties()
        
#             else:
#                 yield path

# #This method is use to format the json data to process for the entity extraction from nlp doc.
# def FormatExtractionData(input):
#     data=[]
    
#     for i in range (len(input["fieldMappingData"])):
        
#         if (input["fieldMappingData"][i]["modelName"] ==""):
#             return {"Result": 0, "Output":"Model Name Missing"}
        
#         if (input["fieldMappingData"][i]["modelName"] == null):
#             return {"Result": 0, "Output":"Identified Model Name as Null"}
        
#         if (input["fieldMappingData"][i]["modelName"] == "None"):
#             return {"Result": 0, "Output":"Identified Model Name as Null"}
                    
#         if ((input["fieldMappingData"][i]["modelName"]) is None):
#             return {"Result": 0, "Output":"Identified Model Name as None"}
        
#         if((len(data)!=0)and(data[len(data)-1]["modelName"]==input["fieldMappingData"][i]["modelName"])):
#             data[len(data)-1]["fieldMappingName"].append(input["fieldMappingData"][i]["fieldMappingName"])
#             data[len(data)-1]["nlpfieldMappingName"].append(input["fieldMappingData"][i]["nlpfieldMappingName"]) # new change for nlpfieldMappingName
#             data[len(data)-1]["fieldMappingID"].append(input["fieldMappingData"][i]["fieldMappingID"])
#         else:
#             eachData={}
#             fieldMappingName=[]
#             fieldMappingID=[]
#             nlpfieldMappingName=[] # new change for nlpfieldMappingName
            
#             fieldMappingName.append(input["fieldMappingData"][i]["fieldMappingName"])
#             fieldMappingID.append(input["fieldMappingData"][i]["fieldMappingID"])
#             nlpfieldMappingName.append(input["fieldMappingData"][i]["nlpfieldMappingName"]) # new change for nlpfieldMappingName

#             eachData["modelName"]=input["fieldMappingData"][i]["modelName"]
#             eachData["fieldMappingName"]=fieldMappingName
#             eachData["fieldMappingID"]=fieldMappingID
#             eachData["nlpfieldMappingName"]=nlpfieldMappingName # new change for nlpfieldMappingName
#             data.append(eachData)
    
#     return {"Result":1 ,"Output":data}

# # This API is designed to get the entity extraction from trained model using spacy nlp concepts.
# @router.post('/ExtractTrainModel') 
# async def ExtractTrainModel(data: Request):
#     apiResult= "Success"
#     try:
#         try:
#             data = await data.json()
#         except ValueError as e:
#             return {"Result": 0, "Output":"API identified invalid json format."}
        
#         valueReturned = FormatExtractionData(data)
#         # print("valueReturned", valueReturned)
#         if(valueReturned ["Result"]==0):
#             return valueReturned ["Output"]
        
#         modelInfo = valueReturned["Output"]   
#         #print("modelInfo--", modelInfo)     
#         fileId=data["fileID"]
#         contractID=data["contractID"]
#         upload_file = data["ocrText"]
#         modelResult=[]

#         with open("Extractiontext.txt", mode="w") as data_file:
#             content = f"Text: {data}"
#             data_file.write(content)   

#         AppAzureExtractionLogs(data, contractID)
        
#         for i in range(len(modelInfo)):
#             my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', modelInfo[i]["modelName"])
#             projectname = my_new_string.replace(" ", "_").lower()               
#             model_dirPath = os.path.join('nlp-models', projectname)
#             print('Modelname===', projectname)

#             if not(os.path.isdir(model_dirPath)):
#                 dir_path = os.path.join('nlp-models', projectname)  # Leave it empty to list files from root directory.
#                 files_list = list_files(
#                     dir_path=dir_path,
#                     share_name=azureShareName,
#                     connection_string=connection_string,
#                     include_properties=False,
#                     recursive=True
#                 )
#                 for k, f in enumerate(files_list, start=1): # List index out of range -error resolved
#                     pass
                    
#             nlp = spacy.load(model_dirPath)
#             nlp.max_length = len(upload_file) # to accept the max lengh of the given data  
#             doc = nlp(upload_file)
#             print("---------------------------------------------------------------------------------------------------------1")
#             for ent in doc.ents:
#                 print(ent.label_)
#             print("---------------------------------------------------------------------------------------------------------2")
            
#             # new change for nlpfieldMappingName
            
#             for j in range(len(modelInfo[i]["nlpfieldMappingName"])):
#                 outputDict={}
#                 count = len(modelInfo[i]["nlpfieldMappingName"])
#                 for ent in doc.ents:
                    
#                     if ent.label_==modelInfo[i]["nlpfieldMappingName"][j]: # new change for nlpfieldMappingName
#                         modelInfo[i]["nlpfieldMappingName"][j]="done"
                        
#                         print("------------------------------------")
#                         print('projectname===', projectname)
#                         print(ent.label_)
#                         print("-------------------------------------------")
#                         outputDict["fieldMappingID"]=modelInfo[i]["fieldMappingID"][j]
#                         outputDict["fieldMappingName"]=modelInfo[i]["fieldMappingName"][j]
#                         outputDict["nlpfieldMappingName"]=ent.label_ # new change for nlpfieldMappingName
#                         outputDict["value"]=ent.text
                        
#                         modelResult.append(outputDict)
#                     else:
#                         pass
#     except Exception as ex:
#         print(f"Error--{ex}")
#         return {"Result" : "Error" , "ErrorMessage" : f"{ex}"}
#     return {"Result" : apiResult , "ModelResult" : modelResult}

# ################################### Abstraction Ends here ###################################################################################

# ################################### App logs Starts here ###################################################################################
# def AppAzureLogs(logMessage: str, logfilename: str, filemode: str, uploadfile: bool, deletefile: bool, modelname: str):
#     try:
#         # print("log message= ", logMessage)
#         my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', logfilename)
#         filename = my_new_string.replace(" ", "_").lower()          
#         # print("filemode", filemode)
#         with open(filename, mode=filemode) as log_file:
#             content = f"{logMessage}"
#             log_file.write('\n')
#             log_file.write(content)        

#         if uploadfile == True:
#             print("upload yes")       
#             my_modelname = re.sub('[^a-zA-Z0-9 \n\.]', '', modelname)
#             modelname = my_modelname.replace(" ", "_").lower()                   
#             current_directory = os.getcwd()
#             rm_dirPath = os.path.join(current_directory)
#             share = ShareClient.from_connection_string(connection_string, share_name=azureShareName)
#             filesdir = []
#             filesdir.append(os.path.join(filename))
        
#             try:
#                 NLPModel = share.get_directory_client("nlp-Logs")
#                 NLPModel.create_directory()
#             except ResourceExistsError:
#                 pass
#             except ssl.CertificateError:
#                 pass
#             try:
#                 NLPModel_ProjectName = share.get_directory_client("nlp-Logs/"+modelname)
#                 NLPModel_ProjectName.create_directory()
#             except ResourceExistsError:
#                 pass
#             except ssl.CertificateError:
#                 pass 
#             properties = share.get_share_properties()
#             # [END get_share_properties]

#             file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-Logs/"+modelname,file_path=filename)
#             # [END create_file_client]
#             filepath = current_directory +"/"+filename
#             # print('filepath-', filepath)
#             # Upload a files
#             with open(filepath, "rb") as source_file:
#                 file.upload_file(source_file)            
#             print("uploaded")   
#             return "Success", "app log file uploading completed"
#         if deletefile == True:
#             print("delete file yes")
#             os.remove(filepath)
#             print('file deleted.')
#     except Exception as ex:
#         print(f"Azure log file upload error -- {ex}")
#         return "Error", ex
        

# def AppAzureExtractionLogs(logMessages: str, contractID):
#     try:
        
#         dt = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        
#         from sqlalchemy import select
#         db = Session(bind=engine, expire_on_commit=False)
#         model_name = db.query(models.contracts).filter(models.contracts.id==contractID).first()
#         print("modelname- ", model_name.displayModelName)        
#         db.close()
        
#         my_modelname = re.sub('[^a-zA-Z0-9 \n\.]', '', model_name.displayModelName)
#         modelname = my_modelname.replace(" ", "_").lower()  
#         filename = dt

#         with open(filename, mode='w') as log_file:
#             content = f"{logMessages}"
#             log_file.write('\n')
#             log_file.write(content) 

#             current_directory = os.getcwd()
#             rm_dirPath = os.path.join(current_directory)
#             share = ShareClient.from_connection_string(connection_string, share_name=azureShareName)
#             filesdir = []
#             filesdir.append(os.path.join(filename))
            
#             try:
#                 NLPModel = share.get_directory_client("nlp-extraction")
#                 NLPModel.create_directory()
#             except ResourceExistsError:
#                 pass
#             except ssl.CertificateError:
#                 pass
#             try:
#                 NLPModel_ProjectName = share.get_directory_client("nlp-extraction/"+modelname)
#                 NLPModel_ProjectName.create_directory()
#             except ResourceExistsError:
#                 pass
#             except ssl.CertificateError:
#                 pass 
#             properties = share.get_share_properties()
            
#             file = ShareFileClient.from_connection_string(connection_string,share_name=azureShareName +"/nlp-extraction/"+modelname,file_path=filename)
            
#             filepath = current_directory +"/"+filename

#             with open(filepath, "rb") as source_file:
#                 file.upload_file(source_file)            
#             print("uploaded")  

#     except Exception as ex:
#         print(f"Azure log file upload error -- {ex}")
#         return "Error", ex

################################### App logs Ends here ###################################################################################

# @router.post('/testAPI')
# async def testAPI():
#    print("testing purpose")
    
# ## CREATE ARRAY FUNCTION --- called in main data split function
# def create_array(split,text_length):
#     #split_by=int(input('Enter split input: '))
#     cycles = text_length//split 
#     #print(cycles)
#     array=[]
#     if (text_length % split == 0):
#         var = split
#         for i in range(cycles):
#             array.append(var)
#             var+=split
#         print("Array: ",array)
#     else:
#         var = split
#         for i in range(cycles+1):
#             array.append(var)
#             var = var+split
#             #print('Cycle1:',var)
#         print("Array: ",array)
        
#     return array

# ## Generic Function Logic
# def data_split_modified(split,orig_len, data):

#     for j in range(0, orig_len):   # 12
#         full_text = data['trainingData'][j]['text']  # j = file number
#         low = 0
#         split_by = split
        
#         array = create_array(split,len(full_text)) ## CALL NEW FUNCTION
        
#         ### UPDATE SPLIT VALUE
#         for k in range(len(array)):
#             for i in data['trainingData'][j]['entities']:
#                 #if i['end'] > low and i['end'] <= array[j]:
#                 if i['start'] < low and i['end'] > low:
#                     value_add = i['end']-i['start']
#                     print("Value to be added: ",value_add)
#                     array[k-1] = array[k-1] + value_add
#                     position = k-1
#                     print("position: ",position)
#                     print("Stage1: ",array)
#                     for x in data['trainingData'][j]['entities']:
#                         if x['start'] < array[position] and x['end'] > array[position]:
#                             array[position] = array[position] + (x['end'] - array[position])
#                             print("Difference found. Updating array!!")
#                     #temp_list.append(value_add)
#                     print('Entity: ',i['label'])
            
#             low = array[k]   
#         print('New Array: ',array)
#         ### SPLIT LOGIC STARTS !!!!!!!!!!!!!!!!!!!!!!!!!!!
            
#         if (len(full_text)% split == 0):
            
#             low = 0
#             for x in range(len(array)):
#                 split_new = array[x]
#                 print('Low start: ',low)
#                 print('Split_new start: ',split_new)
#                 text1 = full_text[low:split_new]       # Character limit
#                 ## Entity structure creation
#                 entities_split=[{'start': 0,
#                              'end': 0,
#                              'label': '',
#                              'fieldMappingID': ''}] * len(data['trainingData'][0]['entities'])
#                 counter = 0   # counter for entity split
#                 ## Entity collection on split data
#                 for i in data['trainingData'][j]['entities']: # max 11 3 3
#                     if i['end'] > low and i['end'] <= split_new:
#                         print('Entered:',counter)
#                         entities_split[counter] = i
#                         entities_split[counter]['start'] = entities_split[counter]['start'] - low
#                         entities_split[counter]['end'] = entities_split[counter]['end'] - low
#                         entities_split[counter]['fieldMappingID'] = entities_split[counter]['fieldMappingID']
#                         counter+=1
          
#                 entities_split = entities_split[0:counter]
#                 # print("Length: ",len(entities_split))
#                 # print(text1)
#                 # print('Main else',entities_split)
#                 dict1 = {"text":text1,"entities":entities_split,"fileID":data['trainingData'][j]["fileID"]}
#                 data['trainingData'].append(dict1)
#                 low = split_new
#         else:
#             low = 0
#             for x in range(len(array)):
#                 split_new = array[x]
#                 print('Low start: ',low)
#                 print('Split_new start: ',split_new)
#                 text1 = full_text[low:split_new]       # Character limit
#                 ## Entity structure creation
#                 entities_split=[{'start': 0,
#                              'end': 0,
#                              'label': '',
#                              'fieldMappingID': ''}] * len(data['trainingData'][0]['entities'])
#                 counter = 0   # counter for entity split
#                 ## Entity collection on split data
#                 for i in data['trainingData'][j]['entities']: # max 11 3 3
#                     if i['end'] > low and i['end'] <= split_new:
#                         print('Entered:',counter)
#                         entities_split[counter] = i
#                         entities_split[counter]['start'] = entities_split[counter]['start'] - low
#                         entities_split[counter]['end'] = entities_split[counter]['end'] - low
#                         entities_split[counter]['fieldMappingID'] = entities_split[counter]['fieldMappingID']
#                         counter+=1

#                 entities_split = entities_split[0:counter]
#                 # print("Length: ",len(entities_split))
#                 # print(text1)
#                 # print('Main else',entities_split)
#                 dict1 = {"text":text1,"entities":entities_split,"fileID":data['trainingData'][j]["fileID"]}
#                 data['trainingData'].append(dict1)
#                 low = split_new

#     # print('Length of original training data', orig_len)
#     del(data['trainingData'][0:orig_len])
#     # print('Length of trimmed training data', len(data['trainingData']))
#     return data
