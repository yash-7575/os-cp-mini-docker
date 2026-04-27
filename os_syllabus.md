ML2011: Operating Systems 
Teaching Scheme:  
Theory: 2  Hours / Week ;       
Laboratory: 2 Hours / Week;  
Total Credits: 3 
Course Prerequisites: Computer Architecture & organization, Data Structure 
Course Objectives: 
1.To learn functions of Operating System 
2.To learnthe importance of concurrency and how to implement concurrent abstractions correctly in 
an OS. 
3.To learn OS scheduling policies and mechanisms. 
4.To deal with deadlock 
5.To learn memory management schemes in various ways to improve performance, and how this 
impacts system complexity 
6. To learn design & develop the Operating system from a scratch. 
Course Relevance: 
Section 1: Topics/Contents 
Unit-I Introduction to OS           
[04 Hours] 
What is OS, Interaction of OS and hardware, Goals of OS, Basic functions of OS, OS 
Services, System Calls, Types of system calls.    
Types of OS: Batch, Multiprogramming, Time sharing, Parallel, Distributed & Real-Time 
OS. 
Unit-II Title: Process Management                                                               
[06 Hours] 
Process Concept, Process States: 2, 5, 7 state models, Process Description, Process Control. 
Threads: Multithreading models, Thread implementations – user level and kernel level 
threads, Symmetric Multiprocessing. 
Concurrency: Issues with concurrency, Principles of Concurrency 
Mutual Exclusion: H/W approaches, S/W approach, OS/Programming Language 
support: Semaphores, Mutex and Monitors.  
Classical Problems of Synchronization: Readers-Writer’s problem, Producer    
Consumer problem, Dining Philosopher problem  
Dept. CSE-AIML                            
A.Y.  2025-26                                                                 
70                               
Bansilal Ramnath Agarwal Charitable Trust’s 
VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE – 37 
(An Autonomous Institute Affiliated to Savitribai Phule Pune University) 
Unit-III Title: Process Scheduling                                                                 
[04 Hours] 
Uniprocessor Scheduling: Scheduling Criteria, Types of Scheduling: Preemptive, 
Non-preemptive, Long-term, Medium-term, Short-term.  
Scheduling Algorithms: FCFS, SJF, RR, Priority. 
Section2: Topics/Contents 
Unit-IV Title: Deadlocks                                                                                
[04 Hours] 
Principles of deadlock, Deadlock Prevention, Deadlock Avoidance, Deadlock Detection, 
Deadlock Recovery 
Unit-V Title: Memory Management                                                             
[06 Hours] 
Memory Management concepts: Memory Management requirements, Memory Partitioning: 
Fixed, Dynamic Partitioning, Buddy Systems, Fragmentation, Paging, Segmentation, Address 
translation.  
Placement Strategies: First Fit, Best Fit, Next Fit and Worst Fit. 
Virtual Memory: Concepts, Swapping, VM with Paging, Page Table Structure, Inverted 
Page Table, Translation Lookaside Buffer, Page Size, VM with Segmentation with combined 
paging and segmentation. 
Page Replacement Policies: FIFO, LRU, Optimal, Clock. 
Swapping issues: Thrashing 
Unit-VI Title: I/O and File Management                                                      
[04 Hours] 
I/O management: I/O Devices - Types, Characteristics of devices, OS design issues for I/O 
management, I/O Buffering.  
Disk Scheduling: FCFS, SCAN, C-SCAN, SSTF. 
File Management: Concepts, File Organization, File Directories, File Sharing. Record 
Blocking, Secondary Storage Management, Free Space management, Security. 
List of Practical’s (Minimum Six to be performed out of 10):  
1. Execution of Basic & Advanced Linux Commands.  
2. Write shell script covering – basic arithmetic, control structures, loops, execution of Linux 
command in shell, command line arguments, functions and arrays.  
3. Solve synchronization problems – Reader writer problem, Producer consumer problem & 
dinning philosopher problem using mutex & semaphore.  
4. Implement CPU scheduling algorithms  
5. Implement Banker’s algorithm  
6. Implement deadlock detection algorithm  
7. Implement placement strategies.  
Dept. CSE-AIML                            
A.Y.  2025-26                                                                 
71                               
Bansilal Ramnath Agarwal Charitable Trust’s 
VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE – 37 
(An Autonomous Institute Affiliated to Savitribai Phule Pune University) 
8. Implement buddy system.  
9. Implement page replacement algorithm  
10. Implement disk scheduling algorithm  
List of Course Project areas:  
1.Design and implementation of a 
i. CPU/ Machine Simulation 
ii. Supervisor Call through interrupt 
Design multi programming operating system phase 1 
2.Design and implementation of a Multiprogramming Operating System: Stage II 
i. Paging 
ii. Error Handling 
iii. Interrupt Generation and Servicing 
iv. Process Data Structure 
3.Design and implementation of a Multiprogramming Operating System: Stage III 
i. I/O Channels& I/O buffering  
ii. Multiprogramming 
iii. I/O Spooling 
4. Design multi programming operating system phase 1 with arithmetic & logical instructions 
5.Design multi programming operating system phase 3 with swapping 
Assessment Scheme: Suggest an Assessment scheme that is best suited for the course. Ensure 360 
degree assessment and check if it covers all aspects of Bloom's Taxonomy. 
Laboratory Continuous Assessment:  100 Marks converted to 10 Marks 
Course Project: End Semester Examination: 100 Marks converted to 20 Marks 
Laboratory Practical: End Semester Examination:100 Marks converted to 50 Marks 
Comprehensive Viva Voce: End Semester Examination: 100 Marks converted to 20 Marks 
Text Books: (As per IEEE format) 
1. Stalling William; “Operating Systems”, 6thEdition, Pearson Education. 
2. Silberschatz A., Galvin P., Gagne G.; “Operating System Concepts”, 9th Edition, John Wiley and Sons. 
3. D M Dhamdhere; "Systems Programming & Operating Systems"; Tata McGraw Hill Publications, ISBN – 
0074635794 
4. John J Donovan; " Systems Programming " ; Tata Mc-Graw Hill edition , ISBN-13978-0-07-460482-3 
Reference Books: (As per IEEE format) 
1. Silberschatz A., Galvin P., Gagne G ;“Operating System Principles” 7th Edition John Wiley and Sons. 
Dept. CSE-AIML                            
A.Y.  2025-26                                                                 
72                               
Bansilal Ramnath Agarwal Charitable Trust’s 
VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE – 37 
(An Autonomous Institute Affiliated to Savitribai Phule Pune University) 
 
 
2. YashavantKanetkar; “Unix Shell Programming”, 2 nd Edition, BPB Publications. 
3. Forouzan B. A., Gilberg R. F.; “Unix And Shell Programming”, 1 st Edition, Australia Thomson Brooks Cole. 
4. Achyut S. Godbole, Atu lKahate; “Operating Systems”, 3 rd Edition, McGraw Hill. 
 
