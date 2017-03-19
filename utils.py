import csv
import copy, random


class Data:
	def __init__(self):
		self.L1 = self.load_L1_data()
		self.L2 = self.load_L2_data()
	def load_L1_data(self):
		L1_data = []
		L1_files = ['data/2014-03-20-HSBC_L1.txt', 'data/2014-03-21-HSBC_L1.txt']
		for input_file in L1_files:
			with open(input_file, 'r') as f:
				L1_day = []
				lines = f.readlines()
				headers = None
				for i in range(len(lines)):
					line = lines[i]
					if i == 0:
						headers = line.split()
					else:
						assert (headers is not None)
						tmp = line.split()
						tmp[1] = tmp[1] + ' ' + tmp[2]
						tmp.pop(2)
						row = {}
						for j in range(len(headers)):
							field = headers[j]
							row[field] = tmp[j]
						L1_day.append(row)
				L1_data.append(L1_day)
		print "L1 data loaded."
		return L1_data
	def load_L2_data(self):
		L2_data = []
		L2_files = ['data/2014-03-20-HSBC_L2_Proj.csv', 'data/2014-03-21-HSBC_L2_Proj.csv']
		for input_file in L2_files:
			with open(input_file, 'rU') as f:
				L2_day = []
				reader = csv.DictReader(f)
				headers = reader.fieldnames
				for line in reader:
					row = {}
					for k in line:
						row[k] = line[k]
					L2_day.append(row)
				L2_data.append(L2_day)
		print "L2 data loaded."
		return L2_data

def compute_mid_price(record):
	best_bid = record['BP1']
	best_ask = record['AP1']
	minimum_tick_size = 0.05
	true_mid_price = (float(best_bid) + float(best_ask)) / float(2)
	remainder = true_mid_price % minimum_tick_size
	#rounded_mid_price = round(true_mid_price/minimum_tick_size) * minimum_tick_size
	rounded_mid_price = true_mid_price
	return rounded_mid_price


def check_time(current_time, next_time, delta_t):
	# we want next_time - current_time >= delta_t
	current_secs = int(''.join(current_time.split(':')[-1].split('.')))
	current_min = int(current_time.split(':')[-2])
	next_secs = int(''.join(next_time.split(':')[-1].split('.')))
	next_min = int(next_time.split(':')[-2])
	min_next_secs = current_secs + 1000 * delta_t
	if (min_next_secs/1000) >= 60:
		min_next_secs = min_next_secs - 60000
		if next_secs >= min_next_secs and next_min != current_min:
			return True
	else:
		if next_secs >= min_next_secs or next_secs < current_secs:
			return True

	return False

def down_sample(data, l, ratio=0.1):
	tmp = []
	for i in range(len(data)):
		if data[i]['label'] == l:
			if random.random() < ratio:
				tmp.append(data[i])
		else:
			tmp.append(data[i])
	data = tmp
	return data


# split dataset to train data, validation data, and test data
def split_data(data, train=0.7, validation=0.1, test=0.2):
	num_rows = len(data)
	train_data = []
	validation_data = []
	test_data = []
	for i in range(num_rows):
		r = random.random()
		if r < train:
			train_data.append(data[i])
		elif r >= train and r < train+validation:
			validation_data.append(data[i])
		else:
			test_data.append(data[i])
	print "train data size: ", len(train_data)
	print "validation data size: ", len(validation_data)
	print "test data size: ", len(test_data)
	return (train_data, validation_data, test_data)


def print_label_stats(labels):
	ctrs = [0, 0, 0]

	for l in labels:
		ctrs[l] += 1

	print "number of labels: ", len(labels)
	print "number of 0-downward: ", ctrs[0]
	print "number of 1-stationary: ", ctrs[1]
	print "number of 2-upward: ", ctrs[2]



# generate limit order book from raw data
# and save it to file

######################
## a sample usage:
# L2 = Data().L2[0]
# delta_t = 5
# gen_clean_data(L2, delta_t, compute_mid_price)

