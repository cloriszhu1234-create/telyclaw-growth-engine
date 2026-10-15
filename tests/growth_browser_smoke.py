"""Test-only complete Discover → Publish → Measure loop. No external navigation allowed."""
from datetime import datetime,timedelta,timezone
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
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));port=listener.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory() as directory:
        env={**os.environ,'DATABASE_PATH':str(Path(directory)/'growth.db'),'X_LIVE_ENABLED':'false','X_BEARER_TOKEN':'','OPENAI_API_KEY':''}
        server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1',port),timeout=.1):break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Growth test server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
                context=browser.new_context(viewport={'width':1440,'height':1100})
                external=[];errors=[]
                def local_only(route):
                    if route.request.url.startswith(base+'/'):route.continue_()
                    else:external.append(route.request.url);route.fulfill(status=200,content_type="text/html",body="Test-only intercepted composer. Nothing published.")
                context.route('**/*',local_only)
                page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
                page.set_default_timeout(8000);page.set_default_navigation_timeout(8000)
                page.add_init_script("localStorage.setItem('telyclaw.language','en')")
                page.goto(base)
                page.locator('.topic').first.wait_for()
                page.locator('[data-tab="performance"]').click()
                page.wait_for_function("document.getElementById('performance-totals').textContent.includes('Not measured')")
                assert 'No published posts' in page.locator('#measurement-editor').inner_text()
                assert 'Not measured' in page.locator('#performance-totals').inner_text()
                now=datetime.now(timezone.utc)
                texts=[
                    'Multi-agent orchestration needs shared state and reliable tool handoffs.',
                    'Coordinating multiple agents requires shared memory and reliable tool routing.',
                    'Agent teams need coordination, shared state and clear tool handoff ownership.',
                    'AI coding assistants generate software but engineers must review security flaws.',
                    'Programming assistants need code tests and security approval before deployment.',
                    'Developers need secure software evaluation when coding assistants produce code.',
                    'Content attribution should connect product clicks and qualified buyer replies.',
                    'Marketing analytics needs qualified engagement and product click attribution.',
                    'Measuring content outcomes requires qualified replies, product clicks and audience quality.'
                ]
                for i,text in enumerate(texts):
                    r=page.request.post(base+'/api/manual/posts',data={'url':f'https://x.com/test_author_{i}/status/{700000+i}',
                        'handle':f'test_author_{i}','text':'TEST ONLY: '+text,'created_at':(now-timedelta(minutes=30)).isoformat()})
                    assert r.status==201,r.text()
                page.locator('[data-tab="opportunities"]').click()
                page.locator('#mode').select_option('manual');page.locator('#window').select_option('168');page.locator('#analyze').click()
                page.locator('.topic').first.wait_for()
                assert page.locator('.topic').count()<9
                assert 'Insufficient historical data' in page.locator('.topic').first.inner_text()
                for label in ['Why It’s Trending','Why TelyClaw Should Care','Recommended Content Move']:
                    assert label in page.locator('#detail').inner_text()
                output=ROOT/'work/browser';output.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(output/'growth-opportunities.png'),full_page=True)
                page.locator('#generate').click();page.locator('#draft-text').wait_for()
                assert page.locator('.angle').count()==3
                page.locator('#draft-text').fill('Agent orchestration needs a buyer test & clear ownership. Which handoff would you measure? #Growth')
                page.locator('#approve-draft').click()
                page.locator('#publishing-controls a').wait_for()
                # Intercept the external composer before any network contact; inspect its encoded text.
                with context.expect_page() as new_page:
                    page.locator('#publishing-controls a').click()
                popup=new_page.value
                for _ in range(50):
                    if external:break
                    page.wait_for_timeout(20)
                assert external and external[0].startswith('https://twitter.com/intent/tweet?text=')
                assert '%26' in external[0] and '%23Growth' in external[0]
                popup.close()
                assert page.request.get(base+'/api/performance').json()['posts']==[]
                # Editing hides publishing controls until the changed draft is approved again.
                page.locator('#draft-text').fill('Agent orchestration needs a buyer test and accountable ownership. Which handoff matters?')
                assert not page.locator('#publishing-controls').is_visible()
                page.locator('#approve-draft').click();page.locator('#published-url').wait_for()
                when=(now.astimezone(timezone(timedelta(hours=8)))-timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M')
                page.locator('#published-url').fill('https://x.com/test_brand/status/800001')
                page.locator('#published-time').fill(when)
                page.locator('#mark-published').click()
                page.locator('#revision').wait_for()
                assert page.locator('#draft-status').text_content()=='published'
                with page.expect_download() as download:
                    page.locator('#export-draft').click()
                assert Path(download.value.path()).read_text().startswith('Agent orchestration')
                page.locator('[data-tab="performance"]').click()
                page.locator('#metric-likes').wait_for()
                for key,value in {'impressions':'1000','likes':'10','reposts':'2','replies':'3','bookmarks':'5'}.items():
                    page.locator('#metric-'+key).fill(value)
                page.locator('#save-metrics').click()
                page.wait_for_function("document.getElementById('performance-totals').textContent.includes('2%')")
                assert '20' in page.locator('#performance-totals').inner_text()
                assert page.locator('#metric-attributed_followers').input_value()==''
                page.locator('#metric-likes').fill('20');page.locator('#save-metrics').click()
                page.wait_for_function("document.getElementById('performance-totals').textContent.includes('3%')")
                value=page.request.get(base+'/api/performance').json()
                assert value['aggregate']['total_engagement']==30 and len(value['posts'][0]['snapshots'])==2
                assert value['topics'][0]['total_engagement']==30
                page.screenshot(path=str(output/'growth-performance.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                assert not errors,errors
                assert len(external)==1  # composer navigation was intercepted, never sent
                assert page.request.get(base+'/api/x/status').json()['requests_used']==0
                browser.close()
                print('PASS: new growth browser loop: clustering/explanations, three angles, edit/approval, intercepted composer intent, manual publication, TXT export, metric snapshots, post/topic totals, honest empty state and mobile; zero external network requests.')
        finally:
            server.terminate();server.wait(timeout=10)


if __name__=='__main__':run()
