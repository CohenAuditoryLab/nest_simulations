import nest
import numpy as np
import matplotlib.pyplot as plt

###########################################
####   PARAMETERS   #######################
###########################################

neuron_mod = 'iaf_psc_exp'
neuron_param = {
	'E_L'     : -70.0, # resting membrane potential (mV)
	'V_reset' : -70.0, # reset membrane potential after spiking (mV)
	'V_th'    : -55.0, # spike threshold (mV)
	'tau_m'   :  10.0  # membrane time constant (ms)
}
base_stim_rate = 2500.0 # stimulus rate (Hz)
tuning_rad = 3.0 # broadness of tuning curve
tono_rad = 3 # radius of stimulation for tonotopic map
freq_num = 9 # number of auditory frequencies
neuron_num = 12 # number of downstream neurons
sim_time = 500.0 # duration of simulation (ms)

# Convert raw integers to corresponding frequencies
def freq_convert(x):
	return 1000*(x+1)/2

# Initialize neuron array of firing rates at each frequency
firing_rates = [[] for i in range(neuron_num)]

nest.ResetKernel() # reset NEST

###########################################
####   NETWORK SETUP   ####################
###########################################

# Tonotopic map of all simulated frequencies
tono_map = nest.Create('poisson_generator',freq_num)

# Connect tonotopic map to downstream neurons
neurons = nest.Create(neuron_mod, neuron_num, neuron_param)
for i in range(freq_num):
	nest.Connect(tono_map[i:i+1],neurons[i:i+tono_rad], 
		         syn_spec={'weight':1000.0})

# Connect spike detectors
spk_det = nest.Create('spike_detector')
nest.Connect(neurons, spk_det)

###########################################
####   SIMULATE   #########################
###########################################

for freq in range(freq_num):
	nest.ResetNetwork()
	nest.SetKernelStatus({'time': 0.0})
	
	# Set rate for each tonotopic neuron based on frequency gof stimulus
	for neuron in tono_map:
		diff = abs(freq-neuron)
		if diff < tuning_rad:
			rate_factor = (tuning_rad-diff)/tuning_rad
			nest.SetStatus([neuron],{'rate': rate_factor*base_stim_rate})
		else:
			nest.SetStatus([neuron],{'rate': 0.0})
	
	# Simulate and record event data from spike detector
	nest.Simulate(sim_time)
	evs = nest.GetStatus(spk_det)[0]['events']
	
	# Plot spike trains
	plt.subplot(331+freq)
	plt.title("Spike Trains at %s Hz" % freq_convert(freq))
	plt.xlabel('time (ms)')
	plt.ylabel('neuron ID')
	plt.gca().set_ylim(1, neuron_num)
	plt.plot(evs['times'], evs['senders']-neuron_num, 'o')

	# Store data on firing rates
	sender_fires = [0] * neuron_num
	for neuron_id in evs['senders']:
		sender_fires[neuron_id-neuron_num-1] += 1
	for i in range(neuron_num):
		firing_rates[i].append(1000*sender_fires[i]/sim_time)

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
for i in range(neuron_num):
	x_axis = [freq_convert(j) for j in range(freq_num)]
	y_axis = firing_rates[i]
	plt.plot(x_axis,y_axis, label = 'Neuron %s' % str(i+1))
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00), ncol=3)
plt.show()