#!/usr/bin/env python

import suds

#WSDL Url
url = 'https://developer4.envoyww.com/WebService/EPAPI_1.0/wsdl.wsdl'

def main():
	"""
	Creates header information required for any SOAP request.
	"""
	client = suds.client.Client(url)
	header = client.factory.create('AuthHeader')
	header.Domain = 'TPELLETIER'
	header.UserId = 'soaptester'
	header.UserPassword = 'password'
	header.OemId = 'TPELLETIERoem'
	header.OemPassword = 'password'
	client.set_options(soapheaders=header)
	print client

main()

