from utils import *
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *

# read in data
LOB = read_in_clean_data('LOB-delta-5.txt')

# extract features
LOB = gen_basic_features(LOB)

# down sample rows with stationary label
# because of much more rows with stationary label than others
# which will cause the imbalanced data problem
LOB = down_sample(LOB, 1)

labels = [row['label'] for row in LOB]
print_label_stats(labels)

# split data
train_data, val_data, test_data = split_data(LOB)

# # convert data to training format
# we can use column_names to find out the column name by its index
X_train, y_train, column_names = convert_format(train_data)
X_val, y_val, columns_names = convert_format(val_data)
X_test, y_test, columns_names = convert_format(test_data)


# train
model = LogisticRegression()
model.fit(X_train, y_train)


# predict
y_pred = model.predict(X_test)



# results
print accuracy_score(y_test, y_pred)