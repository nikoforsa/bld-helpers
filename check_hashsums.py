import os,sys
import hashlib

path_sums='./sums.dat'
path = "./"

def GetDataSums():
    try:
        with open(path_sums) as file:
            line1 = [line.strip() for line in file]
        return line1
    except FileNotFoundError:
        print("file sums.dat does not exist")
        sys.exit()
    except:
        print("Ошибка при работе с файлом")  
        sys.exit()

def GetFileinDir():
    files = os.listdir(path)
    # Filtering only the files.
    files = [f for f in files if os.path.isfile(path+'/'+f)]
    #print(*files, sep="\n")
    return files

def md5sum(f, block_size=None):
    """Returns the MD5 checksum"""
    if block_size is None:
        block_size = 4096
    hash = hashlib.md5()
    with open(path+f, 'rb') as fh:
        block = fh.read(block_size)
        while block:
            hash.update(block)
            block = fh.read(block_size)
    return hash.hexdigest()+'\t'+f

def md5sums(basedir=None, block_size=None):
    filelist = GetFileinDir()
    #print(filelist)
    hash_file = [md5sum(f, block_size=block_size) for f in filelist]
    #    print( md5sum(f, block_size=block_size), f)
    return hash_file

def CheckCompare():
    for f in md5sums():
        for ff in GetDataSums():
            localf = f.split('\t')[0]
            sumsf = ff.split('\t')[0]
            namef = f.split('\t')[1]
            sumsnamef = ff.split('\t')[1]          
            if localf == sumsf and namef == sumsnamef:            
                print(f"Checked file {namef} ")
                print(f"\t | hash {localf} | sums.dat {sumsf} | success ")
            #else:
            #    print(f"hash sums are not identical") 
    
def __main__():
    CheckCompare()

__main__()