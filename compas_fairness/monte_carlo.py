"""Monte Carlo precision for binomial simulation outcomes; not sampling intervals for EO."""
import math
from scipy.stats import norm


def wilson(successes,total,confidence=.95):
    """Wilson interval and plug-in Monte Carlo SE for independent repetitions."""
    if total<=0 or not 0<=successes<=total or not 0<confidence<1:
        raise ValueError('invalid_binomial_counts_or_confidence')
    p=successes/total;z=norm.ppf((1+confidence)/2)
    center=(p+z*z/(2*total))/(1+z*z/total)
    half=z*math.sqrt(p*(1-p)/total+z*z/(4*total**2))/(1+z*z/total)
    return {'fraction':p,'mc_se':math.sqrt(p*(1-p)/total),'mc_low':max(0,center-half),'mc_high':min(1,center+half)}
