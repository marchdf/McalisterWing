# McAlister Wing case

The objective of this study is to establish the performance of the DES
turbulence modeling for simulations of the McAlister experiments. The
experimental setup and data for this case can be found
in
[NACA 0015 wing pressure and trailing vortex measurements (1981) McAlister and Takahashi](http://www.dtic.mil/cgi-bin/GetTRDoc?AD=ADA257317).

## Initial conditions and turbulence modeling

We focus on the case for alpha (angle of attack) = 0 and 12 degrees,
Re = c V_\infty / \nu = 1.5 * 10^6 (corresponding to V_\infty = 46 m/s,
M_\infty = 0.13). The viscosity of air is set to 1.846e-5 kg/ms. The
density is defined by the Reynolds number.


The turbulence modeling framework is DES, a hybrid RANS-LES framework,
with SST as the RANS model and Smagorinsky as the LES
model. Implementation details can be
found
[here](http://nalu.readthedocs.io/en/latest/source/theory/turbulenceModeling.html) and
[here](http://nalu.readthedocs.io/en/latest/source/theory/supportedEquationSet.html#shear-stress-transport-sst-rans-model-suite) in
the Nalu theory documentation. The IC and inflow BC for the SST model
variables are set according to
the
[NASA specifications](https://turbmodels.larc.nasa.gov/flatplate_sst.html):
k_farfield = 9e-9 a^2_\infty = 9e-9/(0.13^2) (46^2) = 0.001127,
omega_farfield = 1e-6 \frac{\rho_\infty a^2_\infty}{\mu_\infty}= 1e-6
1.177/1.846e-5 (46^2/0.13^2) = 7983.14.

## Metric of comparison

### Case 1: alpha = 0, Re = 1.5e6

Simulation results will be compared to experimental results of the
wing surface metrics (Cl, Cp, Cd) as shown in Fig. 18a of the
McAlister paper.


### Case 2: alpha = 12, Re = 1.5e6

In addition to wing surface metrics (Fig. 19a, 21c and 27c), tip
vortex metrics will also be compared to simulation results (Fig. 39 of
McAlister paper).

## Results


## Conclusions
