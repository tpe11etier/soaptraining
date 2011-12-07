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

def createMember(service):
	service = service
	member = service.client.factory.create('Member')
	members = service.client.factory.create('ArrayOfMember')
	contactmethod = service.client.factory.create('ContactMethod')
	contactmethodemail = service.client.factory.create('ContactMethodEmail')
	contactmethods = service.client.factory.create('ArrayOfContactMethod')
	contactmethodemail.Qualifier = 'Office'
	contactmethodemail.EmailAddress = 'tony.pelletier@varolii.com'
	contactmethod.ContactMethodEmail = contactmethodemail
	contactmethods.ContactMethod.append(contactmethod)
	member.Username = 'blahblah3'
	member.FirstName = 'blah'
	member.LastName = 'blah'
	member.Password = 'Blah$1Blah'
	member.AccountEnabled = 'True'
	member.OrganizationId = service.orgid
	member.ContactMethods = contactmethods
	members.Member.append(member)
	print members
	try:
		print service.client.service.MemberCreate(members)
	except suds.WebFault as e:
		print e.fault.detail

def main():
	service = Service()
	createMember(service)


if __name__ == '__main__':
	main()
