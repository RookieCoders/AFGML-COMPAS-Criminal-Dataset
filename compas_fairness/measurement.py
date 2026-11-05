"""Class-conditional measurement inversion, with explicit compatibility checks."""
from itertools import product
import numpy as np

TOL = 1e-10


def invert(joint: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    """joint[d, observed_y] -> hypothetical joint[d, latent_y]. Never repair invalid cells."""
    j = np.asarray(joint, dtype=float)
    if not np.isfinite([alpha, beta]).all() or not (0 <= alpha <= 1 and 0 <= beta <= 1):
        raise ValueError('invalid_error_probability')
    det = 1-alpha-beta
    if det <= 1e-8:
        raise ValueError('uninformative_or_unstable_matrix')
    if j.shape != (2, 2) or not np.isfinite(j).all() or j.min() < -TOL or abs(j.sum()-1)>TOL:
        raise ValueError('invalid_observed_joint')
    q = j[:, 1].sum()
    pi = (q-alpha)/det
    if pi < -TOL or pi > 1+TOL:
        raise ValueError('invalid_latent_prevalence')
    latent = np.column_stack(((1-beta)*j[:,0]-beta*j[:,1],
                               (1-alpha)*j[:,1]-alpha*j[:,0])) / det
    if latent.min() < -TOL:
        raise ValueError('negative_latent_joint')
    matrix = np.array([[1-alpha,beta],[alpha,1-beta]])
    if not np.allclose(latent @ matrix.T, j, atol=TOL, rtol=0) or abs(latent.sum()-1)>TOL:
        raise ValueError('reconstruction_failure')
    return latent


def rates(joint):
    denom = joint.sum(axis=0)
    return np.divide(joint[1], denom, out=np.full(2,np.nan), where=denom > TOL)  # FPR, TPR


def eo(joints):
    r = np.array([rates(j) for j in joints])
    if not np.isfinite(r).all() or len(r)<2:
        return np.nan
    return float(np.ptp(r, axis=0).max())


def observed_joint(y, decision):
    """Supports deterministic decisions or postprocessor selection probabilities."""
    y, d = np.asarray(y), np.asarray(decision)
    if y.ndim!=1 or d.ndim!=1 or y.shape!=d.shape or len(y)==0 or not np.isin(y,[0,1]).all() or not np.isfinite(d).all() or np.any((d<0)|(d>1)):
        raise ValueError('invalid_decisions_or_labels')
    return np.array([[np.mean((1-d)*(y==0)),np.mean((1-d)*(y==1))],
                     [np.mean(d*(y==0)),np.mean(d*(y==1))]])


def scenarios(groups, maximum=.2, step=.025, equal=False):
    """Full four-dimensional grid for two groups; prespecified race/sex contrast slice otherwise."""
    if not (np.isfinite(maximum) and 0<=maximum<=1 and np.isfinite(step) and step>0):
        raise ValueError('invalid_grid_bounds')
    v = np.round(np.arange(0, maximum+1e-12, step), 10)
    if equal:
        return np.array([[[a,b]]*len(groups) for a,b in product(v,v)])
    # For >2 groups the two noise profiles vary by race (or alternating group order).
    contrast = [int('Caucasian' in g) for g in groups]
    if len(groups)==2: contrast=[0,1]
    return np.array([[[a,b] if k==0 else [c,d] for k in contrast]
                     for a,b,c,d in product(v,v,v,v)])


def sweep(joints, scenario_array):
    """Vectorized common feasibility across every compared method and group.

    joints shape M,G,D,Y; scenario_array shape S,G,(alpha,beta).
    Returns EO, common mask, reason code, and group FPR/TPR for every scenario.
    """
    j = np.asarray(joints, dtype=float)
    if (j.ndim!=4 or j.shape[-2:]!=(2,2) or not np.isfinite(j).all() or
        j.min() < -TOL or not np.allclose(j.sum(axis=(-2,-1)),1,atol=TOL,rtol=0)):
        raise ValueError('invalid_observed_joints')
    scenario_array=np.asarray(scenario_array,dtype=float)
    if scenario_array.ndim!=3 or scenario_array.shape[1:]!=(j.shape[1],2) or j.shape[1]<2:
        raise ValueError('invalid_scenario_shape_or_group_count')
    a,b = scenario_array[:,:,0], scenario_array[:,:,1]
    det=1-a-b
    safe=np.where(det>1e-8,det,np.nan)
    z0=((1-b[:,None,:,None])*j[None,:,:,:,0]-b[:,None,:,None]*j[None,:,:,:,1])/safe[:,None,:,None]
    z1=((1-a[:,None,:,None])*j[None,:,:,:,1]-a[:,None,:,None]*j[None,:,:,:,0])/safe[:,None,:,None]
    z=np.stack([z0,z1],axis=-1) # S M G D Y
    bad_params=(~np.isfinite(scenario_array).all(axis=(1,2)) | (scenario_array<0).any(axis=(1,2)) |
                (scenario_array>1).any(axis=(1,2)) | (det<=1e-8).any(axis=1))
    bad_cells=(z < -TOL).any(axis=(1,2,3,4))
    q=j[...,1].sum(axis=-1)
    pi=(q[None]-a[:,None])/safe[:,None]
    bad_prevalence=((pi < -TOL)|(pi>1+TOL)).any(axis=(1,2))
    recon0=(1-a[:,None,:,None])*z0+b[:,None,:,None]*z1
    recon1=a[:,None,:,None]*z0+(1-b[:,None,:,None])*z1
    bad_normalization=(np.abs(z.sum(axis=(3,4))-1)>TOL).any(axis=(1,2))
    bad_reconstruction=bad_normalization | (np.abs(recon0-j[None,:,:,:,0])>TOL).any(axis=(1,2,3)) | (np.abs(recon1-j[None,:,:,:,1])>TOL).any(axis=(1,2,3))
    denom=z.sum(axis=3)
    r=np.divide(z[:,:,:,1,:],denom,out=np.full_like(denom,np.nan),where=denom>TOL)
    undefined=(~np.isfinite(r)).any(axis=(1,2,3))
    reason=np.full(len(a),'ok',dtype=object)
    for mask,label in [(undefined,'undefined_denominator'),(bad_reconstruction,'reconstruction_failure'),
                       (bad_cells,'negative_latent_joint'),(bad_prevalence,'invalid_latent_prevalence'),(bad_params,'invalid_matrix')]:
        reason[mask]=label
    valid=reason=='ok'
    gaps=np.ptp(r,axis=2).max(axis=2)
    gaps[~valid]=np.nan
    r[~valid]=np.nan
    return gaps,valid,reason,r


def validate_variable_elimination():
    """Small measurement BN, queried by VE and independently enumerated.

    X is binary pre-outcome covariate; D is a stochastic decision based on A,X.
    Graph encodes tildeY independent of X,D conditional on Ystar,A.
    """
    from pgmpy.models import DiscreteBayesianNetwork
    from pgmpy.factors.discrete import TabularCPD
    from pgmpy.inference import VariableElimination
    bn=DiscreteBayesianNetwork([('A','X'),('A','Ystar'),('X','Ystar'),('A','D'),('X','D'),('A','Ytilde'),('Ystar','Ytilde')])
    px=[.3,.6]; py=[.15,.5,.3,.75]; pd=[.1,.8,.2,.7]
    # Evidence order A,Ystar: label-one probabilities alpha0,1-beta0,alpha1,1-beta1.
    pt=[.05,.9,.15,.95]
    bn.add_cpds(TabularCPD('A',2,[[.5],[.5]]),
        TabularCPD('X',2,[1-np.array(px),px],evidence=['A'],evidence_card=[2]),
        TabularCPD('Ystar',2,[1-np.array(py),py],evidence=['A','X'],evidence_card=[2,2]),
        TabularCPD('D',2,[1-np.array(pd),pd],evidence=['A','X'],evidence_card=[2,2]),
        TabularCPD('Ytilde',2,[1-np.array(pt),pt],evidence=['A','Ystar'],evidence_card=[2,2]))
    assert bn.check_model()
    query=VariableElimination(bn).query(['Ystar'],evidence={'A':1,'Ytilde':1,'D':1},show_progress=False).values
    enum=np.zeros(2)
    for x,z in product(range(2),repeat=2):
        enum[z]+=(px[1] if x else 1-px[1])*(py[2+x] if z else 1-py[2+x])*pd[2+x]*pt[2+z]
    enum/=enum.sum()
    np.testing.assert_allclose(query,enum,atol=1e-12)
    return {'ve':query.tolist(),'enumeration':enum.tolist(),'max_error':float(abs(query-enum).max())}
