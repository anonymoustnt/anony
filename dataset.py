
import os
import sys
import pickle

import nltk


import torch
import torch.utils.data as data

from PIL import Image

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from config import cleanCaption

class MyDataset(data.Dataset):


	def __init__(self, split, img_dir, vocab, transform, what_elements='triplet', load_image_feature=0):

		self.split = split
		self.img_dir = img_dir
		self.vocab = vocab
		self.transform = transform
		self.what_elements = what_elements
		self.find_get_item_func()

		if load_image_feature:
			self.size_of_loaded_feature = load_image_feature
			self.get_transformed_image = self.load_image_feature

	def find_get_item_func(self):
		if self.what_elements=="triplet":
			self.get_item_func = self.get_triplet
		elif self.what_elements=="query":
			self.get_item_func = self.get_query
		elif self.what_elements=="target":
			self.get_item_func = self.get_target

		elif self.what_elements=='subset':
			self.get_item_func = self.get_subset
		elif self.what_elements == "soft_targets":
			self.get_item_func = self.get_soft_targets
		else:
			print("Dataloader: unknown use case! (asked for '{}')".format(self.what_elements))
			sys.exit(-1)

	def __getitem__(self, index):
		return self.get_item_func(index)





	def get_transformed_image(self, path):
		image = Image.open(os.path.join(self.img_dir, path)).convert('RGB')

		image = self.transform(image)
		return image


	def load_image_feature(self, path):

		path = os.path.join(self.img_dir, path).replace(".png", ".pkl").replace(".jpg", ".pkl")
		try:
			image = torch.tensor(pickle.load(open(path, "rb")))
		except FileNotFoundError:
			print("File not found: {}".format(path))
			return torch.zeros(self.size_of_loaded_feature)
		return image


	def get_transformed_captions(self, capts):

		tokens_capts = [[] for i in range(len(capts))]
		for i in range(len(capts)):
			tokens_capts[i] = nltk.tokenize.word_tokenize(cleanCaption(capts[i]).lower())

		ret_capts = " <and> ".join(capts)
		if len(capts) == 1:
			tokens = tokens_capts[0]
		else:
			tokens = tokens_capts[0] + ['<and>'] + tokens_capts[1]

		sentence = []
		sentence.append(self.vocab('<start>'))
		sentence.extend([self.vocab(token) for token in tokens])
		sentence.append(self.vocab('<end>'))
		text = torch.Tensor(sentence)
		return text, ret_capts






	def get_triplet(self, index):
		raise NotImplementedError

	def get_query(self, index):
		raise NotImplementedError

	def get_target(self, index):
		raise NotImplementedError



	def get_subset(self, index):
		raise NotImplementedError

	def get_soft_targets(self, index):
		raise NotImplementedError






	def get_triplet_info(self, index):

		raise NotImplementedError