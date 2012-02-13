#!/usr/bin/env python

#Imports
import suds
import ConfigParser
import datetime
import base64
import time

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



def queryReport(service):
	delta = datetime.timedelta(min=10)
	start = str(datetime.datetime(2012, 2, 12, 00, 00, 00))
	end = str(datetime.datetime(2012, 2, 13, 00, 00, 00))
	status = 'Completed'
	reportTypeName = 'Completed Deliveries Billing Detail CSV'
	organizationId = service.orgid
	includeFiles = 'True'
	index = 0
	length = 1


	print service.client.service.ReportQueryByDateRangeStatusReportTypeNameOrganizationId(start, end, status, reportTypeName, organizationId, includeFiles, index, length)



def main():
	service = Service()
	queryReport(service)

if __name__ == '__main__':
	main()