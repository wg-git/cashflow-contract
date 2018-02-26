# creates a payment contract, which creates value by time consumption
INIT_TIME_CONTRACT				= "init_time_contract"
# creates a payment contract, which creates value by claiming units
INIT_UNITS_CONTRACT				= "init_units_contract"

# gets the current value of the payment contract
BALANCE						= "get_balance"
# gets the asset value for all open withdrawal requests
OPEN_WITHDRAWAL_VALUE			= "get_open_withdrawal_value"
# gets the amountof assets, which are currently available ofr transferring from the smart contract
AVAILABLE_ASSETS				= "get_available_assets"

# claims units for unit contracts
CLAIM_UNITS					= "units_claim"
# authorizes units after they been clained
AUTHORIZE_UNITS				= "units_authorize"

# requests a withdrawal
REQUEST_WITHDRAWAL				= "withdrawal_request"
# deposits asset for a withdrawal request
DEPOSIT_WITHDRAWAL_REQUEST_ASSETS	= "withdrawal_deposit"
# spents released assets, after they habe been transferred from the smart contract
SPENT_ASSETS					= "spent_assets"

"""
This class holds all valid operation strings for the smart-contract. For those known operations, the argument count is also checked.
"""
class OperationsController():

	def validInitOperationStrings(self):
		operations = ["init_time_contract","init_units_contract"]
		return operations

	def operationArgsAreValid(self, operation_string, args):
		args_count 	= len(args)

		is_init_time_contract = self.isInitTimeContract(operation_string)
		if is_init_time_contract:
			return args_count == 7

		is_init_units_contract = self.isInitUnitsContract(operation_string)
		if is_init_units_contract:
			return args_count == 8

		is_claim_units = self.isClaimUnits(operation_string)
		if is_claim_units:
			return args_count == 2

		is_authorize_units = self.isAuthorizeUnits(operation_string)
		if is_authorize_units:
			return args_count == 2

		is_spent_assets = self.isSpentAssets(operation_string)
		if is_spent_assets:
			return args_count == 2

		return args_count == 1

	def isInitTimeContract(self, operation_string):
		return operation_string == INIT_TIME_CONTRACT

	def isInitUnitsContract(self, operation_string):
		return operation_string == INIT_UNITS_CONTRACT

	def isGetBalance(self, operation_string):
		return operation_string == BALANCE

	def isGetAvailableAssets(self, operation_string):
		return operation_string == AVAILABLE_ASSETS

	def isRequestWithdrawal(self, operation_string):
		return operation_string == REQUEST_WITHDRAWAL

	def isDepositWithdrawalsRequest(self, operation_string):
		return operation_string == DEPOSIT_WITHDRAWAL_REQUEST_ASSETS

	def isGetOpenWithdrawalValue(self, operation_string):
		return operation_string == OPEN_WITHDRAWAL_VALUE

	def isClaimUnits(self, operation_string):
		return operation_string == CLAIM_UNITS

	def isAuthorizeUnits(self, operation_string):
		return operation_string == AUTHORIZE_UNITS

	def isSpentAssets(self, operation_string):
		return operation_string == SPENT_ASSETS
	