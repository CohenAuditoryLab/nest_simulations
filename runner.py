import neuron_testing as test
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import runtime

###########################################
####   PARAMETERS   #######################
###########################################

# Reference external function for 
args = {
	'freq_num': 10,
	'amp_factor': 100,
	'sim_time': 200.0,
	'grid_size': [5.0,5.0],

	'base_stim_rate': 2000.0,
	'tun_rad': 5,

	'neuron_mod': 'iaf_psc_alpha',

	'pyr_layer_num': 500,
	'inh_layer_num': 100,

	'stim_conn_rad': 0.25,
	'stim_conn_p_center': 1.0,
	'stim_conn_p_sigma': 1.0,
	'stim_conn_weight_center': 10.0,
	'stim_conn_weight_sigma': 1.0,

	'pyr_conn_rad': 0.25,
	'pyr_conn_p_center': 1.0,
	'pyr_conn_p_sigma': 2.0,
	'pyr_conn_weight_center': 1.5,
	'pyr_conn_weight_sigma': 1.0,

	'inh_conn_rad': 0.5,
	'inh_conn_p_center': 1.0,
	'inh_conn_p_sigma': 1.0,
	'inh_conn_weight_center': 1.5,
	'inh_conn_weight_sigma': 1.0,

	'seed': 10
}

# Specify independent variable and test range
variable = 'tun_rad'
test_range = [i+1 for i in range(10)]

###########################################
####   SIMULATION   #######################
###########################################

firing_rates = []
init_time = runtime.time()
for i in test_range:
	args[variable] = i
	var_frs = test.main(init_time, test_range.index(i), len(test_range), args)
	firing_rates.append(var_frs)

###########################################
####   CALCULATIONS   #####################
###########################################

# Calculate tuning curve widths
tun_curve_w = [{} for i in test_range]
tun_curve_std = [{} for i in test_range]
for i in range(len(firing_rates)):
	for n in firing_rates[i].keys():
		tuning_widths = [len(j)-j.count(0.0) for j in firing_rates[i][n]]
		tun_curve_w[i][n] = np.mean(tuning_widths)
		neuron_num = args['freq_num']*args[n+'_layer_num']
		tun_curve_std[i][n] = np.std(tuning_widths)

###########################################
####   GRAPHS   ###########################
###########################################

# Basic plot setup
plt.title("Tuning Curve Width v %s" % variable)
plt.xlabel(variable)
plt.ylabel('tuning curve width')
pyr_lab = mlines.Line2D([],[],color='blue',label='pyramidal')
inh_lab = mlines.Line2D([],[],color='red',label='inhibitory')
plt.legend(handles=[pyr_lab,inh_lab])

# Plot separate tuning curve data for pyramidal and inhibitory neurons
for n in firing_rates[0].keys():
	if n == 'pyr':
		plt_sty = 'b-'
	else:
		plt_sty = 'r-'
	y_axis = [dic[n] for dic in tun_curve_w]
	plt.plot(test_range, y_axis, plt_sty)
	plt.errorbar(test_range, y_axis, yerr=[dic[n] for dic in tun_curve_std], 
		         fmt=plt_sty)

# Display results of all simulations
runtime.final(init_time,args['freq_num'],len(test_range))
plt.show()