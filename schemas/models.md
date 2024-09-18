Persistent random walk models
==

| Label    | Method | Description                                                                   |
|----------|--------|-------------------------------------------------------------------------------|
| MODEL000 | CPM    | No persistence                                                                |
| MODEL001 | CPM    | Equation 2 in 10.1084/jem.20061278                                            |
| MODEL002 | CPM    | Equation 3 in 10.1007/978-3-7643-8123-3_7                                     |
| MODEL003 | CPM    | Constant persistence as implemented by ExternalPotentialPlugin in CompuCell3D |
| MODEL004 | CM     | Equation 9 in 10.1371/journal.pcbi.1005991                                    |
| MODEL005 | CPM    | Simple self-reinforcing PRW in the CPM, described below                       |


## MODEL005

We define a simple self-reinforcing P-RW by extending MODEL000 with the following
term:

$$\Delta H_{PRW} = -\lambda_{\text{dir}} * \cos \alpha$$

where $\alpha$ is the angle between directions $\vec{a}$ and $\vec{t}($\sigma$)$, with 
$\vec{a}$ the direction from source $\rightarrow$ target of the copy attempt,
and $\vec{t}(\sigma)$ the current target direction of cell $\sigma$.

Target directions are initialized randomly and updated every step:

$$\vec{t}(\sigma, t)$$ = (1-P_\text{persist}) \vec{t}(\sigma, t-1) + P_\text{persist} \Delta p (\sigma)

where $\Delta p (\sigma)$ is the observed displacement of cell $\sigma$ over the last
$\Delta t$ MCS.

As such, this model has the following motility parameters on top of CPM MODEL000:


| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $\lambda_\text{dir}$ | Lagrange multiplier of this term in the Hamiltonian              |
| $\Delta t$ | Time (in MCS) over which the displacements are computed		              |
| $P_\text{persist}$ | reinforcement parameter; at $P_\text{persist}=0$ the new target direction is fully determined by the displacement in the past $\Delta t$ MCS, whereas at $P_\text{persist}=1$ we keep target directions regardless of actual displacement.   |
