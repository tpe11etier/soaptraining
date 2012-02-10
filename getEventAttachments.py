#!/usr/bin/env python

#Imports
import suds
import ConfigParser
import base64
import csv
import os, sys
import zipfile
import paramiko



CONF = ConfigParser.ConfigParser()
try:
	CONF.read("soap.props")
except IOError as e:
	print 'File %s not found!' % e

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

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


def getEventIds(filename):
	#Get EventId's from the 14th(15th really) which is where the report should always have it.

	filename = filename
	eventIds = []
	finalIds = []
	reader = csv.reader(open(filename, 'r'))
	reader.next() #Skip Header


	#I only want the event id's that have attachments so I'm checking the Filename column for a value first.
	for row in reader:
		if row[15] != '':
			if row[14] != '':
				eventIds.append(int(row[14]))

	#The same event id will be returned numerous times so I'm only keep distinct values.
	for id in eventIds:
		if id not in finalIds:
			finalIds.append(id)
	return finalIds


def getEventAttachments(service):
	service = service

	#docs = [734376, 734463, 734519,734622]
	try:
		eventIds = getEventIds(raw_input("Enter CSV filename: "))
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
			if not os.path.exists("files"):
				os.makedirs("files")

			outfile = open(os.path.join('files',filename), 'wb')
			outfile.write(data)
			outfile.close()
			print filename + ' successfully written out!'
	except suds.WebFault as e:
		print e.fault.detail


def zipFiles():
	print '\nCreating archive...\n'
	zf = zipfile.ZipFile('attachments.zip', mode='w')
	try:
		for file in os.listdir('files'):
			print file
			zf.write(file)
	finally:
		print '\nDone zipping attachments\n.'
		zf.close()


def ftpFiles():
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(
		paramiko.AutoAddPolicy())
		ssh.connect('127.0.0.1', port=22, username='tpelletier', password='tpelletier')
		ftp = ssh.open_sftp()
		print 'Starting file transfer...'
		ftp.put('attachments.zip','incoming/attachments.zip', None)
		print 'File attachments.zip successfully transferred.'
		ftp.close()
	except Exception as e:
		print e



def main():
	service = Service()
	getEventAttachments(service)
	zipFiles()
	ftpFiles()


if __name__ == '__main__':
	main()
