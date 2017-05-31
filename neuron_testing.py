import nest
import nest.topology as topp
import numpy as np
import matplotlib.pyplot as plt

###########################################
####   PARAMETERS   #######################
###########################################

freq_num = 9 # number of auditory frequencies
sample_size = 10 # number of neurons to record from
amp_factor = 500 # strength of signal coming from generators
sim_time = 500.0 # duration of simulation (ms)
grid_size = [10.0,10.0] # side lengths of topological layers (nm)

base_stim_rate = 2000.0 # stimulus rate (Hz)
tuning_rad = 3 # broadness of tuning curve
tono_rad = 3 # radius of stimulation for tonotopic map

neuron_mod = 'iaf_psc_alpha'
pyr_num = 12 # number of pyramidal neurons
inh_num = 2 # number of inhibitory interneurons
neuron_num = pyr_num + inh_num # total number of downstream neurons

tono_layer_param = {
	'extent'   : grid_size,  # size of layer (nm^2)
	'rows'     : amp_factor, # strength of signal amplification
	'columns'  : freq_num,   # one column per frequency
	'elements' : 'poisson_generator'
}
pyr_layer_param = {
	'extent'   : grid_size, # size of layer (nm^2)
	'rows'     : 100,       # relative number of neurons per frequency
	'columns'  : freq_num,  # one column per frequency
	'elements' : neuron_mod
}
inh_layer_param = {
	'extent'   : grid_size, # size of layer (nm^2)
	'rows'     : 10,        # relative number of neurons per frequency
	'columns'  : freq_num,  # one column per frequency
	'elements' : neuron_mod
}

pyr_weight = 1.0 # weight of excitatory synapses
inh_weight = -1.0 # weight of inhibitory synapses

# Convert raw integers to corresponding frequencies
def freq_convert(x):
	return 1000*(x+1)/2

# Print to terminal window live updates with simulation information
def live_update(x):
	trial_str = '0'
	if x < 10:
		trial_str += str(x)
	else:
		trial_str = str(x)
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
	print "XXX   WORKING ON SIMULATION %s of %s   XXX" \
	      % (trial_str,'0'+str(freq_num))
	print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Initialize neuron array of firing rates at each frequency
firing_rates = [[] for i in range(sample_size)]

np.random.seed(20) # set numpy seed for reproducability
nest.ResetKernel() # reset NEST

###########################################
####   NETWORK SETUP   ####################
###########################################

# Create layers
stim_layer = topp.CreateLayer(tono_layer_param)
pyr_layer_1 = topp.CreateLayer(pyr_layer_param)
inh_layer = topp.CreateLayer(inh_layer_param)
pyr_layer_2 = topp.CreateLayer(pyr_layer_param)

# Connect layers
topp.ConnectLayers(stim_layer, pyr_layer_1, {
	'connection_type': 'divergent',
	'mask': {'circular': {'radius': 4.0}},
	'kernel': {'gaussian': {'p_center': 1.0, 'sigma': 0.75}}})
#topp.ConnectLayers(pyr_layer_1, pyr_layer_2, {'connection_type': 'divergent'})
#topp.ConnectLayers(pyr_layer_1, inh_layer, {})
#topp.ConnectLayers(inh_layer, pyr_layer_1, {})
#topp.ConnectLayers(inh_layer, pyr_layer_2, {})

# Connect spike detectors to random pyr_layer_1 neurons
spk_det = nest.Create('spike_detector')
rec_neurons = np.random.choice(nest.GetNodes(pyr_layer_1)[0],
	                           size=sample_size, replace=False).tolist()
nest.Connect(rec_neurons, spk_det)

###########################################
####   SIMULATE   #########################
###########################################

for freq in range(freq_num):
	nest.ResetNetwork()
	nest.SetKernelStatus({'time': 0.0})
	live_update(freq)
	
	# Set rate for stim_layer neurons based on frequency of stimulus
	for row in range(amp_factor):
		for col in range(max(0,freq-tuning_rad),
			             min(freq_num,freq+tuning_rad+1)):
			rate_factor = max(0.0,(tuning_rad-abs(freq-col))/float(tuning_rad))
			nest.SetStatus(topp.GetElement(stim_layer,[col,row]),
				           {'rate': rate_factor*base_stim_rate})
	
	# Simulate and record event data from spike detector
	nest.Simulate(sim_time)
	evs = nest.GetStatus(spk_det)[0]['events']
	
	# Plot spike trains
	plt.subplot(331+freq)
	plt.title("Spike Trains at %s Hz" % freq_convert(freq))
	plt.xlabel('time (ms)')
	plt.ylabel('neuron ID')
	plt.gca().set_ylim(1,sample_size)
	plt.plot(evs['times'],[rec_neurons.index(i)+1 for i in evs['senders']],'o')
	
	# Store data on firing rates
	sender_fires = [0] * sample_size
	for neuron_id in evs['senders']:
		sender_fires[rec_neurons.index(neuron_id)] += 1
	for i in range(sample_size):
		firing_rates[i].append(1000*sender_fires[i]/sim_time)
	
	# Reset rates for stim_layer neurons
	for row in range(amp_factor):
		for col in range(max(0,freq-tuning_rad),
			             min(freq_num,freq+tuning_rad+1)):
			nest.SetStatus(topp.GetElement(stim_layer,[col,row]),
				           {'rate': 0.0})

###########################################
####   SHOW RESULTS   #####################
###########################################

plt.subplots_adjust(wspace=0.3,hspace=0.6)
plt.gcf().set_size_inches(12,10,forward=True)
plt.figure(2)
plt.title("Firing Rate v Frequency")
plt.xlabel('frequency (Hz)')
plt.ylabel('firing rate (spikes/sec)')
plt.gca().set_ylim(0,1.75*max([max(i) for i in firing_rates]))
for i in range(sample_size):
	x_axis = [freq_convert(j) for j in range(freq_num)]
	y_axis = firing_rates[i]
	plt.plot(x_axis,y_axis, label = 'Neuron %s' % str(i+1))
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00), ncol=3)
plt.show()