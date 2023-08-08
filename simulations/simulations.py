def makeOAR( EXEC_DIR, node, core, time ):
    someFile = open( 'oarScript.sh', 'w' )
    print >> someFile, '#!/bin/bash\n'
    print >> someFile, 'EXEC_DIR=%s\n' %( EXEC_DIR )
    print >> someFile, 'MEAM_library_DIR=%s\n' %( MEAM_library_DIR )
    print >> someFile, 'source ~/Project/opt/deepmd-kit/bin/activate ~/Project/opt/deepmd-kit\nexport OMP_NUM_THREADS=%s'%(nThreads*nNode) #--- deep potential stuff
    print >> someFile, 'module load openmpi/4.0.2-gnu730\nmodule load lib/openblas/0.3.13-gnu\n'

    #--- run python script 
#	 print >> someFile, "$EXEC_DIR/%s < in.txt -var OUT_PATH %s -var MEAM_library_DIR %s"%( EXEC, OUT_PATH, MEAM_library_DIR )
#	cutoff = 1.0 / rho ** (1.0/3.0)
    for script,var,indx, execc in zip(Pipeline,Variables,range(100),EXEC):
        if execc[:4] == 'lmp_': #_mpi' or EXEC == 'lmp_serial':
            print >> someFile, "mpirun --oversubscribe -np %s $EXEC_DIR/%s < %s -echo screen -var OUT_PATH \'%s\' -var PathEam %s -var INC \'%s\' %s\n"%(nThreads*nNode, EXEC_lmp, script, OUT_PATH, '${MEAM_library_DIR}', SCRPT_DIR, var)
        elif execc == '_lmp':
            print >> someFile, "$EXEC_DIR/%s < %s -echo screen -var OUT_PATH \'%s\' -var PathEam %s -var INC \'%s\' %s\n"%(EXEC_lmp, script, OUT_PATH, '${MEAM_library_DIR}', SCRPT_DIR, var)
        elif execc == 'py':
            print >> someFile, "python3 %s %s\n"%(script, var)
        elif execc == 'kmc':
#			print >> someFile, "time mpiexec %s %s\n"%(script, var)
            print >> someFile, "mpirun --oversubscribe -np %s -x Buffer=0.0 -x PathEam=%s -x INC=\'%s\' %s %s\n"%(nThreads*nNode,'${MEAM_library_DIR}', SCRPT_DIR,var,script)

    someFile.close()										  


