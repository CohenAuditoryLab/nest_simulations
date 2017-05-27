import nest
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
freq_num = 9 # number of auditory frequencies
neuron_num = 11 # number of downstream neurons
sim_time = 500 # duration of simulation (ms)

###########################################
####   CONNECTIONS   ######################
###########################################
def setupSim(frequency):
	nest.ResetKernel()

	# Generate stimulus, send identical spike trains to target neurons
	stim = nest.Create('parrot_neuron')
	nest.Connect(nest.Create('poisson_generator', params={'rate': stim_rate}),
		         stim)

	# Create tonotopic map of frequencies
	tono_map = nest.Create(neuron_mod, freq_num, neuron_param)
	neurons = nest.Create(neuron_mod, neuron_num, neuron_param)

	# Connect tonotopic map to downstream neurons
	for i in range(len(tono_map)):
		nest.Connect(tono_map[i:i+1],neurons[i:i+3], 
			         syn_spec={'weight':1000.0})

	# Create and connect devices
	volt_mtr = nest.Create('voltmeter')
	spk_det = nest.Create('spike_detector')
	nest.Connect(volt_mtr, neurons)
	nest.Connect(neurons, spk_det)
	nest.Connect(stim, tono_map[frequency:frequency+1], 
		         syn_spec={'weight': 500.0})
	return (volt_mtr, spk_det)

###########################################
####   PLOTTING   #########################
###########################################

# Plot membrane potential and spike trains
def plotSim(frequency, volt_mtr, spk_det):
	plt.subplot(331+frequency)
	plt.title("Spike Trains at %s Hz" % (1000*(frequency+1)/2))
	plt.xlabel('time (ms)')
	plt.ylabel('neuron ID')
	events = nest.GetStatus(spk_det)[0]['events']
	plt.gca().set_ylim(0, neuron_num-1)
	plt.plot(events['times'], events['senders']-neuron_num-1, 'o')

###########################################
####   SIMULATION   #######################
###########################################

for freq in range(freq_num):
	(volt_mtr, spk_det) = setupSim(freq)
	nest.Simulate(sim_time)
	plotSim(freq, volt_mtr, spk_det)

###########################################
####   SHOW RESULTS   #####################
###########################################

plt.subplots_adjust(wspace=0.3,hspace=0.6)
plt.gcf().set_size_inches(12,10,forward=True)
plt.show()