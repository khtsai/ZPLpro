'''
Created on Dec 14, 2017

@author: Chuck
'''

import subprocess
from tempfile import NamedTemporaryFile
from os import remove
import logging
import sys

databaseFilePath = "database.txt"
printerName = ""
QRCodeXPosition = "30"
QRCodeYPosition = "30"
textXPosition = "50"
textYPosition = "300"
parameterList = ["databaseFilePath", "printerName", "QRCodeXPosition"\
                 ,"QRCodeYPosition", "textXPosition", "textYPosition"\
                 ,"debugMode"]
ZPLTemplate = ""
filePath = ""
config = dict()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('ZPLPrinter.log',encoding="utf-16")
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

#printLogging = logging.StreamHandler(sys.stdout)
#logger.addHandler(printLogging)

logger.info('Starting the program...')

try:
    with open('config.txt', 'r', encoding = 'utf-16') as configFile:
        logger.info("Opening config.txt...")
        items = configFile.readlines()
        for item in items:
            if '=' in item:
                logger.debug("Config item {}".format(item))
                key,value = item.split('=', 1)
                logger.debug("Key: {} and Value: {}".format(key,value))
                config[key]=str(value)
                if key not in parameterList:
                    logger.debug("Incorrect parameter {}.".format(key))
            else:
                logger.debug("Config file is not correct!!!!!!!")
    
    logger.info("Finished initializing the config...")
    
    with open(databaseFilePath, encoding = 'utf-16-le') as file:  
        logger.info("Opening database {}...".format(databaseFilePath))
        data = file.readlines() 
    
    logger.info("-"*20)
    logger.info("Finished reading the database...")
    logger.info("-"*20)
            
    for line in data:
        logger.debug("Data item {}".format(line))
        barcodeData, dateData = line.split(",")
        logger.debug("barcodeData: {} and dateData: {}".format(barcodeData, dateData))
        ZPLTemplate += """^XA
    ^BQN,2,10
    ^FO{},{}^FDQA{}^FS
    ^CF0,30
    ^FO{},{}^FD{}^FS
    ^XZ""".format(QRCodeXPosition,QRCodeYPosition,barcodeData,textXPosition,textYPosition,dateData)
        ZPLTemplate += "\n"
        logger.debug(ZPLTemplate)
    
    logger.info("-"*20)
    logger.info("Finished creating ZPL commands...")
    logger.info("-"*20)
    
    with NamedTemporaryFile(delete = False) as file:
        logger.info("Created a temp file...")  
        file.write(ZPLTemplate.encode(encoding='utf-8', errors='strict'))
        printerName = "ZPLSender"#"Zebra ZM400 (203 dpi) - ZPL"
        filePath = file.name
    
    #ssdal.exe /p "[i]PrinterName[/i]" send "[i]FilePathAndName[/i]"
    shellCMD = "ssdal.exe /p \"{}\" send \"{}\"".format(printerName,filePath)
    logger.info("Sending the ZPL commands to the printer...")
    logger.debug(shellCMD)
    output = subprocess.check_output(shellCMD, shell=True)
    logger.debug("CMD: {}".format(str(output)))
    
    remove(filePath)
    logger.debug("Have removed the temp file {}".format(filePath))

except Exception:
    logging.exception('Caught this error....')
    