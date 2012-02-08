#!/usr/bin/env python

#Imports
import suds
import ConfigParser
import base64

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


def getEventAttachments(service):
	service = service

	#Word Doc 734463
	#No attachment Event

	docs = [734376, 734463]

	try:
		#Create Objects
		eventresult = service.client.factory.create('ArrayOfEvent')
		event = service.client.factory.create('ArrayOfstring')

		#Enumerate list of event id's to append to ArrayOfstring and make one SOAP call.
		for index, eventid in enumerate(docs):
			event.string.append(eventid)
		eventresult = service.client.service.EventQueryById(event, 'true')

		#Add Filename and Encoded value to a dictionary(key/value pairs).
		numofevents = len(eventresult.Event)
		files = {}
		num = 0
		while num < numofevents:
			files[eventresult.Event[num].EventFileArgs.EventFileArg[0].UserFileName] = str(eventresult.Event[num].EventFileArgs.EventFileArg[0].EncodedValue)
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
			outfile = open(filename, 'wb')
			outfile.write(data)
			outfile.close()
			print filename + ' successfully written out!'
	except suds.WebFault as e:
		print e.fault.detail


def main():
	service = Service()
	getEventAttachments(service)


if __name__ == '__main__':
	main()
