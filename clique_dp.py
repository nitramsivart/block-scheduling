from decimal import *
import sys

'''
  General outline:
    This code has a nested dictionary, answers, which is the table containing all values. It takes four arguments, in order:
      # people who have already chosen Y
      # people who have already chosen N
      # people left to choose
      a string defining which value we are interested in:
        'yes-count': the number of Y-decisions I expect to be made, at the end, given this situation:
                     answers[100][0][1]['yes-count'] = 101
        'no-count': see above
        'yes-decision': the choice a Y-type would make in this situation. Output is one of the constants Y, N:
                        answers[100][0][1]['yes-decision'] = Y
        'no-decision': see above
        'yes-yes-value': the utility a yes-type would get for choosing yes, in this situation.
                         answers[100][0][1]['yes-yes-value'] = 100 + pi
        'yes-no-value': see above
        'no-yes-value': see above
        'no-no-value': see above
    The values of the dictionary are computed when they are first referenced, using the appropriately named methods below.
    Some values are preset, such as the axes of the table and some constants

  We represent numbers using the Decimal class to avoid weird behavior from rounding errors

'''

# the range we are interested in (should be odd, x axis range). for display purposes only.
# gives the maximum |#Y - #N| we are concerned about.
a = 13

# how many rounds we look at (network size, or y axis range)
b = 70

#No need to change these
c = (a-1)/2 # the midpoint of x-range, used because we start with that many Y decisions
Y = 0 # a constant representing the choice Y
N = 20 # a constant representing the choice N
dim = b+20 # the size of our answers table

# contains all relevant values
answers = {}

#####################################################

'''
  The next methods are used to compute values in answers, or return value if
  it has already been computed. These are the real meat of the program
'''
def yes_count(yes, no, n, p, pi):
  if 'yes-count' not in answers[yes][no][n]:
    yd = yes_decision(yes, no, n-1, p, pi)
    nd = no_decision(yes, no, n-1, p, pi)
    if yd == nd == Y:
      answers[yes][no][n]['yes-count'] = yes_count(yes + 1, no, n-1, p, pi)
    elif yd == nd == N:
      answers[yes][no][n]['yes-count'] = yes_count(yes, no + 1, n-1, p, pi)
    elif yd == Y and nd == N:
      answers[yes][no][n]['yes-count'] = p * yes_count(yes+1, no, n-1, p, pi) + \
                                         (Decimal(1)-p) * yes_count(yes, no+1, n-1, p, pi)
    else:
      raise Exception('no type choosing Y?')
  return answers[yes][no][n]['yes-count']

def no_count(yes, no, n, p, pi):
  if 'no-count' not in answers[yes][no][n]:
    yd = yes_decision(yes, no, n-1, p, pi)
    nd = no_decision(yes, no, n-1, p, pi)
    if yd == nd == Y:
      answers[yes][no][n]['no-count'] = no_count(yes + 1, no, n-1, p, pi)
    elif yd == nd == N:
      answers[yes][no][n]['no-count'] = no_count(yes, no + 1, n-1, p, pi)
    elif yd == Y and nd == N:
      answers[yes][no][n]['no-count'] = p * no_count(yes+1, no, n-1, p, pi) + \
                                         (Decimal(1)-p) * no_count(yes, no+1, n-1, p, pi)
    else:
      raise Exception('no type choosing Y?')
  return answers[yes][no][n]['no-count']

# returns the decision a yes type person would make, given:
# there are already yes Ys, no Ns, and n undecideds
def yes_decision(yes, no, n, p, pi):
  if 'yes-decision' not in answers[yes][no][n]:
    # check what decision a type Y would make
    yes_value = yes_yes_value(yes, no, n, p, pi)
    no_value = yes_no_value(yes, no, n, p, pi)
    if yes_value >= no_value:
      answers[yes][no][n]['yes-decision'] = Y
    else:
      answers[yes][no][n]['yes-decision'] = N

  return answers[yes][no][n]['yes-decision']

# returns the decision a no type person would make, given:
# there are already yes Ys, no Ns, and n undecideds
def no_decision(yes, no, n, p, pi):
  if 'no-decision' not in answers[yes][no][n]:
    # check what decision a type Y would make
    yes_value = no_yes_value(yes, no, n, p, pi)
    no_value = no_no_value(yes, no, n, p, pi)
    if yes_value > no_value:
      answers[yes][no][n]['no-decision'] = Y
    else:
      answers[yes][no][n]['no-decision'] = N

  return answers[yes][no][n]['no-decision']

