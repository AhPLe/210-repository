all files included, check analysis in assess_portfolio/analysis.py
From Arthur LeBlanc/APL
The files included allow specific args to output the targets. There seem to be more digits than what is given in the specified problem, but all the numbers are accurate
example args from examples expected:
example 1: -s 2010-01-01 -e 2010-12-31 -p
example 2: -s 2010-01-01 -e 2010-12-31 -p -x AXP HPQ IBM HNZ -a 0 0 0 1
example 3: -s 2010-06-01 -e 2010-12-31 -p -x GOOG AAPL GLD XOM -a 0.2 0.3 0.4 .1

checklist:
part 1: 
date range input
symbol input
check that allocations sum to one (exits upon issue)
start value input

output statistics from portfolio input:
cr, adr, sddr, sr, ev

(some sampling frequency code was included, but it wasn't really tested)

api specification looks correct with proper variable names
if running the program itself, parameters are allowed with valid examples listed above

