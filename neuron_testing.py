import nest
import matplotlib.pyplot as plt
import nest.voltage_trace

nest.ResetKernel()

neuron_mod = 'iaf_psc_exp' # LIF neuron model with exponential PSCs
syn_static_mod = 'static_synapse' # synapse model with static connections
syn_dep_mod = 'tsodyks2_synapse' # Tsodyks-Markram synapse model with ST plasticity
neuron_param = {
	'C_m'     : 1.0,  # membrane capacitance (pF)
	'E_L'     : 0.0,  # resting membrane potential (mV)
	'V_reset' : 0.0,  # reset membrane potential after spiking (mV)
	'V_th'    : 20.0, # spike threshold (mV) SUBJECT TO CHANGE
	'tau_m'   : 20.0  # membrane time constant (ms)
}
syn_static_param = {
	'delay'   : 1.5 # time delay (ms)
}
syn_dep_param = {
	'U'       : 0.5, # facilitation parameter U
	'delay'   : 1.5, # time delay (ms)
	'tau_rec' : 50.0 # facilitation time (ms)
}

noise = nest.Create('poisson_generator', 
	                params={'rate': 2000.0})
neurons = nest.Create(neuron_mod, 10, params=neuron_param)
voltmtr = nest.Create('voltmeter')
spkdet = nest.Create('spike_detector')
nest.Connect(noise, neurons)
nest.Connect(voltmtr, neurons)
nest.Connect(neurons, spkdet)

nest.Simulate(200)
plt.subplot(121)
nest.voltage_trace.from_device(voltmtr)
plt.subplot(122)
events = nest.GetStatus(spkdet)[0]['events']
plt.plot(events['times'],events['senders'],'o')
plt.show()