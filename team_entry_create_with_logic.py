#!/usr/bin/env python

# Imports
import suds
import ConfigParser

CONF = ConfigParser.ConfigParser()
try:
    CONF.read("soap.props")
except IOError as e:
    print 'File %s not found!' % e

# WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'
# url = 'https://ws.envoyprofiles.com/WebService/EPAPI_1.0/wsdl.wsdl'


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


def team_entry_create_selection_criteria(service):
    '''
    Creates Selection Criteria Team Entry for a given TeamId with AND logic
    ((Location = Boston) And (Floor = First))
    '''
    # Create Team Objects
    team_entry = service.client.factory.create('TeamEntry')
    array_team_entry = service.client.factory.create('ArrayOfTeamEntry')

    # Create Selection Criteria Objects
    team_entry_selection_criteria = service.client.factory.create('TeamEntrySelectionCriteria')
    selection_criteria = service.client.factory.create('SelectionCriteria')
    selection_criteria_logic = service.client.factory.create('SelectionCriteriaLogic')

    ####################################################################################################
    # Left Side of Selection Criteria Begin
    ####################################################################################################

    # Create Left Side Objects
    LEFT_selection_criteria_relationship = service.client.factory.create('SelectionCriteriaRelationship')
    LEFT_selection_criteria_LHSvalue = service.client.factory.create('SelectionCriteriaValue')
    LEFT_selection_criteria_RHSvalue = service.client.factory.create('SelectionCriteriaValue')
    LEFT_selection_criteria_LHSvalue_custom_field = service.client.factory.create('SelectionCriteriaValueCustomField')
    LEFT_selection_criteria_RHSvalue_string = service.client.factory.create('SelectionCriteriaValueString')


    # Specify the Organization Custom Field ID to use and the ValueString
    LEFT_selection_criteria_LHSvalue_custom_field.ValueOrganizationCustomFieldId = 'kitn3ku8k'
    LEFT_selection_criteria_RHSvalue_string.ValueString = 'Boston'
    LEFT_selection_criteria_LHSvalue.SelectionCriteriaValueCustomField = LEFT_selection_criteria_LHSvalue_custom_field
    LEFT_selection_criteria_RHSvalue.SelectionCriteriaValueString = LEFT_selection_criteria_RHSvalue_string


    # Set the relationship type. Type is 'Equal'
    # This reads as Location = 'Boston'
    LEFT_selection_criteria_relationship.Type = 'Equal'
    LEFT_selection_criteria_relationship.LHSSelectionCriteriaValue = LEFT_selection_criteria_LHSvalue
    LEFT_selection_criteria_relationship.RHSSelectionCriteriaValue = LEFT_selection_criteria_RHSvalue

    ####################################################################################################
    # Left Side of Selection Criteria End
    ####################################################################################################


    ####################################################################################################
    # Right Side of Selection Criteria Begin
    ####################################################################################################

    # Create Right Side Objects
    RIGHT_selection_criteria_relationship = service.client.factory.create('SelectionCriteriaRelationship')
    RIGHT_selection_criteria_LHSvalue = service.client.factory.create('SelectionCriteriaValue')
    RIGHT_selection_criteria_RHSvalue = service.client.factory.create('SelectionCriteriaValue')
    RIGHT_selection_criteria_LHSvalue_custom_field = service.client.factory.create('SelectionCriteriaValueCustomField')
    RIGHT_selection_criteria_RHSvalue_string = service.client.factory.create('SelectionCriteriaValueString')

    # Specify the Organization Custom Field ID to use and the ValueString
    RIGHT_selection_criteria_LHSvalue_custom_field.ValueOrganizationCustomFieldId = 'ka5htkuhk'
    RIGHT_selection_criteria_RHSvalue_string.ValueString = 'First'
    RIGHT_selection_criteria_LHSvalue.SelectionCriteriaValueCustomField = RIGHT_selection_criteria_LHSvalue_custom_field
    RIGHT_selection_criteria_RHSvalue.SelectionCriteriaValueString = RIGHT_selection_criteria_RHSvalue_string


    # Set the relationship type. Type is 'Equal'
    # This reads as Floor = 'First'
    RIGHT_selection_criteria_relationship.Type = 'Equal'
    RIGHT_selection_criteria_relationship.LHSSelectionCriteriaValue = RIGHT_selection_criteria_LHSvalue
    RIGHT_selection_criteria_relationship.RHSSelectionCriteriaValue = RIGHT_selection_criteria_RHSvalue

    selection_criteria_logic.Type = 'And'
    selection_criteria_logic.LHSSelectionCriteriaRelationship = LEFT_selection_criteria_relationship
    selection_criteria_logic.RHSSelectionCriteriaRelationship = RIGHT_selection_criteria_relationship

    ####################################################################################################
    # Right Side of Selection Criteria End
    ####################################################################################################


    # The selection criteria name is 'JPMC_ONE' and the TeamId where it will be created is specified.
    # 'kpdwhk4mb' is a Team named 'JPMC'
    selection_criteria.Name = 'JPMC_ONE'
    selection_criteria.SelectionCriteriaLogic = selection_criteria_logic
    # selection_criteria.SelectionCriteriaRelationship = selection_criteria_relationship
    team_entry_selection_criteria.Status = 'Active'
    team_entry_selection_criteria.Order = 0
    team_entry_selection_criteria.TeamId = 'kpdwhk4mb'
    team_entry_selection_criteria.SelectionCriteria = selection_criteria
    team_entry.TeamEntrySelectionCriteria = team_entry_selection_criteria

    # Append the Team Entry to the Team Entry Array
    array_team_entry.TeamEntry.append(team_entry)

    # Send the request
    print service.client.service.TeamEntryCreate(array_team_entry)


def main():
    service = Service()
    team_entry_create_selection_criteria(service)


if __name__ == '__main__':
    main()
