# Offensive words and corresponding negative values.
offensive_words = {'fuck': 10, 'shit': 8, 'bullshit': 9, 'damn': 5, 'holyshit': 7, 'fucking': 9}

def censor(quote):
	"""Censors offensive words in the quote.
	 
	Args:
		quote: quote provided by the user
	 
	Returns:
		Updated quote with censored offensive 
		words with astericks.
	"""
	quote_words = quote.split()
	updated_quote = ''
	for word in quote_words:
		lower_word = word.lower()
		# Handle period and question mark missed by split.
		end = ''
		last = lower_word[-1]
		if not last.isalpha():
			lower_word = lower_word[0 : len(word) - 1]
			word = word[0 : len(word) - 1]
			end = last

		# Handle space or period or question mark.
		space = ' '
		if end:
			space = end + ' '

		# censor words
		if lower_word in offensive_words.keys():
			updated_quote += '*' * len(lower_word) + space
		else:
			updated_quote += word + space
	return updated_quote

def get_offensive_score(quote):
	"""Returns offensive score 
		for corresponding offensive words.
	 
	Args:
		quote: quote provided by the user
	 
	Returns:
		Integer score for offensive words.
	"""
	quote_words = quote.split()
	score = 0
	for word in quote_words:
		word = word.lower()
		last_word = word[-1]
		if not last_word.isalpha():
			word = word[0 : len(word) - 1]
		if word in offensive_words.keys():
			score += offensive_words[word]
	return score

def check_standard(quote):
	"""Returns False if offensive score 
		crosses 15, True otherwise.
	 
	Args:
		quote: quote provided by the user
	 
	Returns:
		False if offensive score crosses 15, True otherwise.
	"""
	if get_offensive_score(quote) > 15:
		return False
	return True

def frequency(posts):
	""" Stores words and their count in dictionary
		and stores count and the corresponding
		words with the same frequency as values.
	 
	Args:
		posts: all posts that are in the database.
	 
	Returns:
		Dcitionary with frequency and a string of words.
	"""
	my_dict = {}
	for post in posts:
		quote = post.quote
		quote_words = quote.split()
		for word in quote_words:
			word = word.lower()
			last_word = word[-1]
			if not last_word.isalpha():
				word = word[0 : len(word) - 1]
			if word in my_dict:
				my_dict[word] += 1
			else:
				my_dict[word] = 1
	# Creates a dictionary with frequency and a string of words.
	new_dict = {}
	for key in my_dict.keys():
		val = my_dict[key]
		if val not in new_dict:
			new_dict[val] = key
		else:
			new_dict[val] += ', ' + key
	return new_dict.items()