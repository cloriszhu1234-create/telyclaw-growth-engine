"""Full Live UI workflow against MockTransport; never contacts X or OpenAI.

Run: python tests/live_browser_smoke.py. Uses isolated temporary SQLite + port 8002.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import socket
import sys
import tempfile
import threading
import time

import httpx
from playwright.sync_api import sync_playwright
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import db, x_api
from app.main import app


def run():
    calls = []
    outcome = {'mode': 'success'}
    created = (datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
    def handler(request):
        calls.append(request)
        if outcome['mode']=='credits':
            return httpx.Response(402,json={'title':'CreditsDepleted'})
        if '/by/username/' in request.url.path:
            return httpx.Response(200,json={'data':{'id':'12345'}})
        return httpx.Response(200,json={'data':[
            {'id':'900001','text':'MOCK TEST DATA: AI agents need human approval before content publishing.', 'created_at':created,
             'public_metrics':{'like_count':0,'retweet_count':0,'reply_count':0}},
            {'id':'900002','text':'MOCK TEST DATA: AI agent workflows need approval, customer insight and ownership.', 'created_at':created,
             'referenced_tweets':[{'id':'800001','type':'quoted'}]},
            {'id':'900003','text':'MOCK TEST DATA: Human approval keeps agent marketing workflows accountable.', 'created_at':created,
             'referenced_tweets':[{'id':'800002','type':'replied_to'}]}
        ],'meta':{'result_count':3}})
    # This adapter replacement is in the test process only; it is not a product mode.
    old_client = x_api.client
    x_api.client = lambda:httpx.Client(transport=httpx.MockTransport(handler))
    with tempfile.TemporaryDirectory() as directory:
        keys=('DATABASE_PATH','X_BEARER_TOKEN','X_LIVE_ENABLED','OPENAI_API_KEY')
        previous={key:os.environ.get(key) for key in keys}
        os.environ.update(DATABASE_PATH=str(Path(directory)/'browser.db'), X_BEARER_TOKEN='non-secret-test-placeholder',X_LIVE_ENABLED='true',OPENAI_API_KEY='')
        server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8002,log_level='error'))
        thread=threading.Thread(target=server.run,daemon=True)
        thread.start()
        try:
            for _ in range(100):
                if server.started:break
                time.sleep(.1)
            else:raise RuntimeError('Mock browser server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1440,'height':1100})
                page.route('**/*',lambda route:route.continue_() if route.request.url.startswith('http://127.0.0.1:8002/') else route.abort())
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto('http://127.0.0.1:8002')
                page.locator('.topic').first.wait_for()
                assert page.locator('#mode').input_value()=='demo'
                assert not calls
                page.locator('#mode').select_option('live')
                page.wait_for_function("document.getElementById('live-status').textContent.includes('Ready')")
                assert not calls
                page.locator('#fetch-x').click()
                page.wait_for_function("document.getElementById('live-facts').textContent.includes('Last response: 3 posts')")
                assert len(calls)==2
                page.locator('#fetch-x').click()
                page.wait_for_function("document.getElementById('live-status').textContent.includes('No new X request')")
                assert len(calls)==2
                page.locator('#analyze').click()
                page.locator('.topic').first.wait_for()
                assert page.locator('#posts').inner_text()=='3'
                assert 'not a platform-wide trend' in page.locator('#detail').inner_text()
                page.locator('#detail details').evaluate('(element)=>element.open=true')
                assert page.locator('#detail a').first.get_attribute('href').startswith('https://x.com/elonmusk/status/')
                assert 'N/A' in page.locator('#detail').inner_text()
                page.locator('#generate').click()
                page.locator('#draft-text').wait_for()
                assert page.locator('.angle').count()==3
                assert 'Local editorial templates' in page.locator('#editor').inner_text()
                assert page.locator('#editor .source-links a').count()>0
                page.locator('#approve-draft').click()
                page.locator('#export-draft').wait_for(state='visible')
                with page.expect_download() as download:
                    page.locator('#export-draft').click()
                assert Path(download.value.path()).read_text()
                assert len(calls)==2
                page.locator('[data-tab="opportunities"]').click()
                # Expire only this test's isolated cache/cooldown to exercise a failed refresh.
                with db.connect() as con:
                    row=con.execute('SELECT payload FROM x_accounts WHERE handle=?',('elonmusk',)).fetchone()
                    import json
                    record=json.loads(row['payload']);record['last_fetch']-=901
                    con.execute('UPDATE x_accounts SET payload=? WHERE handle=?',(json.dumps(record),'elonmusk'))
                    con.execute('UPDATE x_control SET next_fetch_at=0 WHERE id=1')
                outcome['mode']='credits'
                page.locator('#fetch-x').click()
                page.wait_for_function("document.getElementById('live-status').textContent.includes('payment or credit restriction')")
                assert 'Cached: 3 unique posts' in page.locator('#live-facts').inner_text()
                assert len(calls)==3
                page.locator('#analyze').click()
                page.locator('.topic').first.wait_for()
                assert page.locator('#posts').inner_text()=='3'
                output=ROOT/'work/browser';output.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(output/'live-mocked-credit-error.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                page.locator('#mode').select_option('demo')
                page.locator('#analyze').click()
                page.wait_for_function("document.getElementById('posts').textContent==='20'")
                assert len(calls)==3 and not errors
                browser.close()
                print('PASS: mocked Live UI: no automatic fetch, 5-post default, cache reuse, attribution, N/A metrics, content/approval/export, credit error with retained cache, mobile layout, Demo switch; zero real X calls.')
        finally:
            server.should_exit=True
            thread.join(timeout=10)
            x_api.client=old_client
            for key,value in previous.items():
                if value is None:os.environ.pop(key,None)
                else:os.environ[key]=value


if __name__=='__main__':
    run()
