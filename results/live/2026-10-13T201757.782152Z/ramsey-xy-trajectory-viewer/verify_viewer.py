from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
 page=browser.new_page(viewport={'width':1450,'height':1050},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((root/'index.html').read_text(),wait_until='load',timeout=30000)
 page.wait_for_function('window.__viewerReady === true',timeout=30000)
 page.wait_for_timeout(700)
 print('INITIAL',page.evaluate('window.__lastFrame'))
 print('ERRORBOX',page.locator('#errorBox').inner_text())
 print('VECTOR_ELEMENTS',page.locator('#scene polyline').count(),page.locator('#scene circle').count())
 page.screenshot(path=str(root/'previews/interactive_desktop.png'),full_page=False)
 for mode in ['worldline','four','slice']:
  page.select_option('#mode',mode)
  page.wait_for_function(f"window.__lastFrame.mode === '{mode}'")
  page.wait_for_timeout(350)
  if mode=='four':
   page.locator('#rx').fill('20');page.locator('#rx').dispatch_event('input')
   page.wait_for_timeout(350)
   page.evaluate('window.scrollTo(0,0)')
   page.screenshot(path=str(root/'previews/oblique_4d_projection.png'),full_page=False)
 page.click('#interpolate')
 page.evaluate("document.getElementById('time').value='4.300';document.getElementById('time').dispatchEvent(new Event('input'))")
 page.wait_for_function('Math.abs(window.__lastFrame.tau-4.3)<1e-6')
 print('INTERPOLATED',page.evaluate('window.__lastFrame'))
 print('CURRENTTABLE',page.locator('#currentRows').inner_text()[:400])
 # Off-grid points must have no shot counts.
 assert 'Guide only' in page.locator('#currentRows').inner_text()
 page.click('#interpolate')
 page.click('#playButton')
 page.wait_for_function('Math.abs(window.__lastFrame.tau-0.004)<1e-8')
 assert page.evaluate('window.__lastFrame.point_count')==2
 page.click('#playButton')
 page.click('#allButton')
 page.wait_for_function('window.__lastFrame.point_count===26')
 page.locator('.qubit-filter[value="144"]').uncheck()
 page.wait_for_function('window.__lastFrame.visible_series===4')
 assert page.evaluate('window.__lastFrame.point_count')==13
 page.locator('.qubit-filter[value="144"]').check()
 with page.expect_download() as down:
  page.click('#exportSVG')
 down.value.save_as(str(root/'previews/native_scene.svg'))
 with page.expect_download() as down:
  page.click('#exportImage')
 down.value.save_as(str(root/'previews/native_scene.png'))
 page.set_viewport_size({'width':390,'height':844})
 page.wait_for_timeout(400)
 page.screenshot(path=str(root/'previews/interactive_mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+2')
 require_no_errors=not errors
 print('BROWSER_ERRORS',errors)
 (root/'browser_validation.json').write_text(json.dumps({'desktop_checked':True,'mobile_layout_checked':True,'three_projections_checked':True,'interpolation_toggle_checked':True,'measured_only_playback_checked':True,'qubit_filter_checked':True,'no_prestart_extrapolation_checked':True,'svg_export_checked':True,'png_export_checked':True,'rendering':'native SVG, no WebGL','console_page_errors':errors},indent=2))
 browser.close()
 if errors:raise RuntimeError('Browser script errors')
