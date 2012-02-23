#!/usr/bin/env python

"""
This program will do SOAP calls to accomplish the following.
	- Makes a SOAP request to create a report
	- Makes a SOAP request to query report using the report id from the prior call and writes the csv out to the file
	  system.
	- Parses the csv to grab the event id's then uses those to get the files to write out.  Only unique event id's will
	  be used as well as only rows that contain an attachment.
	- Once the files are completed being written out, they are zipped and sent to an ftp site.
"""

#Imports
import suds
import ConfigParser
import base64
import csv
import os, sys
import shutil
import zipfile
import paramiko
import datetime, time
import logging



CONF = ConfigParser.ConfigParser()
try:
	CONF.read("soap.props")
except IOError as e:
	print 'File %s not found!' % e

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s', filename=CONF.get("Logging", "FileName"), filemode='w')


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
	#Creating a new files directory before each run to make sure old data is cleaned out.
	#TODO Make this date based and leave the old directories around
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


def create_report(service, days, format, name, zipoutput, reporttypeid, timezoneid):
	logging.info('Report creation process started...')
	delta = datetime.timedelta(days=days)
	DateRange_End = datetime.datetime.today()
	DateRange = DateRange_End - delta
	d = str(DateRange) + ',' + str(DateRange_End)
	paramsdict = {'DateRange': d}

	#Object creation
	report = service.client.factory.create('Report')
	reports = service.client.factory.create('ArrayOfReport')
	reportparams = service.client.factory.create('ArrayOfReportParameter')

	#Iterate the dictionary to create a new ReportParameter.  Depending on the report run, this might be more than the one.
	for k,v in paramsdict.items():
		reportparam = service.client.factory.create('ReportParameter')
		reportparam.Name = k
		reportparam.Value = v
		reportparams.ReportParameter.append(reportparam)

	report.OutputFormat = format
	report.Name = name
	report.ZipOutput = zipoutput
	report.ReportTypeId = reporttypeid
	report.TimeZoneId = timezoneid
	report.ReportParameters = reportparams
	reports.Report.append(report)


	#Make the request.
	try:
		result = service.client.service.ReportCreate(reports)
		return result.ResponseEntry[0].Id
	except suds.WebFault as e:
		print e.fault.detail
		sys.exit()



def get_report(service, reportId):
	reportIds = service.client.factory.create('ArrayOfstring')
	reportIds.string.append(reportId)

	try:
		result = service.client.service.ReportQueryById(reportIds, 'True')

		if result.Report[0].ReportStatus == 'Completed':
			print 'Report is in Completed state.'
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
			return result
		else:
			print 'Report is still in Processing state...'
			return None

	except suds.WebFault as e:
		print e.fault.detail





def get_event_ids(filename):
	filename = filename

	#Get EventId's from the 14th(15th really) which is where the report should always have it.
	eventIds = []
	finalIds = []

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



def get_event_attachments(service, filename):
	service = service
	filename = filename
	try:
		eventIds = get_event_ids(filename)
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


def zip_files():
	print '\nCreating archive...\n'
	logging.info('\nCreating archive...\n')
	try:
		file = os.path.join('files', 'attachments.zip')
		zf = zipfile.ZipFile(file, mode='w')
		for file in os.listdir('files'):
			if file == 'attachments.zip':
				pass
			else:
				print file
				zf.write(os.path.join('files', file))

		print '\nDone zipping attachments\n.'
		logging.info('\nDone zipping attachments\n.')
		zf.close()
	except IOError as e:
		print e


def ftpFiles(server, port, login, password):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(
			paramiko.AutoAddPolicy())
		ssh.connect(server, port=port, username=login, password=password)
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
	cleanup()
	reportId = create_report(service, 30, 'csv', 'Weekly Deliveries Report', 'False', '19845', '123')
	try:
		result = get_report(service,reportId)
		while result is None:
			time.sleep(3)
			result = get_report(service,reportId)
		else:
			filename =  result.Report[0].ReportFileArgs.ReportFileArg[0].UserFileName
			get_event_attachments(service, filename)
	except suds.WebFault as e:
		print e

	zip_files()
	ftpFiles('127.0.0.1', 22, 'tpelletier', 'tpelletier')


if __name__ == '__main__':
	main()
