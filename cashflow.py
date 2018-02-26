from boa.blockchain.vm.System.ExecutionEngine 	import GetExecutingScriptHash
from boa.blockchain.vm.Neo.Runtime 			import GetTrigger, CheckWitness, Log, Notify
from boa.blockchain.vm.Neo.TriggerType 			import Application, Verification
from boa.blockchain.vm.Neo.Action 				import RegisterAction

from cashflow.operations.operationscontroller 	import OperationsController
from cashflow.payments.payment 				import Payment
from cashflow.payments.withdrawalcontroller	 	import WithdrawalController
from cashflow.attachmentcontroller				import getAttachedAssets, getOutputScriptHashes

OnWithdrawalRequest	= RegisterAction('withdrawal_request', 'uid', 'amount')
OnClaimUnits 		= RegisterAction('claim_units', 'uid', 'units_count')
SpentReleasedAssets	= RegisterAction('spent_assets', 'address', 'amount')

"""
This smart-contract can be used to create payments between two partys. Every payment is only valid between a start and end date. Between those
dates the receiver can withdraw the assets he worked for at any time. 

A job with a monthly salary is a TimeContract. Between the first and the last day of the month, an employee could withdraw his salary at any time. The withdrawal amount would be proportional to the time, that have passed. 
An insurance, which is paid annualy, would be valid from Jan. 1st to Dec 31th. If they choose to, a company could withdrawl a small amount of the fee at the end of every day. 

Contracts, which are depended on goods are UnitContracts. They are also only valid for a certain timerange, but a value is only created, when units are claimed. If the receiver is claiming some units, the owner has to authorize these units, before any assets can be withdrawn. 

Whenever a withdrawal is requested, an event is triggered, so the owner can deposit the requested amount. This way all payments are made just-in-time. If there is a trust issue in the beginning, one can set up an up-front contract. This contract needs to have the overall amount deposited with the initialization.
"""

