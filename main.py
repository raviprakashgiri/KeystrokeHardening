#!/usr/bin/python
import sys
import os

import numpy as np

from random import randint

import random
from simplecrypt import encrypt, decrypt, DecryptionException
from Crypto.Hash import SHA
import os.path
import time,sys
from Crypto.Cipher import AES
import base64
import Crypto

#input = "CorrectPassword"


#encryption mode
mode_encrypt= 'encrypt'
 
# standard deviation
k_val = 2
# mean
t_val = 10

q_val = Crypto.Util.number.getPrime(160, randfunc=None)
#print q_val

# fixed file size as asked
h_history_file_size = 600
contents = ''
# number of features
h_max_entries = 5   # 5 we'll save, from 6th we'll start checking
h_pwd = randint(0, q_val -1)
#print h_pwd
pwd_len = 25
max_features = pwd_len - 1
translated = ''


class Polynomial:
  coef = []

  def __init__(self, coef):
    self.coef = coef

  def val(self, x):
    sum_val = 0
    for i, value in enumerate(self.coef):
      sum_val = sum_val + value*pow(x, i)
    return sum_val

def polynomial_gen(degree, h_pwd):
  coefficient = [h_pwd] + random.sample(xrange(100), degree)
  return Polynomial(coefficient)

#print coefficient    
var_new = polynomial_gen(max_features-1, h_pwd)
print var_new 
#print random.randint(0, 10000)

h_pwd = random.randrange(0, q_val-1)
polynomial = polynomial_gen(max_features-1, h_pwd)
print polynomial.val(1)



'''def alpha_cal(input ,polynomial):
	g_ = hmac.new(input, msg=2*i, digestmod=None) 
	var_ =  (polynomial.val(g_) + g_) % q_val
	return var_
'''

def SHAtoLONG(pwd, input_i):
  shaed = SHA.new(str(input_i) + pwd).hexdigest()
  val_ = long(''.join([str(ord(h)) for h in shaed])) # converts into long -- ascii conversion
  return val_

# we need to hash h_pwd into string to use it as a input for AES
def SHAtoSTRING(input_):
  return SHA.new(str(input_)).hexdigest()

def alpha_cal(pwd, i, polynomial):
	return polynomial.val(2*i) + (SHAtoLONG(pwd, 2*i) % q_val)


def beta_cal(pwd, i, polynomial):
	return polynomial.val(2*i+1) + (SHAtoLONG(pwd, 2*i+1) % q_val)	

'''
hashed = SHA.new(str('ravi')).hexdigest()
nums = long(''.join([str(ord(c)) for c in hashed]))
print hashed
print "rpg" 
#print long(str(ord(c)) for c in hashed)
print nums
'''


def validateInputs(pwd, features):
  if (len(pwd) > pwd_len):
    print 'The maximum password length is '+ str(pwd_len) + ' characters'
    sys.exit()
  if (len(pwd)-1 != len(features)):
    print 'The length of password must equal number of feature values'
    sys.exit()


'''
def beta_cal(input ,polynomial):
	#hashlib.sha224(input.hexdigest()
	g_ = hmac.new(input, msg=2*i+1, digestmod=None) 
	var_ =  (polynomial.val(g_) + g_) % q_val
	return var_
'''
#========== input file parser begins: ===========#

def parser(test_file):
	m_features = []
	for n in xrange(0, len(test_file), 2):  # first two lines at a time
	    pwd = test_file[n]
	    features = map(int, test_file[n+1].split(','))
	    print features
	    # we also need to validate the inputs sometime later....
	    validateInputs(pwd, features)
	    if n <= (h_max_entries * 2) - 2:
	    	m_features.append(features)
	    	if n == (h_max_entries * 2) - 2:
		      h_pwd , table_instruct = create_instruct_table(m_features, pwd)
		      create_hist(h_pwd, contents = m_features)
	      	print "Done step 1"
	    else:
	    	m_features = ready_for_login(pwd, features, table_instruct) # need to do it later
	    	if (m_features == 0):
	        	continue
	      	h_pwd, table_instruct = create_instruct_table(m_features, pwd)
	      	create_hist(h_pwd, contents =m_features) 

#========== input file parser ends: ===========#



#========== ready_for_login begins: ===========#
def ready_for_login(pwd, features, table_instruct):
# return feature from the history file adding new feature on success
    text_ = check_decrypt(
        SHAtoSTRING(getHpwdFromTableInstruct(table_instruct, features, pwd)))
    # if fails then we print 0 to denote denied entry
    if text_:
    	print 1
    else:
      	print 0
      	return 0 

  	m_features = []
  	# appends the new feature in the history file
  	for line in text_.splitlines():   # Sanya, need text_ also... as we have to append the new feature
    	m_features.append(map(int, line.split(','))) # hopefully comma separated, remove if not
	m_features.append(features)
	return m_features
