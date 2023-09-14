# Aeroquest <img width="100" alt="Capture" src="https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/141b9135-41f0-47ad-8de1-eb766afe43ea">

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

 ![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/93e4e7ba-f5bb-4996-ab0d-8b8d60012b1e)

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

## Figures

(Found in examples/examples_new)

### fine-thick-dense-slice

The data for all plots are derived from computations conducted using three different mesh refinement levels, each comprising <b>69</b> VSPAERO simulations per level. The input sources of uncertainty for these simulations are Angle of Attack (AoA), Side Slip Angle (Beta), and Mach number, all following a normal distribution pattern. Every plot within the dataset presents statistical information related to the Coefficient of Pressure (Cp) at a specific location along the wing's span, precisely at the y-coordinate of 2.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/f3161206-48a9-4041-8d26-81e78787f6fd)

This plot illustrates the mean and standard deviation (σ) of the surface pressure coefficient (Cp). The figure displays data for both the lower surface (represented by black curves) and the upper surface (represented by blue curves) along the wing's X-location.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/46d6382a-fff0-4445-aa8e-e11e5a46c85f)

The plot depicts a normalized probability density function (PDF) in relation to the X-location on the wing's surface. The colors on the plot correspond to different ranges of the PDF, ranging from 0 to 1.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/f77a9aeb-e186-445e-a6db-38b6b251427e)

This plot is based on data from the above PDF plot and showcases the PDF distribution at X = 1.6756. It includes pairs of quantiles that delimit 10% of the total probability.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/7e81442d-9a8f-43d1-b29e-d0a75dc58efa)

This plot presents surface pressure coefficient data obtained from VSPAERO calculations on three mesh levels. The color code used is as follows: red for fine mesh, green for medium mesh, and blue for coarse mesh. This data is crucial in estimating errors in QUESTPost.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/1c95468d-d7a9-4b99-8219-a87d62f7e72b)

This plot provides error equations, both real and statistical, along with an equation. It breaks down the mean Cp error bias into components resulting from VSPAERO realization errors (black curve) and errors introduced by QUESTPost during the calculation of the mean Cp statistic. The QUEST error bias is significantly smaller than the VSPAERO error bias across most data points, except at X = 2.8, where they are approximately balanced.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/22873f2c-4d01-4bdf-8539-3708aa9058bf)

This plot ranks the input sources of uncertainty as fractions of unity based on the variation demonstrated in the moments.png plot. Side slip error bias contribution is relatively insignificant across all data points, while the angle of attack (AoA) error bias contribution dominates near the wing's leading edge. The contribution of Mach number error bias is prominent in the downstream portion of the wing at X = 1.8.


### fine-thick-sparse-slice

The data for all plots are derived from computations conducted using three different mesh refinement levels, each comprising <b>729</b> VSPAERO simulations per level. The input sources of uncertainty for these simulations are Angle of Attack (AoA), Side Slip Angle (Beta), and Mach number, all following a normal distribution pattern. Every plot within the dataset presents statistical information related to the Coefficient of Pressure (Cp) at a specific location along the wing's span, precisely at the y-coordinate of 2.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/73dd968a-8239-4bf6-a5a7-74a9ff3a38e3)

This plot illustrates the mean and standard deviation (σ) of the surface pressure coefficient (Cp). The figure displays data for both the lower surface (represented by black curves) and the upper surface (represented by blue curves) along the wing's X-location.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/8394da88-751c-4928-a07e-63f5b47f6271)

The plot depicts a normalized probability density function (PDF) in relation to the X-location on the wing's surface. The colors on the plot correspond to different ranges of the PDF, ranging from 0 to 1.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/0e370a58-7c85-4456-ac47-adb7d0c52816)

This plot is based on data from the above PDF plot and showcases the PDF distribution at X = 1.6756. It includes pairs of quantiles that delimit 10% of the total probability.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/3e1ee353-b447-4a02-afbd-467c7d0e50eb)

This plot presents surface pressure coefficient data obtained from VSPAERO calculations on three mesh levels. The color code used is as follows: red for fine mesh, green for medium mesh, and blue for coarse mesh. This data is crucial in estimating errors in QUESTPost.


![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/319fc5cb-3d6f-4048-93ad-a7caa1f046b1)

This plot provides error equations, both real and statistical, along with an equation. It breaks down the mean Cp error bias into components resulting from VSPAERO realization errors (black curve) and errors introduced by QUESTPost during the calculation of the mean Cp statistic. The QUEST error bias is significantly smaller than the VSPAERO error bias across most data points, except at X = 2.8, where they are approximately balanced.
,

![image](https://github.com/arocketguy/VSPAERO-QUEST/assets/25555091/30f54f35-4ba8-4c19-aea7-aa79b83ad632)

This plot ranks the input sources of uncertainty as fractions of unity based on the variation demonstrated in the moments.png plot. Side slip error bias contribution is relatively insignificant across all data points, while the angle of attack (AoA) error bias contribution dominates near the wing's leading edge. The contribution of Mach number error bias is prominent in the downstream portion of the wing at X = 1.8.


#

<b>Anooshkha Shetty & William Bui​</b>    
<b>NASA AMES</b>   
<b>System Analysis Office – Code AA​</b>
