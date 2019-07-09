# Quick script to combine files + add positioning tokens
filenames = ['mtg_encoded1.txt', 'mtg_encoded2.txt', 'mtg_encoded3.txt', 'mtg_encoded4.txt', 'mtg_encoded5.txt',
             'mtg_encoded6.txt', 'mtg_encoded7.txt', 'mtg_encoded8.txt', 'mtg_encoded9.txt', 'mtg_encoded10.txt']
with open('concat_mtg_encoded.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                if len(line) > 5:
                    outfile.write("<|startoftext|>" +
                                  line.strip() + "<|endoftext|>\n")
