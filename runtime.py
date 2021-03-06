import smtplib
from math import factorial
from itertools import combinations
from email.MIMEText import MIMEText
from email.header import Header
from time import time

# Buffers items for printing to terminal window
def fill_print(item,new_size,fill):
		curr_size = len(str(item))
		if curr_size >= new_size:
			return item
		else:
			return str(fill)*(new_size-curr_size) + str(item)

# Quick conversion from float seconds to integer minutes
def sec_to_min(secs,round_up=False):
	if not round_up:
		secs += 30
	return int(secs/60)

class Runtime(object):

	# var_type is either 'single' or 'double' (manipulating 1 variable or 2)
	def __init__(self,sim_dict,tot_freq,var_type='single',
		         to_mail='2489351405@txt.att.net'):
		self.sim_dict = sim_dict
		self.tot_freq = tot_freq
		self.var_type = var_type
		self.tot_var = len(sim_dict)
		self.tot_trials = 0
		if self.var_type == 'double':
			for var_pair in combinations(sim_dict.keys(),2):
				self.tot_trials += self.tot_freq \
				                   * len(self.sim_dict[var_pair[0]]) \
					           * len(self.sim_dict[var_pair[1]])
			self.tot_var = factorial(self.tot_var)/factorial(self.tot_var-2)/2
		else:
			for key in sim_dict.keys():
				self.tot_trials += len(sim_dict[key])*self.tot_freq
		self.completed_vars = []
		self.init_time = time()
		self.to_mail = to_mail

	# Add a variable to the list of completed variables
	def inc_var(self, var_id):
		self.completed_vars.append(var_id)

	# Send email updates on code progress
	def email(self,subject,body):
		from_mail = 'codenoticesender@gmail.com'

		msg = MIMEText(body.encode('utf-8'),'plain','utf-8')
		msg['From'] = from_mail
		msg['To'] = self.to_mail
		msg['Subject'] = Header(subject, 'utf-8')
		
		mailserver = smtplib.SMTP('smtp.gmail.com',587)
		mailserver.ehlo()
		mailserver.starttls()
		mailserver.ehlo()
		mailserver.login(from_mail, 'nara1998')
		mailserver.sendmail(from_mail, self.to_mail, msg.as_string())
		mailserver.quit()

	# Print to terminal window live updates with simulation information
	def live_update(self,curr_freq,curr_sim,var_id):
		elapsed_time = time()-self.init_time

		tot_sim = 0
		if self.var_type == 'double':
			tot_sim = len(self.sim_dict[var_id[0]]) \
				  * len(self.sim_dict[var_id[1]])
			var_fill = ' PAIR'
		else:
			tot_sim = len(self.sim_dict[var_id])
			var_fill = ''

		completed_trials = self.tot_freq*curr_sim + curr_freq
		for var in self.completed_vars:
			if self.var_type == 'double':
				completed_trials += self.tot_freq \
				                    * len(self.sim_dict[var_id[0]]) \
					            * len(self.sim_dict[var_id[1]])
			else:
				completed_trials += self.tot_freq*len(self.sim_dict[var])
		
		if completed_trials == 0:
			est_wait = -1
		else:
			est_tot_time = (elapsed_time/completed_trials)*self.tot_trials
			est_wait = sec_to_min(est_tot_time - elapsed_time,True)
		
		txts = [
			('XXX TESTING VARIABLE%s %s of %s ') \
				% (var_fill,fill_print(len(self.completed_vars)+1,2,'0'),
				   fill_print(self.tot_var,2,'0')),
			('XXX RUNNING SIMULATION %s of %s ' \
				% (fill_print(curr_sim+1,2,'0'),fill_print(tot_sim,2,'0'))),
			('XXX PLAYING FREQUENCY %s of %s ' \
				% (fill_print(curr_freq+1,2,'0'),
				   fill_print(self.tot_freq,2,'0'))),
			('XXX %s MINUTES HAVE PASSED ' % str(sec_to_min(elapsed_time)))
		]
		if est_wait != -1:
			txts.append(('XXX ESTIMATED %s MINUTES REMAINING ' % str(est_wait)))

		line_len = max([len(txt) for txt in txts])
		print 'X'*(line_len+3)
		for txt in txts:
			print txt + ' '*(line_len-len(txt)) + 'X'*3
		print 'X'*(line_len+3)

	# Print final runtime statistics to terminal window and send email update
	def final(self,send_mail=False):
		if self.var_type == 'double':
			var_fill = 'VARIABLE PAIRS'
		else:
			var_fill = 'VARIABLES'
		txt = ('X   TESTED %s %s AT %s FREQUENCIES IN %s MINUTES   X' \
			% (str(self.tot_var), var_fill, str(self.tot_freq), 
			   str(sec_to_min(time()-self.init_time,True))))
		out_board = 'X'*len(txt)
		in_board = '\n' + 'X' + ' '*(len(txt)-2) + 'X' + '\n'
		print out_board + in_board + txt + in_board + out_board
		if send_mail:
			self.email('Your Simulations are Complete',txt[4::])
