"""Run directly: python tests/browser_smoke.py. Uses an isolated server/database."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
output=Path(os.environ.get('BROWSER_OUTPUT','work/browser'))
output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as directory:
    env={**os.environ,'DATABASE_PATH':str(Path(directory)/'browser.db'),'OPENAI_API_KEY':'','X_BEARER_TOKEN':'','X_LIVE_ENABLED':'false'}
    server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8001'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with socket.create_connection(('127.0.0.1',8001),timeout=.1):break
            except OSError:time.sleep(.1)
        else:raise RuntimeError('Test server did not start')
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.add_init_script("localStorage.setItem('telyclaw.language','en')")
            page.goto('http://127.0.0.1:8001')
            page.locator('.topic').first.wait_for()
            assert int(page.locator('#posts').inner_text())>0
            assert page.locator('.topic').count()>=3
            page.screenshot(path=str(output/'dashboard.png'),full_page=True)
            external=[]
            page.on('request',lambda request:external.append(request.url) if request.url.startswith(('https://api.x.com','https://api.twitter.com')) else None)
            page.locator('#mode').select_option('live')
            page.wait_for_function("document.getElementById('live-status').textContent.includes('X_BEARER_TOKEN')")
            page.locator('#fetch-x').click()
            page.wait_for_function("document.getElementById('live-status').textContent.includes('No X request was made')")
            page.locator('#analyze').click()
            page.wait_for_function("document.getElementById('posts').textContent==='0'")
            assert page.locator('.topic').count()==0
            assert not external
            page.screenshot(path=str(output/'live-missing-credentials.png'),full_page=True)
            page.locator('#mode').select_option('demo')
            page.locator('#analyze').click()
            page.locator('.topic').first.wait_for()
            page.locator('#window').select_option('1')
            assert page.locator('.topic').count()==0
            page.locator('#analyze').click()
            page.locator('.topic').first.wait_for()
            page.locator('#generate').click()
            page.locator('#draft-text').wait_for()
            assert page.locator('.angle').count()==3
            assert not page.locator('#export-draft').is_visible()
            text='AI growth needs human judgment. Turn a signal into one customer question, test a useful perspective, and measure qualified conversations.'
            page.locator('#draft-text').fill(text)
            page.locator('#approve-draft').click()
            page.locator('#export-draft').wait_for(state='visible')
            assert page.locator('#draft-status').text_content()=='approved'
            with page.expect_download() as download:
                page.locator('#export-draft').click()
            assert Path(download.value.path()).read_text()==text
            page.screenshot(path=str(output/'content-studio.png'),full_page=True)
            page.locator('#draft-text').fill('Changed text needs a fresh human review.')
            assert not page.locator('#export-draft').is_visible()
            page.locator('#save-draft').click()
            page.wait_for_function("document.getElementById('draft-status').textContent==='draft'")
            assert not page.locator('#export-draft').is_visible()
            page.locator('[data-tab="sources"]').click()
            page.locator('#handle').fill('demo_newsource')
            page.locator('#add-account button').click()
            page.get_by_text('@demo_newsource',exact=True).wait_for()
            # Import through the real file input and analyze a separate dataset.
            from datetime import datetime,timezone
            upload={'posts':[{'id':str(i),'handle':'new_source','text':text+' Customer insight '+str(i),'created_at':datetime.now(timezone.utc).isoformat()} for i in range(3)]}
            page.locator('#import-file').set_input_files({'name':'posts.json','mimeType':'application/json','buffer':json.dumps(upload).encode()})
            page.locator('#import').click()
            page.wait_for_function("document.getElementById('import-count').textContent.startsWith('3 imported')")
            page.locator('[data-tab="opportunities"]').click()
            page.locator('#mode').select_option('imported')
            page.locator('#analyze').click()
            page.wait_for_function("document.getElementById('posts').textContent==='3'")
            assert 'User-imported' in page.locator('#provenance').inner_text()
            # Persisted state survives reload.
            page.reload()
            page.locator('.topic').first.wait_for()
            assert page.locator('#draft-count').inner_text()=='1'
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(output/'mobile.png'),full_page=True)
            assert not errors,errors
            browser.close()
            print('PASS: desktop/mobile, analysis, 3 angles, edit, approval, export, approval invalidation, account creation, JSON import, persistence; no browser JS errors.')
    finally:
        server.terminate()
        server.wait(timeout=10)
