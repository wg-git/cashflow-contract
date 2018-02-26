from boa.blockchain.vm.Neo.Storage 	import GetContext, Get, Put, Delete
from boa.code.builtins 				import concat

def getFromStorage(storage_key, suffix):
	storage_api = StorageApi()
	return storage_api.getValue(storage_key, suffix)

def putToStorage(storage_key, suffix, storage_value):
	storage_api = StorageApi()
	storage_api.putValue(storage_key, suffix, storage_value)

class StorageApi():

	context = GetContext()

	def putValue(self, storage_path, uid, storage_value):
		path = self.storageKey(storage_path, uid)
		self.put(path, storage_value)

	def getValue(self, storage_path, uid):
		path = self.storageKey(storage_path, uid)
		return self.get(path)

	def deleteValue(self, storage_path, uid):
		path = self.storageKey(storage_path, uid)
		return self.delete(path)

	def storageKey(self, prefix, uid):
		path = concat(prefix, uid)
		return path

	def get(self, key):
		return Get(self.context, key)

	def put(self, key, value):
		Put(self.context, key, value)

	def delete(self, key):
		Delete(self.context, key)