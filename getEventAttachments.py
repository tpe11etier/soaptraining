#!/usr/bin/env python

#Imports
import suds
import ConfigParser
import base64
import csv
import os, sys
import shutil
import zipfile
import paramiko
import datetime
import time
import logging


CONF = ConfigParser.ConfigParser()
try:
	CONF.read("soap.props")
except IOError as e:
	print 'File %s not found!' % e

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s', filename=CONF.get("Logging", "FileName"), filemode='w')
#logging.basicConfig(level=CONF.get("Logging", "Level"),format='%(asctime)s %(levelname)s %(message)s', filename=CONF.get("Logging", "FileName"), filemode='w')

class Service(object):
	def __init__(self):
		"""
        Creates header information required for any SOAP request.
        """
		self.client = suds.client.Client(url)
		header = self.client.factory.create('AuthHeader')
		header.Domain = CONF.get("Auth Header", "domain")
		header.UserId = CONF.get("Auth Header", "userid")
		header.UserPassword = CONF.get("Auth Header", "userpassword")
		header.OemId = CONF.get("Auth Header", "oemid")
		header.OemPassword = CONF.get("Auth Header", "oempassword")
		self.client.set_options(soapheaders=header)
		self.orgid = self.client.service.OrganizationQueryRoot()[0]



def cleanup():
	try:
		if not os.path.exists("files"):
			print 'Creating "files" directory...'
			logging.info('Creating "files" directory...')
			os.makedirs("files")
			print '"files" directory successfully created...'
			logging.info('"files" directory successfully created...')
		else:
			shutil.rmtree("files")
			print 'Deleting "files" directory...'
			logging.info('Deleting "files" directory...')
			os.makedirs("files")
			print '"files" directory successfully created...'
			logging.info('"files" directory successfully created...')
	except Exception as e:
		print e


def createReport(service):
	logging.info('Report creation process started...')
	delta = datetime.timedelta(days=15)
	DateRange_End = datetime.datetime.today()
	DateRange = DateRange_End - delta

	d = str(DateRange) + ',' + str(DateRange_End)

	paramsdict = {'DateRange': d}
	#Object creation
	report = service.client.factory.create('Report')
	reports = service.client.factory.create('ArrayOfReport')
	reportparams = service.client.factory.create('ArrayOfReportParameter')

	for k,v in paramsdict.items():
		reportparam = service.client.factory.create('ReportParameter')
		reportparam.Name = k
		reportparam.Value = v
		reportparams.ReportParameter.append(reportparam)

	report.OutputFormat = 'csv'
	report.Name = 'Weekly Deliveries Report'
	report.ZipOutput = 'False'
	report.ReportTypeId = '19845'
	report.TimeZoneId = '123'
	report.ReportParameters = reportparams
	reports.Report.append(report)


	#Make the request.
	try:
		result =  service.client.service.ReportCreate(reports)
	except suds.WebFault as e:
		print e.fault.detail
		sys.exit()

def queryReport(service):
	deltastart = datetime.timedelta(minutes=5)
	deltaend = datetime.timedelta(minutes=5)
	end = datetime.datetime.now() + deltaend
	start = datetime.datetime.now() - deltastart

	status = 'Completed'
	reportTypeName = 'ED Completed Deliveries Billing Detail CSV'
	organizationId = service.orgid
	includeFiles = 'True'
	length = 1

	try:
		index = service.client.service.ReportQueryByDateRangeStatusReportTypeNameOrganizationIdLength(start, end, status, reportTypeName, organizationId)
		if index is 0:
			print 'Report not found.  Still running?'
			time.sleep(5)
			getEventIds(service)
		else:
			index -= 1
			result = service.client.service.ReportQueryByDateRangeStatusReportTypeNameOrganizationId(start, end, status, reportTypeName, organizationId, includeFiles, index, length)
			return result
	except suds.WebFault as e:
		print e.fault.detail



