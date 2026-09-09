"""Convert the measured 3rd-difference autocorrelation into a noise correlation rho,
and work out where in the speed distribution a 25 ms offset is even detectable."""
import numpy as np, json

c = np.array([1.0, -3.0, 3.0, -1.0])          # 3rd-difference kernel
def acf_of_filtered(rho, L):
    """ACF at lag L of D3 when the underlying label noise is AR(1) with corr rho."""
    def g(k): return rho ** abs(k)            # unit-variance AR(1) autocovariance
    def cov(shift):
        s = 0.0
        for j in range(4):
            for k in range(4):
                s += c[j] * c[k] * g((j + shift) - k)
        return s
    return cov(L) / cov(0)

m = json.load(open('/work/experiments/e08_label_noise/result.json'))
tgt = np.array([m['D3_acf_lag1'], m['D3_acf_lag2'], m['D3_acf_lag3']])
grid = np.linspace(0.0, 0.95, 1901)
err = np.array([np.sum((np.array([acf_of_filtered(r,1),acf_of_filtered(r,2),acf_of_filtered(r,3)]) - tgt)**2) for r in grid])
rho = float(grid[np.argmin(err)])
fit = [round(acf_of_filtered(rho,L),4) for L in (1,2,3)]
print("MEASURED D3 acf      :", list(tgt))
print("WHITE-NOISE predicted: [-0.75, 0.3, -0.05]")
print(f"BEST-FIT AR(1) rho   : {rho:.3f}   -> predicted acf {fit}")

# variance inflation of a mean-of-n estimator under AR(1) vs white
def inflation(rho, n):
    k = np.arange(1, n)
    return 1.0 + 2.0 * np.sum((1 - k / n) * rho ** k)
print("VAR INFLATION vs white  n=5: %.2fx  n=10: %.2fx  n=20: %.2fx"
      % (inflation(rho,5), inflation(rho,10), inflation(rho,20)))

# detectability: a tau ms offset shows as tau*v pixels along track
sc = m['sigma_c_from_3rd_diff_px']
sp = m['speed_px_per_s']
print(f"\nsigma_c = {sc} px   (3rd-difference estimator)")
for tau_ms in (5, 10, 25):
    print(f"  tau = {tau_ms:>2} ms displacement in px, and as a multiple of sigma_c:")
    for name in ('median','p90','p99'):
        d = sp[name] * tau_ms * 1e-3
        print(f"     v={sp[name]:>7.1f} px/s ({name:>6}): {d:6.2f} px = {d/sc:5.2f} sigma_c")
json.dump(dict(rho_ar1=round(rho,3), acf_fit=fit, sigma_c_px=sc,
               var_inflation={'n5':round(float(inflation(rho,5)),3),
                              'n10':round(float(inflation(rho,10)),3),
                              'n20':round(float(inflation(rho,20)),3)}),
          open('/work/experiments/e08_label_noise/ar1.json','w'), indent=1)
