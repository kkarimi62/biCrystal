#--- output thermodynamic variables
#variable varStep equal step
#variable varPress equal press
#variable varTemp equal temp
#variable varTime equal v_varStep*${dt}
#variable varXy	 equal	xy
#variable varLy	 equal	ly
#variable varVol	 equal	vol
#variable varPe	 equal	pe
#variable varPxx	 equal	pxx
#variable varPyy	 equal	pyy
#variable varPzz	 equal	pzz
#variable varPxy	 equal	pxy
#variable varSxy	 equal	-v_varPxy*${cfac}
#variable varSzz	 equal	-v_varPzz*${cfac}
#variable varExy	 equal	v_varXy/v_varLy		
#variable varEzz	 equal	v_varTime*${GammaDot}		
#variable ntherm  equal	ceil(${Nstep}/${nthermo})
#variable varn	 equal	v_ntherm
#fix extra all print ${varn} "${varStep} ${varTime} ${varEzz} ${varTemp} ${varPe} ${varPxx} ${varPyy} ${varSzz} ${varVol}" screen no title "step time ezz temp pe pxx pyy szz vol" file thermo.txt

compute thermo_temp0 bulk temp
variable varTemp equal temp

variable       swap_attempt equal f_4[1]+f_5[1]+f_6[1]+f_7[1]+f_8[1]+f_9[1]
variable       swap_accept  equal f_4[2]+f_5[2]+f_6[1]+f_7[1]+f_8[1]+f_9[1]
#if "${swap_attempt} > 0" then &
#	"variable	   swap_ratio		equal 1.0*${swap_accept}/${swap_attempt}" &
#else &
#	"variable	   swap_ratio		equal 0.0"


thermo 100
thermo_style custom step c_thermo_temp0 pe press vol v_swap_accept v_swap_attempt
thermo_modify norm no