if __name__ == '__main__':
    import os
    import numpy as np

    nruns	 = range(1) #8)
    #
    nThreads = 8
    nNode	 = 1
    #
    jobname  = {
                3:'hydrogenDiffusionInAlMultipleTemp/Temp1000K', 
                4:'mitStuff2nd', 
                5:'pureHydrogenDiffusion_md_MultipleTemps/temp0', #'pureHydrogenDiffusion5th', 
                6:'noDefect/excludeHydrogen', #'hydrogenFree',
               }[6]
    sourcePath = os.getcwd() +\
                {	
                    0:'/junk',
                    1:'/../postprocess/NiCoCrNatom1K',
                    2:'/NiCoCrNatom1KTemp0K',
                    5:'/dataFiles/reneData',
                    4:'/mitPotential',
                    6:'/pureCrystall',
                }[ 4 ] #--- must be different than sourcePath. set it to 'junk' if no path
        #
    sourceFiles = { 0:False,
                    1:['data_init.txt','data_minimized.txt'],
                    2:['data.txt','ScriptGroup.txt'],
                    3:['Topo_ignore'], 
                    4:['data_minimized.txt'],
                    5:['data_init.txt','ScriptGroup.0.txt'], #--- only one partition! for multiple ones, use 'submit.py'
                    6:['sortieproc.0'], 
                    7:['compressed_model.pb','frozen_model.pb'], #'init.lmp'], 
                 }[7] #--- to be copied from the above directory. set it to '0' if no file
    #
    EXEC_DIR = {0:'~/Project/git/lammps2nd/lammps/src', #--- path for executable file
                1:'~/Project/opt/deepmd-kit/bin' #--- path for executable file: deep potential
                }[1]
    #
    MEAM_library_DIR='/home/kamran.karimi1/Project/git/lammps2nd/lammps/potentials'
    #
    SCRPT_DIR = os.getcwd()+'/lmpScripts' 
    #
    SCRATCH = None
    OUT_PATH = '.'
    if SCRATCH:
        OUT_PATH = '/scratch/${SLURM_JOB_ID}'
    #--- py script must have a key of type str!
    LmpScript = {	                0:'in.PrepTemp0',
                    1:'relax.in', 
                    2:'relaxWalls.in', 
                    7:'in.Thermalization', 
                    71:'in.Thermalization', 
                    72:'in.ThermalizationConstantVolume', 
                    4:'in.vsgc', 
                    5:'in.minimization', 
                    51:'in.minimization', 
                    6:'in.shearDispTemp', 
                    8:'in.shearLoadTemp',
                    9:'in.elastic',
                    10:'in.elasticSoftWall',
                    11:'in.relax',
                    12:'in.swap_GB4',
                    'p0':'partition.py', #--- python file
                    'p1':'WriteDump.py',
                    'p2':'DislocateEdge.py',
                    'p21':'DislocateEdge.py',
                    'p3':'kartInput.py',
                    'p4':'takeOneOut.py',
                    'p5':'bash-to-csh.py',
                    'p6':'addAtom.py',
                    'p7':'getTopoDefectFree.py',
                    1.0:'kmc.sh', #--- bash script
                    2.0:'kmcUniqueCRYST.sh', #--- bash script
                } 
    #
    def SetVariables():
        Variable = {
                0:' -var natoms 100000 -var cutoff 3.52 -var ParseData 0 -var ntype 3 -var DumpFile dumpInit.xyz -var WriteData data_init.txt',
                6:' -var buff 0.0 -var T 300 -var P 0.0 -var gammaxy 1.0 -var gammadot 1.0e-04 -var nthermo 10000 -var ndump 1000 -var ParseData 1 -var DataFile Equilibrated_300.dat -var DumpFile dumpSheared.xyz',
                4:' -var T 600.0 -var t_sw 20.0 -var DataFile Equilibrated_600.dat -var nevery 100 -var ParseData 1 -var WriteData swapped_600.dat', 
                5:' -var buff 0.0 -var buffy 0.0 -var nevery 1000 -var ParseData 0 -var natoms 2000 -var ntype 5 -var rho1 0.1 -var rho2 0.1 -var rho3 0.45 -var rho4 0.0 -var rho5 0.35 -var cutoff 3.54  -var DumpFile dumpMin.xyz -var WriteData data_minimized.dat -var seed0 %s -var seed1 %s -var seed2 %s -var seed3 %s'%tuple(np.random.randint(1001,9999,size=4)), 
                51:' -var buff 0.0 -var buffy 0.0 -var nevery 1000 -var ParseData 1 -var DataFile data_minimized.txt -var DumpFile dumpMin.xyz -var WriteData data_minimized.txt', 
                7:' -var buff 0.0 -var T 1500.0 -var P 0.0 -var nevery 100 -var ParseData 1 -var DataFile data_minimized.txt -var DumpFile dumpThermalized.xyz -var WriteData Equilibrated_300.dat',
                71:' -var buff 0.0 -var buffy 0.0 -var T 300.0 -var Tinit 300.0 -var seed %s -var P 0.0 -var nevery 100 -var ParseData 1 -var DataFile data_minimized.dat -var DumpFile dumpThermalized.xyz -var WriteData equilibrated.dat'%np.random.randint(1001,9999),
                72:' -var buff 0.0 -var buffy 0.0 -var T 300.0 -var seed %s -var nevery 100 -var ParseData 1 -var DataFile data_minimized.txt -var DumpFile dumpThermalized.xyz -var WriteData Equilibrated.dat'%np.random.randint(1001,9999),
                8:' -var buff 0.0 -var T 300.0 -var sigm 1.0 -var sigmdt 0.0001 -var ndump 100 -var ParseData 1 -var DataFile Equilibrated_0.dat -var DumpFile dumpSheared.xyz',
                9:' -var natoms 1000 -var cutoff 3.52 -var ParseData 1',
                10:' -var ParseData 1 -var DataFile swapped_600.dat',
                11:' ',
                12:' -var buff 0.0 -var buffy 0.0 -var T 300 -var swap_every 1 -var swap_atoms 1 -var rn %s -var dump_every 10 -var ParseData 1 -var DataFile equilibrated.dat -var DumpFile traj.dump'%np.random.randint(1001,100000),
                'p0':' swapped_600.dat 10.0 %s'%(os.getcwd()+'/../postprocess'),
                'p1':' swapped_600.dat ElasticConst.txt DumpFileModu.xyz %s'%(os.getcwd()+'/../postprocess'),
                'p2':' %s 3.52 30.0 14.0 13.0  data_minimized.txt 4 2 1.0 0.0'%(os.getcwd()+'/lmpScripts'),
                'p21':' %s 3.52 52.0 18.0 26.0 data_init.txt 2 2 1.0 0.0'%(os.getcwd()+'/lmpScripts'),
                'p3':' data_minimized.txt init_xyz.conf %s 2000.0'%(os.getcwd()+'/lmpScripts'),
                'p4':' data_minimized.txt data_minimized.txt %s 1'%(os.getcwd()+'/lmpScripts'),
                'p5':' ',
                'p6':' %s data_minimized.txt data_minimized.txt 10'%(os.getcwd()+'/../../HeaDef/postprocess'),
                'p7':' sortieproc.0 0 Topo_ignore',
                 1.0:'-x DataFile=data_minimized.txt',
                 2.0:'-x DataFile=data_minimized.txt',
                } 
        return Variable
    #--- different scripts in a pipeline
    indices = {
                0:[5,7,6], #--- minimize, thermalize, shear(disp. controlled)
                1:['p2','p6', 51, 72], #--- put a dislocation, add interstitial, minimize, thermalize
                2:[11], #--- mit stuff
                4:[5, 'p6',51,'p3','p5',2.0], #--- create lattice, add H, minimize, kart input, kart.sh to bash shell ,invoke kart
                5:['p2', 'p6',51,'p3','p5',1.0], #--- put a dislocation, add H, minimize, kart input, kart.sh to bash shell ,invoke kart
                6:[5,'p3','p5',1.0], #--- minimize, kart input, kart.sh to bash shell ,invoke kart
#					7:['p21',51,'p3','p5',1.0], #--- dislocate, minimize, kart input, kart.sh to bash shell ,invoke kart
                7:[5,'p6',51,'p3','p5',1.0], #--- minimize, add H, minimize,kart input, kart.sh to bash shell ,invoke kart
                8:['p2',51,'p6',51,'p3','p5',1.0], #--- dislocate, minimize,add H, minimize, kart input, kart.sh to bash shell ,invoke kart
                81:[5,'p6',51,'p3','p5',1.0], #--- minimize,add H, minimize, kart input, kart.sh to bash shell ,invoke kart
                82:[5,'p6',51,72], #--- minimize,add H, minimize, thermalize
                9:['p7','p3','p5',1.0], #--- create Topo_ignore, kart input, kart.sh to bash shell ,invoke kart
                10:[5,71,12],
              }[ 10 ]
    Pipeline = list(map(lambda x:LmpScript[x],indices))
