import smtplib
from email.MIMEText import MIMEText
from email.header import Header
import time as t

# Send email updates on code progress
def email(subject,body):
	from_mail = 'codenoticesender@gmail.com'
	to_mail = '2489351405@txt.att.net'

	msg = MIMEText(body.encode('utf-8'),'plain','utf-8')
	msg['From'] = from_mail
	msg['To'] = to_mail
	msg['Subject'] = Header(subject, 'utf-8')
	
	mailserver = smtplib.SMTP('smtp.gmail.com',587)
	mailserver.ehlo()
	mailserver.starttls()
	mailserver.ehlo()
	mailserver.login(from_mail, 'nara1998')
	mailserver.sendmail(from_mail, to_mail, msg.as_string())
	mailserver.quit()

# Return current time using time module
def time():
	return t.time()

# Buffers items for printing to terminal window
def fill_print(item,new_size,fill):
		curr_size = len(str(item))
		if curr_size >= new_size:
			return item
		else:
			return str(fill)*(new_size-curr_size) + str(item)

# Print to terminal window live updates with simulation information
def live_update(init_time,curr_freq,tot_freq,curr_sim,tot_sim):
	completed_freq = tot_freq*curr_sim+curr_freq
	total_freq = tot_freq*tot_sim
	
	elapsed_time = time()-init_time
	if completed_freq == 0:
		est_wait = -1
	else:
		est_tot_time = (elapsed_time/completed_freq)*total_freq
		est_wait = int((est_tot_time - elapsed_time)/60 + 0.5)
	
	txts = [
		('XXX RUNNING SIMULATION %s of %s ' \
			% (fill_print(curr_sim+1,2,'0'),fill_print(tot_sim,2,'0'))),
		('XXX PLAYING FREQUENCY %s of %s ' \
			% (fill_print(curr_freq+1,2,'0'),fill_print(tot_freq,2,'0'))),
		('XXX %s MINUTES HAVE PASSED ' % str(int(elapsed_time/60)))
	]
	if est_wait != -1:
		txts.append(('XXX ESTIMATED %s MINUTES REMAINING ' % str(est_wait)))

	line_len = max([len(txt) for txt in txts])
	print 'X'*(line_len+3)
	for txt in txts:
		print txt + ' '*(line_len-len(txt)) + 'X'*3
	print 'X'*(line_len+3)

# Print final runtime statistics to terminal window
def final(init_time,tot_freq,tot_sim):
	txt = ('X   RAN %s SIMULATIONS AT %s FREQUENCIES IN %s MINUTES   X' \
		% (str(tot_sim), str(tot_freq), str(int((time()-init_time+30)/60))))
	out_board = 'X'*len(txt)
	in_board = '\n' + 'X' + ' '*(len(txt)-2) + 'X' + '\n'
	print out_board + in_board + txt + in_board + out_board
	email('Your Simulations are Complete',txt[4::])