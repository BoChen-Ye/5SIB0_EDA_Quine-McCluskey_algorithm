# 5SIB0_EDA_Quine-McCluskey_algorithm
 This is our report and code of 5SIB0 in TU/e, 2023. It is about validating QMC algorithm by using Python.

# Abstract
The basic rule of logic synthesis is to reduce hardware cost and delay time. To achieve this, 
QuineMcCluskey(QMC) algorithm is widely used for two-level logic optimization in the past time. It can simplify the input Boolean
expressions on computer. It use prime implicant table to simplify the input Boolean expression which is capable of being programmed 
on a digital computer. This paper presents the principle of QMC algorithm and a validation on its implementation. 
The whole design and validation platform implemented by Python, and then it outputs validation results in terms of four aspects:
consistency validation, correctness validation, running time, and gate-level circuits. Also, We compare our result of running time
with related work and compare QMC algorithm with Espresso result. The experiment show that QMC algorithm is suitable for
cases with few input variables, while Espresso is suitable for cases with many variables.