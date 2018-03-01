# cashflow
A smart contract for the NEO blockchain, which allows for managing of salary payments between two instances.

## Overview

This smart-contract can be used to create payments between two individuals. Every payment is only valid between a start and end date. Between those dates the receiver can withdraw the assets he worked for at any time. This approach aims at a system, where every reoccuring payment is done just in time. Rent, Insurances, Salary, everything is paid for or withdrawn, when it is needed or at custom intervals. This way, you wont run out of money at the end of the month, because everything is being paid for, at any time.

A job with a monthly salary is a TimeContract. Between the first and the last day of the month, an employee could withdraw his salary at any time. The withdrawal amount would be proportional to the time, that have passed. 
An insurance, which is paid annualy, would be valid from Jan. 1st to Dec 31th. If they choose to, a company could withdrawl a small amount of the fee at the end of every day. 

Contracts, which are depended on goods are UnitContracts. They are also only valid for a certain timerange, but a value is only created, when units are claimed. If the receiver is claiming some units, the owner has to authorize these units, before any assets can be withdrawn. 

Whenever a withdrawal is requested, an event is triggered, so the owner can deposit the requested amount. This way all payments are made just-in-time. If there is a trust issue in the beginning, one can set up an up-front contract. This contract needs to have the overall amount deposited with the initialization.

## Getting started

Every initialization has at least these arguments:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 init_time_contract ['uid','principal','receiver',value_in_gas,from_timestamp,to_timestamp,consume_type]
```

You can create a TimeContract, which needs to be filled up front like this:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 init_time_contract ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8','AdbvrPaSNeWks71CR9xRf7wFxoxZp9bTrM','AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y',5,1517443200,1519776000,2] --attach-gas=5
```

A TimeContract, which will be filled every time the receiver requests a withdrawal:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 init_time_contract ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8','AdbvrPaSNeWks71CR9xRf7wFxoxZp9bTrM','AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y',5,1517443200,1519776000,1]
```

A UnitContract, filled up-front:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 init_units_contract ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8','AdbvrPaSNeWks71CR9xRf7wFxoxZp9bTrM','AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y',10,1517443200,1519776000,2,5] --attach-gas=10
```
The additional argument defines, how many units can be filled for this contract.

A UnitContract, filled just-in-time:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 init_units_contract ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8','AdbvrPaSNeWks71CR9xRf7wFxoxZp9bTrM','AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y',10,1517443200,1519776000,1,5]
```
### Balance & Units

Once initialized, you can check your current balance:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 get_balance ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8']
```

For TimeContracts the balance will keep increasing, once the contract has started. UnitContracts generate their balance by units. So you have to claim units, to see your balance increase:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 units_claim ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8',14]
```
These units have to be authorized by the principal:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 units_authorize ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8',14]
```

### Withdrawals

You can withdrawl your current balance amount like this:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 withdrawal_request ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8']
```

The principal can check the open withdrawl amount like this, to see what he needs to deposit:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 get_open_withdrawal_value ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8']
```

### Deposits

You can deposits asset for withdrawal requests like this:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 withdrawal_deposit ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8'] --attach-gas=25.38311391
```

Once the assets has been deposited the receiver can check all the available assets like this:
``` 
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 get_available_assets ['ba5f3437-24bd-3d3c-8b58-3d27fe6d7bf8']
```

When assets are transferred from the smart contract the verification will fire an event, so the transferred assets can be marked as spent. The operation looks like this:
```
testinvoke 0x862c3b0d86e8dba5abfb5bd0517a90e1eecef1e1 spent_assets ['AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y',2]
```
