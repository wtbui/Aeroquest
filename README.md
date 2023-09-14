# Aeroquest

The typical aerodynamic analysis process involves calculating the lift, drag, and moments over the flight regime and passing this data to the vehicle analysis team. Our goal for this project was to enhance the reliability of aerospace CFD simulations and optimize early-stage aircraft design. We worked with two softwares: VSPAERO, a fast aerodynamic solver, and QUEST, uncertainty quantification code. Our work automates the preprocessing of aircraft uncertainty source data, computes aerodynamic forces on models, and generates an aerodynamic database of uncertainty quantification and error estimation for analysis, that can then be propagated down stream in the vehicle design process. 

<b>Aeroquest handles:</b>
  * File IO parsing between VSPAERO/QUEST​
  * Multilevel mesh generation and realization​
    * Creating meshes by hand on OpenVSP
    * Automating meshes through VSPAERO
  * Airfoil slice data handling
  * Fine meshes​
  * Panel method
  * Adjoint solver
    * Instead of solving on three different meshs to get the realization error, our adjoint solver will calculate the error that can be fed into QUEST

<b>Note</b>: This repo will only contain the work we did with QUEST.

## Introduction

Mathematical models arising in computational physics often contain sources of uncertainty. 

* Sources of uncertainty
  * Initial and boundary data
  * <i> Model parameters, e.g., reactive chemistry, RANS turbulence models </i>
  * <i> Random variable fields, e.g., correlated random fields using Karhunen-Loeve representation </i>
 
* Sources of error
  * Finite-dimensional approximation
      * CFD realizations (CFD realization error)
      * Uncertainty statistics
  * <i> Model errors, e.g., geometric models, turbulence models, chemistry models, random field models </i>

QUEST estimates the statistical uncertainty of output quantities of interest by performing multiple CFD simulations (or realizations) using values of uncertain parameters or fields necessary in the estimation of output quantity of interest statistics (QoI). QUEST contains a set of statistics estimators + estimates of estimator error that are cost efficient for a wide range of uncertainty quantification problems.

QUEST contains the application QUESTPrep for setting input sources of uncertainty and the application QUESTPost for post-processing output quantities of interest and estimated QoI errors obtained from grid-based CFD calculations yielding output quantity of interest statistics with error bias estimates

### Theoretical Overview

Depending on the analysis problem, the desired output quantities of interest (QoI) statistics may range from moment statistics (e.g., mean and variance) to probability density function (PDF) distributions. Particular attention is given to the calculation of expectation and variance moment statistics. For a function f(x) and probability density p(x), the expectation (mean) is calculated from the integral:

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/230a1ddb-ee65-4064-b6bc-15c61f4560b7)

and the variance (standard deviation squared) is calculated from the integral:

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/86fc7945-de00-4e02-96ee-602b6118c31d)

In addition, often there is interest in estimating the output probability density distribution denoted by pf:

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/e8aa9009-da3e-4fec-90c6-e3b7f8526012)

#### Estimation of Probability Densities

The Kernel density estimation is an algorithm attributed to Rosenblatt and Parzen for estimating the probability density distribution of an independent and identically distributed (i.i.d.) population of samples. Given a set of N i.i.d. samples fx1; x2; : : : ; xNg, the probability density distribution is estimated from the sum:

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/08249a7d-661d-4b60-9482-8e99c494b7d3)

Data for the kernel density estimator exploits the construction of interpolants using the quadrature point evaluations in dense or sparse tensor Clenshaw-Curtis or Gauss-Patterson quadrature together with Sobol resampling to produce data.

#### Statistical Error Bias Balancing (SEBB)

QUEST is able to estimate uncertainty k-moment statistics with three error bias estimates: (1) statistical CFD realization error bias, (2) numerical statistics approximation error, and (3) statistical model error bias. Measuring error biases helps evaluate the credibility of an estimated k-moment statistic, as the total error in such a statistic results from the sum of these biases. Identifying and quantifying the main sources of error bias in a computed statistic also offers practical benefits for enhancing accuracy. To achieve this, the new Statistical Error Bias Balancing (SEBB) model is introduced. SEBB streamlines error reduction by efficiently allocating computational resources to address the primary sources of bias.

