import neuron_testing as test
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import scipy.stats as stats
from mpl_toolkits.mplot3d import axes3d
from itertools import combinations
from time import strftime
from runtime import Runtime

###########################################
####   PARAMETERS   #######################
###########################################

save_graphs = True # Autosave graphs upon creation?
show_graphs = True # Display all graphs to screen?
send_msg    = True # Send an email when code has run to completion?

# Reference neuron_testing.py for more information on arguments
args = {
	'freq_num': 20,
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
	'pyr_conn_p_center': [0.1*(i+1) for i in range(10)],
	'pyr_conn_p_sigma': [0.1*(i+1) for i in range(20)],
	'pyr_conn_weight_center': [0.1*(i+1) for i in range(20)],
	'pyr_conn_weight_sigma': [0.1*(i+1) for i in range(20)]
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

			###########################################
			####   SIMULATION   #######################
			###########################################

			args[var_pair[0]] = x
			args[var_pair[1]] = y
			sim_num = test_ranges[0].index(x) * len(test_ranges[1]) \
			          + test_ranges[1].index(y)
			firing_rates = test.main(args, rt, sim_num, var_pair)
			
			###########################################
			####   CALCULATIONS   #####################
			###########################################

			# Calculate tuning curve widths and error bars
			for n in firing_rates.keys():
				tuning_widths = [len(j)-j.count(0.0) for j in firing_rates[n]]
				z_vals_all[sim_num][n] = np.mean(tuning_widths)
				sem_vals_all[sim_num][n] = stats.sem(tuning_widths)

			x_vals.append(x)
			y_vals.append(y)
	
	###########################################
	####   GRAPHS   ###########################
	###########################################

	# Basic plot setup
	fig = plt.figure(len(rt.completed_vars)+1)
	ax = fig.gca(projection='3d')
	plt.title("Tuning Curve Width v %s, %s" % (var_pair[0],var_pair[1]))
	ax.set_xlabel(var_pair[0])
	ax.set_ylabel(var_pair[1])
	ax.set_zlabel('tuning curve width')

	# Plot separate tuning curve data for pyramidal and inhibitory neurons
	for n in z_vals_all[0].keys():
		if n == 'pyr':
			c = 'blue'
			plt_sty = 'b-'
		else:
			c = 'red'
			plt_sty = 'r-'
		z_vals = [dic[n] for dic in z_vals_all]
		ax.plot_trisurf(x_vals, y_vals, z_vals, color=c)

	# Reset variable to default value and increment
	args[var_pair[0]] = args_defaults[0]
	args[var_pair[1]] = args_defaults[1]
	rt.inc_var(var_pair)

	# Save the figure
	if save_graphs:
		plt.savefig('figures/%s_%s %s.png' \
			        % (var_pair[0], var_pair[1], strftime("%Y-%m-%d %H:%M")))

# Display results of all simulations
rt.final(send_msg)
if show_graphs:
	plt.show()