#========== ready_for_login ends: ===========#




#========== Create history file begins: ===========#
def do_encryptdecrypt(h_pwd,contents, mode_encrypt):
        start_time = time.time()
        
        if mode_encrypt == 'encrypt':
          enc_secret = AES.new(str(h_pwd)[:32])
          tag_string = (str(contents) +
                  (AES.block_size -
                   len(str(contents)) % AES.block_size) * "\0")
          text = base64.b64encode(enc_secret.encrypt(tag_string))
        elif mode_encrypt == 'decrypt':
          dec_secret = AES.new(str(h_pwd)[:32])
          raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
          text = raw_decrypted.rstrip("\0")
        total_time = round(time.time() - start_time, 2 )
        print('%sion time: %s seconds' %(mode_encrypt, str(total_time)))
        return text
        

def check_decrypt(h_pwd):
        if (os.path.isfile('./history.txt')):
          f1 = open('history.txt')
        contents = do_encryptdecrypt(h_pwd,f1.read(),mode_encrypt='decrypt')
        if contents is not None:
          return true
        
def create_hist(h_pwd, contents):
        if contents is None:
           check_decrypt(h_pwd)
        f2 = open('history.txt','wb')
        res = do_encryptdecrypt(h_pwd,contents,mode_encrypt='encrypt')
        f2.seek(h_history_file_size - len(res))
        f2.write(res)
        f2.close()
        print ('Done hist file creation')

#========== create history file ends: ===========#




#========== instruction table creation begins: ===========#

def create_instruct_table(m_features, pwd):
  
  sigma = np.std(m_features, axis = 0)
  average = np.mean(m_features, axis = 0)
  h_pwd = random.randrange(0, q_val-1)
  poly = polynomial_gen(max_features-1, h_pwd)

  table_instruct=[]

  for i in xrange(0, max_features):
    
    if ((i < len(average)) and ((abs(average[i] - t_val) - 0.0001) > (k_val * sigma[i]))):#0.001,small float subtraction problem
      if (average[i] < t_val):
        table_instruct.append([
          alpha_cal(pwd, i+1, poly),
          beta_cal(pwd+str(random.randrange(0, 1000)), i+1, polynomial_gen(max_features-5, random.randrange(0, q_val-1)))
        ])
      else:
        table_instruct.append([
          alpha_cal(pwd+str(random.randrange(0, 1000)), i+1, polynomial_gen(max_features-5, random.randrange(0, q_val-1))),
          beta_cal(pwd, i+1, poly)
        ])
    else:
      table_instruct.append([
        alpha_cal(pwd, i+1, poly),
        beta_cal(pwd, i+1, poly)
      ])
  return [h_pwd, table_instruct]

#========== instruction table creation ends: ===========#



#============== retrieval from instruction table begins===================#

# retrieves h_pwd from instruction table based on the new feature  and pwd

def getHpwdFromTableInstruct(table_instruct, features, pwd):
  xy_values = []
  for i in xrange(1, max_features+1):
    #boundary check if i > len(features)... for later...#

    # check to see if the feature is less than the provided mean
    if (features[i-1] < t_val):
        xy_values.append([2*i, table_instruct[i-1][0] - ((SHAtoLONG(pwd, 2*i) % q_val))])
    # if the provided feature is greater than the mean
    else:
    	xy_values.append([2*i+1, table_instruct[i-1][1] - ((SHAtoLONG(pwd, 2*i+1) % q_val))])
  return h_pwdLagrange(xy_values, max_features)

# lagrange interpolation to get h_pwd from xy values
def h_pwdLagrange(xy_values, feature_num):
  h_pwd = 0
  nums = []
  dens = []
  dens_sum = 1
  for i in xrange(0, feature_num):
    lambda_num = 1
    lambda_den = 1
    for j in xrange(0, feature_num):
      if (i != j):
        lambda_num *= xy_values[j][0]
        lambda_den *= xy_values[j][0] - xy_values[i][0]
    nums.append(lambda_num * xy_values[i][1])
    dens.append(lambda_den)
  for i in xrange(0, len(nums)):
    h_pwd += get_Num(i, nums, dens)
    dens_sum *= dens[i]
  return h_pwd/dens_sum

#used to minimize the divisions, copied form internet, mentione the source later if necessary...
def get_Num(index, nums, dens):
  num = 1
  for i in xrange(0, len(nums)):
    if i == index:
      num *= nums[i]
    else:
      num *= dens[i]
  return num

#============== retrieval from instruction table ends===================#


'''
content = file2.readlines()

print len(content)
'''

if __name__ == '__main__':
	with open(sys.argv[1], 'r') as my_file:
		parser(my_file.readlines())


























          