Given the following informal definitions:
* u an infinite-dimensional aspirational “truth” solution,
* U an infinite-dimensional model solution,
* Uh a finite-dimensional model solution,
* J(·)(x, t) an output quantities of interest (QoI),
* E[·] an expectation functional,
* QN E[·] a N -evaluation approximated expectation functional,
* RN E[·] a N -evaluation expectation functional quadrature error

Fundamental expectation error decomposition:

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/333e8718-778d-4999-acae-f3ae7027a757)

Depending on which sources of error bias are dominant, additional computational resources can then be allocated to achieve SEBB:
* Reduce expected realization error bias by solving CFD problems more accuractely (e.g., finer meshes),
* Reduce expectation approximation error by calculating statistics more ac-
curately (e.g., more samples or quadrature point evaluations),
* Reduce the expected model error bias by improving the model (e.g., ML
model augmentation, model replacement).

#### Error Estimates for Moment Statistics)

Two forms of externally provided realization error and model error can be accommodated:
* (Type I signed errors). Signed realization error, J(U)-J(Uh), and signed model error, J(u)-J(U),
* (Type II unsigned errors). Unsigned realization error, |J(U)-J(Uh)|, and unsigned model error, |J(u)-J(U)|.

<ins>Type I Signed Error Bound Estimates for Moment Statistics</ins>

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/4a099cb9-4654-43e0-a1e5-85b839682102)

* Expectation error estimate (Type I):

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/11581223-68ab-44f9-a662-0fa05060f026)

* Variance error estimate (Type I):

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/c12ac554-4cab-470d-b14c-a44fbe91414f)

<ins>Type II Unsigned Error Bound Estimates for Moment Statistics</ins>

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/6eb13ff1-410d-4090-9a0f-d2ffc9a0d5cc)

* Expectation error bound (Type II):

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/0f2ff427-71f5-401f-a432-6f5625639439)

* Variance error bound (Type II):

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/0ceb3e58-55f6-45f2-934d-5961fe9082a0)

## Before running:
Use QUESTPrep to generate a database file and OpenVSP to generate geometry(s)

If running on slice data, write a .cuts file to specify cut locations along geometry

<b>NOTE</b>: File paths can only currently be specified within the source code

## Running:
In terminal use command:

```
python3 Aeroquest.py <flags> <mesh number (1-3)> <-slice (IF USING SLICE)>
```

<b>Aeroquest Flags:</b>

-h: Help Menu

-ws: Runs Aeroquest (to run with slice data add -slice)

-wsmg: Runs Aeroquest with mglevel (to run with slice data add -slice)

<b>Debug Flags:</b>

-w: Write .VSPAero Files

-d: Delete .VSPAero Files

-s: Runs VSPAero Solver

-test: Runs test code block

### Testcases:
Included in VSPAERO-QUEST/TestCase are 4 test cases (containing 3 levels of meshes). 
Test cases labeled "Coarse" are debug meshes

### Keep in mind:
* File paths can only be specified within source code at the top 
* When writing .cuts file, do not use locations that will generate duplicate points (Such as y=0 on a wing)
* When slicing thick geometries, upper edge must have negative z values
* Can not handle slice data on geometries with multiple curves

## Example results
![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/d99179f9-6614-4565-9c81-4564c216aa19)
![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/1c2150ac-8d23-467d-bc92-4d90815105f8)
![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/b25ad60c-39b7-4018-acbc-f634db53685e)
![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/59286730-6020-4460-b6eb-cfb5525797f5)


#

<b>Anooshkha Shetty & William Bui​</b>    
<b>NASA AMES</b>   
<b>System Analysis Office – Code AA​</b>
