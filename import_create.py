#!/usr/bin/env python

# Imports
import base64
import suds
import ConfigParser

CONF = ConfigParser.ConfigParser()
try:
    CONF.read("soap.props")
except IOError as e:
    print 'File %s not found!' % e

#WSDL Url
URL = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

class Service(object):
    def __init__(self):
        """
        Creates header information required for any SOAP request.
        """
        self.client = suds.client.Client(URL)
        header = self.client.factory.create('AuthHeader')
        header.Domain = CONF.get("Auth Header", "domain")
        header.UserId = CONF.get("Auth Header", "userid")
        header.UserPassword = CONF.get("Auth Header", "userpassword")
        header.OemId = CONF.get("Auth Header", "oemid")
        header.OemPassword = CONF.get("Auth Header", "oempassword")
        self.client.set_options(soapheaders=header)
        self.orgid = self.client.service.OrganizationQueryRoot()[0]

def import_create(service):
    # Read file in and base64 encode
    file_in = open('tony.csv', 'r').read()
    file_encoded = base64.b64encode(file_in)

    # Create objects
    import_object = service.client.factory.create('Import')
    import_array = service.client.factory.create('ArrayOfImport')
    import_filearg_object = service.client.factory.create('ImportFileArg')
    import_filearg_array = service.client.factory.create('ArrayOfImportFileArg')

    # Set import object attributes
    import_object.OrganizationId = 'kftphkk4k'
    import_object.ImportDefinitionId = 'kqtj5kk5k'

    # Set import file arg object attributes
    import_filearg_object.Name = 'IMPORT_FILE'
    import_filearg_object.Ordinal = '0'
    import_filearg_object.UserFileName = 'tony.csv'
    import_filearg_object.EncodedValue = file_encoded

    # Append import file arg object to array
    import_filearg_array.ImportFileArg.append(import_filearg_object)

    # Set the import object ImportFileArgs attribute to the import file arg array
    import_object.ImportFileArgs = import_filearg_array

    # Append the import object to the import array
    import_array.Import.append(import_object)

    # Call the ImportCreate method
    print service.client.service.ImportCreate(import_array)


def main():
    service = Service()
    try:
        import_create(service)
    except Exception as e:
        print e.fault.detail

if __name__ == '__main__':
    main()

