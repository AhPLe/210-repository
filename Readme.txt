the event executive is apl_extra_event_executive. It can be used for all simulations
Ping-Pong
Ping Circling
and apl_sim_extra (a simplistic disease simulation of a population)
MYSim_LP_Class consists of a parent class which 'helps' some exec functions in theory work, except python does not do as much type checking as I thought. It was still included.

ping-pong and ping circling all have the expected arguments.
apl_sim_extra contains 
dr0 - a way to change the r0 (adj_r0 affected by population density and dlength_time)
dinfected - the percent population that starts infected
dlength_time - the length of time someone infected takes to recover (infected can be cut short by sick, dlength_time affects the time sick and the time infectious after sick before being recovered)
dsick - the percent that become sick (adj_r0 percent affected by dlength_time)
ddead - the percent that once sick die (adj_dead affected only by dlength_time)

events(state changes), a queue for messages, logical processes (initialized, active, I didn't realize was necessary for python, thought it might just be deallocation of memory space - exec and the outer function handled the count for Ping and circle ping)
run_exec is the while loop that continually dequeues messages

edit: apparently apl_sim_extra_hashed version was ran and edited to the more stable version, so is not present