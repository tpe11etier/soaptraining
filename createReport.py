#!/usr/bin/env python

#Imports
import suds
import ConfigParser

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

def createReport(service):
	paramsdict = {'EventId':'kxtttkqxk'}
	#paramsdict = {'DateRange': '{ts \'2011-12-05 00:00:00.0\'\},\{ts \'2011-12-06 00:00:00.0\'\}'}

	#Object creation
	report = service.client.factory.create('Report')
	reports = service.client.factory.create('ArrayOfReport')

	reportparams = service.client.factory.create('ArrayOfReportParameter')

	for k,v in paramsdict.items():
		reportparam = service.client.factory.create('ReportParameter')
		reportparam.Name = k
		reportparam.Value = v
		reportparams.ReportParameter.append(reportparam)

	report.OutputFormat = 'excel'
	report.Name = 'SOAP Test'
	report.ZipOutput = 'False'
	report.ReportTypeId = '9971'
	report.TimeZoneId = '123'
	report.ReportParameters = reportparams
	reports.Report.append(report)
	print report


	#Make the request.
#'''
	try:
		print service.client.service.ReportCreate(reports)
	except suds.WebFault as e:
		print e.fault.detail
#'''
def main():
	service = Service()
	createReport(service)


if __name__ == '__main__':
	main()