MOOCs Links and additional reading material: 
1. https://nptel.ac.in/courses/106105214  
2. https://onlinecourses.nptel.ac.in/noc20_cs04/preview 
3. https://archive.nptel.ac.in/courses/106/102/106102132/ 
4. https://onlinecourses.nptel.ac.in/noc21_cs72/preview 
 
Course Outcomes: 
The student will be able to –  
1. Discuss the functions of a contemporary Operating system with respect to convenience, efficiency 
and the ability to evolve. 
2.  Implement concurrent abstractions correctly in an OS to solve real world problems. 
3.  Use various CPU scheduling algorithms to construct solutions to real world problems. 
4.  Corelate the mechanisms related to deadlock handling in real life situations. 
5.  Distinguish memory management schemes & file management systems in various ways to 
improve performance, and analyze the impact of it on system complexity. 
6.Design & develop the Operating system from a scratch 
  
CO-PO Map:  
CO Program Outcomes (PO) PSO 
  PO1 PO2 PO3 PO4 PO5 PO6 PO7 PO8 PO9 PO10 PO11 PSO1 PSO2 PSO3 
 1 2  2                   3 2  
2 2 2  3 2      2  2       3 3  
3 2 3  3 2      2  2       3 2  
4 2 3   2                3 2  
5 2 3   1               3 2  
6 2  2  3 2    2 2  2  3  3.0 3.0  3 3  
Avg 2 2.5  3.0 1.8   2.0   2.0 2.0  3.0  3.0  3.0  3.0 2.33  
 
CO Attainment levels:  
Weights for attainment levels: L1 - Easy-0.75    L2 - Comfortatble-0.7    L3 – Medium – 0.65  
L4 – Somewhat difficult – 0.6     L5 – Difficult – 0.55 
 
CO1 – L1, CO2 – L2, CO3 – L3, CO4 – L4, CO5 – L4 and CO6 – L5 
Dept. CSE-AIML                            A.Y.  2025-26                                                                 73                               
 
 
Bansilal Ramnath Agarwal Charitable Trust’s 
VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE – 37 
(An Autonomous Institute Affiliated to Savitribai Phule Pune University) 
Future Course Mapping: 
Advanced Operating System, Distributed Operating System, Parallel Computing. 
Job Mapping: 
System Administrator, System Analyst   