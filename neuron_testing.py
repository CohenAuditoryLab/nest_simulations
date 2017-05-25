import nest
import matplotlib.pyplot as plt
import nest.voltage_trace

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
nest.SetDefaults('iaf_psc_exp', neuron_param) # LIF neuron model with exponential PSCs
nest.SetDefaults('static_synapse', syn_static_param) # synapse model with static connections
nest.SetDefaults('tsodyks2_synapse', syn_dep_param) # Tsodyks-Markram synapse model with ST plasticity
nest.ResetKernel()