######
# SI #
######

# Prefixes #
10:
Y  24,
Z  21,
E  18,
P  15,
T  12,
G   9,
M   6,
k   3,
h   2,
da  1,
d  -1,
c  -2,
m  -3,
u  -6,
n  -9,
p -12,
f -15,
a -18,
z -21,
y -24;

# Base Units #
m;
g;
s;
A;
K;
mol;
cd;

# Derived units #
Hz : 1,   s -1;
N  : 1,   m  1, kg  1, s -2;
Pa : 1,   N  1,  m -2;
J  : 1,   N  1,  m  1;
W  : 1,   J  1,  s -1;
C  : 1,   s  1,  A  1;
V  : 1,   W  1,  A -1;
F  : 1,   C  1,  V -1;
Ohm: 1,   V  1,  A -1;
S  : 1,   A  1,  V -1;
Wb : 1,   V  1,  s  1;
T  : 1,  Wb  1,  m -2;
H  : 1,  Wb  1,  A -1;
lm : 1,  cd  1;
lx : 1,  lm  1,  m -2;
Bq : 1,   s -1;
Gy : 1,   J  1, kg -1;
Sv : 1,   J  1, kg -1;
kat: 1, mol  1,  s -1;

#################
# SI-compatible #
#################

# bel
# B;
# barn
# b:          100,  fm 2;
min:           60,   s 1;
h  :           60, min 1;
day:           24,   h 1;
L  :            1,  dm 3;
t  :         1000,  kg 1;
eV :  1.60218e-19,   C 1, V  1;
amu:  1.66054e-27,  kg 1;
au : 149597870700,   m 1;

nautical_mile:    1852,             m 1;
knot         :       1, nautical_mile 1,  h -1;
a            :       1,           dam 2;
bar          :     100,           kPa 1;
Å            :     0.1,            nm 1;
Ci           :  3.7e10,            Bq 1;
R            : 2.58e-4,             C 1, kg -1;
rad          :       1,           cGy 1;
rem          :       1,           cSv 1;

##########
# Non-SI #
##########
lb : 0.453592, kg  1;
in :   0.0254,  m  1;
ft :       12, in  1;
yd :        3, ft  1;
mi :   1760.0, yd  1;
mph:        1, mi  1, h -1;
kph:        1, km  1, h -1;
BMI:        1, kg  1, m -2;

###############
# Information #
###############

# Prefixes #
2:
Yi 80,
Zi 70,
Ei 60,
Pi 50,
Ti 40,
Gi 30,
Mi 20,
Ki 10;

# Units #
b;                   # bits
bps: 1.0, b 1, s -1; # bits per second
B  : 8, b 1;       # bytes
Bps: 1, B 1, s -1; # bytes per second
