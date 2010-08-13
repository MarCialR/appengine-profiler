import time

class Timer():
	def __init__(self):
		self.start_t = None
		self.end_t = None

	def set_begin(self, t):
		assert self.start_t is None
		assert self.end_t is None
		self.start_t = t
	def start(self):
		self.set_begin(time.time())

	def set_end(self, t):
		assert self.start_t is not None
		assert self.end_t is None
		self.end_t = t
	def stop(self):
		self.set_end(time.time())

	def get_and_clear(self):
		assert self.start_t is not None
		assert self.end_t is not None
		diff = self.end_t - self.start_t
		self.start_t = None
		self.end_t = None
		return diff
