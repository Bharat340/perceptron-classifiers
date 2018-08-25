import sys, re, ast

model_file_path = sys.argv[1]
# model_file_path = "averagedmodel.txt"     #f1 0.89843550104
# model_file_path = "vanillamodel.txt"    #f1 0.895301405178
model_file = open(model_file_path, "r")
model_data = model_file.read().split("\n")
test_file_path = sys.argv[2]
# test_file_path = "dev-text.txt"
test_file = open(test_file_path, "r")
test_data = test_file.read().split("\n")

filename = model_file_path.rsplit("/", 1)
filename = filename[len(filename) - 1]
weights = dict()
cached_weights = dict()
class1_bias, class1_beta, class1_c = 0, 0, 1
class2_bias, class2_beta, class2_c = 0, 0, 1

output_data = list()


def read_model_file():
    global class1_bias, class1_beta, class1_c
    global class2_bias, class2_beta, class2_c
    global weights, cached_weights
    if "averagedmodel.txt" == filename:
        class1_bias = ast.literal_eval(model_data[1])
        class2_bias = ast.literal_eval(model_data[2])
        class1_beta = ast.literal_eval(model_data[4])
        class2_beta = ast.literal_eval(model_data[5])
        class1_c = ast.literal_eval(model_data[7])
        class2_c = ast.literal_eval(model_data[8])
        weights = ast.literal_eval(model_data[10])
        cached_weights = ast.literal_eval(model_data[12])

    elif "vanillamodel.txt" == filename:
        class1_bias = ast.literal_eval(model_data[1])
        class2_bias = ast.literal_eval(model_data[2])
        weights = ast.literal_eval(model_data[4])


def process_each_line(identifier, sentence):
    global class1_bias, class1_beta, class1_c
    global class2_bias, class2_beta, class2_c
    global weights, cached_weights
    frequency = dict()
    sentence = sentence.split(" ")
    sentence = [w.lower().strip() for w in sentence]
    for word in sentence:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    class1_activation = class1_bias
    class2_activation = class2_bias
    if "vanillamodel.txt" == filename:
        for word, value in frequency.iteritems():
            if word in weights:
                w = weights[word]
                class1_activation += w[0] * value
                class2_activation += w[1] * value

    elif "averagedmodel.txt" == filename:
        class1_activation -= class1_beta / float(class1_c)
        class2_activation -= class2_beta / float(class2_c)
        for word, value in frequency.iteritems():
            cached_value = (0, 0)
            if word in cached_weights:
                cached_value = cached_weights[word]
            if word in weights:
                w = weights[word]
                class1_activation += value * (w[0] - (cached_value[0] / float(class1_c)))
                class2_activation += value * (w[1] - (cached_value[1] / float(class2_c)))

    class1 = "True" if class1_activation >= 0 else "Fake"
    class2 = "Pos" if class2_activation >= 0 else "Neg"
    return identifier + " " + class1 + " " + class2


def parse_test_file1():
    for line in test_data:
        line = line.split()
        if len(line) < 2:
            continue
        identifier = line[0]
        part1 = line[1:]
        sentence = ' '
        for word in part1:
            sentence += word + " "
        sentence = sentence.strip()
        sentence = re.sub(r'[^\w\s]', '', sentence)
        output_data.append(process_each_line(identifier, sentence))


def parse_test_file():
    for line in test_data:
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        identifier = parts[0]
        sentence = re.sub(r'[^\w\s]', '', parts[1]).lower()
        output_data.append(process_each_line(identifier, sentence))


read_model_file()
parse_test_file()
model_file.close()
test_file.close()
output_file = open("percepoutput.txt", "w")
for line in output_data:
    output_file.write(line + "\n")
output_file.close()
