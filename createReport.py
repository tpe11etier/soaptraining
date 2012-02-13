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

def createReport(service):
	#DateRange = datetime.datetime(2012, 2, 1, 00, 00, 00)
	#DateRange_End = datetime.datetime(2012, 2, 15, 00, 00, 00)
	delta = datetime.timedelta(days=7)
	DateRange_End = datetime.datetime.today()
	DateRange = DateRange_End - delta


	d = str(DateRange) + ',' + str(DateRange_End)


	#paramsdict = {'DateRange': DateRange,'DateRange_End': DateRange_End}
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
	report.ReportTypeId = '9969'
	report.TimeZoneId = '123'
	report.ReportParameters = reportparams
	reports.Report.append(report)
	print report


	#Make the request.
	try:
		result =  service.client.service.ReportCreate(reports)
		return  result.ResponseEntry[0].Id
	except suds.WebFault as e:
		print e.fault.detail


def getReport(service, reportid):
	reports = service.client.factory.create('ArrayOfstring')
	reports.string.append(reportid)
	try:
		result = service.client.service.ReportQueryById(reports, 'True')
		if  result.Report[0].ReportStatus == 'Completed':
			filename =  result.Report[0].ReportFileArgs.ReportFileArg[0].UserFileName
			encodedfile = result.Report[0].ReportFileArgs.ReportFileArg[0].EncodedValue

			encodedstring = encodedfile.encode('utf-8')
			str_list = []
			for line in encodedstring:
				line = line.rstrip()
				str_list.append(line)
			string = ''.join(str_list)
			data = base64.b64decode(string)
			print data
			outfile = open(filename, 'w')
			outfile.write(data)
			outfile.close()
		else:
			print 'Report still running...'
			time.sleep(5)
			getReport(service,reportid)
	except suds.WebFault as e:
		print e.fault.detail


def main():
	service = Service()
	reportid = createReport(service)
	getReport(service,reportid)

if __name__ == '__main__':
	main()