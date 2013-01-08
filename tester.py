#!/usr/bin/env python

#Imports
import suds

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'


class Service(object):
    def __init__(self):
        """
        Creates header information required for any SOAP request.
        GS  gsoem   t$eN3uz*
        """
        self.client = suds.client.Client(url)
        header = self.client.factory.create('AuthHeader')
        header.Domain = 'GS'
        header.UserId = 'psadmin'
        header.UserPassword = 'W!sc0nsin'
        header.OemId = 'gsoem'
        header.OemPassword = 't$eN3uz*'
        self.client.set_options(soapheaders=header)
        self.orgid = self.client.service.OrganizationQueryRoot()[0]


def create_member(service):
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


def query_teams(service):
    service = service
    orgs = service.client.factory.create('ArrayOfstring')
    orgs.string.append(service.orgid)
    try:
        print service.client.service.TeamQueryByOrganizationId(orgs, 0, 20)
    except suds.WebFault as e:
        print e.fault.detail


def query_team_by_id(service):
    service = service

    teamids = [2021145]
    teams = service.client.factory.create('ArrayOfstring')
    for teamid in teamids:
        teams.string.append(teamid)

    try:
        print service.client.service.TeamQueryById(teams)
    except suds.WebFault as e:
        print e.fault.detail


def team_update_by_id(service):
    service = service

    #teamids = [1189458, 1239030, 1360521, 1521640, 1997660]
    team = service.client.factory.create('Team')
    print team
    teams = service.client.factory.create('ArrayOfTeam')

    team.TeamId = 'k85pdk9q3'
    team.Name = 'CACTUS  Development'
    team.Type = 'Phase'
    team.ReadOnlyInUserInterface = 'True'

    teams.Team.append(team)
    print teams
    try:
        print service.client.service.TeamUpdate(teams, 'false')
    except suds.WebFault as e:
        print e.fault.detail


def main():
    service = Service()
    # query_team_by_id(service)
    team_update_by_id(service)



if __name__ == '__main__':
    main()
