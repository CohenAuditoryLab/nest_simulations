import nest
import matplotlib.pyplot as plt
import nest.voltage_trace

neuron_mod = 'iaf_psc_exp'
neuron_param = {
	'E_L'     : -70.0, # resting membrane potential (mV)
	'V_reset' : -70.0, # reset membrane potential after spiking (mV)
	'V_th'    : -55.0, # spike threshold (mV)
	'tau_m'   : 10.0   # membrane time constant (ms)
}
stim_param = {
	'rate': 2000.0 # firing rate (Hz)
}
nest.ResetKernel()

# Generate stimulus, send identical spike trains to target neurons
stim_gen = nest.Create('poisson_generator', params=stim_param)
stim = nest.Create('parrot_neuron')
nest.Connect(stim_gen,stim)

# Create and connect neurons
neurons = nest.Create(neuron_mod, 10, neuron_param)
voltmeter = nest.Create('voltmeter')
spk_det = nest.Create('spike_detector')
nest.Connect(stim, neurons, syn_spec={'weight':100.0})
nest.Connect(voltmeter, neurons)
nest.Connect(neurons, spk_det)

nest.Simulate(500)

# Plot membrane potential and spike trains
plt.subplot(211)
nest.voltage_trace.from_device(voltmeter)
plt.subplot(212)
events = nest.GetStatus(spk_det)[0]['events']
plt.plot(events['times'],events['senders'], 'o')
plt.show()