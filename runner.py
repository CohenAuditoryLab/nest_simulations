import neuron_testing as test

# Setup base parameters for simulations
args = {
	'freq_num': 25,
	'sample_size': 20,
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

# Run variable simulations
for i in range(5):
	args['tun_rad'] = i+1
	test.main(args)