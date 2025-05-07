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
| MODEL006 | CPM    | Persistent motion controlled by cell-intrinsic orientation under effect of continuous time noise |
| MODEL007 | CPM    | Persistent motion controlled by cell-intrinsic orientation under effect of continuous time noise and self-reenforcement of direction of motion |

## MODEL003

The model is a Langevin PRW from extension of MODEL003 with the following term:

```math
\Delta H_{PRW} = \vec{\lambda}_{\text{dir}} \cdot \vec{a}
```

where $\vec{\lambda}_{\text{dir}}$ is a vector of coefficients and 
$\vec{a}$ is the direction from source $\rightarrow$ target of the copy attempt. 

## MODEL004

The model is a Langevin PRW with particle migration velocity $\vec{v}_{\text{mot}}$, 

```math
\vec{v}_{\text{mot}} = s_{\text{mot}} \frac{(1-b) \vec{\xi} + b \vec{d}_{\text{bias}}}{\| (1-b) \vec{\xi} + b \vec{d}_{\text{bias}} \|}
```

where $s_{\text{mot}}$ is a migration speed, 
$b$ is a migration bias, 
$\vec{\xi}$ is a random unit vector, and 
$\vec{d}_{\text{bias}}$ is a migration bias direction. 
The migration velocity changes with a probability,

```math
\Pr \left(\text{change} \vec{v}_{\text{mot}} \right) = \frac{\Delta t}{T_{\text{per}}}
```

where $\Delta t$ is the time step and $T_{\text{per}}$ is a persistence time.

## MODEL005

We define a simple self-reinforcing P-RW by extending MODEL000 with the following
term:

$$\Delta H_{PRW} = -\lambda_{\text{dir}} * \cos \alpha$$

where $\alpha$ is the angle between directions $\vec{a}$ and $\vec{t}(\sigma)$, with 
$\vec{a}$ the direction from source $\rightarrow$ target of the copy attempt,
and $\vec{t}(\sigma)$ the current target direction of cell $\sigma$.

Target directions are initialized randomly and updated every step:

$$\vec{t}(\sigma, t) = (1-P_\text{persist}) \vec{t}(\sigma, t-1) + P_\text{persist} \Delta p (\sigma)$$

where $\Delta p (\sigma)$ is the observed displacement of cell $\sigma$ over the last
$\Delta t$ MCS.

As such, this model has the following motility parameters on top of CPM MODEL000:


| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $\lambda_\text{dir}$ | Lagrange multiplier of this term in the Hamiltonian              |
| $\Delta t$ | Time (in MCS) over which the displacements are computed		              |
| $P_\text{persist}$ | reinforcement parameter; at $P_\text{persist}=0$ the new target direction is fully determined by the displacement in the past $\Delta t$ MCS, whereas at $P_\text{persist}=1$ we keep target directions regardless of actual displacement.   |


## MODEL006

We define a simple Langevin PRW based on cell orientation α under continuous white noise of intensity ω. 
Cell velocity is controlled by Lagrange multiplier µ.

$$ d\alpha/dt = \omega \xi $$

$$\Delta H_{PRW} = - \mu a_{\sigma} ( \vec{\delta C} · \vec{e(\alpha)} ) $$

where $a_{\sigma}$ is the cell size, $\vec{\delta C}$ is the cell center displacement due to the update and $\vec{e(α)}$, a unit vector in direction of α.

Alternatively, the cell mass displacement  $a_{\sigma}  \vec{\delta C}$ can also be estimated using the local copy attempt direction. It will be on the same scale, but obviously is not exacltly the same. Would be very interesting to compare both and find the approximate factor.

**Implementation**: 
Temporal evolution of $\alpha$ shall be performed using a discretized forward Euler scheme with a time step set to 1 MCS (or less). We use $\xi$ for the amplitude for the random noise.

$$ \alpha(t+dt) = \alpha(t) + random_norm(0,\xi) * \sqrt{dt} $$

where random_norm draws a random number from the Gaussian distribution $(0,\xi)$.

Before logging, $\alhpa$ shall be mapped within the range ${0,2\pi}$ .





## MODEL007

We define a simple Langevin PRW based on cell orientation α under continuous white noise of intensity ω. 
In addition, the observed cell velocity $\vec{v}$ gradually ($R$) self-reinforces the actual movement, 
allowing the cell to adapt to external constraints (obstacles, collisions).

Cell velocity is controlled by Lagrange multiplier µ.

$$ d\alpha/dt = \omega \xi $$

$$\Delta H_{PRW} = - \mu a_{\sigma}  ( \vec{\delta C} · \vec{e(\alpha)} )  + R \sin( \angle{ \vec{v} } - \alpha) $$

where $a_{\sigma} is the cell size, $\vec{\delta C}$ is the cell center displacement due to the update, 
$\vec{e(α)}$ a unit vector in direction of α and $\angle{ \vec{v} }$ the angular direction of motion.
