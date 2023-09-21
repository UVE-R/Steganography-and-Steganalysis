# Need to generate large prime for seed
import random

# Generate random n bit integer
def rand_odd(n):
    num = random.randint(2 ** (n - 1), 2**n)
    if num % 2 == 0:
        num += 1
    return num


# Return false if n is composite
# Return true if n is probabily prime
def miller_rabin(n, k = 40):

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):

        a = random.randrange(2, n - 1)
        x = pow(a, s, n)

        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
        
    return True


# Return an n bit prime
def generatePrime(n):
    while True:
        num = rand_odd(n)
        if miller_rabin(num, 40):
            return num 
        