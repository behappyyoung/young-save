filename = 'genome_snp_map.txt'
try:
    with open(filename, "rU") as fp:
        content = fp.readlines()
    count = 0
    for line in content:
        count += 1
        line_l = line.strip().split('\t')
        print(count, line_l)
    fp.close()
except IOError:
    pass