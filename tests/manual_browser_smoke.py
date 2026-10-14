"""User-driven import → analysis → approval/export; isolated DB, no external traffic."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import socket
import subprocess
import sys
import tempfile
import time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def run():
    with tempfile.TemporaryDirectory() as directory:
        env={**os.environ,'DATABASE_PATH':str(Path(directory)/'manual.db'),
            'X_BEARER_TOKEN':'','X_LIVE_ENABLED':'false','OPENAI_API_KEY':''}
        server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8003'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1',8003),timeout=.1):break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Manual test server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1440,'height':1100})
                external=[];errors=[]
                def local_only(route):
                    if route.request.url.startswith('http://127.0.0.1:8003/'):
                        route.continue_()
                    else:
                        external.append(route.request.url);route.abort()
                page.route('**/*',local_only)
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto('http://127.0.0.1:8003')
                page.locator('.topic').first.wait_for()
                page.locator('[data-tab="sources"]').click()
                when=(datetime.now(timezone(timedelta(hours=8)))-timedelta(minutes=20)).strftime('%Y-%m-%dT%H:%M')
                def fill(identifier,author,text):
                    page.locator('#manual-url').fill(f'https://x.com/{author}/status/{identifier}')
                    page.locator('#manual-handle').fill('@'+author)
                    page.locator('#manual-text').fill(text)
                    page.locator('#manual-time').fill(when)
                fill('1001','test_author','TEST INPUT: AI agents need human approval for content workflows.')
                page.locator('#save-manual').click()
                page.wait_for_function("document.getElementById('manual-count').textContent.startsWith('1 saved')")
                assert 'N/A' in page.locator('#manual-list').inner_text()
                fill('1001','test_author','This duplicate must not overwrite the saved text.')
                page.locator('#save-manual').click()
                page.wait_for_function("document.getElementById('manual-result').textContent.includes('already been')")
                assert page.locator('#manual-text').input_value().startswith('This duplicate')
                fill('1002','other_author','TEST INPUT: Human approval and ownership make AI agent workflows useful for marketing.')
                page.locator('#manual-likes').fill('0')
                page.locator('#save-manual').click()
                page.wait_for_function("document.getElementById('manual-count').textContent.startsWith('2 saved')")
                page.locator('[data-tab="opportunities"]').click()
                page.locator('#mode').select_option('manual')
                page.locator('#analyze').click()
                page.wait_for_function("document.getElementById('posts').textContent==='2'")
                assert 'Too few' in page.locator('#sample-warning').inner_text()
                assert page.locator('#accounts').inner_text()=='2'
                page.locator('#detail details').evaluate('(element)=>element.open=true')
                assert page.locator('#detail a').first.get_attribute('href').startswith('https://x.com/')
                assert 'N/A' in page.locator('#detail').inner_text()
                output=ROOT/'work/browser';output.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(output/'manual-opportunities.png'),full_page=True)
                page.locator('#generate').click()
                page.locator('#draft-text').wait_for()
                assert page.locator('.angle').count()==3
                assert page.locator('#editor .source-links a').count()>0
                assert not page.locator('#export-draft').is_visible()
                page.locator('#draft-text').fill('AI growth needs useful customer insight and human judgment. What would you test first?')
                page.locator('#approve-draft').click()
                page.locator('#export-draft').wait_for(state='visible')
                with page.expect_download() as download:
                    page.locator('#export-draft').click()
                assert Path(download.value.path()).read_text().startswith('AI growth needs')
                page.reload()
                page.locator('.topic').first.wait_for()
                assert page.locator('#mode').input_value()=='demo'
                page.locator('[data-tab="sources"]').click()
                assert page.locator('#manual-count').inner_text().startswith('2 saved')
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                page.screenshot(path=str(output/'manual-form-mobile.png'),full_page=True)
                assert page.request.get('http://127.0.0.1:8003/api/x/status').json()['requests_used']==0
                assert not external and not errors,(external,errors)
                browser.close()
                print('PASS: Manual form, multiple accounts, duplicate preservation, N/A and zero counts, sparse warning, source links, 3 angles, approval/download, persistence and mobile layout; no external requests.')
        finally:
            server.terminate();server.wait(timeout=10)


if __name__=='__main__':
    run()
