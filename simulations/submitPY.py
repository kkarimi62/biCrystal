if __name__ == '__main__':
    import sys
    import os
    import numpy as np
    #---
#     lnums = [ 36, 108  ]
#     string=open('simulations.py').readlines() #--- python script
    lnums = [ 39, 117, 122 ]
    string=open('simulations-ncbj-slurm.py').readlines() #--- python script
    #---
    Temps={
                0:300,
#                 1:400,
#                 2:500,
#                 3:600,
#                 4:700,
#                 5:800,
#                 6:900,
            }
    
    SwapEvery={
#                 0:10,
#                 1:20,
#                 2:40,
#                 3:80,
                4:100
                }
    SwapNumber={
                0:0.1,
                1:0.2,
                2:0.4
                }
    natom = 1200
    #---
    count = 0
    for keys_t in Temps:
        temp = Temps[keys_t]
        for key_s in SwapEvery:
            nevery = SwapEvery[key_s]
            for key_n in SwapNumber:
                nswap = int(SwapNumber[key_n] * natom / 6) #--- six pairs
                #---	densities
                inums = lnums[ 0 ] - 1
                string[ inums ] = "\t7:\'withDefectWithwall/SwapNumber/number%s\',\n"%(key_n) #--- change job name
                #---
                inums = lnums[ 1 ] - 1
                string[ inums ] = "\t72:\' -var seed %%s -var buff 0.0 -var buffy 0.0 -var Tinit %s -var T %s -var nevery 100 -var ParseData 1 -var DataFile data_init.txt -var DumpFile dumpThermalized.xyz -var WriteData equilibrated.dat\'%%np.random.randint(1001,9999),\n"%(temp,temp)
                #---
                inums = lnums[ 2 ] - 1
                string[ inums ] = "\t12:\' -var buff 0.0 -var buffy 3.5 -var T %s -var swap_every %s -var swap_atoms %s -var rn %%s -var dump_every 10 -var ParseData 1 -var DataFile equilibrated.dat -var DumpFile traj.dump\'%%np.random.randint(1001,100000),\n"%(temp,nevery,nswap)
                #---
                sfile=open('junk%s.py'%count,'w');sfile.writelines(string);sfile.close()
                os.system( 'python2 junk%s.py'%count )
                os.system( 'rm junk%s.py'%count )
                count += 1
