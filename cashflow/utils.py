from boa.blockchain.vm.Neo.Blockchain 			import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header 				import GetTimestamp, GetConsensusData
from boa.blockchain.vm.Neo.Runtime 			import Log

from boa.code.builtins 						import concat, list, range, take, substr

def blockTimeStamp():
	current_height = GetHeight()
	current_header = GetHeader(current_height)
	current_time 	= GetTimestamp(current_header)

	return current_time

def isInByteArray(haystack,needle):

	if not len(haystack):
		return False

	for item in haystack:
		if item == needle:
			return True
		else:
			n=0

	return False

