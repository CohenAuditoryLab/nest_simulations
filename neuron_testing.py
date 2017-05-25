import nest
import matplotlib.pyplot as plt
import nest.voltage_trace

def new_neurons(n):
	neuron_mod = 'iaf_psc_alpha'
	neuron_param = {
		'E_L'     : -70.0, # resting membrane potential (mV)
		'V_reset' : -70.0, # reset membrane potential after spiking (mV)
		'V_th'    : -55.0, # spike threshold (mV)
		'tau_m'   : 10.0   # membrane time constant (ms)
	}
	return nest.Create(neuron_mod, n, neuron_param)

# frequency is some integer 1000 < n <= 4000
def stimulate(frequency, time):
	nest.SetStatus([stimuli[frequency-1001]], {'rate': 2000.0})
	nest.Simulate(time)
	nest.SetStatus([stimuli[frequency-1001]], {'rate': 0.0})


stimuli = nest.Create('poisson_generator', 3000)
neurons = new_neurons(3000)
voltmeter = nest.Create('voltmeter')
nest.Connect(stimuli, neurons, 'one_to_one', {'weight': 50.0})
nest.Connect(voltmeter, neurons)

for i in range(1001,4001):
	stimulate(i,25)

nest.voltage_trace.from_device(voltmeter)
plt.show()