import os.path
import re
import time

import  requests
if __name__=="__main__":
    # lol
    contains_gifs = requests.get("https://forum.margonem.pl/?task=forum&show=posts&id=514155&fbclid=IwAR2V5Xt5VvbuqvzIjZ4wRyY_xe64gbC7ahjan-tuDKS5S2zXlTvkd2Jc4to")
    pattern = re.compile(r'https:\/\/\S+?(?:gif)')

    download_int = 0
    for m in re.findall(pattern, str(contains_gifs.content, 'utf-8')):
        what_to_download = m
        file = open(os.path.join("ludziki",os.path.basename(what_to_download)), 'wb')
        file.write(requests.get(what_to_download).content)
        file.flush()
        file.close()
        download_int += 1
        time.sleep(1)
        print(download_int)
