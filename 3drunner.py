import neuron_testing as test
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import scipy.stats as stats
from itertools import combinations
from time import strftime
from runtime import Runtime

###########################################
####   PARAMETERS   #######################
###########################################

# Send an email when code has run to completion?
send_msg = True

# Display all graphs to screen?
show_graphs = False

# Reference neuron_testing.py for more information on arguments
args = {
	'freq_num': 5,
	'amp_factor': 100,
	'sim_time': 100.0,
	'grid_size': [5.0,5.0],

	'base_stim_rate': 2000.0,
	'tun_rad': 4,

	'neuron_mod': 'iaf_psc_alpha',

	'pyr_layer_num': 500,
	'inh_layer_num': 500,

	'stim_conn_rad': 0.25,
	'stim_conn_p_center': 0.5,
	'stim_conn_p_sigma': 1.0,
	'stim_conn_weight_center': 10.0,
	'stim_conn_weight_sigma': 0.25,

	'pyr_conn_rad': 0.5,
	'pyr_conn_p_center': 1.0,
	'pyr_conn_p_sigma': 2.0,
	'pyr_conn_weight_center': 1.5,
	'pyr_conn_weight_sigma': 1.0,

	'inh_conn_rad': 0.5,
	'inh_conn_p_center': 1.0,
	'inh_conn_p_sigma': 1.0,
	'inh_conn_weight_center': 1.5,
	'inh_conn_weight_sigma': 1.0,

	'sample_size': 400,
	'seed': 10
}

# Specify independent variables and corresponding test ranges
var_dict = {
	'pyr_conn_p_center': [0.1*(i+1) for i in range(5)],
	'pyr_conn_p_sigma': [0.1*(i+1) for i in range(5)],
	'pyr_conn_weight_center': [0.1*(i+1) for i in range(5)],
	#'pyr_conn_weight_sigma': [0.1*(i+1) for i in range(5)]
}
rt = Runtime(var_dict,args['freq_num'],'double')

# Run simulations for each specified variable
for var_pair in combinations(var_dict.keys(),2):
	args_defaults = (args[var_pair[0]],args[var_pair[1]])
	test_ranges = (var_dict[var_pair[0]],var_dict[var_pair[1]])
	tot_trials = len(test_ranges[0])*len(test_ranges[1])
	
	x_vals = []
	y_vals = []
	z_vals_all = [{} for i in range(tot_trials)]
	sem_vals_all = [{} for i in range(tot_trials)]

	for x in test_ranges[0]:
		for y in test_ranges[1]:
			curr_trial = len(rt.completed_vars)

			###########################################
			####   SIMULATION   #######################
			###########################################

			args[var_pair[0]] = x
			args[var_pair[1]] = y
			var_num = test_ranges[0].index(x) * len(test_ranges[1]) \
			          + test_ranges[1].index(y)
			firing_rates = test.main(args, rt, var_num, var_pair)
			
			###########################################
			####   CALCULATIONS   #####################
			###########################################

			# Calculate tuning curve widths and error bars
			for n in firing_rates.keys():
				tuning_widths = [len(j)-j.count(0.0) for j in firing_rates[n]]
				z_vals_all[curr_trial][n] = np.mean(tuning_widths)
				sem_vals_all[curr_trial][n] = stats.sem(tuning_widths)

			x_vals.append(x)
			y_vals.append(y)
	
	rt.inc_var(var_pair)

	###########################################
	####   GRAPHS   ###########################
	###########################################

	# Basic plot setup
	plt.figure(len(rt.completed_vars)+1)
	rt.inc_var(variable)
	plt.title("Tuning Curve Width v %s" % variable)
	plt.xlabel(variable)
	plt.ylabel('tuning curve width')

	# Plot separate tuning curve data for pyramidal and inhibitory neurons
	for n in firing_rates[0].keys():
		if n == 'pyr':
			plt_sty = 'b-'
		else:
			plt_sty = 'r-'
		y_axis = [dic[n] for dic in tun_curve_w]
		plt.plot(test_range, y_axis, plt_sty)
		plt.errorbar(test_range, y_axis, 
			         yerr=[dic[n] for dic in tun_curve_sem], fmt=plt_sty)

	# Reset variable to default value
	args[variable] = args_default
	plt.savefig('figures/%s %s.png' % (variable,strftime("%Y-%m-%d %H:%M")))

# Display results of all simulations
rt.final(send_msg)
if show_graphs:
	plt.show()