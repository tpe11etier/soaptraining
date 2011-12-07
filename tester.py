#!/usr/bin/env python

#Imports
import suds

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

class Service(object):
	def __init__(self):
		"""
        Creates header information required for any SOAP request.
        """
		self.client = suds.client.Client(url)
		header = self.client.factory.create('AuthHeader')
		header.Domain = 'TPELLETIER'
		header.UserId = 'soaptester'
		header.UserPassword = 'Soap$1Tester'
		header.OemId = 'TPELLETIERoem'
		header.OemPassword = 'TPELLETIER$1oem'
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
	member.Username = 'blahblah2'
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



def queryTeams(service):
	service = service
	orgs = service.client.factory.create('ArrayOfstring')
	orgs.string.append(service.orgid)
	try:
		print service.client.service.TeamQueryByOrganizationId(orgs,0,20)
	except suds.WebFault as e:
		print e.fault.detail

def main():
	service = Service()
	queryTeams(service)


if __name__ == '__main__':
	main()