def gen_clean_data(L2, delta_t, compute_price):

	############################################
	## construct limit order book
	print "start building limit order book ..."

	LOB = []

	# initialize limit order book with first recor
	last_row = L2[0]

	# each update should result in a new status of limit order book
	for i in range(1, len(L2)):
		row = copy.deepcopy(last_row)
		tmp = L2[i]
		for key in tmp:
			if tmp[key] != '*' and tmp[key] != 'NA':
				row[key] = tmp[key]
		LOB.append(row)
		last_row = row

	print "limit order book finished."
	


	############################################
	## label data
	print "start labeling data"

	ps = []
	for i in range(len(LOB)):
		record = LOB[i]
		ps.append({'p': compute_price(record), 'time_stamp': record['TIMESTAMP']})

	labels = []
	for i in range(len(ps)-1):
		current_price = ps[i]['p']
		current_time = ps[i]['time_stamp']
		# we try to find the mid_price delta_t seconds after the current one
		for j in range(i+1, len(ps)):
			next_time = ps[j]['time_stamp']
			if check_time(current_time, next_time, delta_t):
				next_price = ps[j]['p']
				if abs(next_price - current_price) < 1e-06:
					# label stationary 1
					labels.append(1)
				elif next_price > current_price:
					# label upward 2
					labels.append(2)
				else:
					# label downward 0
					labels.append(0)
				break

	LOB = LOB[:len(labels)]
	for i in range(len(LOB)):
		LOB[i]['label'] = labels[i]
	print "labeling completed."

	print_label_stats(labels)

	############################################
	## save data

	############################################
	## save data

	columns = ["SEQ","TIMESTAMP","BP10","BSize10","BP9","BSize9","BP8","BSize8","BP7","BSize7","BP6","BSize6","BP5","BSize5","BP4","BSize4","BP3","BSize3","BP2","BSize2","BP1","BSize1","AP1","ASize1","AP2","ASize2","AP3","ASize3","AP4","ASize4","AP5","ASize5","AP6","ASize6","AP7","ASize7","AP8","ASize8","AP9","ASize9","AP10","ASize10", "label"]
	file_name = "LOB-delta-" + str(delta_t) + ".txt"
	with open(file_name, 'w') as f:
		f.write(','.join(columns) + '\n')
		for i in range(len(LOB)):
			features = []
			for j in range(len(columns)):
				features.append(str(LOB[i][columns[j]]))
			f.write(','.join(features) + '\n')

	print "clean data saved to " + file_name

	return


def read_in_clean_data(input_file):
	columns = ["SEQ","TIMESTAMP","BP10","BSize10","BP9","BSize9","BP8","BSize8","BP7","BSize7","BP6","BSize6","BP5","BSize5","BP4","BSize4","BP3","BSize3","BP2","BSize2","BP1","BSize1","AP1","ASize1","AP2","ASize2","AP3","ASize3","AP4","ASize4","AP5","ASize5","AP6","ASize6","AP7","ASize7","AP8","ASize8","AP9","ASize9","AP10","ASize10", "label"]
	LOB = []
	with open(input_file, 'r') as f:
		lines = f.readlines()
		for i in range(len(lines)):
			line = lines[i]
			if i == 0:
				continue
			features = line.split(',')
			row = {}
			for j in range(len(columns)):
				if j == 0 or (j > 1 and j < len(columns)-1):
					features[j] = float(features[j])
				elif j == len(columns)-1:
					features[j] = int(features[j])
				row[columns[j]] = features[j]
			LOB.append(row)
	return LOB

def gen_basic_features(data):
	# generate som basic features
	# APi, ASizei, BPi, BSizei for best 5 levels
	tmp = []
	for i in range(len(data)):
		row = {}
		for j in range(1, 6):
			row['AP'+str(j)] = data[i]['AP'+str(j)]
			row['ASize'+str(j)] = data[i]['ASize'+str(j)]
			row['BP'+str(j)] = data[i]['BP'+str(j)]
			row['BSize'+str(j)] = data[i]['BSize'+str(j)]
		row['label'] = data[i]['label']
		tmp.append(row)
	data = tmp
	return data

def convert_format(data):
	columns = data[0].keys()
	columns.remove('label')
	print columns
	X = []
	y = []
	for i in range(len(data)):
		row = []
		for j in range(len(columns)):
			row.append(data[i][columns[j]])
		X.append(row)
		y.append(data[i]['label'])
	return (X, y, columns)
