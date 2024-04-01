# Visualize-Chase-Algorithm-in-Python


## Update on 2024/04/01
### Chase with Distinguished Variables
#### Definition
![chase](img/chase_with_dv.png)

#### Implementation
```commandline
chase_with_distinguished_variables.py
```


## Update on 2024/03/30
### Simple Chase
#### Definition
Given R, a set of functional/multi-value dependencies
Check if desired dependency can be fulfilled

#### Implementation
```commandline
simple_chase.py
```

Example 1: 4 A->>B,C;D->C A->C
![simple1.1](img/simple_example1.1.png)
![simple1.2](img/simple_example1.2.png)

Example 2: 4 A->>B;B->>C A->>C
![simple2.1](img/simple_example2.1.png)
![simple2.2](img/simple_example2.2.png)

## Update on 2024/03/22
### Chase checking lossless decomposition
#### Definition
Given R, a set of functional dependencies only (no mvd)
Check if desired decomposition is lossless

#### Implementation
```commandline
chase_checking_lossless_decomposition.py
chase_checking_lossless_decomposition_GUI.py
```

Example 1: 3 C->B R1(A,C), R2(B,C)
![Example1](img/Example1.png)

Example 2: 6 B->E,EF->C,BC->A,AD->E R1(A,B,C,F),R2(A,D,E),R3(B,D,F)
![Example2](img/Example2.1.png)
![Example2](img/Example2.2.png)
![Example2](img/Example2.3.png)

Example 3: 3 A->C R1(A,B),R2(B,C)
![Example3](img/Example3.png)

GUI version by Yijia
![GUI1](img/GUI1.png)
![GUI2](img/GUI2.png)
![GUI3](img/GUI3.png)