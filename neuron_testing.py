import nest
import matplotlib.pyplot as plt
import nest.voltage_trace

neuron_mod = 'iaf_psc_exp'
neuron_param = {
	'C_m'     : 1.0,  # membrane capacitance (pF)
	'E_L'     : 0.0,  # resting membrane potential (mV)
	'V_reset' : 0.0,  # reset membrane potential after spiking (mV)
	'V_th'    : 20.0, # spike threshold (mV) SUBJECT TO CHANGE
	'tau_m'   : 20.0  # membrane time constant (ms)
}
nest.ResetKernel()