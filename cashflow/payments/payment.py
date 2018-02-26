from boa.blockchain.vm.Neo.Runtime 			import Notify
from boa.code.builtins 						import concat
from boa.blockchain.vm.System.ExecutionEngine 	import GetExecutingScriptHash

from cashflow.storage.storageapi 				import StorageApi, getFromStorage
from cashflow.utils 						import blockTimeStamp
from cashflow.attachmentcontroller				import getAttachedAssets

FACTOR = 100000000

"""
The payment class holds all properties and their storage paths for the different payment contract types.
Modifying those properties is done, using the given methods.
"""

class Payment():

	# the owner, who is depositing assets for the receiver
	STORAGE_KEY_PRINCIPAL_ADDRESS	= "principal_address/"
	# the receiver is paid for claimed units or for his working time
	STORAGE_KEY_RECEIVER_ADDRESS	= "receiver_address/"
	# the total assets amount, which will be spent
	STORAGE_KEY_OVERALL_VALUE	= "overall_value/"
	# the total number of units, which are spent over the contracts duration
	STORAGE_KEY_TOTAL_UNITS		= "total_units/"
	# the number of units, already withdrawn
	STORAGE_KEY_SPENT_UNITS		= "spent_units/"
	# the number of units, which are currently available
	STORAGE_KEY_CURRENT_UNITS	= "current_units/"
	# the number of units, which are currently reserved for a withdrawal
	STORAGE_KEY_RESERVED_UNITS	= "reserved_units/"
	# the number of units, which are currently being claimed
	STORAGE_KEY_OPEN_UNITS		= "open_units/"
	# the timestamp, which defines the payment contract duration start
	STORAGE_KEY_FROM_TIMESTAMP	= "from_timestamp/"
	# the timestamp, which defines the payment contract duration end
	STORAGE_KEY_TO_TIMESTAMP		= "to_timestamp/"
	# the way value is creeted. Over time, or by claiming units. TIME <--> UNITS
	STORAGE_KEY_CONSUME_TYPE		= "consume_type/"
	# the way, assets will be deposited. Just in time, whenever a withdrawal request occurs, or up front at initialization
	STORAGE_KEY_PAYMENT_TYPE		= "payment_type/"
	# the amount of assets, which were deposited up front
	STORAGE_KEY_UP_FRONT_HOLDINGS	= "up_front_holdings/"

	PAYMENT_TYPE_JUST_IN_TIME 	= b'\x01'
	PAYMENT_TYPE_UP_FRONT 		= b'\x02'

	CONSUME_TYPE_TIME 			= b'\x01'
	CONSUME_TYPE_UNITS 			= b'\x02'

	def initialize(self, args, consume_type):

		if not consume_type:
			return "error: no consume type defined"

		uid 				= args[0]
		principal_address 	= args[1]
		receiver_address 	= args[2]
		overall_value 		= args[3]
		from_timestamp		= args[4]
		to_timestamp		= args[5]
		payment_type		= args[6]

		storage_api = StorageApi()

		overall_value = overall_value * FACTOR

		# when initializing an up-front contract, the total asset amount has to be attached 
		if payment_type == self.PAYMENT_TYPE_UP_FRONT:
			contract_script_hash	= GetExecutingScriptHash()
			attached_assets 		= getAttachedAssets(contract_script_hash)

			if attached_assets.gas_attached == 0:
				return 'error: no gas attached'

			if attached_assets.gas_attached != overall_value:
				return 'error: attached gas is not matching overall value'
			
			storage_api.putValue(self.STORAGE_KEY_UP_FRONT_HOLDINGS, uid, attached_assets.gas_attached)
		
		storage_api.putValue(self.STORAGE_KEY_PRINCIPAL_ADDRESS, uid, principal_address)
		storage_api.putValue(self.STORAGE_KEY_RECEIVER_ADDRESS, uid, receiver_address)
		storage_api.putValue(self.STORAGE_KEY_OVERALL_VALUE, uid, overall_value)
		storage_api.putValue(self.STORAGE_KEY_FROM_TIMESTAMP, uid, from_timestamp)
		storage_api.putValue(self.STORAGE_KEY_TO_TIMESTAMP, uid, to_timestamp)
		storage_api.putValue(self.STORAGE_KEY_PAYMENT_TYPE, uid, payment_type)

		storage_api.putValue(self.STORAGE_KEY_SPENT_UNITS, uid, 0)
		storage_api.putValue(self.STORAGE_KEY_OPEN_UNITS, uid, 0)
		storage_api.putValue(self.STORAGE_KEY_RESERVED_UNITS, uid, 0)
		storage_api.putValue(self.STORAGE_KEY_CURRENT_UNITS, uid, 0)

		storage_api.putValue(self.STORAGE_KEY_CONSUME_TYPE, uid, consume_type)

		# for TimeContracts the total unit count is defined by the timestamps
		if consume_type == self.CONSUME_TYPE_TIME:
			total_units 	= to_timestamp - from_timestamp
			storage_api.putValue(self.STORAGE_KEY_TOTAL_UNITS, uid, total_units)
			return True

		# for UnitContracts the total unit count is set by the invoker
		elif consume_type == self.CONSUME_TYPE_UNITS:
			total_units	= args[7]
			storage_api.putValue(self.STORAGE_KEY_TOTAL_UNITS, uid, total_units)
			return True
		else:
			return False

		return True

	def initializeTimeContract(self, args):
		consume_type = self.CONSUME_TYPE_TIME
		return self.initialize(args, consume_type)

	def initializeUnitsContract(self, args):
		consume_type = self.CONSUME_TYPE_UNITS
		return self.initialize(args, consume_type)

	def isInUse(self, uid):
		return self.getPrincipalAddress(uid)

	def hasStarted(self, uid):
		from_timestamp = self.getFromTimestamp(uid)
		current_time 	= blockTimeStamp()

		if current_time < from_timestamp:
			return False
		
		return True

	# the seconds passed since the contract started
	def getCurrentTimeUnits(self,uid):
		current_time	= blockTimeStamp()

		from_timestamp	= self.getFromTimestamp(uid)
		to_timestamp	= self.getToTimestamp(uid)

		if current_time < from_timestamp:
			return 0
		
		if current_time > to_timestamp:
			current_time = to_timestamp

		current_time 	= current_time - from_timestamp
		return current_time

	# the current available units count
	def getUnitsBalance(self,uid):
		current_units 	= self.getCurrentUnits(uid)

		if current_units == 0:
			return 0

		spent_units	= self.getSpentUnits(uid)
		reserved_units	= self.getReservedUnits(uid)

		current_units -= spent_units
		current_units -= reserved_units

		return current_units

	# the current asset value, which could be withdrawn
	def getBalance(self,uid):
		units_balance 	= self.getUnitsBalance(uid)

		if units_balance == 0:
			return 0

		total_units 	= self.getTotalUnits(uid)
		overall_value 	= self.getOverallValue(uid)

		units_factor			= (total_units * FACTOR) / units_balance
		overall_current_value 	= (overall_value * FACTOR) / units_factor

		return overall_current_value

	# units need to be reserved, when they are being withdrawn, so they wont count, when getting the curren units
	def reserveUnitsForWithdrawal(self,uid,units):
		storage_api 		= StorageApi()

		reserved_units = storage_api.getValue(self.STORAGE_KEY_RESERVED_UNITS, uid)
		reserved_units += units
		storage_api.putValue(self.STORAGE_KEY_RESERVED_UNITS, uid, reserved_units)

		return reserved_units

	# when the assets for a withdrawal request have been deposited, the units for the total asset amount have to be spent too
	def spentUnitsAfterWithdrawalAuthorize(self,uid,released_assets,reduce_reserved):
		storage_api 	= StorageApi()
		overall_value 	= storage_api.getValue(self.STORAGE_KEY_OVERALL_VALUE, uid)
		total_units 	= storage_api.getValue(self.STORAGE_KEY_TOTAL_UNITS, uid)

		value_factor	= (overall_value * FACTOR) / released_assets
		units  		= (total_units * FACTOR) / value_factor

		spent_units = storage_api.getValue(self.STORAGE_KEY_SPENT_UNITS, uid)
		spent_units += units
		storage_api.putValue(self.STORAGE_KEY_SPENT_UNITS, uid, spent_units)

		# for an up-front payment contract, units were never reserved, but immediately released
		if reduce_reserved:
			reserved_units = storage_api.getValue(self.STORAGE_KEY_RESERVED_UNITS, uid)
			reserved_units -= units
			storage_api.putValue(self.STORAGE_KEY_RESERVED_UNITS, uid, reserved_units)

		return spent_units

	# the contracts receiver can claim units he worked for. After authorization he can withdraw the assets value.
	def claimUnits(self,uid,units_to_claim):
		storage_api 	= StorageApi()
		consume_type	= storage_api.getValue(self.STORAGE_KEY_CONSUME_TYPE, uid)

		if consume_type == self.CONSUME_TYPE_TIME:
			Notify('error: you cant claim units for a time contract')
			return False

		current_units 	= storage_api.getValue(self.STORAGE_KEY_CURRENT_UNITS, uid)
		open_units 	= storage_api.getValue(self.STORAGE_KEY_OPEN_UNITS, uid)
		total_units 	= storage_api.getValue(self.STORAGE_KEY_TOTAL_UNITS, uid)

		if units_to_claim == 0:
			Notify('error: you cant claim 0 units')
			return False

		if units_to_claim > total_units:
			Notify('error: number of claimed units is higher than total units')
			return False

		claimable_units = total_units - current_units - open_units

		if units_to_claim > claimable_units:
			Notify('error: number of claimed units is higher than available units')
			return False

		open_units 	+= units_to_claim
		storage_api.putValue(self.STORAGE_KEY_OPEN_UNITS, uid, open_units)

		return open_units

	# the contracts owner can authorize open units, so the receiver can withdraw their assets value.
	def authorizeOpenUnits(self,uid,units_to_authorize):
		storage_api 	= StorageApi()
		open_units 	= storage_api.getValue(self.STORAGE_KEY_OPEN_UNITS, uid)

		if units_to_authorize == 0:
			return 'error: you cant authorize 0 units'

		if units_to_authorize > open_units:
			return 'error: you cant authorize more units than there are open ones'

		current_units 	= storage_api.getValue(self.STORAGE_KEY_CURRENT_UNITS, uid)

		open_units 	-= units_to_authorize
		current_units 	+= units_to_authorize

		storage_api.putValue(self.STORAGE_KEY_OPEN_UNITS, uid, open_units)
		storage_api.putValue(self.STORAGE_KEY_CURRENT_UNITS, uid, current_units)

		return current_units

	def getType(self, uid):
		return getFromStorage(self.STORAGE_KEY_PAYMENT_TYPE, uid)

	def getConsumeType(self, uid):
		return getFromStorage(self.STORAGE_KEY_CONSUME_TYPE, uid)

	def getPrincipalAddress(self, uid):
		return getFromStorage(self.STORAGE_KEY_PRINCIPAL_ADDRESS, uid)

	def getReceiverAddress(self, uid):
		return getFromStorage(self.STORAGE_KEY_RECEIVER_ADDRESS, uid)

	def getFromTimestamp(self, uid):
		return getFromStorage(self.STORAGE_KEY_FROM_TIMESTAMP, uid)

	def getToTimestamp(self, uid):
		return getFromStorage(self.STORAGE_KEY_TO_TIMESTAMP, uid)

	def getOverallValue(self, uid):
		return getFromStorage(self.STORAGE_KEY_OVERALL_VALUE, uid)

	def getTotalUnits(self, uid):
		return getFromStorage(self.STORAGE_KEY_TOTAL_UNITS, uid)

	def getReservedUnits(self, uid):
		return getFromStorage(self.STORAGE_KEY_RESERVED_UNITS, uid)

	def getSpentUnits(self, uid):
		return getFromStorage(self.STORAGE_KEY_SPENT_UNITS, uid)

	def getCurrentUnits(self, uid):
		consume_type 	= self.getConsumeType(uid)

		# for a TimeContract, the current units are always the seconds, which passed since the beginning timestamp
		if consume_type == self.CONSUME_TYPE_TIME:
			return self.getCurrentTimeUnits(uid)
		elif consume_type == self.CONSUME_TYPE_UNITS:
			return getFromStorage(self.STORAGE_KEY_CURRENT_UNITS, uid)
		else:
			n=0

		return False
