from boa.blockchain.vm.System.ExecutionEngine 	import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction 			import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output 				import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime 			import Notify

from boa.code.builtins 						import concat
from cashflow.utils							import isInByteArray

"""
This class was mostly taken from the nex neo-ico-template. 
"""

class Attachments():
	gas_attached 	= 0
	sender_addr 	= 0
	receiver_addr 	= 0
	gas_asset_id 	= b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'

# This will get all the script_hashes, which are found in the transaction outputs
def getOutputScriptHashes():
	attachment 			= Attachments()
	tx 					= GetScriptContainer()
	references 			= tx.References
	script_hashes			= []

	if len(references) > 0:
		for output in tx.Outputs:
			if output.AssetId != attachment.gas_asset_id:
				Notify('error: only gas, please')
				return False

			script_hash = output.ScriptHash
			script_hashes.append(script_hash)

	return script_hashes

# this will get all the assets for a specific script_hash, which are present in the transaction outputs
def getAttachedAssets(receiver) -> Attachments:

	attachment 			= Attachments()
	tx 					= GetScriptContainer()
	references 			= tx.References
	attachment.receiver_addr = receiver

	if len(references) > 0:
		reference 			= references[0]
		attachment.sender_addr 	= reference.ScriptHash

		sent_amount_gas = 0

		for output in tx.Outputs:
			if output.AssetId != attachment.gas_asset_id:
				Notify('error: only gas please')
				return False

			if output.ScriptHash == receiver:
				sent_amount_gas += output.Value

			else:
				n=0

		Notify(sent_amount_gas)
		attachment.gas_attached = sent_amount_gas

	return attachment