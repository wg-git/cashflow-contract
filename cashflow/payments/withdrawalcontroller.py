from boa.blockchain.vm.Neo.Runtime 			import Log, Notify

from cashflow.storage.storageapi 				import StorageApi, getFromStorage

"""
This class handles all the withdrawal request creation and modifications. 
"""

class WithdrawalController():

	# the current withdrawal request
	STORAGE_KEY_WITHDRAWAL_REQUEST				= "withdrawal_request/"
	# the value of the current withdrawal request
	STORAGE_KEY_WITHDRAWAL_REQUEST_VALUE			= "withdrawal_request_value/"
	# the units of for current withdrawal request
	STORAGE_KEY_WITHDRAWAL_REQUEST_UNITS			= "withdrawal_request_units/"
	# the asset amount, which has been released for an address
	STORAGE_KEY_RELEASED_ASSETS					= "released_assets/"

	def initialize(self,uid,receiver):
		storage_api 	= StorageApi()

		storage_api.putValue(self.STORAGE_KEY_RELEASED_ASSETS, receiver, 0)

	# creates a withdrawal request for the uid of a payment contract
	def createNewWithdrawalRequest(self,uid,units,units_value):
		storage_api 		= StorageApi()
		
		storage_api.putValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST, uid, 'ACTIVE')
		storage_api.putValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST_UNITS, uid, units)		
		storage_api.putValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST_VALUE, uid, units_value)		

		return True

	# deletes allwithdrawal request information, after a withdrawal request has been authorized
	def clearWithdrawalRequest(self,uid):
		storage_api 		= StorageApi()

		storage_api.deleteValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST, uid)
		storage_api.deleteValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST_UNITS, uid)		
		storage_api.deleteValue(self.STORAGE_KEY_WITHDRAWAL_REQUEST_VALUE, uid)	

		return True

	# this will increase the amount of released assets, after a withdrawal has been authorized and deposited
	def releaseAttachedAssets(self,address,attached_assets_value):
		storage_api 		= StorageApi()

		released_assets 	= storage_api.getValue(self.STORAGE_KEY_RELEASED_ASSETS, address)
		released_assets 	+= attached_assets_value
		storage_api.putValue(self.STORAGE_KEY_RELEASED_ASSETS, address, released_assets)

		return released_assets

	# this will consume released assets after they have been transferred from the smart contract
	def spentAssets(self,address,spent_assets_value):
		storage_api 		= StorageApi()

		spent_assets_value = spent_assets_value * 100000000

		released_assets 	= storage_api.getValue(self.STORAGE_KEY_RELEASED_ASSETS, address)
		released_assets 	-= spent_assets_value
		storage_api.putValue(self.STORAGE_KEY_RELEASED_ASSETS, address, released_assets)

		return released_assets

	def getReleasedAssets(self,address):
		return getFromStorage(self.STORAGE_KEY_RELEASED_ASSETS, address)

	def getWithdrawalRequest(self,uid):
		return getFromStorage(self.STORAGE_KEY_WITHDRAWAL_REQUEST, uid)

	def getOpenWithdrawalValue(self,uid):
		return getFromStorage(self.STORAGE_KEY_WITHDRAWAL_REQUEST_VALUE, uid)

