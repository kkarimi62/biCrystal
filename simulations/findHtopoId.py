import pandas as pd
import pdb 
import os

n=32
for i in range(n):
    sfile = 'test0/Run%s/sortieproc.0'%i

    os.system('python lmpScripts/getTopoDefectFree.py %s 0 Topo_ignore%s'%(sfile,i))
    os.system('wc -l Topo_ignore%s'%i)
