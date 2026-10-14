#!/usr/bin/env python3
"""Build an offline four-coordinate visualization from the supplied measured CSV.

No network, IBM Runtime, credentials, or QPU operations are used.
Run with --video to also generate an explicitly illustrative MP4 preview.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np

ROOT = Path(__file__).resolve().parent
CONDITIONS = ('plain', 'echo', 'window c0', 'window c1')
LABELS = {'plain': 'Plain Ramsey', 'echo': 'Echo', 'window c0': 'Window c0', 'window c1': 'Window c1'}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_data() -> dict:
    """Verify the supplied table hashes and all plotted numerical identities."""
    manifest = json.loads((ROOT / 'data/source_manifest.json').read_text())
    references = {p['path']: p for p in manifest['files']}
    for name in ('ramsey_observations.csv', 'ramsey_fits_model_dependent.csv'):
        p = ROOT / 'data' / name
        require(hashlib.sha256(p.read_bytes()).hexdigest() == references['data/' + name]['sha256'], 'Input hash mismatch: ' + name)
    with (ROOT / 'data/ramsey_observations.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    with (ROOT / 'data/ramsey_fits_model_dependent.csv').open(newline='') as f:
        fit = {r['condition']: r for r in csv.DictReader(f)}
    series = []
    for condition in CONDITIONS:
        for qubit, role in ((136, 'A'), (144, 'B')):
            observations = sorted((r for r in rows if r['condition'] == condition and int(r['physical_qubit']) == qubit), key=lambda r: float(r['executed_idle_us']))
            require(bool(observations), 'Missing series')
            points = []
            for r in observations:
                require(r['timing_qualified'] == 'True', 'Unqualified X/Y timing')
                kx, nx, ky, ny = (int(r[k]) for k in ('x_zero', 'x_shots', 'y_zero', 'y_shots'))
                require(nx > 0 and ny > 0 and 0 <= kx <= nx and 0 <= ky <= ny, 'Invalid counts')
                x, y = 2*kx/nx-1, 2*ky/ny-1
                radius, phase = math.hypot(x, y), math.atan2(y, x)
                for observed, name in ((x, 'x_exp'), (y, 'y_exp'), (radius, 'observed_radius'), (phase, 'observed_principal_phase_rad')):
                    require(abs(observed-float(r[name])) < 2e-14, 'Numerical inconsistency: ' + name)
                points.append(dict(t=float(r['executed_idle_us']), x=x, y=y, r=radius, phase=phase, kx=kx, nx=nx, ky=ky, ny=ny,
                                   xlow=float(r['x_jeffreys95_low']), xhigh=float(r['x_jeffreys95_high']), ylow=float(r['y_jeffreys95_low']), yhigh=float(r['y_jeffreys95_high'])))
            ff = fit[condition + '/' + role]
            series.append(dict(condition=condition, qubit=qubit, role=role, points=points, alias_resolved=ff['alias_resolved']=='True', compatible_aliases_mhz=[float(x) for x in ff['compatible_aliases_mhz'].split(';')]))
    require(sum(len(s['points']) for s in series) == 26, 'Expected 26 observed coordinate pairs')
    times = sorted({p['t'] for s in series for p in s['points']})
    require(times == [0.004, 3.604, 5.604, 7.604], 'Unexpected time grid')
    values = np.array([[p['x'],p['y'],p['r'],p['t']] for s in series for p in s['points']])
    lo, hi = values.min(axis=0), values.max(axis=0)
    data = dict(schema='reality-ripple-four-coordinate/1', source_commit=manifest['source_commit'], source_kind='supplied derived-data archive', input_csv_sha256=hashlib.sha256((ROOT/'data/ramsey_observations.csv').read_bytes()).hexdigest(),
                coordinate_order=['X','Y','R','executed_idle_us'], radius_is_derived=True, full_state_tomography=False,
                times_us=times, scaling={'center': ((hi+lo)/2).tolist(), 'halfspan': ((hi-lo)/2).tolist()}, series=series)
    return data


def interpolate(s: dict, tau: float) -> tuple[float,float,float] | None:
    """Illustrative X/Y interpolation only; no extrapolation, phase unwrapping or fit."""
    points = s['points']
    if tau < points[0]['t']-1e-10 or tau > points[-1]['t']+1e-10:
        return None
    ts = np.array([p['t'] for p in points])
    x = float(np.interp(tau, ts, [p['x'] for p in points]))
    y = float(np.interp(tau, ts, [p['y'] for p in points]))
    return x, y, math.hypot(x, y)


def validate_interpolation(data: dict) -> dict:
    endpoint_error = 0.0
    radius_error = 0.0
    for s in data['series']:
        for p in s['points']:
            found = interpolate(s, p['t'])
            require(found is not None, 'Missing measured endpoint')
            endpoint_error = max(endpoint_error, max(abs(a-b) for a,b in zip(found,(p['x'],p['y'],p['r']))))
        for t in np.linspace(s['points'][0]['t'],s['points'][-1]['t'],101):
            x,y,r = interpolate(s,float(t))
            radius_error=max(radius_error,abs(r-math.hypot(x,y)))
        require(interpolate(s,s['points'][0]['t']-.001) is None, 'Extrapolation before first point')
        require(interpolate(s,s['points'][-1]['t']+.001) is None, 'Extrapolation after last point')
    require(endpoint_error < 2e-14, 'Connector changed observations')
    return dict(observations=26, trajectories=8, unique_executed_idle_settings=4, all_counts_checked=True, input_hashes_verified=True,
                maximum_connector_endpoint_error=endpoint_error, maximum_derived_radius_error=radius_error, extrapolation='forbidden',
                uncertainties='Source marginal Jeffreys intervals retained only at acquired points; no interpolated uncertainty',
                python=platform.python_version(), numpy=np.__version__, visualization_engine='native SVG / JavaScript; no WebGL')


def build_html(data: dict) -> None:
    jsdata=json.dumps(data,ensure_ascii=False,allow_nan=False).replace('</','<\\/')
    html=(ROOT/'viewer_template.html').read_text().replace('__MEASUREMENTS__',jsdata)
    require('__MEASUREMENTS__' not in html and '__PLOTLY_LIBRARY__' not in html, 'Unfilled template')
    (ROOT/'index.html').write_text(html)
    (ROOT/'data/measurements_4d.json').write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def draw_previews(data: dict, video: bool=False) -> None:
    """Each chart has one 3D axes; use Matplotlib's default colors and styling."""
    import os, tempfile
    os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'reality-ripple-mpl'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, FFMpegWriter
    from matplotlib.ticker import MaxNLocator
    (ROOT/'previews').mkdir(exist_ok=True)
    for mode in ('spacetime','four_coordinates'):
        fig=plt.figure(figsize=(11,8.6))
        ax=fig.add_subplot(111,projection='3d')
        for s in data['series']:
            pts=s['points']; times=np.linspace(pts[0]['t'],pts[-1]['t'],70)
            coords=np.array([interpolate(s,float(t)) for t in times])
            actual=np.array([[p['x'],p['y'],p['r']] for p in pts])
            z=times if mode=='spacetime' else coords[:,2]
            ax.plot(coords[:,0],coords[:,1],z,linestyle='--',linewidth=1.5,label=f"{LABELS[s['condition']]} / Q{s['qubit']}")
            # Use a single points trace per series without a manually selected palette.
            ax.scatter(actual[:,0],actual[:,1],[p['t'] for p in pts] if mode=='spacetime' else actual[:,2],s=35,marker='o' if s['qubit']==136 else 'D',depthshade=False)
        ax.set_xlabel('X = 2 pₓ(0) − 1',labelpad=12)
        ax.set_ylabel('Y = 2 pᵧ(0) − 1',labelpad=12)
        ax.set_zlabel('Executed idle τ (μs)' if mode=='spacetime' else 'R = √(X² + Y²), derived',labelpad=12)
        ax.set_xlim(.85,1.025);ax.set_ylim(-.13,.16)
        if mode=='spacetime':ax.set_zlim(0,7.9);ax.set_zticks(data['times_us'])
        else:ax.set_zlim(.85,1.025);ax.zaxis.set_major_locator(MaxNLocator(5))
        ax.view_init(elev=24,azim=43)
        ax.set_box_aspect((1,1.12,1.1))
        fig.suptitle('Reality Ripple · measured local-coherence trajectories',fontsize=18,y=.975)
        subtitle='Spacetime view: X, Y, executed idle τ. Radius and phase are derived.' if mode=='spacetime' else 'Spatial coordinates: X, Y, R. Time is the fourth coordinate in the interactive animation.'
        fig.text(.5,.935,subtitle,ha='center',fontsize=10)
        ax.legend(loc='upper left',bbox_to_anchor=(-.08,.98),fontsize=8.5,frameon=False)
        fig.text(.04,.055,'26 measured X/Y pairs · 8 trajectories · IBM Fez · 13 October 2026',fontsize=10)
        fig.text(.04,.032,'Markers: acquired points. Dashed connections: illustrative interpolation only; no phase unwrapping.',fontsize=9)
        fig.text(.04,.013,'R is not independently measured Z. Each time setting uses separately prepared circuits.',fontsize=9)
        fig.subplots_adjust(left=.04,right=.93,bottom=.09,top=.9)
        fig.savefig(ROOT/f'previews/{mode}.png',dpi=190)
        fig.savefig(ROOT/f'previews/{mode}.svg')
        plt.close(fig)
    if not video:
        return
    # An illustrative animated connector view, explicitly labeled at every frame.
    fig=plt.figure(figsize=(10.8,8.0))
    ax=fig.add_subplot(111,projection='3d')
    ax.set_xlim(.85,1.025);ax.set_ylim(-.14,.17);ax.set_zlim(.85,1.025)
    ax.set_xlabel('X',labelpad=9);ax.set_ylabel('Y',labelpad=9);ax.set_zlabel('R = √(X²+Y²), derived',labelpad=9)
    ax.set_box_aspect((1,1.13,1.1));ax.view_init(elev=25,azim=44)
    objects=[]
    for s in data['series']:
        # Empty measured traces take the default palette; no explicit colors.
        line,=ax.plot([],[],[],linestyle='--',linewidth=1.7,marker='o' if s['qubit']==136 else 'D',markersize=4,label=f"{LABELS[s['condition']]} / Q{s['qubit']}")
        objects.append(line)
    ax.legend(loc='upper left',bbox_to_anchor=(-.12,.99),fontsize=8,frameon=False)
    title=fig.suptitle('',fontsize=18,y=.975)
    status=fig.text(.5,.925,'',ha='center',fontsize=11)
    fig.text(.05,.055,'Fourth coordinate: executed idle τ, animated at a slowed display rate.',fontsize=10)
    fig.text(.05,.032,'Dashed lines and intermediate cursor positions are visual guides, not measured evolution.',fontsize=9)
    fig.text(.05,.012,'Only 26 coordinate pairs are observed. R is derived. Echo/window frequency aliases remain unresolved.',fontsize=9)
    fig.subplots_adjust(left=.035,right=.93,bottom=.1,top=.895)
    frames=[]
    tt=data['times_us']
    for i,t in enumerate(tt):
        frames.extend([t]*12)
        if i<len(tt)-1:frames.extend(np.linspace(t,tt[i+1],27)[1:-1].tolist())
    frames.extend([tt[-1]]*15)
    def update(frame):
        tau=frames[frame]
        exact=any(abs(tau-t)<1e-9 for t in tt)
        title.set_text(f'Reality Ripple · τ = {tau:.3f} μs')
        status.set_text('ACQUIRED TIME SETTING' if exact else 'ILLUSTRATIVE CONNECTOR · NOT A MEASUREMENT')
        for s,line in zip(data['series'],objects):
            first=s['points'][0]['t']
            if tau<first-1e-9:
                line.set_data_3d([],[],[]);continue
            # Each frame connects only acquired past points plus a marked current guide.
            times=[p['t'] for p in s['points'] if p['t']<=tau+1e-9]
            if not any(abs(tau-t)<1e-9 for t in times):times.append(tau)
            coords=np.array([interpolate(s,float(t)) for t in times])
            line.set_data_3d(coords[:,0],coords[:,1],coords[:,2])
            line.set_markevery(list(range(len(times)-1))+([len(times)-1] if exact else []))
        # A small camera orbit is display motion only; the time readout stays explicit.
        ax.view_init(elev=25,azim=44+12*frame/(len(frames)-1))
        return objects+[title,status]
    movie=FuncAnimation(fig,update,frames=len(frames),interval=1000/12,blit=False)
    movie.save(ROOT/'previews/reality_ripple_4d_time.mp4',writer=FFMpegWriter(fps=12,bitrate=1700,codec='libx264',extra_args=['-pix_fmt','yuv420p','-movflags','+faststart']),dpi=100)
    plt.close(fig)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',action='store_true',help='Generate a clearly labeled illustrative animated preview')
    args=parser.parse_args()
    data=load_data();audit=validate_interpolation(data)
    build_html(data);draw_previews(data,args.video)
    (ROOT/'validation.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('Built standalone 4D explorer and static previews from 26 verified coordinate pairs.')
    if args.video:print('Created a time-animated MP4; interpolated frames are explicitly labeled.')

if __name__=='__main__':
    main()
