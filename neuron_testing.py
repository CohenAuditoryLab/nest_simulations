import nest
import numpy as np
import matplotlib.pyplot as plt
import nest.voltage_trace

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
stim_rate = 2000.0 # stimulus rate (Hz)
stim_weight = 500.0 # strength of connection from stimulus to tonotopic map
freq_num = 9 # number of auditory frequencies
neuron_num = 11 # number of downstream neurons
sim_time = 500.0 # duration of simulation (ms)

nest.ResetKernel() # reset NEST
np.random.seed(20) # set seed for reproducability

###########################################
####   NETWORK SETUP   ####################
###########################################

# Generate stimulus and send identical spike trains through parrot neuron
stim_gen = nest.Create('poisson_generator', params={'rate': stim_rate})
stim = nest.Create('parrot_neuron')
nest.Connect(stim_gen, stim)

# Connect stimulus to tonotopic map, all synapses initially deactivated
tono_map = nest.Create(neuron_mod, freq_num, neuron_param)
nest.Connect(stim, tono_map, syn_spec={'weight': 0.0})
conns = nest.GetConnections(stim)

# Connect tonotopic map to downstream neurons
neurons = nest.Create(neuron_mod, neuron_num, neuron_param)
for i in range(len(tono_map)):
	nest.Connect(tono_map[i:i+1],neurons[i:i+3], syn_spec={'weight':1000.0})

# Connect spike detectors
spk_det = nest.Create('spike_detector')
nest.Connect(neurons, spk_det)

###########################################
####   RESULTS   ##########################
###########################################

# Store data on firing rates for each frequency simulation
firing_rates = []

# Plot membrane potential and spike trains
def plot_sim(frequency, events):
	plt.subplot(331+frequency)
	plt.title("Spike Trains at %s Hz" % (1000*(frequency+1)/2))
	plt.xlabel('time (ms)')
	plt.ylabel('neuron ID')
	plt.gca().set_ylim(0, neuron_num-1)
	plt.plot(events['times'], events['senders']-neuron_num-1, 'o')

def store_firing_rates(frequency, events):
	sender_fires = [0] * neuron_num
	for neuron_id in events['senders']:
		sender_fires[neuron_id-neuron_num-1] += 1
	for i in range(neuron_num):
		sender_fires[i] = sender_fires[i]/sim_time
	firing_rates.append((frequency, sender_fires))

###########################################
####   SIMULATIONS   ######################
###########################################

for freq in range(freq_num):
	nest.ResetNetwork()
	nest.SetKernelStatus({'time': 0.0})
	nest.SetStatus(conns[freq:freq+1],{'weight': stim_weight})
	nest.Simulate(sim_time)
	nest.SetStatus(conns[freq:freq+1],{'weight': 0.0})
	evs = nest.GetStatus(spk_det)[0]['events']
	plot_sim(freq, evs)
	store_firing_rates(freq, evs)

###########################################
####   SHOW RESULTS   #####################
###########################################

plt.subplots_adjust(wspace=0.3,hspace=0.6)
plt.gcf().set_size_inches(12,10,forward=True)
plt.show()
print firing_rates