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
		self.org = self.client.service.OrganizationQueryRoot() #Returns whole SOAP Request.
		self.orgid = self.client.service.OrganizationQueryRoot()[0]  #Returns OrgId.

def main():
	service = Service()
	print service.org



if __name__ == '__main__':
	main()
