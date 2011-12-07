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

def createEvent(service):
	#Details of the email.
	argsdict = {'EMAIL_ADDR': 'tony.pelletier@varaolii.com', 'SUBJECT':'Test Message', 'BODY':'This is the Body.', 'SENDER':'tony.pelletier@gmail.com'}

	#Object creation
	event = service.client.factory.create('Event')
	events = service.client.factory.create('ArrayOfEvent')
	team = service.client.factory.create('EventTeam')
	teams = service.client.factory.create('ArrayOfEventTeam')
	aargs = service.client.factory.create('ArrayOfEventArg')
	team.TeamId = 'ks3d5kkkb'
	teams.EventTeam.append(team)

	for k,v in argsdict.items():
		args = service.client.factory.create('EventArg')
		args.Name = k
		args.Value = v
		aargs.EventArg.append(args)
	event.Status = 'Unknown'
	event.EventTypeId = '2634'
	event.EventArgs = aargs
	event.EventTeams = teams
	events.Event.append(event)

	#Make the request.
	try:
		print service.client.service.EventCreate(events)
	except suds.WebFault as e:
		print e.fault.detail

def main():
	service = Service()
	createEvent(service)


if __name__ == '__main__':
	main()