#	Variables = list(map(lambda x:Variable[x], indices))
#        print('EXEC=',EXEC)
    #
    EXEC_lmp = ['lmp_mpi','lmp_serial','_lmp'][2]
    durtn = ['23:59:59','00:09:59','167:59:59'][ 0 ]
    mem = '12gb'
    partition = ['gpu-v100','parallel','cpu2019','single'][1]
    #--
    DeleteExistingFolder = True
    #
    EXEC = list(map(lambda x:np.array([EXEC_lmp,'py','kmc'])[[ type(x) == type(0), type(x) == type(''), type(x) == type(1.0) ]][0], indices))	
    if DeleteExistingFolder:
        print('rm %s'%jobname)
        os.system( 'rm -rf %s;mkdir -p %s' % (jobname,jobname) ) #--- rm existing
    os.system( 'rm jobID.txt' )
    # --- loop for submitting multiple jobs
    path=os.getcwd() + '/%s' % ( jobname)
    os.system( 'ln -s %s/%s %s' % ( EXEC_DIR, EXEC_lmp, path ) ) # --- create folder & mv oar script & cp executable
    for irun in nruns:
        counter = irun
        Variable = SetVariables()
        Variables = list(map(lambda x:Variable[x], indices))
        writPath = os.getcwd() + '/%s/Run%s' % ( jobname, irun ) # --- curr. dir
        print ' create %s' % writPath
        os.system( 'mkdir -p %s' % ( writPath ) ) # --- create folder
        #---
        for script,indx in zip(Pipeline,range(100)):
#			os.system( 'cp %s/%s %s/lmpScript%s.txt' %( SCRPT_DIR, script, writPath, indx) ) #--- lammps script: periodic x, pxx, vy, load
            os.system( 'ln -s %s/%s %s' %( SCRPT_DIR, script, writPath) ) #--- lammps script: periodic x, pxx, vy, load
        if sourceFiles: 
            for sf in sourceFiles:
                os.system( 'cp %s/Run%s/%s %s' %(sourcePath, irun, sf, writPath) ) #--- lammps script: periodic x, pxx, vy, load
        #---
        makeOAR( path, 1, nThreads, durtn) # --- make oar script
        os.system( 'chmod +x oarScript.sh; mv oarScript.sh %s' % ( writPath) ) # --- create folder & mv oar scrip & cp executable
        jobname0 = jobname.split('/')[0] #--- remove slash
        os.system( 'sbatch --partition=%s --mem=%s --time=%s --job-name %s.%s --output %s.%s.out --error %s.%s.err \
                        --chdir %s -c %s -n %s %s/oarScript.sh >> jobID.txt'\
                       % ( partition, mem, durtn, jobname0, counter, jobname0, counter, jobname0, counter \
                           , writPath, nThreads, nNode, writPath ) ) # --- runs oarScript.sh! 
#			counter += 1


    os.system( 'mv jobID.txt %s' % ( os.getcwd() + '/%s' % ( jobname ) ) )
