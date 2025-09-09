Persistent random walk models
===

Overview:

| Label    | Method | Description                                                                   |
|----------|--------|-------------------------------------------------------------------------------|
| [MODEL000](#model000) | CPM    | No persistence                                                                |
| MODEL001 | CPM    | Equation 2 in 10.1084/jem.20061278                                            |
| MODEL002 | CPM    | Equation 3 in 10.1007/978-3-7643-8123-3_7                                     |
| [MODEL003](#model003) | CPM    | Constant persistence as implemented by ExternalPotentialPlugin in CompuCell3D |
| MODEL004 | CM     | Equation 9 in 10.1371/journal.pcbi.1005991                                    |
| [MODEL005](#model005) | CPM    | Simple self-reinforcing PRW in the CPM, described below                       |
| [MODEL006](#model006) | CPM    | Persistent motion controlled by cell-intrinsic orientation under effect of continuous time noise |
| MODEL007 | CPM    | Persistent motion controlled by cell-intrinsic orientation under effect of continuous time noise and self-reenforcement of direction of motion |
| [MODEL008](#model008) | CPM    | Chemotaxis: chemotaxis CPM coupled to a PDE |

## Cellular Potts Models (CPM)

This section describes the general notation, representation, initial condition and update algorithm of the Cellular Potts Model (CPM). The specific models built within this overall framework are described in the section [CPM-based models](#cpm-based-models) below.

### Representation and notation
The CPM is implemented as a (square) lattice $G_\text{CPM}$ of width $w$ and height $h$, consisting of $n_p = w \times h$ pixels $p$ with periodic boundary conditions in all dimensions.
The identity function $\sigma(p)$ reflects by which cell the position is currently occupied. Since we are considering only single-cell models here:

$$\sigma(p) = \begin{cases}
0 & \text{unoccupied}\\
1 & \text{occupied the cell}\\
\end{cases}$$

Generally speaking, we also define the "cell type" function $\tau(p)$ as:

$$\tau(p) = \begin{cases}
0 & \sigma(p) = 0\\
1 & \text{otherwise}
\end{cases}$$

But since $\sigma(p) \in 0,1$ for our single-cell models, $\sigma(p) = \tau(p)$ for all models considered here.

### Initial condition

Starting with an empty CPM ($\sigma(p) = 0 \quad \forall \quad p \in G_\text{CPM}$), before the start of the simulation, a single cell was seeded as a collection of the following 31 pixels:

```
			[ 48, 47 ], [ 48, 48 ], [ 48, 49 ], [ 49, 46 ], [ 49, 47 ], 
			[ 49, 48 ], [ 49, 49 ], [ 49, 50 ], [ 49, 51 ], [ 50, 46 ], 
			[ 50, 47 ], [ 50, 48 ], [ 50, 49 ], [ 50, 50 ], [ 50, 51 ], 
			[ 50, 52 ], [ 51, 47 ], [ 51, 48 ], [ 51, 49 ], [ 51, 50 ], 
			[ 51, 51 ], [ 51, 52 ], [ 51, 53 ], [ 52, 47 ], [ 52, 48 ], 
			[ 52, 49 ], [ 52, 50 ], [ 52, 51 ], [ 53, 48 ], [ 53, 49 ], 
			[ 53, 50 ]
```

This list was obtained by running a single cell in [MODEL000](#model000) until equilibrium. As such, 
there was no burnin time before the start of the simulation.

### Update algorithm

#### Naive variant

Every Monte Carlo Step (MCS), $n_p = w \times h$ copy attempts are performed using the following modified Metropolis-Hastings algorithm. 
Naively speaking, the basic algorithm to perform one MCS works as follows:

- initialize $\Delta t = 0$

- while $\Delta t < n_p$:

  1. $\Delta t$++
  2. Uniformly sample a source pixel $p_s$ on $G_\text{CPM}$
  3. Uniformly sample a target pixel $p_t$ from its neighborhood defined by neighborhood function $\cal{N}^\text{MH}(p_s)$.
  4. Evaluate the difference $\Delta \mathcal{H}$ in the global system energy $\mathcal{H}$ (defined below) that would arise from the proposed update: $\sigma(p_t) \leftarrow \sigma(p_s)$
  5. Accept change $\sigma(p_t) \leftarrow \sigma(p_s)$ with probability :
  
$$P_\text{copy}(p_s \rightarrow p_t) = \begin{cases}
  1 & \Delta \mathcal{H} \leq 0\\
  e^{-\Delta \mathcal{H} / T} & \text{otherwise}
  \end{cases}$$

Where $\Delta \mathcal{H}$ is the change in the global energy or *Hamiltonian* $\mathcal{H}$ that would be induced 
by the proposed change, and the temperature parameter $T$ controls the acceptance rate of "unfavourable" copy attempts ($\Delta \mathcal{H} > 0$). See section [CPM-based models](#cpm-based-models) for details on how $\Delta \mathcal{H}$ is specified.

We'll call the abovementioned algorithm the "naive" algorithm. In practice, this is inefficient since in many cases, $\sigma(p_s) = \sigma(p_t)$ and there is no need to evaluate the corresponding $\Delta \mathcal{H}$. 

#### "edgelist" variant

In practice, we therefore use the so-called "edgelist" algorithm instead:

- initialize $\Delta t = 0$

- while $\Delta t < 1$:

  1. Create a list $\cal{E}$ of pixels $p$ for which at least one neighbor $n_p \in \cal{N}^\text{MH} (p)$ has $\sigma(n_p) \neq \sigma(p)$. Denote the number of pixels in this list $n_E$.
  2. Uniformly sample $p_s$ from $\cal{E}$
  3. $\Delta t \leftarrow \Delta t + \frac{1}{n_E}$ (the expected time this would have taken to find a $p_s \in \cal{E}$ through uniform sampling from the entire grid)
  4. Proceed with steps 3-5 of the [naive algorithm](#naive-variant).

### Overview of shared CPM implementation details

| Parameter/choice | Description                                                                 | Value |
|-----------|-----------------------------------------------------------------------------|-------|
| Lattice type | Type of lattice (square/hex/...) | square |
| $w \times h$ | Grid dimensions in horizontal and vertical direction (number of pixels) | 100 $\times$ 100 pixels |
| Boundary conditions | | periodic |
| Initial condition | | $\sigma(p) = 0$ except for a specific list of pixels initialized with $\sigma(p)=1$, see [Initial condition](#initial-condition) above. |
| Update algorithm | How is $p_s$ sampled?  | [edgelist](#edgelist-variant) |
| $\cal{N}^\text{MH}$ | Neighborhood definition used for sampling neighboring $p_s, p_t$ in the modified Metropolis-Hastings algorithm | 2nd-order (Moore) |
| $T$ | CPM temperature controlling acceptance rate of energetically unfavourable updates | T = 10 |

### Definition of time
In all CPM models, we relate the time discrete Monte Carlo Step to continuous simulation time such that 1 MCS corresponds to 1 a.t.u.


## CPM-based models

Within the overall framework described above, the individual models are further specified in terms of their Hamiltonian $H$ controlling the system dynamics.

### MODEL000

Model000 is the basis for all other models and considers a standard, single-cell CPM with only area and perimeter terms (diffusive motion without persistence). The Hamiltonian is:

$$H = H_\text{area} + H_\text{perimeter}$$

$$H_\text{area} =  \lambda_\text{area} \left (A(t) - A_\text{target} \right)^2$$

$$H_\text{perimeter} =  \lambda_\text{perim} \left ( P(t) - P_\text{target} \right)^2$$

with $A(t)$ and $P(t)$ the cell's current area and perimeter, respectively.

In addition to the [shared implementation details](#overview-of-shared-cpm-implementation-details), we specify:

| Parameter | Description                                                                 | Value |
|-----------|-----------------------------------------------------------------------------|-------|
| $\lambda_\text{area}$ | Lagrange multiplier of the area term in the Hamiltonian		              | 2.0 |
| $A_\text{target}$  | Cell target area (in # pixels) | 36|
| $\lambda_\text{perim}$ | Lagrange multiplier of the perimeter term in the Hamiltonian	| 2.0 |	           
| $P_\text{target}$  | Cell target perimeter (as defined [here](https://bmcbiophys.biomedcentral.com/articles/10.1186/s13628-015-0022-x) ) | 60 |
| $\cal{N}^\text{S}$ | Neighborhood used to define surface/perimeter | 2nd-order (Moore) |


### Shared definition of work terms

Model000 results in a single cell with only diffusive motion. The other models introduce active motility by adding a so-called "work term" to the CPM that favours copy attempts in a (static or dynamic) target direction. 

#### General work term

We define a general work term for movement along a given direction as the energy difference $\Delta H (p_\text{src} \rightarrow p_\text{tgt})$ associated with a proposed copy attempt from source pixel $p_\text{src}$ into target pixel $p_\text{tgt}$, involving cells $\sigma_\text{src}$ and $\sigma_\text{tgt}$. The general formula is:

$$\Delta H_\text{work} = \delta_\text{src} \Delta H_\text{work} (\sigma_\text{src}) + \delta_\text{tgt} \Delta H_\text{work}(\sigma_\text{tgt})$$

where $\delta_\text{src}, \delta_\text{tgt} \in 0,1$ determine whether the force acts on the "protruding" cell $\sigma_\text{src}$ and/or the "retracting" cell $\sigma_\text{tgt}$.  We describe this as `cpm_force_mode` which can be `"extension"` ($\delta_\text{src} = 1, \delta_\text{tgt} = 0$), `"retraction"` ($\delta_\text{src} = 0, \delta_\text{tgt} = 1$), `"reciprocal"` ($\delta_\text{src} = \delta_\text{tgt} = 1$).  

The definition of $\Delta H_\text{work} (\sigma)$ depends on the specific model.

#### Directional work term

Specifically we consider work terms that apply a (cell-intrinsic or extrinsic) force in a given direction. To define the work $\Delta H_\text{work} (\sigma)$ associated with movement of cell $\sigma$ along a given target direction vector, we specify: 

$$\Delta H_\text{work} (\sigma) = \Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

where:
- we rename $\Delta H_\text{work} (\sigma) = \Delta H_\text{dir} (\sigma)$ to indicate the type of work term
- $\vec{dx}(\sigma)$ is the movement of cell $\sigma$ that would be induced by the proposed copy attempt. This can be defined in several ways (`cpm_update_direction`): `"source-to-target-unnorm"` (the unnormalized vector from $s \rightarrow t$), `"source-to-target-norm"` (idem, but normalized to unit length), or `"cell-mass-displacement"` (induced movement of cell $\sigma$'s center of mass, multiplied by its current number of pixels)
- $\vec{b}(\sigma)$ is the target direction along which some extrinsic/intrinsic force acts. This and its temporal dynamics are specified in the individual models below.
- $\lambda_\text{dir}(\sigma)$ defines the magnitude of the acting force and can be cell-dependent. For the case $\sigma = 0$ (the "background" rather than a cell), we assume $\lambda_\text{dir}(\sigma=0) = 0$.

The following figure illustrates the relation between the different models (further detailed below): 

<img width="922" height="322" alt="image" src="https://github.com/user-attachments/assets/1287fd3b-c1b1-4840-8507-038a5e425da3" />

**Figure : Implementations of directional work terms.** In general, the work term $\Delta H_\text{dir}$ considers the alignment between the proposed movement vector, $\vec{d}\_x$, and the force causing the motion, $\vec{b}$. (A): In this overall framework, we obtain model000 by setting the force magnitude $\lambda_\text{dir} = 0$. (B) The simplest implementation specifies $\vec{b}$ as a unit vector in a static target direction, and yields ballistic motion (albeit with fluctuations arising from the CPM dynamics). (C,D) To achieve a persistent random walk, we update the direction of the force $\vec{b}(t)$ over time. In model005 (C), $\vec{b}(t)$ is updated based on the cell's recent displacement history, whereas in model006 (D), it is updated independently of movement history by adding Gaussian noise to the target angle. 

### MODEL003

Extends MODEL000 with a work term to favour motion in a static target direction (yielding ballistic motion in a predefined direction). Starting from the general work term as defined above: 

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

we rephrase as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{v} _ { \text{copy}} \cdot \vec{e}_\alpha \right)$$

i.e. we define:

- $\vec{dx}(\sigma) = \vec{v}_\text{copy}$ as the **unnormalized** vector from source pixel $s$ to target pixel $t$; i.e. `cpm_update_direction` = `source-to-target-unnorm`
- $\vec{b}(\sigma) = \vec{e}_\alpha = ( \cos \alpha, \sin \alpha )$, a unit vector in a (fixed) reference direction $\alpha$.

| Parameter | Description                                                                 | Value | 
|-----------|-----------------------------------------------------------------------------|-------|
| $\lambda_\text{dir}$ | Lagrange multiplier of the work term, controls the cell speed.	 | 10 |
| $\alpha$ | Angle (to the positive x-axis) of the fixed target direction              | 0 |
| `cpm_force_mode` | Does the force act on extending and/or retracting copy attempts? (see [General work term](#general-work-term))   | "extension", i.e. $\delta_\text{src} = 1, \delta_\text{tgt} = 0$ | 
| `cpm_update_direction` | How do we defined the proposal direction $\vec{dx}(\sigma)$? (see [Directional work term](#directional-work-term)) | "source-to-target-unnorm", i.e.  $\vec{dx}(\sigma)$ is the unnormalized vector $s\rightarrow t$    |

All other parameters are as described in the [general implementation details](#overview-of-shared-cpm-implementation-details) and [model000](#model000).

### MODEL005

Similar to MODEL003, but target directions can now adapt through self-reinforcement of random fluctuations, yielding a persistent random walk rather than ballistic motion. Specifically, we rephrase the reference direction in the work term:

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{v}_{\text{copy}} \cdot \tfrac{\vec{u}(t)}{ \Vert \vec{u}(t) \Vert } \right)$$


i.e. we define:
- update direction as in [MODEL003](#model003): $\vec{dx}(\sigma) = \vec{v}_\text{copy}$ as the **unnormalized** vector from source pixel $s$ to target pixel $t$; i.e. `cpm_update_direction` = `source-to-target-unnorm`
- target direction $\vec{b}(\sigma) = \tfrac{\vec{u}(t)}{ \Vert \vec{u}(t) \Vert }$

which now also gets a temporal update:

$$\vec{u}(t)= \vec{\Delta c} (\Delta t)$$

where $\vec{\Delta c}(\Delta t)$ is the (normalized) observed displacement vector of the cell centroid over the last $\Delta t$ MCS. Note: while $t < \Delta t$, $\vec{b}(\sigma) = \vec{e}_{\alpha 0}$, a unit vector in direction $\alpha_0$.


| Parameter | Description                                                                 | Value |
|-----------|-----------------------------------------------------------------------------|--------|
| $\lambda_\text{dir}$ | Lagrange multiplier of the work term, controls the cell speed.     | 10 (same as [model003](#model003) ) |
| $\Delta t$   | Time interval (in MCS) over which we evaluate the cell's recent displacement; this determines persistence time of the random walk.      | 50 MCS |
| $\alpha_0$ | Initial direction (angle to positive x-axis) | 0 |
| `cpm_force_mode` | Does the force act on extending and/or retracting copy attempts? (see [General work term](#general-work-term))   | Same as [model003](#model003): "extension", i.e. $\delta_\text{src} = 1, \delta_\text{tgt} = 0$ | 
| `cpm_update_direction` | How do we defined the proposal direction $\vec{dx}(\sigma)$? (see [Directional work term](#directional-work-term)) | Same as [model003](#model003): "source-to-target-unnorm", i.e.  $\vec{dx}(\sigma)$ is the unnormalized vector $s\rightarrow t$    |

All other parameters are as described in the [general implementation details](#overview-of-shared-cpm-implementation-details) and [model000](#model000).


### MODEL006

This simple, Langevin PRW model is similar to MODEL005, but directly evolves the cell orientation with angular noise. 

Specifically, we rephrase the work term 

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( \vec{dx}(\sigma) \cdot \vec{b}(\sigma) \right)$$

as

$$\Delta H_\text{dir} (\sigma) = \lambda_\text{dir}(\sigma) \left( A(\sigma,t)\vec{\delta c}(\sigma) \cdot \vec{e}_\alpha(\sigma,t) \right)$$

i.e. compared to MODEL003 we make $\alpha (\sigma)$ dynamic as $\alpha (\sigma, t)$ and replace the source $\rightarrow$ target vector $\vec{v}_\text{copy}$ with the cell mass displacement induced by the copy attempt:

$$\vec{dx}(\sigma) = A(\sigma,t)\vec{\delta c}(\sigma) $$

where $\vec{\delta c}(\sigma )$ is the cell centroid displacement due to the proposed update, $A(\sigma, t)$ is the cell's current area. Furthermore, we let the cell orientation $\alpha$ diffuse over time with Gaussian noise:

$$\alpha(\sigma, t) = \alpha(\sigma, t-\Delta t) + \epsilon \sqrt{\Delta t}, \quad \epsilon \sim \mathcal{N}(0,\xi^2)$$

Without loss of generality, we assume the integer $\Delta t = 1$ MCS, such that the temporal evolution equation simplifies accordingly.

$$ \vec{e}_\alpha(\sigma, t) = \left(\cos \quad \alpha(\sigma, t), \sin \quad \alpha(\sigma, t) \right)$$


| Parameter | Description                                                                 | Value |
|-----------|-----------------------------------------------------------------------------|--------|
| $\lambda_\text{dir}$ | Lagrange multiplier of the work term, controls the cell speed.     | 5  |
| $\alpha(0)$   | Initial angle (to the positive x-axis) of the target direction $\alpha$.     | 0 |
| $\xi$   | Standard deviation of noise added to the cell direction (larger $\xi$ implies lower persistence time).   | 0.09 |
| `cpm_force_mode` | Does the force act on extending and/or retracting copy attempts? (see [General work term](#general-work-term))   | Unlike [model003](#model003), now "reciprocal", i.e. $\delta_\text{src} = \delta_\text{tgt} = 1$ | 
| `cpm_update_direction` | How do we defined the proposal direction $\vec{dx}(\sigma)$? (see [Directional work term](#directional-work-term)) | Unlike [model003](#model003), now "cell-mass-displacement", i.e.   $\vec{dx}(\sigma) = A(\sigma,t)\vec{\delta c}(\sigma) $    |

All other parameters are as described in the [general implementation details](#overview-of-shared-cpm-implementation-details) and [model000](#model000).


### MODEL008
This model implements chemotaxis of a single cell in a coupled chemotactic field. Both the CPM and the chemokine grid have periodic boundaries. 

#### CPM
We use model000 along with the following work term:

$$\Delta H_\text{chem} (\sigma) = \lambda_\text{chem}(\sigma) \left( c( p_\text{tgt} ) - c( p_\text{src} ) \right)$$

where $c(p)$ is the current chemokine concentration at pixel p, and $p_\text{src},p_\text{tgt}$ are the source and target pixel of the copy attempt.

#### PDE
The chemokine is implemented on a separate (Float32) grid of the same dimensions as the CPM itself (initial condition: zero everywhere). The chemokine is described by the following PDE:

$$\frac{\partial c(p)}{\partial t} = \beta(p)  + D\nabla^2 c(p) - k_\text{decay}c(p) $$

where $D$ is the diffusion coefficient (in pixels<sup>2</sup>/MCS), $k_\text{decay}$ the degradation rate per MCS, and $\beta(p)$ the chemokine production:

$$\beta(p) = \begin{cases}
k_\text{prod} & p = p_\text{chem source}\\
0 & \text{otherwise}
\end{cases} $$

The PDE is implemented using a finite difference scheme (https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Finite_differences) with h = 1, and solved with $N_{ds}=10$ steps after every MCS in the CPM (where $D$, $k_\text{prod}$ and $k_\text{decay}$ have to be divided by $N_{ds}$ to maintain the same effective rates per MCS).





| Parameter | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| $\lambda_\text{chem}$ | As Model003, the Lagrange multiplier controls sensitivity to the chemokine gradient.     |
| $p_\text{chem source}$ | Location of the point source of the chemokine |
| $k_\text{prod}$ | Units of chemokine produced per MCS at the point source |
| $k_\text{decay}$ | Fraction of chemokine that decays each MCS at a given location |
| $D$ | diffusion coefficient in pixels<sup>2</sup>/MCS) |
| $N_{ds}$ | number of PDE steps performed after every MCS |
| `cpm_force_mode` | "extension", i.e. $\delta_\text{src} = 1, \delta_\text{tgt} = 0$ (see "work term")              |


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


