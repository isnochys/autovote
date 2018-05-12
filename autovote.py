from beem.account import Account
from beem.comment import Comment
from beem.steem import Steem
from beem.exceptions import ContentDoesNotExistsException
from datetime import timedelta
from beembase import operations
from beem.transactionbuilder import TransactionBuilder

import configparser
config = configparser.ConfigParser()
ret = config.read('settings.ini')
if not ret:
	config.read('settings-sample.ini')

voter = ''
signer = ''
wallet_pw = ''
votee_list=[]
for co in config:
	if co == 'DEFAULT':
		voter = config[co]['voter']
		wallet_pw = config[co]['wallet_pw']
		if 'signer' in config[co]:
			signer = config[co]['signer']
		else:
			signer = voter
			
	else:
		votee_list.append({'author':co,'percent':config[co]['percent'],'min_vp':config[co]['min_vp'],'wait':config[co]['wait']})

ops=[]
voter_account = Account(voter)
voter_vp = voter_account.vp

for autovote in votee_list:
	counter =0
	c_list = {}
	account = Account(autovote['author'])
	percent = float(autovote['percent'])
	min_vp = float(autovote['min_vp'])
	wait = int(autovote['wait'])
	for c in map(Comment, account.history_reverse(only_ops=["comment"])):
		if c.permlink in c_list:
		  continue
		try:
			 c.refresh()
		except ContentDoesNotExistsException:
			 continue
		c_list[c.permlink] = 1
		if not c.is_comment():
			counter +=1
			if voter not in c.get_votes() and c.time_elapsed() > timedelta(minutes=wait) and c.time_elapsed() < timedelta(days=6.5):
				op = operations.Vote(
									   **{"voter": voter,
											  "author": c.author,
											  "permlink": c.permlink,
											  "weight": int(percent * 100)
										   }
									)
				ops.append(op)
				voter_vp -= percent * 2 /100
		if counter >10 or voter_vp < min_vp:
			# going back 10 entries should be enough (50 minutes, on a spamming account e.g.)
			break
			
if ops:
	stm = Steem()
	stm.wallet.unlock(wallet_pw)
	tb = TransactionBuilder()
	tb.appendOps(ops)
	tx.appendSigner(signer, 'posting')
	tx.sign()
	returncode = tx.broadcast()
	print(returncode)
