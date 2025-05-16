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

## CPM-based models

### Definition of time
In all CPM models, we relate the time discrete Monte Carlo Step to continuous simulation time such that 1 MCS corresponds to 1 a.t.u.

### MODEL000

A standard, single-cell CPM with only area and perimeter terms (diffusive motion without persistence).

$$H = H_\text{area} + H_\text{perimeter}$$

$$H_\text{area} =  \lambda_\text{area} \left (A(t) - A_\text{target} \right)^2$$

$$H_\text{perimeter} =  \lambda_\text{perim} \left ( P(t) - P_\text{target} \right)^2$$

with $A(t)$ and $P(t)$ the cell's current area and perimeter, respectively.

| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $T$ | CPM temperature             |
| $\lambda_\text{area}$ | Lagrange multiplier of the area term in the Hamiltonian		              |
| $A_\text{target}$  | Cell target area (in # pixels) |
| $\lambda_\text{perim}$ | Lagrange multiplier of the perimeter term in the Hamiltonian		              |
| $P_\text{target}$  | Cell target perimeter (in # pixels within neighborhood radius not belonging to same cell; unless explicitly mentioned otherwise, we consider the 3x3 Moore neighborhood) |

### Shared definition of work terms

#### General work term

We define a general work term for movement along a given direction as the energy difference $\Delta H (s \rightarrow t)$ associated with a proposed copy attempt from source pixel $s$ into target pixel $t$, involving cells $\sigma_s$ and $\sigma_t$. The general formula is:

$$\Delta H_\text{work} = \delta_s \Delta H_\text{work} (\sigma_s) + \delta_t \Delta H_\text{work}(\sigma_t)$$

where $\delta_s, \delta_t \in 0,1$ determine whether the force acts on the "protruding" cell $\sigma_s$ and/or the "retracting" cell $\sigma_t$.  We describe this as `cpm_force_mode` which can be `"extension"` ($\delta_s = 1, \delta_t = 0$), `"retraction"` ($\delta_s = 0, \delta_t = 1$), `"reciprocal"` ($\delta_s = \delta_t = 1$).  

The definition of $\Delta H_\text{work} (\sigma)$ depends on the specific model.

#### Directional work term

Specifically we consider work terms that apply a (cell-intrinsic or extrinsic) force in a given direction. To define the work $\Delta H_\text{work} (\sigma)$ associated with movement of cell $\sigma$ along a given target direction vector, we specify: 

$$\Delta H_\text{work} (\sigma) = \Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

where:
- we rename $\Delta H_\text{work} (\sigma) = \Delta H_\text{dir} (\sigma)$ to indicate the type of work term
- $\vec{dx}(\sigma)$ is the movement of cell $\sigma$ that would be induced by the proposed copy attempt. This can be defined in several ways (`cpm_update_direction`): `"source-to-target-unnorm"` (the unnormalized vector from $s \rightarrow t$), `"source-to-target-norm"` (idem, but normalized to unit length), or `"cell-mass-displacement"` (induced movement of cell $\sigma$'s center of mass, multiplied by its current number of pixels)
- $\vec{b}(\sigma)$ is the target direction along which some extrinsic/intrinsic force acts. This and its temporal dynamics are specified in the individual models below.
- $\lambda_\text{dir}(\sigma)$ defines the magnitude of the acting force and can be cell-dependent. For the case $\sigma = 0$ (the "background" rather than a cell), we assume $\lambda_\text{dir}(\sigma=0) = 0$.

### MODEL003

Extends MODEL000 with a work term to favour motion in a static target direction (yielding ballistic motion in a predefined direction). Starting from the general work term as defined above: 

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

we rephrase as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{v} _ { \text{copy}} \cdot \vec{e}_\alpha \right)$$

i.e. we define:

- $\vec{dx}(\sigma) = \vec{v}_\text{copy}$ as the **unnormalized** vector from source pixel $s$ to target pixel $t$; i.e. `cpm_update_direction` = `source-to-target-unnorm`
- $\vec{b}(\sigma) = \vec{e}_\alpha = ( \cos \alpha, \sin \alpha )$, a unit vector in a (fixed) reference direction $\alpha$.

| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $T$ | As Model000             |
| $\lambda_\text{area}$ | As Model000		              |
| $A_\text{target}$  | As Model000 |
| $\lambda_\text{perim}$ | As Model000		              |
| $P_\text{target}$  | As Model000 |
| $\lambda_\text{dir}$ | Lagrange multiplier of the work term, controls the cell speed.	              |
| $\alpha$ | Angle (to the positive x-axis) of the fixed target direction              |
| `cpm_force_mode` | "extension", i.e. $\delta_s = 1, \delta_t = 0$ (see "work term")              |
| `cpm_update_direction` | "source-to-target-unnorm", i.e.  $\vec{dx}(\sigma)$ is the unnormalized vector $s\rightarrow t$    |

### MODEL005

Similar to MODEL003, but target directions can adapt through self-reinforcement of random fluctuations, yielding a persistent random walk rather than ballistic motion. Specifically, we rephrase the reference direction in the work term:

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{v}_{\text{copy}} \cdot \tfrac{\vec{u}(t)}{ \Vert \vec{u}(t) \Vert } \right)$$


i.e. we define:
- update direction as MODEL003: $\vec{dx}(\sigma) = \vec{v}_\text{copy}$ as the **unnormalized** vector from source pixel $s$ to target pixel $t$; i.e. `cpm_update_direction` = `source-to-target-unnorm`
- target direction $\vec{b}(\sigma) = \tfrac{\vec{u}(t)}{ \Vert \vec{u}(t) \Vert }$

which now also gets a temporal update:

$$\vec{u}(t)= \vec{\Delta c} (\Delta t)$$

where $\vec{\Delta c}(\Delta t)$ is the (normalized) observed displacement vector of the cell centroid over the last $\Delta t$ MCS. 


| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $T$ | As Model000             |
| $\lambda_\text{area}$ | As Model000		              |
| $A_\text{target}$  | As Model000 |
| $\lambda_\text{perim}$ | As Model000		              |
| $P_\text{target}$  | As Model000 |
| $\lambda_\text{dir}$ | As Model003, the Lagrange multiplier controls the cell speed.     |
| $\Delta t$   | Time interval (in MCS) over which we evaluate the cell's recent displacement; this determines persistence time of the random walk.      |
| `cpm_force_mode` | "extension", i.e. $\delta_s = 1, \delta_t = 0$ (see "work term")              |
| `cpm_update_direction` | "source-to-target-unnorm", i.e.  $\vec{dx}(\sigma)$ is the unnormalized vector $s\rightarrow t$         |



### MODEL006

This simple, Langevin PRW model is similar to MODEL005, but directly evolves the cell orientation with angular noise. 

Specifically, we rephrase the work term 

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( A(\sigma,t)\vec{\delta c}(\sigma) \cdot \vec{e}_\alpha(\sigma,t) \right)$$

i.e. compared to MODEL003 we make $\alpha (\sigma)$ dynamic as $\alpha (\sigma, t)$ and replace the source $\rightarrow$ target vector $\vec{v}_\text{copy}$ with the cell mass displacement induced by the copy attempt:

$$\vec{dx}(\sigma) = A(\sigma,t)\vec{\delta c}(\sigma) $$

where $\vec{\delta c}(\sigma )$ is the cell centroid displacement due to the proposed update, $A(\sigma, t)$ is the cell's current area. Furthermore, we let the cell orientation $\alpha$ diffuse over time with Gaussian noise:

$$\alpha(\sigma, t) = \alpha(\sigma, t-\Delta t) + \epsilon\sqrt{\Delta t}, \quad \epsilon \sim \mathcal{N}(0,\xi^2)$$

$$ \vec{e}_\alpha(\sigma, t) = \left(\cos \quad \alpha(\sigma, t), \sin \quad \alpha(\sigma, t) \right)$$
			
with step size $\Delta t$ an integer $\geq 1$ MCS.

| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $T$ | As Model000             |
| $\lambda_\text{area}$ | As Model000		              |
| $A_\text{target}$  | As Model000 |
| $\lambda_\text{perim}$ | As Model000		              |
| $P_\text{target}$  | As Model000 |
| $\lambda_\text{dir}$ | As Model003, the Lagrange multiplier controls the cell speed.     |
| $\Delta t$   | Evolution time step of changes in target direction, in (a positive integer number of) MCS.    |
| $\xi$   | Standard deviation of noise added to the cell direction (larger $\xi$ implies lower persistence time).   |
| `cpm_force_mode` | "extension", i.e. $\delta_s = 1, \delta_t = 0$ (see "work term")              |
| `cpm_update_direction` | "cell-mass-displacement", i.e.   $\vec{dx}(\sigma) = A(\sigma,t)\vec{\delta c}(\sigma) $     |


### MODEL007

TO DO match description to that of the models above. 

We define a simple Langevin PRW based on cell orientation α under continuous white noise of intensity ω. 
In addition, the observed cell velocity $\vec{v}$ gradually ($R$) self-reinforces the actual movement, 
allowing the cell to adapt to external constraints (obstacles, collisions).

Cell velocity is controlled by Lagrange multiplier µ.

$$ d\alpha/dt = \omega \xi $$

$$\Delta H_{PRW} = - \mu a_{\sigma}  ( \vec{\delta C} · \vec{e(\alpha)} )  + R \sin( \angle{ \vec{v} } - \alpha) $$

where $a_{\sigma} is the cell size, $\vec{\delta C}$ is the cell center displacement due to the update, 
$\vec{e(α)}$ a unit vector in direction of α and $\angle{ \vec{v} }$ the angular direction of motion.



## Other formalisms

### MODEL004

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


