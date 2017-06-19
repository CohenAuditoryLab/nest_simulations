import nest
import nest.topology as topp
import numpy as np
from runtime import Runtime

# function runs simulation using dictionary of parameters
def main(args,rt,sim_num,var_id):
	
	###########################################
	####   PARAMETERS   #######################
	###########################################

	freq_num = args['freq_num'] # number of auditory frequencies
	amp_factor = args['amp_factor'] # strength of signal coming from generators
	sim_time = args['sim_time'] # duration of simulation (ms)
	grid_size = args['grid_size'] # side lengths of topological layers (nm)

	base_stim_rate = args['base_stim_rate'] # stimulus rate (Hz)
	tun_rad = args['tun_rad'] # broadness of tuning curve

	neuron_mod = args['neuron_mod']

	stim_layer_param = {
		'extent'   : grid_size,  # size of layer (nm^2)
		'rows'     : amp_factor, # strength of signal amplification
		'columns'  : freq_num,   # one column per frequency
		'elements' : 'poisson_generator'
	}
	pyr_layer_param = {
		'extent'   : grid_size,             # size of layer (nm^2)
		'rows'     : args['pyr_layer_num'], # neurons per frequency
		'columns'  : freq_num,              # one column per frequency
		'elements' : neuron_mod
	}
	inh_layer_param = {
		'extent'   : grid_size,             # size of layer (nm^2)
		'rows'     : args['inh_layer_num'], # neurons per frequency
		'columns'  : freq_num,              # one column per frequency
		'elements' : neuron_mod
	}
	stim_conn_param = {
		'connection_type': 'divergent', # connection based on target layer
		'mask': {'circular': {'radius': grid_size[0]*args['stim_conn_rad']}},
		'kernel': {'gaussian': { # connection probability based on distance
			'p_center': args['stim_conn_p_center'],
			'sigma': args['stim_conn_p_sigma']
		}},
		'weights': {'gaussian': { # weight of connection based on distance
			'p_center': args['stim_conn_weight_center'],
			'sigma': args['stim_conn_weight_sigma'],
			'min': 0.0
		}}
	}
	pyr_conn_param = {
		'connection_type': 'divergent', # connection based on target layer
		'mask': {'circular': {'radius': grid_size[0]*args['pyr_conn_rad']}},
		'kernel': {'gaussian': { # connection probability based on distance
			'p_center': args['pyr_conn_p_center'],
			'sigma': args['pyr_conn_p_sigma']
		}},
		'weights': {'gaussian': { # weight of connection based on distance
			'p_center': args['pyr_conn_weight_center'],
			'sigma': args['pyr_conn_weight_sigma'],
			'min': 0.0
		}}
	}
	inh_conn_param = {
		'connection_type': 'divergent', # connection based on target layer
		'mask': {'circular': {'radius': grid_size[0]*args['inh_conn_rad']}},
		'kernel': {'gaussian': { # connection probability based on distance
			'p_center': args['inh_conn_p_center'],
			'sigma': args['inh_conn_p_sigma']
		}},
		'weights': {'gaussian': { # weight of connection based on distance
			'p_center': -1*args['inh_conn_weight_center'],
			'sigma': args['inh_conn_weight_sigma'],
			'max': 0.0
		}}
	}
	pypy_conn_param = {
		'connection_type': 'divergent', # connection based on target layer
		'mask': {'circular': {'radius': grid_size[0]*args['pypy_conn_rad']}},
		'kernel': {'gaussian': { # connection probability based on distance
			'p_center': args['pypy_conn_p_center'],
			'sigma': args['pypy_conn_p_sigma']
		}},
		'weights': {'gaussian': { # weight of connection based on distance
			'p_center': args['pypy_conn_weight_center'],
			'sigma': args['pypy_conn_weight_sigma'],
			'min': 0.0
		}}
	}

	sample_size = args['sample_size'] # number of neurons to randomly sample
	np.random.seed(args['seed']) # set numpy seed for reproducability
	
	nest.ResetKernel() # reset NEST
	nest.SetKernelStatus({'local_num_threads': 3}) # threading for efficiency

	###########################################
	####   NETWORK SETUP   ####################
	###########################################

	# Create layers
	layers = {
		'stim': topp.CreateLayer(stim_layer_param),
		'pyr' : topp.CreateLayer(pyr_layer_param),
		'inh' : topp.CreateLayer(inh_layer_param)
	}

	# Connect layers
	topp.ConnectLayers(layers['stim'], layers['pyr'], stim_conn_param)
	topp.ConnectLayers(layers['pyr'], layers['inh'], pyr_conn_param)
	topp.ConnectLayers(layers['inh'], layers['pyr'], inh_conn_param)
	topp.ConnectLayers(layers['pyr'], layers['pyr'], pypy_conn_param)

	# Connect spike detectors to random recording neurons
	spk_det = {
		'pyr': nest.Create('spike_detector'),
		'inh': nest.Create('spike_detector')
	}
	rec_neurons = {
  		'pyr': np.random.choice(nest.GetNodes(layers['pyr'])[0],
 		                        size=sample_size, 
 		                        replace=False).tolist(),
 		'inh': np.random.choice(nest.GetNodes(layers['inh'])[0],
 		                        size=sample_size, 
 		                        replace=False).tolist()
  	}
	for n in spk_det.keys():
		nest.Connect(rec_neurons[n], spk_det[n])

	###########################################
	####   SIMULATION   #######################
	###########################################

	# Initialize dictionary of firing rates
	firing_rates = {
		'pyr': [[] for i in range(sample_size)],
		'inh': [[] for i in range(sample_size)]
	}

	for freq in range(freq_num):
		nest.ResetNetwork()
		nest.SetKernelStatus({'time': 0.0})
		rt.live_update(freq, sim_num, var_id)
		
		# Set rate for stim_layer neurons based on frequency of stimulus
		for row in range(amp_factor):
			for col in range(max(0,freq-tun_rad),
				             min(freq_num,freq+tun_rad+1)):
				rate_fac = max(0.0,(tun_rad-abs(freq-col))/float(tun_rad))
				nest.SetStatus(topp.GetElement(layers['stim'],[col,row]),
					           {'rate': rate_fac*base_stim_rate})
		
		# Simulate and record event data from spike detectors
		nest.Simulate(sim_time)
		
		# Store firing rate data for each set of neurons
		for n in spk_det.keys():
			sender_fires = [0] * sample_size
			for i in nest.GetStatus(spk_det[n])[0]['events']['senders']:
				sender_fires[rec_neurons[n].index(i)] += 1
			for i in range(sample_size):
				firing_rates[n][i].append(1000*sender_fires[i]/sim_time)
		
		# Reset rates for stim_layer neurons
		for row in range(amp_factor):
			for col in range(max(0,freq-tun_rad),
				             min(freq_num,freq+tun_rad+1)):
				nest.SetStatus(topp.GetElement(layers['stim'],[col,row]),
					           {'rate': 0.0})

	return firing_rates