def getReport(service):
	try:
		result = queryReport(service)
		if not isinstance(result, suds.sax.text.Text):
			filename =  result.Report[0].ReportFileArgs.ReportFileArg[0].UserFileName
			encodedfile = result.Report[0].ReportFileArgs.ReportFileArg[0].EncodedValue

			encodedstring = encodedfile.encode('utf-8')
			str_list = []
			for line in encodedstring:
				line = line.rstrip()
				str_list.append(line)
			string = ''.join(str_list)
			data = base64.b64decode(string)
			outfile = open(filename, 'w')
			outfile.write(data)
			outfile.close()
			shutil.copyfile(filename, os.path.join('files', filename))
			print filename + ' report succesfully written out...'
			logging.info(filename + ' report succesfully written out...')
			return filename
	except suds.WebFault as e:
		print e.fault.detail


def getEventIds(service):
	service = service

	#Get EventId's from the 14th(15th really) which is where the report should always have it.
	eventIds = []
	finalIds = []
	filename = getReport(service)

	if filename is not None:
		try:
			reader = csv.reader(open(filename, 'r'))
			reader.next() #Skip Header
			#I only want the event id's that have attachments so I'm checking the Filename column for a value first.
			for row in reader:
				print row
				logging.info(row)
				if row:
					if row[18] != '':
						if row[17] != '':
							eventIds.append(int(row[17]))

			#The same event id will be returned numerous times so I'm only keep distinct values.
			for id in eventIds:
				if id not in finalIds:
					finalIds.append(id)
			return finalIds
		except Exception as e:
			print e
	else:
		print 'File still being written out...'
		sys.exit()



def getEventAttachments(service):
	service = service
	try:
		eventIds = getEventIds(service)
	except Exception as e:
		print e
		sys.exit()


	try:
		#Create Objects
		event = service.client.factory.create('ArrayOfstring')

		#Enumerate list of event id's to append to ArrayOfstring and make one SOAP call.
		for index, eventid in enumerate(eventIds):
			event.string.append(eventid)

		#Make the SOAP call and store the results in eventresult
		#The boolean determines whether attachments are included in the response.
		#True if all attachments should be included with a response document.
		#False if you don't want attachments in a response document.
		eventresult = service.client.service.EventQueryById(event, 'true')

		#Get number of event's returned
		numofevents = len(eventresult.Event)

		#Add Filename(s) and Encoded value(s) to a dictionary(key/value pairs).
		files = {}
		num = 0
		while num < numofevents:
			numofattachments = len(eventresult.Event[num].EventFileArgs.EventFileArg)
			numa = 0
			while numa < numofattachments:
				files[eventresult.Event[num].EventFileArgs.EventFileArg[numa].UserFileName] = str(eventresult.Event[num].EventFileArgs.EventFileArg[numa].EncodedValue)
				numa += 1
			num += 1


		#Iterate the dictionary and decode the values to write them out.
		for filename, encodedfile in files.items():
			encodedstring = encodedfile.encode('utf-8')
			str_list = []
			for line in encodedstring:
				line = line.rstrip()
				str_list.append(line)
			string = ''.join(str_list)
			data = base64.b64decode(string)


			outfile = open(os.path.join('files',filename), 'wb')
			outfile.write(data)
			outfile.close()
			print filename + ' successfully written out!'
			logging.info(filename + ' successfully written out!')
	except suds.WebFault as e:
		print e.fault.detail


def zipFiles():
	print '\nCreating archive...\n'
	logging.info('\nCreating archive...\n')
	file = os.path.join('files', 'attachments.zip')
	zf = zipfile.ZipFile(file, mode='w')
	try:
		for file in os.listdir('files'):
			if file == 'attachments.zip':
				pass
			else:
				print file
				zf.write(os.path.join('files', file))
	finally:
		print '\nDone zipping attachments\n.'
		logging.info('\nDone zipping attachments\n.')
		zf.close()


def ftpFiles():
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(
			paramiko.AutoAddPolicy())
		ssh.connect('127.0.0.1', port=22, username='tpelletier', password='tpelletier')
		ftp = ssh.open_sftp()
		print 'Starting file transfer...'
		logging.info('Starting file transfer...')
		ftp.put(os.path.join('files','attachments.zip'),'incoming/attachments.zip', None)
		print 'File attachments.zip successfully transferred.'
		logging.info('File attachments.zip successfully transferred.')
		ftp.close()
	except Exception as e:
		print e



def main():
	service = Service()
	createReport(service)
	time.sleep(3)
	getEventAttachments(service)
	zipFiles()
	ftpFiles()


if __name__ == '__main__':
	main()