# the value of a yes type choosing yes
def yes_yes_value(yes, no, n, p, pi):
  if 'yes-yes-value' not in answers[yes][no][n]:
    answers[yes][no][n]['yes-yes-value'] = pi + yes_count(yes+1, no, n, p, pi) - Decimal(1)
  return answers[yes][no][n]['yes-yes-value']

# the value of a yes type choosing no
def yes_no_value(yes, no, n, p, pi):
  if 'yes-no-value' not in answers[yes][no][n]:
    answers[yes][no][n]['yes-no-value'] = no_count(yes, no+1, n, p, pi) - Decimal(1)
  return answers[yes][no][n]['yes-no-value']

# the value of a no type choosing yes
def no_yes_value(yes, no, n, p, pi):
  if 'no-yes-value' not in answers[yes][no][n]:
    answers[yes][no][n]['no-yes-value'] = yes_count(yes+1, no, n, p, pi) - Decimal(1)
  return answers[yes][no][n]['no-yes-value']

# the value of a no type choosing no
def no_no_value(yes, no, n, p, pi):
  if 'no-no-value' not in answers[yes][no][n]:
    answers[yes][no][n]['no-no-value'] = pi + no_count(yes, no+1, n, p, pi) - Decimal(1)
  return answers[yes][no][n]['no-no-value']

#####################################################

'''
  The following methods are for display purpose only, printing out a table of relevant values
  Vertical axis is number of nodes left to choose
  Horizontal axis is #Y-#N
'''
# basically shows where cascades form. S means that people choose their type
# Y and N are instances where people always choose that type - this corresponds to a cascade
def bandwidth():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      if no_decision(j,c,i,p,pi) == yes_decision(j,c,i,p,pi) == Y:
        print 'Y\t',
      elif no_decision(j,c,i,p,pi) == yes_decision(j,c,i,p,pi) == N:
        print 'N\t',
      else:
        print 'S\t',
    print ""

# For a yes-type node: utility difference for choosing Y vs N
def yes_diff():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((yes_yes_value(j,c,i,p,pi) - yes_no_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# For a no-type node: utility difference for choosing Y vs N
def no_diff():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((no_yes_value(j,c,i,p,pi) - no_no_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# Value for a yes-type node choosing yes
def yes_yes():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((yes_yes_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# Value for a yes-type node choosing no 
def yes_no():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((yes_no_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# Value for a no-type node choosing yes 
def no_yes():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((no_yes_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# Value for a no-type node choosing no
def no_no():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str((no_no_value(j,c,i,p,pi)).quantize(Decimal('1.000'))) + '\t',
    print ""

# What a yes-type node will choose
def yes_dec():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str(yes_decision(j,c,i,p,pi)) + '\t',
    print ""

# What a no-type node will choose
def no_dec():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str(no_decision(j,c,i,p,pi)) + '\t',
    print ""

# Expected number of Y decisions (at the end)
def yes_c():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str(yes_count(j,c,i,p,pi).quantize(Decimal('1.000'))) + '\t',
    print ""

# Expected number of N decisions (at the end)
def no_c():
  print '\t',
  for j in range(a):
    print str(j - c) + '\t',
  print ""
  for i in range(b):
    print str(i) + '\t',
    for j in range(a):
      print str(no_count(j,c,i,p,pi).quantize(Decimal('1.000'))) + '\t',
    print ""

#####################################################

# Reset needs to be called whenever p, pi change, so that we refresh the dictionary values.
# otherwise we will think values have been computed but they correspond to previous parameters.
def reset():
  answers_temp = {}
  for yes in range(dim):
    answers_temp[yes] = {}
    for no in range(dim):
      answers_temp[yes][no] = {}
      for n in range(dim):
        answers_temp[yes][no][n] = {}
      answers_temp[yes][no][0]['yes-count'] = Decimal(yes)
      answers_temp[yes][no][0]['no-count'] = Decimal(no)
  return answers_temp

#####################################################

#p = Decimal('.999999')
#pi = Decimal('1.0000000001')

# take p, pi values from terminal
p = Decimal(sys.argv[1])
pi = Decimal(sys.argv[2])
answers = reset()
# we can display whatever we want
bandwidth()
