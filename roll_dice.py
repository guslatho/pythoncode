import numpy as np

# Dice Simulation Script
# Simulates the rolling of an x amount of dices, each having an y amount
# of faces. For each dice, the amount of rolls can be determined as well.
# For example, 5 six-sided dices can be generated to be rolled 8 times
# each.
# In addition, bias can be input for the dices. A value of '1' means no
# bias. For each increment, one value of the dice will have relative increased
# odds to be rolled of 'x', where x is the bias set. For instance, a bias
# of '3' would result in certain values on one side of the dice to have an
# 3x increased chance to be thrown relative to the values on the other
# sides of the dice.
# Dices are procedurally generated in a manner resulting in opposing faces
# always adding up to the total set face_count+1. For instance, for a 6-sided
# dice the vectors for each face-pair would be [1,6], [2,5], [3,4], for a total
# sum of 7. 

# Create rng seed
rng = np.random.default_rng(seed=12345)

# User inputs for defining dice characteristics
print('Welcome to Dice Roll Simulations!')
print('Please enter the amount of dices to generate.')
DICES=int(input())
print('Enter the amount of faces each dice has (e.g. 6 = 6-sided dice)')
FACE_COUNT=int(input())
print('Enter the amount of times to roll each dice')
ROLL_COUNT=int(input())
print('Enter the bias for the dice(s). Bias causes dices to roll certain '
      'values more often than others. For no bias, type 1. For high bias'
      ', input a value x times 1')
BIAS=int(input())

# Following is a starting print for a small loading bar: at different points
# in the calculations additional dots are printed (added) to the bar.
print('\n[Rolling the dices', end='.')

# Returns frequency count
def frequency_distribution(numpy_list):

    value_count = np.zeros((ROLL_COUNT,2),dtype='int32')

    # Count number of times each value is present
    for number in range(len(numpy_list)):
       
        mode = np.sum(numpy_list==number)
        value_count[number][0] = number
        value_count[number][1] = mode

    # Remove value with 0 counts
    value_count = value_count[value_count[:,1]!=0]
        
    return value_count

# Returns the mode of a distribution. If multiple faces have the same
# roll-count they will all be output.
def mode(numpy_list):

    # Load frequency distribution of list
    freq_count = frequency_distribution(numpy_list)

    # Verify which value is most prevalent among the freq distribution
    max_count = np.max(freq_count[:,1])

    return freq_count[freq_count[:,1]==max_count]

# For creating a dice with certain amount of faces (FACE_COUNT) and BIAS
def create_dice():

    # This var stores numbers of faces. If the dice is odd, it'll remove 1
    dice_faces = FACE_COUNT - FACE_COUNT%2
    
    # Given that opposite numbers are on opposite side of dice, create 2 sides
    # of the dice
    halfway_point = int(dice_faces/2)
    dice_top_half = np.array(np.arange(1,halfway_point+1))
    dice_bottom_half = np.array(dice_faces-np.arange(0,halfway_point))

    # Create random sequence for determining position of each pair on dice
    random_sequence = np.random.choice(2,halfway_point)

    # Create top side of dice, selected randomly from top/bottom arrays
    top = np.where(random_sequence,dice_top_half,dice_bottom_half)
    rng.shuffle(top)

    # Given top integers, create bottom side. Reverse bottom (value on
    # opposite side of 1st should be at the very end)
    bottom = np.flip(dice_faces+1 - top)

    # Merge top and bottom into 1 dice. [0] to remove outer brackets
    dice = np.array([top,bottom])
    dice = dice.reshape((1,dice_faces))[0]    

    # If it's an odd-numbered dice, add in the last number
    if FACE_COUNT%2 == 1:
        position = rng.integers(0,dice_faces)
        dice = np.insert(dice,position,FACE_COUNT)
      
    return dice

# For creating odds array for biased dices
def create_dice_odds():

    # Odds array
    odds_array = np.arange(0,FACE_COUNT)
    width = np.sqrt(-1*(1-BIAS))/(FACE_COUNT-1)
    odds_array =- (odds_array*width)**2 + BIAS
    odds_total = np.sum(odds_array)
    odds_array = odds_array/odds_total

    return odds_array

print('', end='.')

# Create lists to store dices/rolls/odds
dice_list = np.zeros((DICES,FACE_COUNT),dtype='int32')
odds_list = np.zeros((DICES,FACE_COUNT),dtype='float32')
dice_rolls = np.zeros((DICES,ROLL_COUNT),dtype='int32')

print('', end='.')

# Generate dices and rolls
for dice in range(DICES):

    # Generate dices and dice odds, add them to respective lists
    dice_list[dice] = create_dice()
    odds_list[dice] = create_dice_odds()

    # Generate rolls for each dice 
    for roll in range(ROLL_COUNT):
        dice_rolls[dice][roll] = np.random.choice(dice_list[dice],
                                                  1, p=odds_list[dice])
    print('', end='.')

# Create list for storing means
dice_means = np.zeros(DICES,dtype='float32')

for dice in range(DICES):
    dice_means[dice] = np.mean(dice_rolls[dice])

print('.]')
print('\nCalculations have been completed!\n')
print('''To view a complete list of all generated list, type 'dices'.
to output a list of all rolls, type 'rolls'. For means, type 'means'.
To view the full frequency distribution of each dice/roll combination,
type 'freq'. To view the mode for each rolls, type 'mode')''')

while True:
    print('\nInput a command or type \'esc\' to quit. Type \'help\' for '
          'a list of available commands')
    choice = input()
    if choice == 'dices':
        print(f'{(DICES)} dices were generated in total according to the ',end='')
        print(f'following layouts (if bias > 1, number towards the left have ',end='')
        print(f'a larger chance of being rolled):')
        print(dice_list)
    elif choice == 'rolls':
        print(f'{DICES} dices were each rolled a ({ROLL_COUNT}) amount of ',end='')
        print(f'times, resulting in the following output:')
        print(dice_rolls)
    elif choice == 'means':
        print('Mean of rolls for each individual dice: ', end = '')
        for dice in dice_means:
            print('['+str(dice)+']', end = ' ')
        print()
    elif (choice == 'freq' and ROLL_COUNT>1):
        print('Frequency format follows the following format for ', end='')
        print('each individual value:')
        print('value: n')
        print(f'Values that were not rolled are omitted')
        for dice in range(DICES):           
            freq_current = frequency_distribution(dice_rolls[dice])
            print('Dice number ' + str(dice+1) + ':')
            for frequ in range((len(freq_current))):
                freq_number = freq_current[frequ][0]
                amount = freq_current[frequ][1]
                freq_str = f'{freq_number}: {amount}'
                print(freq_str)
            #print(freq_current)        
    elif (choice == 'mode' and ROLL_COUNT>1):
        for dice in range(DICES):
            mode_current = mode(dice_rolls[dice])
            print('Dice number ' + str(dice+1) + ':')
            print('Value(s) ' + str(mode_current[:,0])[1:-1] + ' were most', end=' ')
            print('rolled with a frequency of ' + str(mode_current[0,1]))
    elif (choice == 'freq' or choice == 'mode'):
        print('Mode/frequency distribution doesn\'t apply with roll count of 1!')
    elif choice == 'help':
            print('''
            'dices': output list of all dices generated
            'rolls': output list of all rolls
            'means': generate list of means for each dice
            'freq': generate frequency distribution list
            'mode': output mode for each dice
            ''')
    elif choice == 'esc':
        break
    else:
        print('Please enter a valid input')
        