def Main(operation_string_para, args):
	trigger = GetTrigger()

	if trigger == Verification:
		# all the hashes, which were found in the transaction outputs
		script_hashes 			= getOutputScriptHashes()

		if not script_hashes:
			return False

		withdrawal_controller 	= WithdrawalController()

		for script_hash in script_hashes:
			# these are all the assets, which were created by requesting withdrawals
			released_assets 	= withdrawal_controller.getReleasedAssets(script_hash)
			
			if released_assets:
				attachment 		= getAttachedAssets(script_hash)
				# if the requestes asset value is not higher than the stored asset value, allow withdrawal
				if attachment.gas_attached <= released_assets:
					SpentReleasedAssets(script_hash, attachment.gas_attached)
					return True
			else:
				n=0

		return False

	elif trigger == Application:

		if operation_string_para != None:

			args_count = len(args)

			if args_count < 1:
				return 'error: please provide operation arguments'

			# the operation controller check for arguments count and operation string matches
			operations_controller 	= OperationsController()
			# the withdrawal controller is reponsible for handling the withdrawal requests from the contracts receiver
			withdrawal_controller 	= WithdrawalController()

			init_operation_strings 	= operations_controller.validInitOperationStrings()

			# after the receiver has transferred assets from the smart contract, the amount of his released assets has to be reduced.
			if operations_controller.isSpentAssets(operation_string_para):
				if not operations_controller.operationArgsAreValid(operation_string_para, args):
					return 'error: operation arguments count invalid'

				address 		= args[0]
				spent_assets 	= args[1]
				return withdrawal_controller.spentAssets(address, spent_assets)

			# the uid is the identifier for every payment contract between two partys
			uid 			= args[0]
			payment 		= Payment()
			payment_in_use = payment.isInUse(uid)

			# only handle init operations at this point
			for init_operation_string in init_operation_strings:
				if operation_string_para == init_operation_string:

					if not operations_controller.operationArgsAreValid(operation_string_para, args):
						return 'error: operation arguments count invalid'

					if payment_in_use:
						return 'error: cant initialize payment contract. uid is in use'

					principal = args[1]
					receiver 	= args[2]
					withdrawal_controller.initialize(uid,receiver)

					if operations_controller.isInitTimeContract(operation_string_para):
						return payment.initializeTimeContract(args)

					if operations_controller.isInitUnitsContract(operation_string_para):
						return payment.initializeUnitsContract(args)

			# all remaining operations need an initialized payment contract
			if not payment_in_use:
				return 'error: operation invalid. payment contract not in use'

			if not operations_controller.operationArgsAreValid(operation_string_para, args):
				return 'error: operation arguments count invalid'

			payment_has_started = payment.hasStarted(uid)
			
			if not payment_has_started:
				return 'error: operation invalid. payment contract not in use yet'

			# the balance is the available amount, minus spent units and those, which are currently
			if operations_controller.isGetBalance(operation_string_para):
				return payment.getBalance(uid)

			principal 	= payment.getPrincipalAddress(uid)
			receiver 		= payment.getReceiverAddress(uid)

			is_principal 	= CheckWitness(principal)
			is_receiver 	= CheckWitness(receiver)

			# only the receiver can claim units, which he worked for in a UnitsContract
			if operations_controller.isClaimUnits(operation_string_para):
				if not is_receiver:
					return 'error: not authorized'

				units_to_claim = args[1]
				units_to_claim = payment.claimUnits(uid,units_to_claim)

				if units_to_claim:
					OnClaimUnits(uid,units_to_claim)

				return units_to_claim

			# only the owner can authorized units, which the receiver claimed
			if operations_controller.isAuthorizeUnits(operation_string_para):
				if not is_principal:
					return "error: not authorized"

				units_to_authorize 	= args[1]
				return payment.authorizeOpenUnits(uid,units_to_authorize)

			# this will return the total amount of available assets transferred by withdrawal requests
			# the receiver can use this, to get the amount of assets he can spent from the smart-contract
			if operations_controller.isGetAvailableAssets(operation_string_para):
				if is_receiver:
					return withdrawal_controller.getReleasedAssets(receiver)

				return False

			# this will return the amount of assets, which the receiver has requested
			#  the owner can use this, to deposit assets for the receiver
			if operations_controller.isGetOpenWithdrawalValue(operation_string_para):
				if not is_principal:
					return "error: not authorized"

				return withdrawal_controller.getOpenWithdrawalValue(uid)

			payment_type 		= payment.getType(uid)

			# only the receiver can request withdrawals from the smart-contract
			if operations_controller.isRequestWithdrawal(operation_string_para):
				if not is_receiver:
					return "error: not authorized"

				existing_withdrawal_request 	= withdrawal_controller.getWithdrawalRequest(uid)

				if existing_withdrawal_request:
					return 'error: withdrawal request in progress. please wait until it finishes'

				units_balance 		= payment.getUnitsBalance(uid)
				
				if units_balance == 0:
					return 'error: withdrawal request invalid. nothing to withdraw'

				current_value 		= payment.getBalance(uid)
				
				# if this payment contract was created with all assets deposited up front, there is no need to trigger an event. 
				# The withdrawal amount is released immediately
				if payment_type == payment.PAYMENT_TYPE_UP_FRONT:
					payment.spentUnitsAfterWithdrawalAuthorize(uid,current_value,False)
					withdrawal_controller.releaseAttachedAssets(receiver,current_value)

					return current_value
				# all the assets for a withdrawal requests within a just-in-time contract need to deposited manually by the owner
				elif payment_type == payment.PAYMENT_TYPE_JUST_IN_TIME:
					withdrawal_controller.createNewWithdrawalRequest(uid,units_balance,current_value)
					payment.reserveUnitsForWithdrawal(uid,units_balance)
					OnWithdrawalRequest(uid,current_value)

					return current_value

				return False
			# this operation is used by the owner to deposit assets for the requested amount
			if operations_controller.isDepositWithdrawalsRequest(operation_string_para):
				if not is_principal:
					return "error: not authorized"

				if payment_type == payment.PAYMENT_TYPE_UP_FRONT:
					Notify('error: you cant deposit assets for an up-front contract')
					return False

				existing_withdrawal_request 	= withdrawal_controller.getWithdrawalRequest(uid)

				if not existing_withdrawal_request:
					return 'error: there is no pending withdrawal request'

				# we get all the assets, which are attached and are ment for the smart-contracts script hash
				contract_script_hash	= GetExecutingScriptHash()
				attached_assets 		= getAttachedAssets(contract_script_hash)
				attached_gas 			= attached_assets.gas_attached

				if attached_gas == 0:
					return 'error: no gas attached'

				open_withdrawal_value 	= withdrawal_controller.getOpenWithdrawalValue(uid)

				# One can never deposit more assets than the requested amount
				if attached_gas != open_withdrawal_value:
					return 'error: attached gas amount has to match withdrawal requests value'

				payment.spentUnitsAfterWithdrawalAuthorize(uid,attached_gas,True)
				withdrawal_controller.releaseAttachedAssets(receiver,attached_gas)
				withdrawal_controller.clearWithdrawalRequest(uid)

				return attached_gas

		return 'error: no operation string provided'

	return 'error: unknown triger'
