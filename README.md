# McAlister Wing case

The objective of this study is to establish the performance of the DES
turbulence modeling for simulations of the McAlister experiments. The
experimental setup and data for this case can be found
in
[NACA 0015 wing pressure and trailing vortex measurements (1981) McAlister and Takahashi](http://www.dtic.mil/cgi-bin/GetTRDoc?AD=ADA257317).

## Visualization runs

For these runs, the initial conditions were set as follows. The Re =
\frac{c \rho V_\infty}{\mu} = 1.5 * 10^6 (corresponding to V_\infty =
46 m/s = 150.9 ft/s, M_\infty = 0.13, see page 9 of the McAlister
paper). The viscosity of air is set to 1.846e-5 kg/(m s) = 3.855e-7
slugs/(ft s). The density is defined by the Reynolds number, \rho =
\frac{\mu Re}{c V_\infty} = 1.9749 kg/m^3 = 0.003832 slugs/ft^3.

The turbulence modeling framework is DES, a hybrid RANS-LES framework,
with SST as the RANS model and Smagorinsky as the LES
model. Implementation details can be
found
[here](http://nalu.readthedocs.io/en/latest/source/theory/turbulenceModeling.html) and
[here](http://nalu.readthedocs.io/en/latest/source/theory/supportedEquationSet.html#shearstress-transport-sst-rans-model-suite) in
the Nalu theory documentation. The IC and inflow BC for the SST model
variables are set according to
the
[NASA specifications](https://turbmodels.larc.nasa.gov/flatplate_sst.html):
k_farfield = 9e-9 a^2_\infty = 9e-9 \frac{46^2}{0.13^2} = 0.001127
m^2/s^2 = 0.01213 ft^2/s^2, omega_farfield = 1e-6 \frac{\rho_\infty
a^2_\infty}{\mu_\infty}= 1e-6 \frac{1.9749}{1.846e-5}
\frac{46^2}{0.13^2} = 13395 1/s. This leads to a \frac{\mu_T}{\mu} =
0.009, similar to the NASA specifications.
