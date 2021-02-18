import csv
import sys

def convert(filename):
    f = open(filename, "r")
    data = f.readlines()
    
    with open(filename[:-4]+'.csv','w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow('time, A1, A2, A3, A4')
        for everyline in data:
            if 'Read Value' in everylien:
                time, _, _, sensor = everyline.split(',')
                sensor = sensor.split(' ')[2][2:].split('-')
                sensor = ''.join(sensor)

                splitted = list([int(sensor[i:i+4], 16)/1000 for i in range(0, len(sensor),4)])
                splitted.insert(0, time)
                writer.writerow(splitted)
                print(splitted)
                    
def usage():
    print('expecting one argument: name of text file to read')
    sys.exit()
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    else:
        convert(sys.argv[1])
